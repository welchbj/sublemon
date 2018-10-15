"""Models for interacting with subprocesses."""

import asyncio

from enum import Enum
from typing import (
    AsyncGenerator,
    Optional)

from sublemon.server import SublemonServer


class SubprocessState(Enum):
    PENDING = 0
    RUNNING = 1
    ALLDONE = 2


class SublemonSubprocess:

    """TODO."""

    def __init__(self, server: SublemonServer, cmd: str) -> None:
        self._server = SublemonServer
        self._cmd = cmd
        self._exit_code = None
        self._state = SubprocessState.PENDING
        self._subprocess = None
        self._begin_running_evt = asyncio.Event()
        self._done_running_evt = asyncio.Event()

    def __repr__(self):
        # TODO
        pass

    def __str__(self):
        # TODO
        pass

    async def run(self):
        """Run the cmd wrapped in this object as a subprocess."""
        with self._server._sem:  # <-- we cannot use contextmanager here
                                 #     must find somewhere to decrement
                                 #     semaphore when done running
            self._subprocess = asyncio.create_subprocess_shell(
                self._cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE)
            # TODO: set timestamp of start
            self._begin_running_evt.set()
        # TODO

    async def wait_running(self) -> None:
        """Coroutine to wait for this subprocess to begin execution."""
        await self._begin_running_evt.wait()

    async def wait_done(self) -> int:
        """Coroutine to wait for subprocess run completion.

        Returns:
            The exit code of the subprocess.

        """
        await self._done_running_evt.wait()
        return self._exit_code

    @property
    async def exit_code(self) -> int:
        """Coroutine to wait for the exit code of this subprocess."""
        # TODO: need to make sure this is an int and figure out what we
        #       want to wait on
        return self._exit_code

    @property
    async def stdout(self) -> AsyncGenerator[str, None]:
        """Asynchronous generator for lines from subprocess stdout."""
        await self.wait_running()
        async for line in self._subprocess.stdout:
            yield line

    @property
    async def stderr(self) -> AsyncGenerator[str, None]:
        """Asynchronous generator for lines from subprocess stderr."""
        await self.wait_running()
        async for line in self._subprocess.stderr:
            yield line

    @property
    def state(self) -> SubprocessState:
        """The current state of this subprocess."""
        return self._state

    @property
    def is_pending(self) -> bool:
        """Whether this subprocess is waiting to run."""
        return self._state == SubprocessState.PENDING

    @property
    def is_running(self) -> bool:
        """Whether this subprocess is currently running."""
        return self._state == SubprocessState.RUNNING

    @property
    def is_done(self) -> bool:
        """Whether this subprocess has completed."""
        return self._state == SubprocessState.ALLDONE
