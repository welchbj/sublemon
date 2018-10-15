"""The main event of this library."""

import asyncio

from typing import List

from sublemon.models import SpawnedSubprocess


class SublemonServer:

    """TODO."""

    def __init__(self, max_concurrency: int=-1) -> None:
        self._max_concurrency = max_concurrency
        self._sem = asyncio.Semaphore(max_concurrency)

    async def spawn(self, *cmds: str) -> List[SpawnedSubprocess]:
        """Coroutine to spawn the specified subprocesses.

        Note:
            This will only spawn the allowable number of subprocesses as per
            ``max_concurrency``. The remainder of commands will still be
            returned within ``SpawnedSubprocess`` objects, but will still
            be in a ``PENDING`` state.

        """
        # TODO
        pass

#    def running_subprocesses(self) -> List[SpawnedSubprocess]:
#        """Get the currently-executing subprocesses."""
#        # TODO
#        pass
#
#    def pending_subprocesses(self) -> List[SpawnedSubprocess]:
#        """Get the subprocesses waiting to begin execution."""
#        # TOD
#        pass

    @property
    def max_concurrency(self) -> int:
        """The maximum number of subprocesses that can run concurrently."""
        return self._max_concurrency
