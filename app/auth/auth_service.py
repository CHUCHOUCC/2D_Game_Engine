from app.auth.errors import InvalidCredentialsError
from app.auth.session import Session
from datetime import timedelta
from datetime import datetime, timezone
# How long a token stays valid. You choose it (for example 1 hour).
SESSION_DURATION = timedelta(hours=1)



class AuthService:

    def __init__(self, users, sessions, hasher, tokens, session_duration=SESSION_DURATION):
        self._users = users
        self._sessions = sessions
        self._hasher = hasher
        self._tokens = tokens
        self._session_duration = session_duration


    def register(self, username, email, password):
        clean_email = email.strip().lower()
        salt , password_hash = self._hasher.create(password)

        return self._users.create(username, clean_email, salt, password_hash)


    def log_in(self, email, password):
        clean_email = email.strip().lower()
        user = self._users.find_by_email(clean_email)

        if user is None or self._hasher.verify(password,user.salt,user.password_hash) == False:
            raise InvalidCredentialsError

        token = self._tokens.generate()
        expires_at = datetime.now(timezone.utc) + self._session_duration

        self._sessions.create(Session(user.id, self._tokens.hash(token), expires_at))
        return token
    
    def user_from_token(self, token):
        """Return the User that owns this token, or raise InvalidTokenError.

        - Look the session up by the hash of the token.
        - Missing session -> InvalidTokenError.
        - Expired session -> delete it and raise InvalidTokenError.
        - Session whose user no longer exists -> InvalidTokenError.
        """
        raise NotImplementedError

    def log_out(self, token):
        """Delete the session of this token. An unknown token is not an error."""
        raise NotImplementedError
