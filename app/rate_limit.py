"""Per-client request limits (sliding window), kept in memory.

Login, registration and the AI are expensive or sensitive, so they get much
lower limits than the rest of the API. Over the limit the API answers 429 with
a Retry-After header. One instance only: several instances would each count
on their own (use a shared store such as Redis if the service is scaled out).
"""
import json
import math
import threading
import time
from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True)
class Rule:
    """At most `limit` requests per `window` seconds for paths starting with `prefix`."""

    name: str
    prefix: str
    limit: int
    window: float
    methods: tuple = ("POST",)

    def matches(self, method: str, path: str) -> bool:
        return path.startswith(self.prefix) and (not self.methods or method in self.methods)


DEFAULT_RULES = (
    Rule("register", "/auth/register", 5, 60),
    Rule("login", "/auth/login", 10, 60),
    Rule("refresh", "/auth/refresh", 30, 60),
    Rule("password", "/auth/password", 5, 300),
    Rule("ai", "/projects/", 20, 60),  # only paths that contain /ai, see _rules_for
    Rule("global", "/", 300, 60, methods=()),
)


class SlidingWindowLimiter:
    """Remembers the time of each request per key and drops the old ones."""

    def __init__(self, clock=time.monotonic):
        self._clock = clock
        self._hits: dict = {}
        self._lock = threading.Lock()

    def hit(self, key: str, limit: int, window: float) -> float:
        """Record a request. Returns 0 if allowed, or the seconds to wait if not."""
        now = self._clock()
        with self._lock:
            hits = self._hits.setdefault(key, deque())
            while hits and hits[0] <= now - window:
                hits.popleft()
            if len(hits) >= limit:
                return max(0.0, hits[0] + window - now)
            hits.append(now)
            return 0.0

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


def client_ip(scope, trusted_proxy_hops: int = 0) -> str:
    """The caller's address. Behind a proxy (Render, Nginx) X-Forwarded-For is
    only trusted for the number of proxies we know are in front of us."""
    if trusted_proxy_hops > 0:
        for name, value in scope.get("headers", []):
            if name == b"x-forwarded-for":
                addresses = [a.strip() for a in value.decode("latin-1").split(",") if a.strip()]
                if len(addresses) >= trusted_proxy_hops:
                    return addresses[-trusted_proxy_hops]
    client = scope.get("client")
    return client[0] if client else "unknown"


class RateLimitMiddleware:
    """ASGI middleware that applies the rules to every HTTP request."""

    def __init__(self, app, limiter: SlidingWindowLimiter, rules=DEFAULT_RULES, trusted_proxy_hops: int = 0):
        self.app = app
        self.limiter = limiter
        self.rules = rules
        self.trusted_proxy_hops = trusted_proxy_hops

    def _rules_for(self, method: str, path: str):
        for rule in self.rules:
            if rule.name == "ai" and "/ai" not in path:
                continue
            if rule.matches(method, path):
                yield rule

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["method"] == "OPTIONS":
            await self.app(scope, receive, send)
            return
        ip = client_ip(scope, self.trusted_proxy_hops)
        for rule in self._rules_for(scope["method"], scope["path"]):
            wait = self.limiter.hit(f"{rule.name}:{ip}", rule.limit, rule.window)
            if wait:
                await _too_many_requests(send, math.ceil(wait))
                return
        await self.app(scope, receive, send)


async def _too_many_requests(send, retry_after: int) -> None:
    body = json.dumps({"detail": "Too many requests, slow down"}).encode()
    await send({
        "type": "http.response.start",
        "status": 429,
        "headers": [
            (b"content-type", b"application/json"),
            (b"retry-after", str(max(1, retry_after)).encode()),
            (b"content-length", str(len(body)).encode()),
        ],
    })
    await send({"type": "http.response.body", "body": body})
