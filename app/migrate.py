"""Apply the SQL files in migrations/ that the database has not run yet.

Usage (PowerShell):  python -m app.migrate
Each file runs in its own transaction and is recorded in schema_migrations,
so running the command twice is safe.
"""
import pathlib

from dotenv import load_dotenv

MIGRATIONS_DIR = pathlib.Path(__file__).resolve().parent.parent / "migrations"

_CREATE_TRACKING_TABLE = """
create table if not exists schema_migrations (
    name       text        primary key,
    applied_at timestamptz not null default now()
)
"""


def migration_files(directory: pathlib.Path = MIGRATIONS_DIR) -> list:
    """The migration files, in the order they must run (by their number prefix)."""
    return sorted(directory.glob("*.sql"))


def applied_names(connection) -> set:
    rows = connection.execute("select name from schema_migrations").fetchall()
    return {row["name"] for row in rows}


def apply_pending(connection, directory: pathlib.Path = MIGRATIONS_DIR) -> list:
    """Run every pending migration and return the names that were applied."""
    connection.execute(_CREATE_TRACKING_TABLE)
    connection.commit()
    done = applied_names(connection)
    applied = []
    for path in migration_files(directory):
        if path.stem in done:
            continue
        with connection.transaction():
            connection.execute(path.read_text(encoding="utf-8"))
            connection.execute("insert into schema_migrations (name) values (%s)", (path.stem,))
        applied.append(path.stem)
    return applied


def main() -> None:
    from app.database import get_connection

    load_dotenv()
    with get_connection() as connection:
        applied = apply_pending(connection)
    print(f"{len(applied)} migration(s) applied")
    for name in applied:
        print(f"  {name}")


if __name__ == "__main__":
    main()
