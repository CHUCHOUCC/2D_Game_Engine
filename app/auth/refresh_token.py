from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class RefreshToken:
    """A stored refresh token (only its hash) inside a login family."""

    id: int
    user_id: int
    token_hash: str
    family_id: str
    expires_at: datetime
    revoked_at: datetime | None = None

    def is_usable(self) -> bool:
        return self.revoked_at is None and datetime.now(timezone.utc) < self.expires_at
