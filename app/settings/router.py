from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.auth.dependencies import current_user
from app.auth.user import User
from app.database import database_connection
from .repository import SettingsRepository

router = APIRouter(prefix="/me/settings", tags=["settings"])


class SettingsIn(BaseModel):
    """Everything the settings wheel can change."""

    theme: Literal["light", "dark", "system"] = "dark"
    language: Literal["es", "en"] = "es"
    show_grid: bool = True
    snap_to_grid: bool = True
    grid_size: int = Field(default=32, ge=8, le=128)
    music_volume: int = Field(default=70, ge=0, le=100)
    sfx_volume: int = Field(default=80, ge=0, le=100)


def get_settings_repository(connection=Depends(database_connection)) -> SettingsRepository:
    return SettingsRepository(connection)


@router.get("")
def read_settings(repo: SettingsRepository = Depends(get_settings_repository), user: User = Depends(current_user)):
    return repo.get(user.id)


@router.put("")
def save_settings(body: SettingsIn, repo: SettingsRepository = Depends(get_settings_repository),
                  user: User = Depends(current_user)):
    return repo.save(user.id, body.model_dump())
