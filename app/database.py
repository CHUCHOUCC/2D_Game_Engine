import os

import psycopg
from psycopg.rows import dict_row


def get_connection():
    """Open a new connection to the database configured in DATABASE_URL.

    prepare_threshold=None disables server-side prepared statements, which
    Supabase's transaction pooler (pgbouncer) does not support.
    """
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    return psycopg.connect(url, row_factory=dict_row, prepare_threshold=None)


def database_connection():
    """FastAPI dependency: one connection per request, shared by every repository.

    The transaction is committed when the request succeeds and rolled back if it raises.
    """
    with get_connection() as connection:
        yield connection


class LazyConnection:
    """Opens the real connection only on the first query.

    Routes that answer from the cache never touch PostgreSQL, so they should not pay for opening a
    connection either (a new TLS connection to the database on every request).
    """

    def __init__(self, factory=get_connection):
        self._factory = factory
        self._connection = None

    @property
    def opened(self) -> bool:
        return self._connection is not None

    def execute(self, *args, **kwargs):
        if self._connection is None:
            self._connection = self._factory()
        return self._connection.execute(*args, **kwargs)

    def finish(self, failed: bool) -> None:
        if self._connection is None:
            return
        try:
            if failed:
                self._connection.rollback()
            else:
                self._connection.commit()
        finally:
            self._connection.close()
            self._connection = None


def lazy_database_connection():
    """FastAPI dependency like database_connection, but the connection opens on first use."""
    connection = LazyConnection()
    try:
        yield connection
    except BaseException:
        connection.finish(failed=True)
        raise
    connection.finish(failed=False)
