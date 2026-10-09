import pytest

from app.auth.user import User


def make_user():
    return User(1, "jesus", "j@example.com", b"salt", b"hash")


def test_user_exposes_read_only_values():
    user = make_user()
    assert user.salt == b"salt"
    assert user.password_hash == b"hash"
    assert user.email == "j@example.com"


def test_user_values_cannot_be_overwritten():
    user = make_user()
    with pytest.raises(AttributeError):
        user.password_hash = b"other"


def test_user_repr_hides_secrets():
    text = repr(make_user())
    assert "jesus" in text
    assert "hash" not in text
    assert "salt" not in text
