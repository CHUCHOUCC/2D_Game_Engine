from app.auth.errors import InvalidCredentialsError, InvalidTokenError
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
        token_hash = self._tokens.hash(token)
        session = self._sessions.find_by_token_hash(token_hash)

        if session is None:
            raise InvalidTokenError

        if not session.is_valid():
            self._sessions.delete(token_hash)
            raise InvalidTokenError

        
        user = self._users.find_by_id(session.user_id)

        if user is None:
            raise InvalidTokenError

        return user


    def log_out(self, token):
        hash_token = self._tokens.hash(token)
        self._sessions.delete(hash_token)
