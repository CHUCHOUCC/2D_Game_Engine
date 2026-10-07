
class User:
    def __init__(self,id,username,email,salt,password_hash):
        self.id = id
        self.username = username
        self._salt = salt 
        self._email = email
        self._password_hash = password_hash

    @property
    def salt(self) -> bytes:
        return self._salt

    @property
    def password_hash(self) -> bytes:
        return self._password_hash

    @property
    def email(self) -> str:
        return self._email

    def __repr__(self) -> str:
        return f"User(id={self.id}, username={self.username!r})"

    