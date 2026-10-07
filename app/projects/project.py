from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Project:
    """A game project: a name, its owner and the scene (a list of game objects)."""

    id: int
    owner_id: int
    name: str
    scene: list
    updated_at: datetime
