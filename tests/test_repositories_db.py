"""Integration tests for the SQL repositories.

They need a real PostgreSQL database with the project's tables. Set TEST_DATABASE_URL
to run them (use a throw-away database, never the production one). Without it they
are skipped, so the normal `pytest` run keeps working with no database.

Every test runs inside a transaction that is rolled back at the end.
"""
import os
from datetime import datetime, timedelta, timezone

import psycopg
import pytest
from psycopg.rows import dict_row

from app.auth.errors import EmailAlreadyRegisteredError
from app.auth.user_repository import UserRepository

DATABASE_URL = os.environ.get("TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(DATABASE_URL is None, reason="TEST_DATABASE_URL is not set")


@pytest.fixture
def connection():
    with psycopg.connect(DATABASE_URL, row_factory=dict_row, prepare_threshold=None) as conn:
        yield conn
        conn.rollback()


@pytest.fixture
def users(connection):
    return UserRepository(connection)



def new_user(users, email="repo-test@example.com"):
    return users.create("repo-test", email, b"\x01" * 16, b"\x02" * 64)


def test_create_user_returns_the_stored_values_as_bytes(users):
    user = new_user(users)
    assert user.id is not None
    assert user.salt == b"\x01" * 16
    assert user.password_hash == b"\x02" * 64
    assert isinstance(user.salt, bytes)


def test_find_user_by_email_and_by_id(users):
    user = new_user(users)
    assert users.find_by_email("repo-test@example.com").id == user.id
    assert users.find_by_id(user.id).email == "repo-test@example.com"
    assert users.find_by_email("nobody@example.com") is None
    assert users.find_by_id(999999999) is None


def test_duplicate_email_raises_a_domain_error(connection, users):
    version = connection.execute("select version() as v").fetchone()["v"]
    if "PGlite" in version:
        pytest.skip("PGlite's socket server drops the connection after a SQL error")
    new_user(users)
    with pytest.raises(EmailAlreadyRegisteredError):
        new_user(users)


# --- JWT login tables -------------------------------------------------------

from app.audit import AuditLog
from app.auth.login_attempt_repository import LoginAttemptRepository
from app.auth.refresh_token_repository import RefreshTokenRepository
from app.auth.revoked_token_repository import RevokedTokenRepository

FAMILY = "11111111-2222-3333-4444-555555555555"


def test_refresh_token_round_trip_and_rotation(connection, users):
    user = new_user(users)
    tokens = RefreshTokenRepository(connection)
    expires = datetime.now(timezone.utc) + timedelta(days=1)
    first = tokens.create(user.id, "r" * 64, FAMILY, expires, "pytest")
    assert tokens.find_by_hash("r" * 64) == first
    assert first.family_id == FAMILY
    assert first.is_usable()
    second = tokens.create(user.id, "s" * 64, FAMILY, expires)
    tokens.mark_replaced(first.id, second.id)
    assert tokens.find_by_hash("r" * 64).revoked_at is not None
    tokens.revoke_family(FAMILY)
    assert tokens.find_by_hash("s" * 64).is_usable() is False


def test_revoke_all_refresh_tokens_of_a_user(connection, users):
    user = new_user(users)
    tokens = RefreshTokenRepository(connection)
    expires = datetime.now(timezone.utc) + timedelta(days=1)
    tokens.create(user.id, "t" * 64, FAMILY, expires)
    tokens.revoke_all_for_user(user.id)
    assert tokens.find_by_hash("t" * 64).revoked_at is not None


def test_revoked_access_tokens(connection, users):
    user = new_user(users)
    revoked = RevokedTokenRepository(connection)
    assert revoked.is_revoked("jti-1") is False
    revoked.revoke("jti-1", user.id, datetime.now(timezone.utc) + timedelta(minutes=5))
    revoked.revoke("jti-1", user.id, datetime.now(timezone.utc) + timedelta(minutes=5))  # twice is fine
    assert revoked.is_revoked("jti-1") is True
    revoked.revoke("jti-old", user.id, datetime.now(timezone.utc) - timedelta(minutes=5))
    assert revoked.purge_expired() >= 1
    assert revoked.is_revoked("jti-old") is False


def test_login_attempts_count_only_recent_failures(connection):
    attempts = LoginAttemptRepository(connection)
    attempts.record("x@example.com", "1.1.1.1", False)
    attempts.record("x@example.com", "1.1.1.1", False)
    attempts.record("x@example.com", "1.1.1.1", True)
    since = datetime.now(timezone.utc) - timedelta(minutes=1)
    assert attempts.failures_since("x@example.com", since) == 2
    assert attempts.failures_since("x@example.com", datetime.now(timezone.utc) + timedelta(minutes=1)) == 0


def test_roles_and_last_login(users):
    user = new_user(users)
    users.add_role(user.id, "creator")
    users.add_role(user.id, "creator")
    users.add_role(user.id, "no-such-role")
    assert users.roles_of(user.id) == ("creator",)
    users.touch_last_login(user.id)


def test_audit_log_records_actions(connection, users):
    user = new_user(users)
    log = AuditLog(connection)
    log.record(user.id, "user.login", "user", user.id, {"ok": True}, "127.0.0.1")
    entries = log.recent_for_user(user.id)
    assert entries[0]["action"] == "user.login"
    assert entries[0]["details"] == {"ok": True}
