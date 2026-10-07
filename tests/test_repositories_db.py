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
from app.auth.session import Session
from app.auth.session_repository import SessionRepository
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


@pytest.fixture
def sessions(connection):
    return SessionRepository(connection)


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


def test_duplicate_email_raises_a_domain_error(users):
    new_user(users)
    with pytest.raises(EmailAlreadyRegisteredError):
        new_user(users)


def test_session_round_trip(users, sessions):
    user = new_user(users)
    expires = datetime.now(timezone.utc) + timedelta(hours=1)
    sessions.create(Session(user.id, "a" * 64, expires))
    found = sessions.find_by_token_hash("a" * 64)
    assert found.user_id == user.id
    assert found.expires_at == expires
    assert found.is_valid() is True


def test_unknown_session_is_none(sessions):
    assert sessions.find_by_token_hash("f" * 64) is None


def test_expired_session_is_stored_but_not_valid(users, sessions):
    user = new_user(users)
    sessions.create(Session(user.id, "b" * 64, datetime.now(timezone.utc) - timedelta(seconds=1)))
    assert sessions.find_by_token_hash("b" * 64).is_valid() is False


def test_delete_session(users, sessions):
    user = new_user(users)
    sessions.create(Session(user.id, "c" * 64, datetime.now(timezone.utc) + timedelta(hours=1)))
    sessions.delete("c" * 64)
    assert sessions.find_by_token_hash("c" * 64) is None
    sessions.delete("c" * 64)  # deleting again must not fail
