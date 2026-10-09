"""Rules a new password must follow, with a reason the client can show.

Length matters more than symbols (NIST SP 800-63B), so the policy asks for
8+ characters, some variety, and refuses well-known and personal passwords.
"""
import re

MIN_LENGTH = 8
MAX_LENGTH = 128

# A short list of the most used passwords (the full lists have millions).
COMMON_PASSWORDS = frozenset({
    "password", "password1", "password123", "12345678", "123456789", "1234567890", "qwerty123",
    "qwertyuiop", "11111111", "00000000", "iloveyou", "sunshine", "princess", "football",
    "baseball", "welcome1", "admin123", "letmein1", "dragon123", "monkey123", "abc12345",
    "contrasena", "contraseña", "123123123", "passw0rd", "superman", "trustno1", "starwars",
    "asdfghjkl", "zaq12wsx", "1q2w3e4r", "q1w2e3r4", "aa123456", "computer", "whatever",
    "qazwsx123", "michelle", "jennifer", "corvette", "mustang1", "shadow12", "master12",
})


class WeakPasswordError(ValueError):
    """The password breaks the policy; the message says why."""


def check_password(password: str, email: str = "", username: str = "") -> None:
    """Raise WeakPasswordError when the password is not acceptable."""
    if len(password) < MIN_LENGTH:
        raise WeakPasswordError(f"Password must have at least {MIN_LENGTH} characters")
    if len(password) > MAX_LENGTH:
        raise WeakPasswordError(f"Password must have at most {MAX_LENGTH} characters")
    lowered = password.lower()
    if lowered in COMMON_PASSWORDS:
        raise WeakPasswordError("Password is too common")
    if len(set(password)) < 4:
        raise WeakPasswordError("Password repeats too few characters")
    if re.fullmatch(r"\d+", password):
        raise WeakPasswordError("Password cannot be only numbers")
    personal = [email.split("@")[0].lower(), username.lower()]
    if any(len(part) >= 4 and part in lowered for part in personal):
        raise WeakPasswordError("Password cannot contain your email or username")
