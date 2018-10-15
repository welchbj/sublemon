"""The main event of this library."""

import asyncio

from contextlib import suppress
from typing import (
    List,
    Set)

from sublemon.models import SublemonSubprocess

_DEFAULT_MC: int = 25
_DEFAULT_PD: float = 0.1


class SublemonServer:

    """TODO."""

    def __init__(self, max_concurrency: int=_DEFAULT_MC) -> None:
        self._max_concurrency = max_concurrency
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
            # TODO: raise exception
            pass

        self._task = asyncio.ensure_future(self._poll())
        self._is_running = True

    async def stop(self) -> None:
        """Coroutine to stop execution of this server."""
        if not self._is_running:
            # TODO: raise exception
            pass

        self._task.cancel()
        self._is_running = False
        with suppress(asyncio.CancelledError):
            await self._task

    async def _poll(self, poll_delta=_DEFAULT_PD) -> None:
        """Coroutine to poll status of running subprocesses."""
        while True:
            await asyncio.sleep(poll_delta)
            for subproc in list(self._running_set):
                subproc._poll()

    async def spawn(self, *cmds: str) -> List[SublemonSubprocess]:
        """Coroutine to spawn the specified subprocesses.

        Note:
            This will only spawn the allowable number of subprocesses as per
            ``max_concurrency``. The remainder of commands will still be
            returned within ``SublemonSubprocess`` objects, but will still
            be in a ``PENDING`` state.

        """
        subprocs = [SublemonSubprocess(self, cmd) for cmd in cmds]
        tasks = [subproc.spawn() for subproc in subprocs]
        await asyncio.gather(*tasks)
        return subprocs

    async def spawn_and_complete(self, *cmds: str) -> None:
        """Coroutine to spawn subprocesses and block until completion."""
        # TODO
        pass

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
        """The maximum number of subprocesses that can run concurrently."""
        return self._max_concurrency
