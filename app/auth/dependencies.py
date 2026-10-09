import os
from functools import lru_cache

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.audit import AuditLog
from app.database import database_connection

from .auth_service import AuthService
from .errors import InvalidTokenError
from .jwt_codec import JwtCodec
from .login_attempt_repository import LoginAttemptRepository
from .password_hasher import PasswordHasher
from .refresh_token_repository import RefreshTokenRepository
from .revoked_token_repository import RevokedTokenRepository
from .token_generator import TokenGenerator
from .user import User
from .user_repository import UserRepository

# auto_error=False: we answer with our own 401 so the message is consistent.
_bearer = HTTPBearer(auto_error=False)


@lru_cache(maxsize=4)
def _codec_for(secret: str) -> JwtCodec:
    return JwtCodec(secret)


def get_jwt_codec() -> JwtCodec:
    """The access-token signer, configured with JWT_SECRET (32+ characters).

    One codec per secret is reused across requests.
    """
    secret = os.environ.get("JWT_SECRET", "")
    if len(secret) < 32:
        raise HTTPException(status_code=503, detail="JWT_SECRET is not configured")
    return _codec_for(secret)


def get_auth_service(connection=Depends(database_connection), jwt_codec: JwtCodec = Depends(get_jwt_codec)) -> AuthService:
    """Build the login service with the real SQL repositories."""
    return AuthService(
        UserRepository(connection),
        RefreshTokenRepository(connection),
        RevokedTokenRepository(connection),
        PasswordHasher(),
        TokenGenerator(),
        jwt_codec,
        attempts=LoginAttemptRepository(connection),
        audit=AuditLog(connection),
    )


def get_commit(connection=Depends(database_connection)):
    """Commit what the request wrote so far.

    An error response rolls the request back. Routes call this first when the
    rows written before the error must survive: a failed login attempt (for the
    lockout) or the revocation of a stolen refresh-token family.
    """
    return connection.commit


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=401,
        detail="Invalid or missing token",
        headers={"WWW-Authenticate": "Bearer"},
    )


def bearer_token(credentials: HTTPAuthorizationCredentials = Depends(_bearer)) -> str:
    """The raw token from the 'Authorization: Bearer <token>' header."""
    if credentials is None:
        raise _unauthorized()
    return credentials.credentials


def current_user(token: str = Depends(bearer_token), service: AuthService = Depends(get_auth_service)) -> User:
    """The logged-in user, or a 401 if the token is invalid, expired or revoked."""
    try:
        return service.user_from_token(token)
    except InvalidTokenError:
        raise _unauthorized()
