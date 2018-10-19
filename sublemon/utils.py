"""Asynchronous / misc utilities."""

import asyncio
import contextlib
import sys

from aiostream import stream
from typing import (
    Any,
    AsyncGenerator)


async def amerge(*agens) -> AsyncGenerator[Any, None]:
    """Thin wrapper around aiostream.stream.merge."""
    xs = stream.merge(*agens)
    async with xs.stream() as streamer:
        async for x in streamer:
            yield x


def crossplat_loop_run(coro) -> Any:
    """Cross-platform method for running a subprocess-spawning coroutine.

    Returns:
        The result of the coroutine.

    """
    if sys.platform == 'win32':
        loop = asyncio.ProactorEventLoop()
    else:
        loop = asyncio.new_event_loop()

    asyncio.set_event_loop(loop)
    with contextlib.closing(loop):
        loop.run_until_complete(coro)
