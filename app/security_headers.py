from starlette.middleware.base import BaseHTTPMiddleware

# The API only returns JSON, so the strictest policy is safe.
HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
    "Cache-Control": "no-store",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=()",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Resource-Policy": "same-site",
}
# Browsers must only use HTTPS for a year once they saw the API over HTTPS.
HSTS = "max-age=31536000; includeSubDomains"
# The interactive docs load their own scripts and styles.
DOCS_PATHS = ("/docs", "/redoc", "/openapi.json")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds defensive HTTP headers to every API response."""

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        is_docs = request.url.path.startswith(DOCS_PATHS)
        for name, value in HEADERS.items():
            if is_docs and name == "Content-Security-Policy":
                continue
            response.headers.setdefault(name, value)
        if _is_https(request):
            response.headers.setdefault("Strict-Transport-Security", HSTS)
        return response


def _is_https(request) -> bool:
    """True for HTTPS, also behind a proxy that terminates TLS (Render, Nginx)."""
    forwarded = request.headers.get("x-forwarded-proto", "")
    return request.url.scheme == "https" or forwarded.split(",")[0].strip() == "https"
