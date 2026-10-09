from datetime import timedelta

import jwt
import pytest

from app.auth.errors import InvalidTokenError
from app.auth.jwt_codec import JwtCodec
from tests.fakes import TEST_JWT_SECRET


def codec(**kwargs):
    return JwtCodec(TEST_JWT_SECRET, **kwargs)


def test_a_short_secret_is_refused():
    with pytest.raises(ValueError):
        JwtCodec("too-short")


def test_issue_and_decode_round_trip():
    token, claims = codec().issue_access(7, ("creator",))
    decoded = codec().decode_access(token)
    assert decoded == claims
    assert decoded.user_id == 7
    assert decoded.roles == ("creator",)


def test_every_token_has_a_unique_id():
    ids = {codec().issue_access(1)[1].jti for _ in range(50)}
    assert len(ids) == 50


def test_a_token_signed_with_another_secret_is_rejected():
    token, _ = JwtCodec("x" * 40).issue_access(1)
    with pytest.raises(InvalidTokenError):
        codec().decode_access(token)


def test_a_tampered_token_is_rejected():
    token, _ = codec().issue_access(1)
    header, payload, signature = token.split(".")
    with pytest.raises(InvalidTokenError):
        codec().decode_access(f"{header}.{payload}x.{signature}")


def test_an_expired_token_is_rejected():
    token, _ = codec(access_duration=timedelta(seconds=-5)).issue_access(1)
    with pytest.raises(InvalidTokenError):
        codec().decode_access(token)


def test_a_token_from_another_issuer_is_rejected():
    token, _ = codec(issuer="someone-else").issue_access(1)
    with pytest.raises(InvalidTokenError):
        codec().decode_access(token)


def test_a_token_of_another_type_is_rejected():
    token = jwt.encode(
        {"sub": "1", "jti": "a", "iss": "2d-engine-backend", "exp": 9999999999, "type": "refresh"},
        TEST_JWT_SECRET,
        algorithm="HS256",
    )
    with pytest.raises(InvalidTokenError):
        codec().decode_access(token)


def test_the_none_algorithm_is_rejected():
    token = jwt.encode(
        {"sub": "1", "jti": "a", "iss": "2d-engine-backend", "exp": 9999999999, "type": "access"},
        key=None,
        algorithm="none",
    )
    with pytest.raises(InvalidTokenError):
        codec().decode_access(token)
