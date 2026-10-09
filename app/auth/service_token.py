import uuid
from datetime import datetime, timedelta, timezone

import jwt

SERVICE_ISSUER = "2d-engine-backend"
AI_AUDIENCE = "ai-service"


class ServiceTokenIssuer:
    """Signs very short-lived JWTs the backend sends to internal services.

    The AI service checks the signature, the audience and the expiry, so a
    leaked token is useless after a minute and only works against that service.
    """

    def __init__(self, secret: str, audience: str = AI_AUDIENCE, lifetime: timedelta = timedelta(seconds=60)):
        if len(secret) < 32:
            raise ValueError("Service secret must have at least 32 characters")
        self._secret = secret
        self._audience = audience
        self._lifetime = lifetime

    def issue(self, subject: str = "backend", scope: str = "ai") -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "iss": SERVICE_ISSUER,
            "aud": self._audience,
            "sub": subject,
            "scope": scope,
            "jti": uuid.uuid4().hex,
            "iat": now,
            "exp": now + self._lifetime,
        }
        return jwt.encode(payload, self._secret, algorithm="HS256")
