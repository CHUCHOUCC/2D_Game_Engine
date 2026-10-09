from datetime import timedelta

import pytest

from app.auth.errors import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    InvalidTokenError,
    TooManyAttemptsError,
)
from app.auth.token_generator import TokenGenerator
from tests.fakes import AuthFixture

PASSWORD = "correct horse"


def registered(fixture):
    return fixture.service.register("jesus", "jesus@example.com", PASSWORD)


def logged_in(fixture):
    registered(fixture)
    return fixture.service.log_in("jesus@example.com", PASSWORD)


def test_register_returns_a_user_with_an_id():
    user = registered(AuthFixture())
    assert user.id is not None
    assert user.username == "jesus"
    assert user.email == "jesus@example.com"


def test_register_never_stores_the_plain_password():
    fixture = AuthFixture()
    registered(fixture)
    stored = fixture.users.find_by_email("jesus@example.com")
    assert stored.password_hash != PASSWORD.encode()
    assert len(stored.salt) == 16


def test_register_normalizes_the_email_and_trims_the_username():
    fixture = AuthFixture()
    fixture.service.register("  jesus ", "  Jesus@Example.COM ", PASSWORD)
    user = fixture.users.find_by_email("jesus@example.com")
    assert user is not None
    assert user.username == "jesus"


def test_register_rejects_a_duplicate_email_even_with_other_case():
    fixture = AuthFixture()
    registered(fixture)
    with pytest.raises(EmailAlreadyRegisteredError):
        fixture.service.register("other", "JESUS@example.com", "another password")


def test_register_grants_the_creator_role():
    fixture = AuthFixture()
    user = registered(fixture)
    assert fixture.users.roles_of(user.id) == ("creator",)


def test_log_in_returns_an_access_and_a_refresh_token():
    pair = logged_in(AuthFixture())
    assert pair.access_token.count(".") == 2  # header.payload.signature
    assert len(pair.refresh_token) >= 40
    assert pair.expires_in == 15 * 60


def test_access_token_carries_the_user_and_roles():
    fixture = AuthFixture()
    pair = logged_in(fixture)
    claims = fixture.jwt.decode_access(pair.access_token)
    assert claims.user_id == 1
    assert claims.roles == ("creator",)


def test_log_in_accepts_the_email_in_any_case():
    fixture = AuthFixture()
    registered(fixture)
    assert fixture.service.log_in(" JESUS@example.com", PASSWORD)


def test_log_in_stores_only_the_hash_of_the_refresh_token():
    fixture = AuthFixture()
    pair = logged_in(fixture)
    stored = list(fixture.refresh_tokens.tokens.values())
    assert [t.token_hash for t in stored] == [TokenGenerator().hash(pair.refresh_token)]


def test_log_in_with_a_wrong_password_fails():
    fixture = AuthFixture()
    registered(fixture)
    with pytest.raises(InvalidCredentialsError):
        fixture.service.log_in("jesus@example.com", "wrong password")


def test_log_in_with_an_unknown_email_fails_with_the_same_error():
    with pytest.raises(InvalidCredentialsError):
        AuthFixture().service.log_in("nobody@example.com", "whatever")


def test_every_log_in_creates_different_tokens():
    fixture = AuthFixture()
    registered(fixture)
    first = fixture.service.log_in("jesus@example.com", PASSWORD)
    second = fixture.service.log_in("jesus@example.com", PASSWORD)
    assert first.access_token != second.access_token
    assert first.refresh_token != second.refresh_token


def test_failed_and_successful_logins_are_recorded():
    fixture = AuthFixture()
    registered(fixture)
    with pytest.raises(InvalidCredentialsError):
        fixture.service.log_in("jesus@example.com", "nope", ip_address="1.2.3.4")
    fixture.service.log_in("jesus@example.com", PASSWORD)
    assert [(a[1], a[2]) for a in fixture.attempts.attempts] == [("1.2.3.4", False), ("", True)]
    assert fixture.users.last_logins == [1]


