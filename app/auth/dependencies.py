from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.database import database_connection

from .auth_service import AuthService
from .errors import InvalidTokenError
from .password_hasher import PasswordHasher
from .session_repository import SessionRepository
from .token_generator import TokenGenerator
from .user import User
from .user_repository import UserRepository

# auto_error=False: we answer with our own 401 so the message is consistent.
_bearer = HTTPBearer(auto_error=False)


def get_auth_service(connection=Depends(database_connection)) -> AuthService:
    """Build the login service with the real SQL repositories."""
    return AuthService(
        UserRepository(connection),
        SessionRepository(connection),
        PasswordHasher(),
        TokenGenerator(),
    )


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
    """The logged-in user, or a 401 if the token is unknown, expired or logged out."""
    try:
        return service.user_from_token(token)
    except InvalidTokenError:
        raise _unauthorized()
