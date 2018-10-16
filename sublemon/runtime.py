"""The main event of this library."""

import asyncio

from contextlib import suppress
from typing import (
    AsyncGenerator,
    List,
    Set)

from sublemon.errors import SublemonRuntimeError
from sublemon.subprocess import SublemonSubprocess
from sublemon.utils import amerge

_DEFAULT_MC: int = 25
_DEFAULT_PD: float = 0.1


class Sublemon:

    """The runtime for spawning subprocesses."""

    def __init__(self, max_concurrency: int=_DEFAULT_MC,
                 poll_delta: float=_DEFAULT_PD) -> None:
        self._max_concurrency = max_concurrency
        self._poll_delta = poll_delta
        self._sem = asyncio.BoundedSemaphore(max_concurrency)
        self._is_running = False
        self._pending_set: Set[SublemonSubprocess] = set()
        self._running_set: Set[SublemonSubprocess] = set()

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.stop()

    async def start(self) -> None:
        """Coroutine to run this server."""
        if self._is_running:
            raise SublemonRuntimeError(
                'Attempted to start an already-running `Sublemon` instance')

        self._task = asyncio.ensure_future(self._poll())
        self._is_running = True

    async def stop(self) -> None:
        """Coroutine to stop execution of this server."""
        if not self._is_running:
            raise SublemonRuntimeError(
                'Attempted to stop an already-stopped `Sublemon` instance')

        self._task.cancel()
        self._is_running = False
        with suppress(asyncio.CancelledError):
            await self._task

    async def _poll(self) -> None:
        """Coroutine to poll status of running subprocesses."""
        while True:
            await asyncio.sleep(self._poll_delta)
            for subproc in list(self._running_set):
                subproc._poll()

    async def stdout_lines(self, *cmds: str) -> AsyncGenerator[str, None]:
        """Coroutine to spawn commands and async yield decoded text lines.

        Note:
            The same ``max_concurrency`` restriction that applies to ``spawn``
            also applies here.

        """
        sps = self.spawn(*cmds)
        async for line in amerge(*[sp.stdout for sp in sps]):
            yield line.decode('utf-8').rstrip()

    async def spawn_and_complete(self, *cmds: str) -> None:
        """Coroutine to spawn subprocesses and block until completion.

        Note:
            The same ``max_concurrency`` restriction that applies to ``spawn``
            also applies here.

        """
        subprocs = await self.spawn(*cmds)
        subproc_wait_coros = [subproc.wait_done() for subproc in subprocs]
        await asyncio.gather(*subproc_wait_coros)

    def spawn(self, *cmds: str) -> List[SublemonSubprocess]:
        """Coroutine to spawn shell commands.

        If ``max_concurrency`` is reached during the attempt to spawn the
        specified subprocesses, excess subprocesses will block while attempting
        to acquire this server's semaphore.

        """
        subprocs = [SublemonSubprocess(self, cmd) for cmd in cmds]
        for sp in subprocs:
            asyncio.ensure_future(sp.spawn())
        return subprocs

    @property
    def running_subprocesses(self) -> Set[SublemonSubprocess]:
        """Get the currently-executing subprocesses."""
        return self._running_set

    @property
    def pending_subprocesses(self) -> Set[SublemonSubprocess]:
        """Get the subprocesses waiting to begin execution."""
        return self._pending_set

    @property
    def max_concurrency(self) -> int:
        """The max number of subprocesses that can be running concurrently."""
        return self._max_concurrency

    @property
    def poll_delta(self) -> float:
        """The number of seconds to sleep in between polls of subprocesses."""
        return self._poll_delta
