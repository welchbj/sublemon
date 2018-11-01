# Working with `Sublemon` Objects

The main way to kick off subprocesses in this library is through instances of the `Sublemon` class.

## Creating new `Sublemon` objects

TODO: with context manager (preferred)
TODO: without context manager

## Customizing the runtime

`Sublemon` objects have a couple of different parameters that can be used to configure how subprocesses are scheduled and monitored:

* `max_concurrency -> int` - TODO
* `poll_delta -> float` - TODO

## Spawning subprocesses

TODO: spawn
TODO: gather
TODO: iter_lines

## Blocking on subprocess execution

TODO

## Additional properties

* `running_subprocesses -> Set[SublemonSubprocess]` - TODO
* `pending_subprocesses -> Set[SublemonSubprocess]` - TODO 
* `max_concurrency -> int` - TODO
* `poll_delta -> float` - TODO

