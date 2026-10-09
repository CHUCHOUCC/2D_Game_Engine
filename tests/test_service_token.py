import jwt
import pytest

from app.auth.service_token import ServiceTokenIssuer

KEY = "a-shared-service-secret-of-32-chars!"


def decode(token, audience="ai-service"):
    return jwt.decode(token, KEY, algorithms=["HS256"], audience=audience)


def test_a_short_secret_is_refused():
    with pytest.raises(ValueError):
        ServiceTokenIssuer("short")


def test_token_has_issuer_audience_scope_and_a_one_minute_life():
    claims = decode(ServiceTokenIssuer(KEY).issue())
    assert claims["iss"] == "2d-engine-backend"
    assert claims["aud"] == "ai-service"
    assert claims["sub"] == "backend"
    assert claims["scope"] == "ai"
    assert claims["exp"] - claims["iat"] == 60


def test_token_for_one_audience_is_rejected_by_another():
    token = ServiceTokenIssuer(KEY, audience="ai-service").issue()
    with pytest.raises(jwt.InvalidAudienceError):
        decode(token, audience="billing")


def test_each_token_is_unique():
    issuer = ServiceTokenIssuer(KEY)
    assert len({decode(issuer.issue())["jti"] for _ in range(20)}) == 20
