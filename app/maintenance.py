"""Housekeeping for the login tables.

Usage (PowerShell):  python -m app.maintenance
Safe to run as often as you like (for example once a day as a cron job).
"""
from dotenv import load_dotenv

# Revoked access tokens are only needed until they would have expired anyway.
_PURGE_REVOKED = "delete from revoked_access_tokens where expires_at < now()"
# Refresh tokens are kept 30 days after they expire, for the audit trail.
_PURGE_REFRESH = "delete from refresh_tokens where expires_at < now() - interval '30 days'"
# Login attempts only matter for the lockout window; keep a week of history.
_PURGE_ATTEMPTS = "delete from login_attempts where attempted_at < now() - interval '7 days'"
_PURGE_LEGACY_SESSIONS = "delete from sessions where expires_at < now()"


def purge(connection) -> dict:
    """Delete rows nobody needs any more and return how many went per table."""
    counts = {}
    for table, sql in (
        ("revoked_access_tokens", _PURGE_REVOKED),
        ("refresh_tokens", _PURGE_REFRESH),
        ("login_attempts", _PURGE_ATTEMPTS),
        ("sessions", _PURGE_LEGACY_SESSIONS),
    ):
        counts[table] = connection.execute(sql).rowcount
    connection.commit()
    return counts


def main() -> None:
    from app.database import get_connection

    load_dotenv()
    with get_connection() as connection:
        for table, count in purge(connection).items():
            print(f"{table}: {count} row(s) deleted")


if __name__ == "__main__":
    main()
