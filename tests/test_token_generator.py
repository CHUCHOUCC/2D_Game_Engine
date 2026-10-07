import re

from app.auth.token_generator import TokenGenerator


def test_generate_returns_a_long_url_safe_string():
    token = TokenGenerator().generate()
    assert isinstance(token, str)
    assert len(token) >= 40
    assert re.fullmatch(r"[A-Za-z0-9_-]+", token)


def test_each_generated_token_is_different():
    generator = TokenGenerator()
    tokens = {generator.generate() for _ in range(100)}
    assert len(tokens) == 100


def test_hash_is_deterministic():
    generator = TokenGenerator()
    token = generator.generate()
    assert generator.hash(token) == generator.hash(token)


def test_hash_is_64_hex_characters_and_not_the_token():
    generator = TokenGenerator()
    token = generator.generate()
    token_hash = generator.hash(token)
    assert re.fullmatch(r"[0-9a-f]{64}", token_hash)
    assert token_hash != token


def test_different_tokens_have_different_hashes():
    generator = TokenGenerator()
    assert generator.hash("token-a") != generator.hash("token-b")


def test_hash_matches_the_known_sha256_of_a_fixed_input():
    # SHA-256 of the text "abc", a standard reference value.
    expected = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert TokenGenerator().hash("abc") == expected