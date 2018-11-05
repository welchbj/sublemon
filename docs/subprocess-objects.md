# Working with `SublemonSubprocess` Objects

The `SublemonSubprocess` class provides a small wrapper over the [`Process` class](https://docs.python.org/3/library/asyncio-subprocess.html#asyncio.asyncio.subprocess.Process) provided by `asyncio`, with the plumbing allowing it to interact with `Sublemon` runtime objects as well as a future extra lifetime-related coroutines.

## Hashing and equality between objects

Instances of `SublemonSubprocess` are hashable, but each instance is spawned with a UUID to ensure that hashes of otherwise-identical instances never collide. This can be useful for tracking subjects

## Lifetime events

This class also provides some awaitable events in the form of `wait_running` and `wait_done` coroutines. The `wait_running` coroutine will block until an underlying subprocess has actually been spawned on the system and the `wait_done` coroutine will block until the subprocess has terminated. Here's an example so you can see the gist of how this works:

```python
>>> import asyncio
>>> from sublemon import crossplat_loop_run, Sublemon
>>> async def example():
...     async with Sublemon(max_concurrency=1) as s:
...         sp_one, sp_two = s.spawn(
...                 'python -c "import time; time.sleep(1)"',
...                 'python -c "import time; time.sleep(1)"')
...         await asyncio.gather(
...                 sp_one.wait_running(),
...                 sp_two.wait_running())
...         print('Both subprocesses now running!')
...         await asyncio.gather(
...                 sp_one.wait_done(),
...                 sp_two.wait_done())
...         print('Both subprocesses all done!')
...
>>> crossplat_loop_run(example())
Both subprocesses now running!
Both subprocesses all done!

```

## Additional properties

* `stdout -> AsyncGenerator[str, None]` - an asynchronous generator yielding the raw line-by-line bytes from the subprocess's stdout stream
* `stderr -> AsyncGenerator[str, None]` - an asynchronous generator yielding the raw line-by-line bytes from the subprocess's stderr stream
* `cmd -> str` - the shell command used (or that will be used) to spawn this subprocess
* `exit_code -> Optional[int]` - the exit code of the subprocess, which will be `None` until the subprocess terminates
* `is_pending -> bool` - whether the subprocess is still waiting to be spawned
* `is_running -> bool` - whether the subprocess is currently executing
* `is_done -> bool` - whether the subprocess has completed execution
* `scheduled_at -> datetime` - when this subprocess moved into a pending state within the `Sublemon` instance from which it was spawned
* `began_at -> Optional[datetime]` - when this subprocess was actually spawned and began execution from within the corresponding `Sublemon` instance
