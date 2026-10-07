from datetime import timedelta

import pytest

from app.auth.auth_service import AuthService
from app.auth.errors import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    InvalidTokenError,
)
from app.auth.password_hasher import PasswordHasher
from app.auth.token_generator import TokenGenerator
from tests.fakes import FakeSessionRepository, FakeUserRepository


def make_service(session_duration=None):
    users = FakeUserRepository()
    sessions = FakeSessionRepository()
    if session_duration is None:
        service = AuthService(users, sessions, PasswordHasher(), TokenGenerator())
    else:
        service = AuthService(users, sessions, PasswordHasher(), TokenGenerator(), session_duration)
    return service, users, sessions


def registered(service):
    return service.register("jesus", "jesus@example.com", "correct horse")


def test_register_returns_a_user_with_an_id():
    service, _, _ = make_service()
    user = registered(service)
    assert user.id is not None
    assert user.username == "jesus"
    assert user.email == "jesus@example.com"


def test_register_never_stores_the_plain_password():
    service, users, _ = make_service()
    registered(service)
    stored = users.find_by_email("jesus@example.com")
    assert stored.password_hash != b"correct horse"
    assert len(stored.salt) == 16


def test_register_normalizes_the_email():
    service, users, _ = make_service()
    service.register("jesus", "  Jesus@Example.COM ", "correct horse")
    assert users.find_by_email("jesus@example.com") is not None


def test_register_rejects_a_duplicate_email_even_with_other_case():
    service, _, _ = make_service()
    registered(service)
    with pytest.raises(EmailAlreadyRegisteredError):
        service.register("other", "JESUS@example.com", "another password")


def test_log_in_returns_a_token():
    service, _, _ = make_service()
    registered(service)
    token = service.log_in("jesus@example.com", "correct horse")
    assert isinstance(token, str)
    assert len(token) >= 40


def test_log_in_accepts_the_email_in_any_case():
    service, _, _ = make_service()
    registered(service)
    assert service.log_in(" JESUS@example.com", "correct horse")


def test_log_in_stores_only_the_hash_of_the_token():
    service, _, sessions = make_service()
    registered(service)
    token = service.log_in("jesus@example.com", "correct horse")
    assert token not in sessions.sessions
    assert TokenGenerator().hash(token) in sessions.sessions


def test_log_in_with_a_wrong_password_fails():
    service, _, _ = make_service()
    registered(service)
    with pytest.raises(InvalidCredentialsError):
        service.log_in("jesus@example.com", "wrong password")


def test_log_in_with_an_unknown_email_fails_with_the_same_error():
    service, _, _ = make_service()
    with pytest.raises(InvalidCredentialsError):
        service.log_in("nobody@example.com", "whatever")


def test_every_log_in_creates_a_different_token():
    service, _, _ = make_service()
    registered(service)
    first = service.log_in("jesus@example.com", "correct horse")
    second = service.log_in("jesus@example.com", "correct horse")
    assert first != second


def test_user_from_token_returns_the_owner():
    service, _, _ = make_service()
    user = registered(service)
    token = service.log_in("jesus@example.com", "correct horse")
    assert service.user_from_token(token).id == user.id


def test_user_from_token_rejects_an_unknown_token():
    service, _, _ = make_service()
    with pytest.raises(InvalidTokenError):
        service.user_from_token("not-a-real-token")


def test_an_expired_token_is_rejected_and_its_session_removed():
    service, _, sessions = make_service(session_duration=timedelta(seconds=-1))
    registered(service)
    token = service.log_in("jesus@example.com", "correct horse")
    with pytest.raises(InvalidTokenError):
        service.user_from_token(token)
    assert sessions.sessions == {}


def test_log_out_makes_the_token_useless():
    service, _, _ = make_service()
    registered(service)
    token = service.log_in("jesus@example.com", "correct horse")
    service.log_out(token)
    with pytest.raises(InvalidTokenError):
        service.user_from_token(token)


def test_log_out_with_an_unknown_token_does_not_fail():
    service, _, _ = make_service()
    service.log_out("not-a-real-token")
