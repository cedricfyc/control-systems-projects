class AuthorisationError(Exception):
    """Raised when a user is not authorized to perform an action."""


class AuthenticationError(Exception):
    """Raised when authentication fails."""