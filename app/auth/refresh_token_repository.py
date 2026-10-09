from .refresh_token import RefreshToken

_COLUMNS = "id, user_id, token_hash, family_id::text as family_id, expires_at, revoked_at"


class RefreshTokenRepository:
    """Reads and writes the 'refresh_tokens' table with hand-written SQL."""

    def __init__(self, connection):
        self._connection = connection

    def create(self, user_id: int, token_hash: str, family_id: str, expires_at, user_agent: str = "") -> RefreshToken:
        row = self._connection.execute(
            f"insert into refresh_tokens (user_id, token_hash, family_id, expires_at, user_agent) "
            f"values (%s, %s, %s, %s, %s) returning {_COLUMNS}",
            (user_id, token_hash, family_id, expires_at, user_agent[:300]),
        ).fetchone()
        return RefreshToken(**row)

    def find_by_hash(self, token_hash: str):
        row = self._connection.execute(
            f"select {_COLUMNS} from refresh_tokens where token_hash = %s", (token_hash,)
        ).fetchone()
        return RefreshToken(**row) if row else None

    def mark_replaced(self, token_id: int, replaced_by: int) -> None:
        self._connection.execute(
            "update refresh_tokens set revoked_at = now(), replaced_by = %s where id = %s",
            (replaced_by, token_id),
        )

    def revoke(self, token_id: int) -> None:
        self._connection.execute(
            "update refresh_tokens set revoked_at = now() where id = %s and revoked_at is null", (token_id,)
        )

    def revoke_family(self, family_id: str) -> None:
        self._connection.execute(
            "update refresh_tokens set revoked_at = now() where family_id = %s and revoked_at is null",
            (family_id,),
        )

    def revoke_all_for_user(self, user_id: int) -> None:
        self._connection.execute(
            "update refresh_tokens set revoked_at = now() where user_id = %s and revoked_at is null", (user_id,)
        )
