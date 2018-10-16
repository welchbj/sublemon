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
