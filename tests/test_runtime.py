"""Tests for the subprocessing-spawning functionality of `sublemon`."""

import unittest
import shutil
import sys

from sublemon import (
    crossplat_loop_run,
    Sublemon,
    SublemonRuntimeError)

NO_PY = shutil.which('python') is None
if NO_PY:
    print('`python` in PATH is required for testing `sublemon` runtime tests',
          file=sys.stderr)


def _sp_sleep_for(t: int) -> str:
    """Return the subprocess cmd for sleeping for `t` seconds."""
    return 'python -c "import time; time.sleep({})"'.format(t)


def _sp_exit_with(e: int) -> str:
    """Return the subprocess cmd for exiting with `e` exit code."""
    return 'python -c "import sys; sys.exit({})"'.format(e)


@unittest.skipIf(NO_PY, 'need `python` in PATH')
class TestRuntime(unittest.TestCase):

    def test_basic_init(self):
        """Test the basic properties of a spawned server."""
        async def test():
            async with Sublemon(max_concurrency=1, poll_delta=1.0) as s:
                self.assertEqual(s.max_concurrency, 1)
                self.assertEqual(s.poll_delta, 1.0)
                self.assertEqual(s.running_subprocesses, set())
                self.assertEqual(s.pending_subprocesses, set())
        crossplat_loop_run(test())

    def test_double_start(self):
        """Ensure double starting the server raises an exception."""
        async def test():
            with self.assertRaises(SublemonRuntimeError):
                async with Sublemon() as s:
                    await s.start()
        crossplat_loop_run(test())

    def test_stop_not_started(self):
        """Ensure stopping a stopped server raises an exception."""
        async def test():
            with self.assertRaises(SublemonRuntimeError):
                s = Sublemon()
                await s.stop()
            with self.assertRaises(SublemonRuntimeError):
                async with Sublemon() as s:
                    pass
                await s.stop()
        crossplat_loop_run(test())

    def test_subprocess_tracking(self):
        """Ensure subprocesses move between the running/pending sets."""
        async def test():
            # TODO
            assert True
        crossplat_loop_run(test())

    def test_concurrency_limiting(self):
        """Ensure the `max_concurrency` option works as expected."""
        async def test():
            # TODO
            assert True
        crossplat_loop_run(test())

    def test_empty_generators(self):
        """Ensure that nothing is yielded from expected empty subprocesses."""
        async def test():
            # TODO
            assert True
        crossplat_loop_run(test())

    def test_stop_server_with_running_subprocs(self):
        """Test stopping the server while subprocesses are still running."""
        async def test():
            # TODO
            assert True
        crossplat_loop_run(test())

    def test_joined_lines(self):
        """Test joining and iterating over lines joined from subprocesses."""
        async def test():
            # TODO
            assert True
        crossplat_loop_run(test())

    def test_gather(self):
        """Test `gather` concurrent functionality."""
        async def test():
            async with Sublemon() as s:
                exit_codes = await s.gather(
                    _sp_exit_with(0),
                    _sp_exit_with(1),
                    _sp_exit_with(2),
                    _sp_exit_with(3),
                    _sp_exit_with(4))
                self.assertEqual(exit_codes, [0, 1, 2, 3, 4])
        crossplat_loop_run(test())
