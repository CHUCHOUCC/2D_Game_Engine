"""A request id on every request and response, an access log line without
secrets, and a generic 500 answer that never leaks internal details."""
import json
import logging
import re
import time
import uuid

logger = logging.getLogger("app.access")

# Accept the caller's id only if it is short and harmless (it ends up in logs).
_SAFE_ID = re.compile(r"^[A-Za-z0-9._-]{8,64}$")


def request_id_of(scope) -> str:
    for name, value in scope.get("headers", []):
        if name == b"x-request-id":
            candidate = value.decode("latin-1")
            if _SAFE_ID.match(candidate):
                return candidate
    return uuid.uuid4().hex


class RequestContextMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        rid = request_id_of(scope)
        scope.setdefault("state", {})["request_id"] = rid
        started = time.perf_counter()
        status = {"code": 500}

        async def send_with_id(message):
            if message["type"] == "http.response.start":
                status["started"] = True
                status["code"] = message["status"]
                message.setdefault("headers", []).append((b"x-request-id", rid.encode()))
            await send(message)

        try:
            await self.app(scope, receive, send_with_id)
        except Exception as error:
            # Answered here (inside CORS) instead of by Starlette's outermost error
            # middleware, so the browser can read the 500 and its request id.
            logger.exception("Unhandled error rid=%s", rid, exc_info=error)
            if status.get("started"):
                raise
            await _internal_error(send_with_id, rid)
        finally:
            # Path only: query strings may carry data we do not want in logs.
            logger.info(
                "%s %s %s %.1fms rid=%s",
                scope["method"], scope["path"], status["code"], (time.perf_counter() - started) * 1000, rid,
            )


async def _internal_error(send, rid: str) -> None:
    """Tell the client nothing internal: only that it failed and the id to report."""
    body = json.dumps({"detail": "Internal server error", "request_id": rid}).encode()
    await send({
        "type": "http.response.start",
        "status": 500,
        "headers": [(b"content-type", b"application/json"), (b"content-length", str(len(body)).encode())],
    })
    await send({"type": "http.response.body", "body": body})
