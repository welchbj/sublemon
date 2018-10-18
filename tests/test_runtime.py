"""Tests for the subprocessing-spawning functionality of `sublemon`."""

import asyncio
import unittest
import shutil
import sys
import time

from sublemon import (
    crossplat_loop_run,
    Sublemon,
    SublemonRuntimeError)

NO_PY = shutil.which('python') is None
if NO_PY:
    print('`python` in PATH is required for testing `sublemon` runtime tests',
          file=sys.stderr)


_SLEEP_DELAY = 0.1


def _sp_sleep_for(t: int) -> str:
    """Return the subprocess cmd for sleeping for `t` seconds."""
    return 'python -c "import time; time.sleep({})"'.format(t)


def _sp_exit_with(e: int) -> str:
    """Return the subprocess cmd for exiting with `e` exit code."""
    return 'python -c "import sys; sys.exit({})"'.format(e)


def _sp_print_stdout(m: str) -> str:
    """Return the subprocess cmd to print `m` to stdout."""
    return 'python -c "print(\'{}\')"'.format(m)


def _sp_print_stderr(m: str) -> str:
    """Return the subprocess cmd to print `m` to stderr."""
    return 'python -c "import sys; print(\'{}\', file=sys.stderr)"'.format(m)


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

    def test_spawn_from_non_started(self):
        """Ensure spawning from an idle server raises an exception."""
        async def test():
            with self.assertRaises(SublemonRuntimeError):
                s = Sublemon()
                s.spawn('anything')
        crossplat_loop_run(test())

    def test_subprocess_tracking(self):
        """Ensure subprocesses move between the running/pending sets."""
        async def test():
            async with Sublemon(max_concurrency=2) as s:
                one, two = s.spawn(
                    _sp_sleep_for(2 * _SLEEP_DELAY),
                    _sp_sleep_for(2 * _SLEEP_DELAY))
                three, = s.spawn(_sp_sleep_for(5 * _SLEEP_DELAY))
                await asyncio.gather(
                    one.wait_running(),
                    two.wait_running())
                self.assertTrue(one in s.running_subprocesses)
                self.assertTrue(two in s.running_subprocesses)
                self.assertTrue(three not in s.running_subprocesses)
                self.assertTrue(three in s.pending_subprocesses)
                await asyncio.gather(
                    one.wait_done(),
                    two.wait_done(),
                    three.wait_running())
                self.assertTrue(one not in s.running_subprocesses)
                self.assertTrue(two not in s.running_subprocesses)
                self.assertTrue(three in s.running_subprocesses)
                await asyncio.gather(three.wait_done())
                self.assertEqual(len(s.running_subprocesses), 0)
                self.assertEqual(len(s.pending_subprocesses), 0)
                self.assertEqual(one.exit_code, 0)
                self.assertEqual(two.exit_code, 0)
                self.assertEqual(three.exit_code, 0)
        crossplat_loop_run(test())

    def test_concurrency_limiting(self):
        """Ensure the `max_concurrency` option works as expected."""
        async def test():
            times = []
            for scalar in (1, 2, 4, 8,):
                start = time.perf_counter()
                async with Sublemon(max_concurrency=scalar) as s:
                    cmds = [_sp_sleep_for(_SLEEP_DELAY) for _ in range(8)]
                    await s.gather(*cmds)
                end = time.perf_counter()
                times.append(end - start)
            self.assertTrue(times[0] > times[1])
            self.assertTrue(times[1] > times[2])
            self.assertTrue(times[2] > times[3])
        crossplat_loop_run(test())

    def test_stop_server_with_running_subprocs(self):
        """Test stopping the server while subprocesses are still running."""
        async def test():
            s = Sublemon()
            await s.start()
            one, two = s.spawn(
                _sp_sleep_for(3 * _SLEEP_DELAY),
                _sp_sleep_for(3 * _SLEEP_DELAY))
            await asyncio.gather(
                one.wait_running(),
                two.wait_running())
            await s.stop()
            # just want to make sure this terminates without exceptions
        crossplat_loop_run(test())

    def test_iter_lines(self):
        """Test iterating over lines from spawned subprocesses."""
        async def test():
            cmds = [
                _sp_print_stdout('A'),
                _sp_print_stdout('B'),
                _sp_print_stderr('C'),
                _sp_print_stderr('D')]
            async with Sublemon() as s:
                # test stdout
                stdout_lines = []
                async for line in s.iter_lines(*cmds, stream='stdout'):
                    stdout_lines.append(line)
                self.assertTrue('A' in stdout_lines)
                self.assertTrue('B' in stdout_lines)
                self.assertEqual(2, len(stdout_lines))

                # test stderr
                stderr_lines = []
                async for line in s.iter_lines(*cmds, stream='stderr'):
                    stderr_lines.append(line)
                self.assertTrue('C' in stderr_lines)
                self.assertTrue('D' in stderr_lines)
                self.assertEqual(2, len(stderr_lines))

                # test all streams
                lines = []
                async for line in s.iter_lines(*cmds):
                    lines.append(line)
                self.assertTrue('A' in lines)
                self.assertTrue('B' in lines)
                self.assertTrue('C' in lines)
                self.assertTrue('D' in lines)
                self.assertEqual(4, len(lines))
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
