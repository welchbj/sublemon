# Utilities

This library ships with a couple of basic utility functions to make your life a little bit easier.

## Merging asynchronous generators

When you spawn a lot of subprocesses, you may have a lot of asynchronous output pipes to deal with. If you'd like to combine them into a single asynchronous generator, then the `amerge` function is for you. This function is thin wrapper around the elegant [merge](https://aiostream.readthedocs.io/en/stable/operators.html#aiostream.stream.merge) function provided by the great [aiostream](https://aiostream.readthedocs.io) library.

Here's an example that merges the `stdout` and `stderr` asynchronous output streams of a simple subprocess:

```python
>>> from sublemon import amerge, crossplat_loop_run, Sublemon
>>> async def example():
...     async with Sublemon() as s:
...         subproc, = s.spawn('echo hi from stdout && echo hi from stderr 1>&2')
...         async for line in amerge(subproc.stdout, subproc.stderr):
...             print(line.rstrip().decode('utf-8'))
...
>>> crossplat_loop_run(example())
hi from stdout
hi from stderr

```

## Running subprocess-spawning coroutines

Unfortunately, the default [asyncio event loop](https://docs.python.org/3/library/asyncio-eventloop.html#event-loop-implementations) implementation does not support subprocess-spawning on Windows. Fortunately, `sublemon` ships with a utility function `crossplat_loop_run` to handle event loop configuration so that subprocesses can be spawned regardless of the platform you're running on. This method works by swapping out the active event loop on Windows with an instance of the [ProactorEventLoop](https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.ProactorEventLoop) implementation.

This function is used in pretty much all of the examples within this library's documentation, so take a look around to see how it is used.

This function can kick off the execution of any coroutine (although there's no reason to use it if you're not planning on spawning subprocesses). It's also important to note that this method will set the active loop to a newly instantiated one (even if you aren't running on Windows), so this method is really meant to be run to kick off the main entry point to your program.
