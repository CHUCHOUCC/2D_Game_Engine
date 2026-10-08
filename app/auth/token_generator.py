import hashlib
import secrets


class TokenGenerator:
    """Random opaque tokens (refresh tokens) and their SHA-256 hash.

    Only the hash is stored in the database, never the token itself.
    """

    def generate(self) -> str:
        return secrets.token_urlsafe(32)

    def hash(self, token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()
