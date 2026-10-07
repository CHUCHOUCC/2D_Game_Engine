from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field

from .auth_service import AuthService
from .dependencies import bearer_token, current_user, get_auth_service
from .errors import EmailAlreadyRegisteredError, InvalidCredentialsError
from .user import User

router = APIRouter(prefix="/auth", tags=["auth"])

_EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class RegisterIn(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: str = Field(pattern=_EMAIL_PATTERN, max_length=254)
    password: str = Field(min_length=8, max_length=128)


class LoginIn(BaseModel):
    email: str = Field(min_length=1, max_length=254)
    password: str = Field(min_length=1, max_length=128)


def _user_json(user: User) -> dict:
    # Never include the salt or the password hash.
    return {"id": user.id, "username": user.username, "email": user.email}


@router.post("/register", status_code=201)
def register(body: RegisterIn, service: AuthService = Depends(get_auth_service)):
    try:
        user = service.register(body.username, body.email, body.password)
    except EmailAlreadyRegisteredError:
        raise HTTPException(status_code=409, detail="Email already registered")
    return _user_json(user)


@router.post("/login")
def log_in(body: LoginIn, service: AuthService = Depends(get_auth_service)):
    try:
        token = service.log_in(body.email, body.password)
    except InvalidCredentialsError:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
def me(user: User = Depends(current_user)):
    return _user_json(user)


@router.post("/logout", status_code=204)
def log_out(token: str = Depends(bearer_token), service: AuthService = Depends(get_auth_service)):
    service.log_out(token)
    return Response(status_code=204)
