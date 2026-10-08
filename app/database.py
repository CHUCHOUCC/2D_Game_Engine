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
