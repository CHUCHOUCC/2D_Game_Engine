from typing import List, Literal

from pydantic import BaseModel, Field, model_validator

MAX_EVENTS = 500
MAX_RUN_MS = 60 * 60 * 1000  # one hour


class PlayEventIn(BaseModel):
    """Something that happened during a run (coin taken, hit, enemy defeated...)."""

    kind: str = Field(min_length=1, max_length=30)
    x: float | None = None
    y: float | None = None
    at_ms: int = Field(default=0, ge=0, le=MAX_RUN_MS)


class RunResult(BaseModel):
    """The numbers the game sends when a run ends. The AI learns from them."""

    outcome: Literal["won", "lost", "quit"]
    score: int = Field(ge=0, le=1_000_000)
    coins_collected: int = Field(ge=0, le=10_000)
    coins_total: int = Field(ge=0, le=10_000)
    enemies_defeated: int = Field(ge=0, le=10_000)
    damage_taken: int = Field(ge=0, le=10_000)
    deaths: int = Field(ge=0, le=1_000)
    duration_ms: int = Field(ge=0, le=MAX_RUN_MS)
    events: List[PlayEventIn] = Field(default_factory=list, max_length=MAX_EVENTS)

    @model_validator(mode="after")
    def collected_not_more_than_total(self):
        if self.coins_collected > self.coins_total:
            raise ValueError("coins_collected cannot exceed coins_total")
        return self

    def summary(self) -> dict:
        """The run without its event list: what the learning model looks at."""
        return self.model_dump(exclude={"events"})
