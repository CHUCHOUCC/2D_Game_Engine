class User:

    def __init__(self, id: int | None, username: str, email: str,
                 salt: bytes, password_hash: bytes):
        self.id = id
        self.username = username
        self._email = email
        self._salt = salt
        self._password_hash = password_hash

    @property
    def email(self) -> str:
        return self._email

    @property
    def salt(self) -> bytes:
        return self._salt

    @property
    def password_hash(self) -> bytes:
        return self._password_hash

    def __repr__(self) -> str:
        return f"User(id={self.id}, username={self.username!r})"
