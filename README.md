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

The [`demo/readme.py`](demo/readme.py) script (shown below) provides a simple example of spawning subprocesses with `sublemon`.
```python
"""Demo from the README."""

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
            start = time.time()
            await asyncio.gather(one(s), two(s))
            end = time.time()
            print('Limiting to', c, 'concurrent subprocess(es) took',
                  end-start, 'seconds\n')


async def one(s: Sublemon):
    """Say 'hi' and 'bye' using output merging."""
    shell_cmds = [
        'sleep 1 && echo subprocess 1 in coroutine one',
        'sleep 1 && echo subprocess 2 in coroutine one']
    async for line in s.stdout_lines(*shell_cmds):
        print(line)


async def two(s: Sublemon):
    """Say 'hi' and 'bye' via stdout pipes."""
    echo_hi, echo_bye = s.spawn(
        'sleep 1 && echo subprocess 1 in coroutine two',
        'sleep 1 && echo subprocess 2 in coroutine two')
    async for line in amerge(echo_hi.stdout, echo_bye.stdout):
        print(line.decode('utf-8'), end='')


if __name__ == '__main__':
    crossplat_loop_run(main())

```

Executing this script should provide the following output:
```
subprocess 1 in coroutine one
subprocess 2 in coroutine one
subprocess 1 in coroutine two
subprocess 2 in coroutine two
Limiting to 1 concurrent subprocess(es) took 4.439314842224121 seconds

subprocess 1 in coroutine two
subprocess 2 in coroutine two
subprocess 1 in coroutine one
subprocess 2 in coroutine one
Limiting to 2 concurrent subprocess(es) took 2.2350566387176514 seconds

subprocess 1 in coroutine two
subprocess 1 in coroutine one
subprocess 2 in coroutine two
subprocess 2 in coroutine one
Limiting to 4 concurrent subprocess(es) took 1.0966482162475586 seconds
```