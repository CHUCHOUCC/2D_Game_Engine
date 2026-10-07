import hashlib, secrets, hmac

class PasswordHasher:

    def _hash(self, password: str, salt: bytes) -> bytes:
        return hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1)

    
    def create(self, password):
           salt = secrets.token_bytes(16)
           password_hash = self._hash(password, salt)
           return salt, password_hash

    def verify(self, attempt: str, salt: bytes, stored_hash: bytes) -> bool : 
              
              result = self._hash(attempt, salt)
              is_match = hmac.compare_digest(result,stored_hash)
              return is_match
              