def test_too_many_failures_lock_the_account_even_with_the_right_password():
    fixture = AuthFixture()
    registered(fixture)
    for _ in range(5):
        with pytest.raises(InvalidCredentialsError):
            fixture.service.log_in("jesus@example.com", "wrong password")
    with pytest.raises(TooManyAttemptsError):
        fixture.service.log_in("jesus@example.com", PASSWORD)


def test_user_from_token_returns_the_owner():
    fixture = AuthFixture()
    pair = logged_in(fixture)
    assert fixture.service.user_from_token(pair.access_token).id == 1


def test_user_from_token_rejects_garbage_and_refresh_tokens():
    fixture = AuthFixture()
    pair = logged_in(fixture)
    with pytest.raises(InvalidTokenError):
        fixture.service.user_from_token("not-a-real-token")
    with pytest.raises(InvalidTokenError):
        fixture.service.user_from_token(pair.refresh_token)


def test_an_expired_access_token_is_rejected():
    fixture = AuthFixture(jwt_options={"access_duration": timedelta(seconds=-1)})
    pair = logged_in(fixture)
    with pytest.raises(InvalidTokenError):
        fixture.service.user_from_token(pair.access_token)


def test_refresh_rotates_the_refresh_token():
    fixture = AuthFixture()
    first = logged_in(fixture)
    second = fixture.service.refresh(first.refresh_token)
    assert second.refresh_token != first.refresh_token
    assert fixture.service.user_from_token(second.access_token).id == 1


def test_reusing_a_rotated_refresh_token_revokes_the_whole_family():
    fixture = AuthFixture()
    first = logged_in(fixture)
    second = fixture.service.refresh(first.refresh_token)
    with pytest.raises(InvalidTokenError):
        fixture.service.refresh(first.refresh_token)
    with pytest.raises(InvalidTokenError):
        fixture.service.refresh(second.refresh_token)
    assert (1, "token.reuse_detected") in fixture.audit.entries


def test_an_expired_refresh_token_is_rejected():
    fixture = AuthFixture(refresh_duration=timedelta(seconds=-1))
    pair = logged_in(fixture)
    with pytest.raises(InvalidTokenError):
        fixture.service.refresh(pair.refresh_token)


def test_unknown_refresh_token_is_rejected():
    with pytest.raises(InvalidTokenError):
        AuthFixture().service.refresh("made-up")


def test_log_out_makes_both_tokens_useless():
    fixture = AuthFixture()
    pair = logged_in(fixture)
    fixture.service.log_out(pair.access_token, pair.refresh_token)
    with pytest.raises(InvalidTokenError):
        fixture.service.user_from_token(pair.access_token)
    with pytest.raises(InvalidTokenError):
        fixture.service.refresh(pair.refresh_token)


def test_log_out_with_unknown_tokens_does_not_fail():
    AuthFixture().service.log_out("not-a-real-token", "nor-this")


def test_log_out_cannot_revoke_another_users_refresh_token():
    fixture = AuthFixture()
    alice = logged_in(fixture)
    fixture.service.register("bob", "bob@example.com", PASSWORD)
    bob = fixture.service.log_in("bob@example.com", PASSWORD)
    fixture.service.log_out(bob.access_token, alice.refresh_token)
    assert fixture.service.refresh(alice.refresh_token)


def test_log_out_everywhere_revokes_every_refresh_token():
    fixture = AuthFixture()
    registered(fixture)
    one = fixture.service.log_in("jesus@example.com", PASSWORD)
    two = fixture.service.log_in("jesus@example.com", PASSWORD)
    fixture.service.log_out_everywhere(1)
    for pair in (one, two):
        with pytest.raises(InvalidTokenError):
            fixture.service.refresh(pair.refresh_token)


def test_one_address_failing_on_many_emails_is_locked_out():
    fixture = AuthFixture()
    registered(fixture)
    for n in range(20):
        with pytest.raises(InvalidCredentialsError):
            fixture.service.log_in(f"guess{n}@example.com", "x", ip_address="6.6.6.6")
    with pytest.raises(TooManyAttemptsError):
        fixture.service.log_in("jesus@example.com", PASSWORD, ip_address="6.6.6.6")
    assert fixture.service.log_in("jesus@example.com", PASSWORD, ip_address="1.1.1.1")
