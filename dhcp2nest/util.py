"""
Utility functions for dhcp2nest
"""
import asyncio.subprocess
from subprocess import Popen, PIPE
from threading import Thread
from functools import wraps


def run_until_complete(coro, timeout=None, loop=None):
    """
    Run an asyncio loop for a particular coroutine, returning its value or
    raising a timeout if the futures do not complete before the timeout has
    elapsed.
    """
    # Get the current loop if necessary
    loop = loop or asyncio.get_event_loop()

    @asyncio.coroutine
    def waiter():
        """
        Construct a coroutine that waits for the futures in coros and returns a
        list
        """
        for future in asyncio.as_completed([coro], loop=loop, timeout=timeout):
            result = yield from future
            return result

    return loop.run_until_complete(waiter())


def async_test(timeout=None, loop=None):
    """
    Return a decorator that wraps a coroutine such that it can be used as a test
    """
    def decorator(test):
        @wraps(test)
        def wrapper(*args, **kwargs):
            return run_until_complete(test(*args, **kwargs), timeout=timeout,
                    loop=loop)
        return wrapper
    return decorator


def follow_file(fn, max_lines=100, loop=None):
    """
    Return a Queue that is fed lines (up to max_lines) from the given file (fn)
    continuously, starting with the last line in the file

    The implementation given here was inspired by
    http://stackoverflow.com/questions/12523044/how-can-i-tail-a-log-file-in-python
    """
    fq = asyncio.Queue(maxsize=max_lines, loop=loop)

    @asyncio.coroutine
    def _follow_file_task(fn, fq):
        """
        Queue lines from the given file (fn) continuously, even as the file
        grows or is replaced

        WARNING: This generator will block forever on the tail subprocess--no
        timeouts are enforced.
        """
        # Use system tail with name-based following and retry
        create = asyncio.create_subprocess_exec("tail", "-n1", "-F", fn,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL)
        proc = yield from create

        # Loop forever on pulling data from tail
        line = True
        while line:
            line = yield from proc.stdout.readline()
            yield from fq.put(line.decode('utf-8'))

    # Spawn a thread to read data from tail
    asyncio.async(_follow_file_task(fn, fq), loop=loop)

    # Return the queue
    return fq
