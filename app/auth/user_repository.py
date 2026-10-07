import psycopg.errors

from .errors import EmailAlreadyRegisteredError
from .user import User

_COLUMNS = "id, username, email, salt, password_hash"


def _to_user(row) -> User:
    # bytea columns can come back as memoryview; User expects plain bytes.
    return User(row["id"], row["username"], row["email"], bytes(row["salt"]), bytes(row["password_hash"]))


class UserRepository:
    """Reads and writes the 'users' table with hand-written SQL."""

    def __init__(self, connection):
        self._connection = connection

    def create(self, username: str, email: str, salt: bytes, password_hash: bytes) -> User:
        try:
            row = self._connection.execute(
                f"insert into users (username, email, salt, password_hash) "
                f"values (%s, %s, %s, %s) returning {_COLUMNS}",
                (username, email, salt, password_hash),
            ).fetchone()
        except psycopg.errors.UniqueViolation:
            raise EmailAlreadyRegisteredError(email)
        return _to_user(row)

    def find_by_email(self, email: str):
        row = self._connection.execute(
            f"select {_COLUMNS} from users where email = %s", (email,)
        ).fetchone()
        return _to_user(row) if row else None

    def find_by_id(self, user_id: int):
        row = self._connection.execute(
            f"select {_COLUMNS} from users where id = %s", (user_id,)
        ).fetchone()
        return _to_user(row) if row else None
