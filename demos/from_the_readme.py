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
