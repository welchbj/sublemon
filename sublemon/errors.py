"""Custom error types for `sublemon`."""


class SublemonError(Exception):
    """Base exception type for the `sublemon` library."""


class SublemonRuntimeError(SublemonError):
    """Exception type for `sublemon` runtime errors."""


class SublemonLifetimeError(SublemonError):
    """Exception type for improper access of `sublemon` object attributes."""
