class AuthError(Exception):
    """Base class for every error of the login module."""


class EmailAlreadyRegisteredError(AuthError):
    """Another account already uses this email."""


class InvalidCredentialsError(AuthError):
    """Wrong email or password. The message never says which one was wrong.

    attempts_left says how many more failures the email has before the lockout
    (None when the service does not count attempts).
    """

    def __init__(self, attempts_left=None):
        super().__init__("Invalid email or password")
        self.attempts_left = attempts_left


class InvalidTokenError(AuthError):
    """The token is unknown, expired or logged out."""


class TooManyAttemptsError(AuthError):
    """Too many failed logins for this email in a short time."""
