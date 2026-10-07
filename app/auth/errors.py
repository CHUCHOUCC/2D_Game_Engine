class AuthError(Exception):
    """Base class for every error of the login module."""


class EmailAlreadyRegisteredError(AuthError):
    """Another account already uses this email."""


class InvalidCredentialsError(AuthError):
    """Wrong email or password. The message never says which one was wrong."""


class InvalidTokenError(AuthError):
    """The token is unknown, expired or logged out."""
