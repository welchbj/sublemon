"""Custom error types for `sublemon`."""


class SublemonError(Exception):
    """Base exception type for the `sublemon` library."""


class SublemonRuntimeError(SublemonError):
    """Exception type for `sublemon` runtime errors."""


class SublemonSubprocessLifetimeError(SublemonError):
    """Exception type for accessing non-existent attributes on a subprocess."""
