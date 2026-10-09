from dataclasses import dataclass


@dataclass(frozen=True)
class TokenPair:
    """What a successful login or refresh returns to the client."""

    access_token: str
    refresh_token: str
    expires_in: int  # seconds until the access token expires

    def to_json(self) -> dict:
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "token_type": "bearer",
            "expires_in": self.expires_in,
        }
