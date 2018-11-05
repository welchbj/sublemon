# Exceptions

This library defines a few custom exception types, explored below.

## The base `SublemonError` exception type

The `SublemonError` is base type from which all exceptions raised by this library will inherit. Exceptions of this type should never be explicitly thrown, as this type exists only as a catch-all for any exceptions raised by this library.

## The `SublemonRuntimeError` exception type

This is an exception type for errors related to instances of the `Sublemon` class. You can expect this exception to be raised in the following situations:

* Attempting to `start()` an already-started instance of the `Sublemon` class
* Attempting to `stop()` a not-yet-started instance of the `Sublemon` class
* Attempting to `spawn()` subprocesses from a not-yet-started instance of the `Sublemon` class
* Passing an invalid `stream` kwarg value to the `iter_lines` generator provided by instances of the `Sublemon` class

## The `SublemonLifetimeError` exception type

This is an exception type for errors related to improper access of attributes on `SublemonSubprocess` objects with regard to the lifetime of their encapsulated subprocess. You can expect this exception to raised in the following situations:

* Attempting to poll (via the internal `_poll()` method) a `SublemonSubprocess` that has not begun execution 
* An internal subprocess-handling error occured, causing the encapsulated subprocess to terminate without setting its `exit_code` or other metadata
