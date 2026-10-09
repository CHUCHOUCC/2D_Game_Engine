"""In-memory stand-ins for the login repositories.

They have the same methods as the real SQL repositories, so the login logic
can be tested without a database.
"""
from dataclasses import replace
from datetime import datetime, timezone

from app.auth.auth_service import AuthService
from app.auth.errors import EmailAlreadyRegisteredError
from app.auth.jwt_codec import JwtCodec
from app.auth.password_hasher import PasswordHasher
from app.auth.refresh_token import RefreshToken
from app.auth.token_generator import TokenGenerator
from app.auth.user import User

TEST_JWT_SECRET = "test-secret-that-is-long-enough-for-hs256"


class FakeUserRepository:

    def __init__(self):
        self._users = {}
        self._roles = {}
        self._next_id = 1
        self.last_logins = []

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

    def add_role(self, user_id, role_name):
        self._roles.setdefault(user_id, set()).add(role_name)

    def roles_of(self, user_id):
        return tuple(sorted(self._roles.get(user_id, ())))

    def touch_last_login(self, user_id):
        self.last_logins.append(user_id)


class FakeRefreshTokenRepository:

    def __init__(self):
        self.tokens = {}
        self._next_id = 1

    def create(self, user_id, token_hash, family_id, expires_at, user_agent=""):
        token = RefreshToken(self._next_id, user_id, token_hash, family_id, expires_at)
        self.tokens[token.id] = token
        self._next_id += 1
        return token

    def find_by_hash(self, token_hash):
        return next((t for t in self.tokens.values() if t.token_hash == token_hash), None)

    def _revoke_where(self, condition):
        now = datetime.now(timezone.utc)
        for token_id, token in list(self.tokens.items()):
            if condition(token) and token.revoked_at is None:
                self.tokens[token_id] = replace(token, revoked_at=now)

    def mark_replaced(self, token_id, replaced_by):
        self._revoke_where(lambda t: t.id == token_id)

    def revoke(self, token_id):
        self._revoke_where(lambda t: t.id == token_id)

    def revoke_family(self, family_id):
        self._revoke_where(lambda t: t.family_id == family_id)

    def revoke_all_for_user(self, user_id):
        self._revoke_where(lambda t: t.user_id == user_id)


class FakeRevokedTokenRepository:

    def __init__(self):
        self.revoked = {}

    def revoke(self, jti, user_id, expires_at):
        self.revoked[jti] = (user_id, expires_at)

    def is_revoked(self, jti):
        return jti in self.revoked


class FakeLoginAttempts:

    def __init__(self):
        self.attempts = []

    def record(self, email, ip_address, succeeded):
        self.attempts.append((email, ip_address, succeeded, datetime.now(timezone.utc)))

    def failures_since(self, email, since):
        return sum(1 for e, _, ok, at in self.attempts if e == email and not ok and at >= since)

    def failures_from_ip_since(self, ip_address, since):
        return sum(1 for _, ip, ok, at in self.attempts if ip == ip_address and not ok and at >= since)


class FakeAuditLog:

    def __init__(self):
        self.entries = []

    def record(self, user_id, action, entity_type="", entity_id="", details=None, ip_address=""):
        self.entries.append((user_id, action))


class AuthFixture:
    """A real AuthService wired to in-memory repositories."""

    def __init__(self, **kwargs):
        self.users = FakeUserRepository()
        self.refresh_tokens = FakeRefreshTokenRepository()
        self.revoked = FakeRevokedTokenRepository()
        self.attempts = FakeLoginAttempts()
        self.audit = FakeAuditLog()
        self.jwt = JwtCodec(TEST_JWT_SECRET, **kwargs.pop("jwt_options", {}))
        self.service = AuthService(
            self.users, self.refresh_tokens, self.revoked, PasswordHasher(), TokenGenerator(), self.jwt,
            attempts=self.attempts, audit=self.audit, **kwargs,
        )
