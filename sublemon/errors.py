"""Custom error types for `sublemon`."""


class SublemonError(Exception):
    """Base exception type for the `sublemon` library."""


class SublemonRuntimeError(SublemonError):
    """Exception type for `sublemon` runtime errors."""
