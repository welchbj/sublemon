# Working with `Sublemon` Objects

The main way to kick off subprocesses in this library is through instances of the `Sublemon` class.

## Creating new `Sublemon` objects

There are a couple of ways of setting up and configuring `Sublemon` runtime managers. The preferred method is to use the `async with` statement, since this handles all clean-up for you. Below is a simple example.
```python
>>> from sublemon import crossplat_loop_run, Sublemon
>>> async def example():
...     async with Sublemon() as s:
...         print(s)
...
>>> crossplat_loop_run(example())
max concurrency: 25, poll delta: 0.01, 0 running and 0 pending subprocesses

```

An equivalent example with manually stopping the `Sublemon` object is shown below.
```python
>>> from sublemon import crossplat_loop_run, Sublemon
>>> async def example():
...     s = Sublemon()
...     await s.start()
...     print(s)
...     await s.stop()
...
>>> crossplat_loop_run(example())
max concurrency: 25, poll delta: 0.01, 0 running and 0 pending subprocesses

```

## Customizing the runtime

`Sublemon` objects have a couple of different parameters that can be used to configure how subprocesses are scheduled and monitored:

* `max_concurrency -> int` - the maximum number of subprocesses that this `Sublemon` instance will allow to be running at each time
* `poll_delta -> float` - the interval in seconds that this `Sublemon` instance will wait between each time it polls the status of its running subprocesses

## Spawning subprocesses

`Sublemon` objects offer a few choices for methods of spawning subprocesses, depending on the level of interaction you'd like with your spawned subprocesses.

The first method is `spawn`, which accepts a variable number of commands and will return a `SublemonSubprocess` object for each of these commands. Below is a simple example.
```python
>>> from sublemon import crossplat_loop_run, Sublemon
>>> async def example():
...     async with Sublemon() as s:
...         one, two = s.spawn('echo one', 'echo two')
...         async for line in one.stdout:
...             print(line.rstrip().decode())
...         async for line in two.stdout:
...             print(line.rstrip().decode())
...
>>> crossplat_loop_run(example())
one
two

```

Another option is the `gather` method, which accepts a variable number of commands, blocks on all of their execution, and returns the corresponding exit codes from each of the commands. A simple example is shown below.
```python
>>> from sublemon import crossplat_loop_run, Sublemon
>>> async def example():
...     async with Sublemon() as s:
...         zero, one = await s.gather(
...             'python -c "import sys; sys.exit(0)"',
...             'python -c "import sys; sys.exit(1)"')
...         print(zero)
...         print(one)
...
>>> crossplat_loop_run(example())
0
1

```

The final method is `iter_lines`. This method accepts a variable number of commands and asynchronously yields the decoded lines of output from the stdout and stderr streams of each corresponding spawned subprocess. Below is a simple example.
```python
>>> from sublemon import crossplat_loop_run, Sublemon
>>> async def example():
...     async with Sublemon() as s:
...         async for line in s.iter_lines('echo hi', 'sleep 1 && echo bye'):
...             print(line)
...
>>> crossplat_loop_run(example())
hi
bye

```

## Blocking on subprocess execution

If you have a `Sublemon` instance with running subprocesses, you can use the `block` coroutine to block until all pending and running subprocesses terminate their execution. A simple example is shown below.
```python
>>> from sublemon import crossplat_loop_run, Sublemon
>>> async def example():
...     async with Sublemon() as s:
...         s.spawn('sleep 1', 'sleep 2')
...         await s.block()
>>> crossplat_loop_run(example())

```

## Additional properties

* `running_subprocesses -> Set[SublemonSubprocess]` - a set of subprocesses currently running
* `pending_subprocesses -> Set[SublemonSubprocess]` - a set of subprocesses waiting to begin execution
