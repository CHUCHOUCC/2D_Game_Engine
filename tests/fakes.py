"""In-memory stand-ins for the user and session repositories.

They have the same methods as the real SQL repositories, so the login logic
can be tested without a database.
"""
from app.auth.errors import EmailAlreadyRegisteredError
from app.auth.user import User


class FakeUserRepository:

    def __init__(self):
        self._users = {}
        self._next_id = 1

    def create(self, username, email, salt, password_hash):
        if any(u.email == email for u in self._users.values()):
            raise EmailAlreadyRegisteredError(email)
        user = User(self._next_id, username, email, salt, password_hash)
        self._users[user.id] = user
        self._next_id += 1
        return user

    def find_by_email(self, email):
        for user in self._users.values():
            if user.email == email:
                return user
        return None

    def find_by_id(self, user_id):
        return self._users.get(user_id)


class FakeSessionRepository:

    def __init__(self):
        self.sessions = {}

    def create(self, session):
        self.sessions[session.token_hash] = session

    def find_by_token_hash(self, token_hash):
        return self.sessions.get(token_hash)

    def delete(self, token_hash):
        self.sessions.pop(token_hash, None)
