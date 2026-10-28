"""Rejects request bodies bigger than a limit (413) before the app reads them.

A scene of 1500 objects is about 150 KB, so 1 MB leaves plenty of room while
stopping clients that try to exhaust memory with huge uploads.
"""
import json

MAX_BODY_BYTES = 1_000_000


class BodyTooLarge(Exception):
    pass


class BodyLimitMiddleware:
    def __init__(self, app, max_bytes: int = MAX_BODY_BYTES):
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        for name, value in scope.get("headers", []):
            if name == b"content-length" and value.isdigit() and int(value) > self.max_bytes:
                await _payload_too_large(send)
                return

        received = 0

        async def limited_receive():
            # Also counts bodies sent without Content-Length (chunked).
            nonlocal received
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > self.max_bytes:
                    raise BodyTooLarge()
            return message

        try:
            await self.app(scope, limited_receive, send)
        except BodyTooLarge:
            await _payload_too_large(send)


async def _payload_too_large(send) -> None:
    body = json.dumps({"detail": "Request body too large"}).encode()
    await send({
        "type": "http.response.start",
        "status": 413,
        "headers": [(b"content-type", b"application/json"), (b"content-length", str(len(body)).encode())],
    })
    await send({"type": "http.response.body", "body": body})
