"""
Custom error classes for Mirage backend.
"""


class MirageError(Exception):
    """Base error for Mirage application."""
    pass


class AuthenticationError(MirageError):
    """Raised when authentication fails."""
    pass


class ValidationError(MirageError):
    """Raised when validation fails."""
    pass


class NotFoundError(MirageError):
    """Raised when a resource is not found."""
    pass


class ServiceUnavailableError(MirageError):
    """Raised when an external service is unavailable."""
    pass
