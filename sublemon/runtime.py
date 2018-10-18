"""The main event of this library."""

import asyncio
import itertools

from contextlib import suppress
from typing import (
    AsyncGenerator,
    List,
    Set)

from sublemon.errors import SublemonRuntimeError
from sublemon.subprocess import SublemonSubprocess
from sublemon.utils import amerge

_DEFAULT_MC: int = 25
_DEFAULT_PD: float = 0.01


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

        self._poll_task = asyncio.ensure_future(self._poll())
        self._is_running = True

    async def stop(self) -> None:
        """Coroutine to stop execution of this server."""
        if not self._is_running:
            raise SublemonRuntimeError(
                'Attempted to stop an already-stopped `Sublemon` instance')

        await self.block()
        self._poll_task.cancel()
        self._is_running = False
        with suppress(asyncio.CancelledError):
            await self._poll_task

    async def _poll(self) -> None:
        """Coroutine to poll status of running subprocesses."""
        while True:
            await asyncio.sleep(self._poll_delta)
            for subproc in list(self._running_set):
                subproc._poll()

    async def iter_lines(
            self,
            *cmds: str,
            stream: str='both') -> AsyncGenerator[str, None]:
        """Coroutine to spawn commands and yield text lines from stdout."""
        sps = self.spawn(*cmds)
        if stream == 'both':
            agen = amerge(
                amerge(*[sp.stdout for sp in sps]),
                amerge(*[sp.stderr for sp in sps]))
        elif stream == 'stdout':
            agen = amerge(*[sp.stdout for sp in sps])
        elif stream == 'stderr':
            agen = amerge(*[sp.stderr for sp in sps])
        else:
            raise SublemonRuntimeError(
                'Invalid `stream` kwarg received: `' + str(stream) + '`')
        async for line in agen:
            yield line.decode('utf-8').rstrip()

    async def gather(self, *cmds: str) -> List[int]:
        """Coroutine to spawn subprocesses and block until completion.

        Note:
            The same `max_concurrency` restriction that applies to `spawn`
            also applies here.

        Returns:
            The exit codes of the spawned subprocesses, in the order they were
            passed.

        """
        subprocs = self.spawn(*cmds)
        subproc_wait_coros = [subproc.wait_done() for subproc in subprocs]
        return await asyncio.gather(*subproc_wait_coros)

    async def block(self) -> None:
        """Block until all running and pending subprocesses have finished."""
        await asyncio.gather(
            *itertools.chain(
                (sp.wait_done() for sp in self._running_set),
                (sp.wait_done() for sp in self._pending_set)))

    def spawn(self, *cmds: str) -> List[SublemonSubprocess]:
        """Coroutine to spawn shell commands.

        If `max_concurrency` is reached during the attempt to spawn the
        specified subprocesses, excess subprocesses will block while attempting
        to acquire this server's semaphore.

        """
        if not self._is_running:
            raise SublemonRuntimeError(
                'Attempted to spawn subprocesses from a non-started server')

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
