"""Models for interacting with subprocesses."""

import asyncio
import uuid

from datetime import datetime
from typing import (
    AsyncGenerator,
    Optional)


class SublemonSubprocess:

    """Logical encapsulation of a subprocess."""

    def __init__(self, server: 'Sublemon', cmd: str) -> None:
        self._server = server
        self._cmd = cmd
        self._scheduled_at = datetime.now()
        self._uuid = uuid.uuid4()
        self._began_at: Optional[datetime] = None
        self._exit_code: Optional[int] = None
        self._subprocess: Optional[asyncio.subprocess.Process] = None
        self._began_running_evt = asyncio.Event()
        self._done_running_evt = asyncio.Event()

    def __repr__(self) -> str:
        return '<SublemonSubprocess [{}]>'.format(str(self))

    def __str__(self) -> str:
        return '{} -> `{}`'.format(self._scheduled_at, self._cmd)

    def __hash__(self) -> int:
        return hash((self._cmd, self._uuid,))

    def __eq__(self, other) -> bool:
        return (self._cmd == other._cmd and
                self._scheduled_at == other._scheduled_at)

    def __ne__(self, other) -> bool:
        return not (self == other)

    async def spawn(self):
        """Spawn the command wrapped in this object as a subprocess."""
        self._server._pending_set.add(self)
        await self._server._sem.acquire()
        self._subprocess = await asyncio.create_subprocess_shell(
            self._cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)
        self._began_at = datetime.now()
        if self in self._server._pending_set:
            self._server._pending_set.remove(self)
        self._server._running_set.add(self)
        self._began_running_evt.set()

    async def wait_running(self) -> None:
        """Coroutine to wait for this subprocess to begin execution."""
        await self._began_running_evt.wait()

    async def wait_done(self) -> int:
        """Coroutine to wait for subprocess run completion.

        Returns:
            The exit code of the subprocess.

        """
        await self._done_running_evt.wait()
        return self._exit_code

    def _poll(self) -> None:
        """Check the status of the wrapped running subprocess.

        Note:
            This should only be called on currently-running tasks.

        """
        if self._subprocess.returncode is not None:
            self._exit_code = self._subprocess.returncode
            self._done_running_evt.set()
            self._server._running_set.remove(self)
            self._server._sem.release()

    @property
    async def stdout(self) -> AsyncGenerator[str, None]:
        """Asynchronous generator for lines from subprocess stdout."""
        await self.wait_running()
        async for line in self._subprocess.stdout:  # type: ignore
            yield line

    @property
    async def stderr(self) -> AsyncGenerator[str, None]:
        """Asynchronous generator for lines from subprocess stderr."""
        await self.wait_running()
        async for line in self._subprocess.stderr:  # type: ignore
            yield line

    @property
    def cmd(self) -> str:
        """The shell command that this subprocess will/is/did run."""
        return self._cmd

    @property
    def exit_code(self) -> Optional[int]:
        """The exit code of this subprocess."""
        return self._exit_code

    @property
    def is_pending(self) -> bool:
        """Whether this subprocess is waiting to run."""
        return not self._began_running_evt.is_set()

    @property
    def is_running(self) -> bool:
        """Whether this subprocess is currently running."""
        return (self._began_running_evt.is_set() and
                not self._done_running_evt.is_set())

    @property
    def is_done(self) -> bool:
        """Whether this subprocess has completed."""
        return self._done_running_evt.is_set()

    @property
    def scheduled_at(self) -> datetime:
        """The time this object was scheduled on the server."""
        return self._scheduled_at

    @property
    def began_at(self) -> Optional[datetime]:
        """The time the subprocess began execution.

        Note:
            This will be `None` until the subprocess has actually begun
            execution.

        """
        return self._began_at
