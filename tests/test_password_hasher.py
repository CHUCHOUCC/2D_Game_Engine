from app.auth.PasswordHasher import PasswordHasher


def test_create_returns_salt_and_hash_as_bytes():
    salt, password_hash = PasswordHasher().create("abc")
    assert isinstance(salt, bytes)
    assert isinstance(password_hash, bytes)


def test_hash_does_not_contain_the_plain_password():
    salt, password_hash = PasswordHasher().create("abc")
    assert b"abc" not in password_hash
    assert b"abc" not in salt


def test_same_password_gets_different_salt_and_hash_each_time():
    hasher = PasswordHasher()
    salt_1, hash_1 = hasher.create("abc")
    salt_2, hash_2 = hasher.create("abc")
    assert salt_1 != salt_2
    assert hash_1 != hash_2


def test_verify_accepts_the_correct_password():
    hasher = PasswordHasher()
    salt, password_hash = hasher.create("abc")
    assert hasher.verify("abc", salt, password_hash) is True


def test_verify_rejects_a_wrong_password():
    hasher = PasswordHasher()
    salt, password_hash = hasher.create("abc")
    assert hasher.verify("other", salt, password_hash) is False


def test_one_hasher_serves_many_users_independently():
    hasher = PasswordHasher()
    salt_a, hash_a = hasher.create("alpha")
    salt_b, hash_b = hasher.create("beta")
    assert hasher.verify("alpha", salt_a, hash_a)
    assert hasher.verify("beta", salt_b, hash_b)
    assert not hasher.verify("alpha", salt_b, hash_b)