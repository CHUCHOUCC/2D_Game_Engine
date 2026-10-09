class RevokedTokenRepository:
    """The 'revoked_access_tokens' table: access tokens killed before they expire."""

    def __init__(self, connection):
        self._connection = connection

    def revoke(self, jti: str, user_id: int, expires_at) -> None:
        self._connection.execute(
            "insert into revoked_access_tokens (jti, user_id, expires_at) values (%s, %s, %s) "
            "on conflict (jti) do nothing",
            (jti, user_id, expires_at),
        )

    def is_revoked(self, jti: str) -> bool:
        row = self._connection.execute(
            "select 1 from revoked_access_tokens where jti = %s", (jti,)
        ).fetchone()
        return row is not None

    def purge_expired(self) -> int:
        """Delete rows whose token would be rejected anyway; returns how many."""
        cursor = self._connection.execute("delete from revoked_access_tokens where expires_at < now()")
        return cursor.rowcount
