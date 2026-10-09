import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import jwt

from .errors import InvalidTokenError

ALGORITHM = "HS256"
ACCESS_TOKEN_TYPE = "access"


@dataclass(frozen=True)
class AccessClaims:
    """What the backend trusts after checking an access token's signature."""

    user_id: int
    jti: str
    expires_at: datetime
    roles: tuple


class JwtCodec:
    """Signs and checks short-lived access tokens (JWT, HS256).

    The token carries the user id ("sub"), a unique id ("jti") so it can be
    revoked before it expires, and the user's roles.
    """

    def __init__(self, secret: str, issuer: str = "2d-engine-backend",
                 access_duration: timedelta = timedelta(minutes=15)):
        if len(secret) < 32:
            raise ValueError("JWT secret must have at least 32 characters")
        self._secret = secret
        self._issuer = issuer
        self.access_duration = access_duration

    def issue_access(self, user_id: int, roles=()) -> tuple[str, AccessClaims]:
        # JWT times are whole seconds; drop the microseconds so claims round-trip.
        now = datetime.now(timezone.utc).replace(microsecond=0)
        claims = AccessClaims(user_id, uuid.uuid4().hex, now + self.access_duration, tuple(roles))
        payload = {
            "sub": str(user_id),
            "jti": claims.jti,
            "iss": self._issuer,
            "iat": now,
            "exp": claims.expires_at,
            "type": ACCESS_TOKEN_TYPE,
            "roles": list(claims.roles),
        }
        return jwt.encode(payload, self._secret, algorithm=ALGORITHM), claims

    def decode_access(self, token: str) -> AccessClaims:
        try:
            payload = jwt.decode(
                token,
                self._secret,
                algorithms=[ALGORITHM],
                issuer=self._issuer,
                options={"require": ["sub", "jti", "exp", "iss", "type"]},
            )
        except jwt.PyJWTError as error:
            raise InvalidTokenError(type(error).__name__) from error
        if payload.get("type") != ACCESS_TOKEN_TYPE:
            raise InvalidTokenError("not an access token")
        try:
            user_id = int(payload["sub"])
        except ValueError as error:
            raise InvalidTokenError("bad subject") from error
        expires_at = datetime.fromtimestamp(payload["exp"], timezone.utc)
        return AccessClaims(user_id, payload["jti"], expires_at, tuple(payload.get("roles", ())))
