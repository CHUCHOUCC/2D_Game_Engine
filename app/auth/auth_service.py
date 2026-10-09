import uuid
from datetime import datetime, timedelta, timezone

from .errors import InvalidCredentialsError, InvalidTokenError, TooManyAttemptsError
from .token_pair import TokenPair

# How long a refresh token stays valid; the access token lives much less (JwtCodec).
REFRESH_DURATION = timedelta(days=7)
# After this many failed logins in LOCKOUT_WINDOW the email is locked for a while.
MAX_FAILED_LOGINS = 5
# One address trying many emails is also slowed down.
MAX_FAILED_LOGINS_PER_IP = 20
LOCKOUT_WINDOW = timedelta(minutes=15)
DEFAULT_ROLE = "creator"


class AuthService:
    """Register, log in, refresh and log out. The login rules live here.

    - Access tokens are short JWTs; logging out revokes their id (jti).
    - Refresh tokens are random strings; only their hash is stored. Each use
      rotates them. Reusing an already rotated token means it was stolen, so
      the whole login family is revoked.
    """

    def __init__(self, users, refresh_tokens, revoked_tokens, hasher, tokens, jwt_codec,
                 attempts=None, audit=None, refresh_duration=REFRESH_DURATION):
        self._users = users
        self._refresh_tokens = refresh_tokens
        self._revoked = revoked_tokens
        self._hasher = hasher
        self._tokens = tokens
        self._jwt = jwt_codec
        self._attempts = attempts
        self._audit = audit
        self._refresh_duration = refresh_duration
        # Verifying against a dummy hash keeps "unknown email" as slow as "wrong password".
        self._dummy_salt, self._dummy_hash = hasher.create("dummy password for timing")

    def register(self, username, email, password):
        clean_email = email.strip().lower()
        salt, password_hash = self._hasher.create(password)
        user = self._users.create(username.strip(), clean_email, salt, password_hash)
        self._users.add_role(user.id, DEFAULT_ROLE)
        self._record(user.id, "user.register")
        return user

    def log_in(self, email, password, ip_address="", user_agent="") -> TokenPair:
        clean_email = email.strip().lower()
        self._check_not_locked(clean_email, ip_address)
        user = self._users.find_by_email(clean_email)
        if user is None:
            self._hasher.verify(password, self._dummy_salt, self._dummy_hash)
            valid = False
        else:
            valid = self._hasher.verify(password, user.salt, user.password_hash)
        if self._attempts is not None:
            self._attempts.record(clean_email, ip_address, valid)
        if not valid:
            raise InvalidCredentialsError
        self._users.touch_last_login(user.id)
        self._record(user.id, "user.login", ip_address=ip_address)
        return self._issue_pair(user.id, str(uuid.uuid4()), user_agent)

    def refresh(self, refresh_token: str, user_agent="") -> TokenPair:
        stored = self._refresh_tokens.find_by_hash(self._tokens.hash(refresh_token))
        if stored is None:
            raise InvalidTokenError("unknown refresh token")
        if stored.revoked_at is not None:
            # A rotated token came back: someone else has a copy. Kill the family.
            self._refresh_tokens.revoke_family(stored.family_id)
            self._record(stored.user_id, "token.reuse_detected")
            raise InvalidTokenError("refresh token reused")
        if not stored.is_usable():
            raise InvalidTokenError("refresh token expired")
        pair, new_token = self._issue_pair(stored.user_id, stored.family_id, user_agent, return_stored=True)
        self._refresh_tokens.mark_replaced(stored.id, new_token.id)
        return pair

    def user_from_token(self, access_token):
        claims = self._jwt.decode_access(access_token)
        if self._revoked.is_revoked(claims.jti):
            raise InvalidTokenError("revoked")
        user = self._users.find_by_id(claims.user_id)
        if user is None:
            raise InvalidTokenError("user no longer exists")
        return user

    def log_out(self, access_token, refresh_token=None):
        """Revoke the access token and, if given, its refresh token. Never fails."""
        try:
            claims = self._jwt.decode_access(access_token)
        except InvalidTokenError:
            claims = None
        if claims is not None:
            self._revoked.revoke(claims.jti, claims.user_id, claims.expires_at)
            self._record(claims.user_id, "user.logout")
        if refresh_token:
            stored = self._refresh_tokens.find_by_hash(self._tokens.hash(refresh_token))
            if stored is not None and (claims is None or stored.user_id == claims.user_id):
                self._refresh_tokens.revoke_family(stored.family_id)

    def log_out_everywhere(self, user_id: int) -> None:
        self._refresh_tokens.revoke_all_for_user(user_id)
        self._record(user_id, "user.logout_all")

    def _issue_pair(self, user_id, family_id, user_agent, return_stored=False):
        access, _ = self._jwt.issue_access(user_id, self._users.roles_of(user_id))
        refresh = self._tokens.generate()
        expires_at = datetime.now(timezone.utc) + self._refresh_duration
        stored = self._refresh_tokens.create(user_id, self._tokens.hash(refresh), family_id, expires_at, user_agent)
        pair = TokenPair(access, refresh, int(self._jwt.access_duration.total_seconds()))
        return (pair, stored) if return_stored else pair

    def _check_not_locked(self, email, ip_address=""):
        if self._attempts is None:
            return
        since = datetime.now(timezone.utc) - LOCKOUT_WINDOW
        if self._attempts.failures_since(email, since) >= MAX_FAILED_LOGINS:
            raise TooManyAttemptsError
        if ip_address and self._attempts.failures_from_ip_since(ip_address, since) >= MAX_FAILED_LOGINS_PER_IP:
            raise TooManyAttemptsError

    def _record(self, user_id, action, **extra):
        if self._audit is not None:
            self._audit.record(user_id, action, "user", user_id, **extra)
