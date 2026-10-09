from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.audit import AuditLog
from app.auth.dependencies import current_user
from app.auth.user import User
from app.database import database_connection

router = APIRouter(prefix="/me", tags=["profile"])

_FIELDS = ("display_name", "avatar_url", "bio", "country")


class ProfileIn(BaseModel):
    display_name: str = Field(default="", max_length=50)
    avatar_url: str = Field(default="", max_length=300, pattern=r"^(https://\S+)?$")
    bio: str = Field(default="", max_length=500)
    country: str = Field(default="", max_length=56)


class ProfileRepository:
    """The 'user_profiles' table: optional public details of a user."""

    def __init__(self, connection):
        self._connection = connection

    def get(self, user_id: int) -> dict:
        row = self._connection.execute(
            f"select {', '.join(_FIELDS)} from user_profiles where user_id = %s", (user_id,)
        ).fetchone()
        return dict(row) if row else {field: "" for field in _FIELDS}

    def save(self, user_id: int, profile: dict) -> dict:
        updates = ", ".join(f"{f} = excluded.{f}" for f in _FIELDS)
        row = self._connection.execute(
            f"insert into user_profiles (user_id, {', '.join(_FIELDS)}) values (%s, %s, %s, %s, %s) "
            f"on conflict (user_id) do update set {updates} returning {', '.join(_FIELDS)}",
            (user_id, *(profile[f] for f in _FIELDS)),
        ).fetchone()
        return dict(row)


def get_profiles(connection=Depends(database_connection)) -> ProfileRepository:
    return ProfileRepository(connection)


def get_audit_log(connection=Depends(database_connection)) -> AuditLog:
    return AuditLog(connection)


@router.get("/profile")
def read_profile(profiles: ProfileRepository = Depends(get_profiles), user: User = Depends(current_user)):
    return {"username": user.username, "email": user.email, **profiles.get(user.id)}


@router.put("/profile")
def save_profile(body: ProfileIn, profiles: ProfileRepository = Depends(get_profiles),
                 user: User = Depends(current_user)):
    return {"username": user.username, "email": user.email, **profiles.save(user.id, body.model_dump())}


@router.get("/activity")
def my_activity(audit: AuditLog = Depends(get_audit_log), user: User = Depends(current_user)):
    """The latest security events of the account (logins, logouts, token reuse)."""
    return [
        {"action": row["action"], "created_at": row["created_at"].isoformat()}
        for row in audit.recent_for_user(user.id, limit=20)
    ]
