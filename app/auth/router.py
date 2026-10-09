from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field

from .auth_service import AuthService
from .dependencies import bearer_token, current_user, get_auth_service, get_commit
from .errors import EmailAlreadyRegisteredError, InvalidCredentialsError, InvalidTokenError, TooManyAttemptsError
from .user import User

router = APIRouter(prefix="/auth", tags=["auth"])

_EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class RegisterIn(BaseModel):
    username: str = Field(min_length=1, max_length=50, pattern=r"\S")
    email: str = Field(pattern=_EMAIL_PATTERN, max_length=254)
    password: str = Field(min_length=8, max_length=128)


class LoginIn(BaseModel):
    email: str = Field(min_length=1, max_length=254)
    password: str = Field(min_length=1, max_length=128)


class RefreshIn(BaseModel):
    refresh_token: str = Field(min_length=1, max_length=200)


class LogoutIn(BaseModel):
    refresh_token: str | None = Field(default=None, max_length=200)


def _user_json(user: User) -> dict:
    # Never include the salt or the password hash.
    return {"id": user.id, "username": user.username, "email": user.email}


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else ""


@router.post("/register", status_code=201)
def register(body: RegisterIn, service: AuthService = Depends(get_auth_service)):
    try:
        user = service.register(body.username, body.email, body.password)
    except EmailAlreadyRegisteredError:
        raise HTTPException(status_code=409, detail="Email already registered")
    return _user_json(user)


@router.post("/login")
def log_in(body: LoginIn, request: Request, service: AuthService = Depends(get_auth_service),
           commit=Depends(get_commit)):
    try:
        pair = service.log_in(body.email, body.password, _client_ip(request), request.headers.get("user-agent", ""))
    except TooManyAttemptsError:
        raise HTTPException(status_code=429, detail="Too many failed attempts, try again later")
    except InvalidCredentialsError:
        commit()  # keep the failed attempt, or the lockout could never count it
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return pair.to_json()


@router.post("/refresh")
def refresh(body: RefreshIn, request: Request, service: AuthService = Depends(get_auth_service),
            commit=Depends(get_commit)):
    try:
        pair = service.refresh(body.refresh_token, request.headers.get("user-agent", ""))
    except InvalidTokenError:
        commit()  # keep a family revocation caused by a reused token
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    return pair.to_json()


@router.get("/me")
def me(user: User = Depends(current_user)):
    return _user_json(user)


@router.post("/logout", status_code=204)
def log_out(body: LogoutIn | None = None, token: str = Depends(bearer_token),
            service: AuthService = Depends(get_auth_service)):
    service.log_out(token, body.refresh_token if body else None)
    return Response(status_code=204)


@router.post("/logout-all", status_code=204)
def log_out_everywhere(user: User = Depends(current_user), service: AuthService = Depends(get_auth_service)):
    service.log_out_everywhere(user.id)
    return Response(status_code=204)
