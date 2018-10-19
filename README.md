# sublemon

A local server for asynchronously spawning and monitoring subprocesses via `asyncio`. Very much a work in progress.


## License

`sublemon` uses the [MIT License](https://opensource.org/licenses/MIT).


## Installation

To get the latest version from PyPI, use:
```sh
pip install sublemon
```

Alternatively, install the latest version from version control:
```sh
pip install https://github.com/welchbj/sublemon/archive/master.tar.gz
```


## Basic Usage

The below example shows some of the basic subprocess-spawning functionality of this library:
```python
import asyncio
import time

from sublemon import (
    amerge,
    crossplat_loop_run,
    Sublemon)


async def main():
    """`sublemon` library example!"""
    for c in (1, 2, 4,):
        async with Sublemon(max_concurrency=c) as s:
            start = time.perf_counter()
            await asyncio.gather(one(s), two(s))
            end = time.perf_counter()
            print('Limiting to', c, 'concurrent subprocess(es) took',
                  end-start, 'seconds\n')


async def one(s: Sublemon):
    """Spin up some subprocesses, sleep, and echo a message for this coro."""
    shell_cmds = [
        'sleep 1 && echo subprocess 1 in coroutine one',
        'sleep 1 && echo subprocess 2 in coroutine one']
    async for line in s.iter_lines(*shell_cmds):
        print(line)


async def two(s: Sublemon):
    """Spin up some subprocesses, sleep, and echo a message for this coro."""
    subprocess_1, subprocess_2 = s.spawn(
        'sleep 1 && echo subprocess 1 in coroutine two',
        'sleep 1 && echo subprocess 2 in coroutine two')
    async for line in amerge(subprocess_1.stdout, subprocess_2.stdout):
        print(line.decode('utf-8'), end='')


if __name__ == '__main__':
    crossplat_loop_run(main())

```

Executing this example would yield the following console output, demonstrating `sublemon`'a ability to rate-limit pooled subprocess execution:
```
subprocess 1 in coroutine one
subprocess 2 in coroutine one
subprocess 1 in coroutine two
subprocess 2 in coroutine two
Limiting to 1 concurrent subprocess(es) took 4.251494415589895 seconds

subprocess 1 in coroutine one
subprocess 2 in coroutine one
subprocess 2 in coroutine two
subprocess 1 in coroutine two
Limiting to 2 concurrent subprocess(es) took 2.1220036135871787 seconds

subprocess 1 in coroutine one
subprocess 2 in coroutine one
subprocess 1 in coroutine two
subprocess 2 in coroutine two
Limiting to 4 concurrent subprocess(es) took 1.083995944693033 seconds
```


## Development

The development requirements can be installed with:
```sh
pip install -r dev-requirements.txt
```

Then try running the tests with:
```sh
python -m unittest discover
```