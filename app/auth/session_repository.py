from .session import Session


class SessionRepository:
    """Reads and writes the 'sessions' table with hand-written SQL.

    Only the SHA-256 hash of a token is ever stored, never the token itself.
    """

    def __init__(self, connection):
        self._connection = connection

    def create(self, session: Session) -> None:
        self._connection.execute(
            "insert into sessions (token_hash, user_id, expires_at) values (%s, %s, %s)",
            (session.token_hash, session.user_id, session.expires_at),
        )

    def find_by_token_hash(self, token_hash: str):
        row = self._connection.execute(
            "select user_id, token_hash, expires_at from sessions where token_hash = %s",
            (token_hash,),
        ).fetchone()
        if row is None:
            return None
        return Session(row["user_id"], row["token_hash"], row["expires_at"])

    def delete(self, token_hash: str) -> None:
        self._connection.execute("delete from sessions where token_hash = %s", (token_hash,))
