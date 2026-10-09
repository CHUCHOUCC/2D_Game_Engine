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
        # A plain SQL savepoint keeps the request's transaction usable after a
        # duplicate email without committing it early.
        self._connection.execute("savepoint create_user")
        try:
            row = self._connection.execute(
                f"insert into users (username, email, salt, password_hash) "
                f"values (%s, %s, %s, %s) returning {_COLUMNS}",
                (username, email, salt, password_hash),
            ).fetchone()
        except psycopg.errors.UniqueViolation:
            self._connection.execute("rollback to savepoint create_user")
            raise EmailAlreadyRegisteredError(email)
        self._connection.execute("release savepoint create_user")
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

    def add_role(self, user_id: int, role_name: str) -> None:
        """Grant a role by name. Unknown role names are ignored."""
        self._connection.execute(
            "insert into user_roles (user_id, role_id) select %s, id from roles where name = %s "
            "on conflict do nothing",
            (user_id, role_name),
        )

    def roles_of(self, user_id: int) -> tuple:
        rows = self._connection.execute(
            "select r.name from user_roles ur join roles r on r.id = ur.role_id "
            "where ur.user_id = %s order by r.name",
            (user_id,),
        ).fetchall()
        return tuple(row["name"] for row in rows)

    def touch_last_login(self, user_id: int) -> None:
        self._connection.execute("update users set last_login_at = now() where id = %s", (user_id,))
