"""
Utility functions for dhcp2nest
"""
import asyncio
from queue import Queue
from subprocess import Popen, PIPE
from threading import Thread


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


def follow_file(fn, max_lines=100):
    """
    Return a Queue that is fed lines (up to max_lines) from the given file (fn)
    continuously

    The implementation given here was inspired by
    http://stackoverflow.com/questions/12523044/how-can-i-tail-a-log-file-in-python
    """
    fq = Queue(maxsize=max_lines)

    def _follow_file_thread(fn, fq):
        """
        Queue lines from the given file (fn) continuously, even as the file
        grows or is replaced

        WARNING: This generator will block forever on the tail subprocess--no
        timeouts are enforced.
        """
        # Use system tail with name-based following and retry
        p = Popen(["tail", "-n0", "-F", fn], stdout=PIPE)

        # Loop forever on pulling data from tail
        line = True
        while line:
            line = p.stdout.readline().decode('utf-8')
            fq.put(line)

    # Spawn a thread to read data from tail
    Thread(target=_follow_file_thread, args=(fn, fq), daemon=True).start()

    # Return the queue
    return fq
