import hashlib
import hmac
import secrets


class PasswordHasher:
    """Salted scrypt hashing for passwords.

    create() returns a fresh (salt, hash) pair; verify() re-hashes the attempt
    with the stored salt and compares in constant time.
    """

    SALT_BYTES = 16

    def _hash(self, password: str, salt: bytes) -> bytes:
        return hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1)

    def create(self, password: str) -> tuple[bytes, bytes]:
        salt = secrets.token_bytes(self.SALT_BYTES)
        return salt, self._hash(password, salt)

    def verify(self, attempt: str, salt: bytes, stored_hash: bytes) -> bool:
        return hmac.compare_digest(self._hash(attempt, salt), stored_hash)
