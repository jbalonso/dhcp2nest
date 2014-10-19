"""
Utility functions for dhcp2nest
"""
from queue import Queue
from subprocess import Popen, PIPE
from threading import Thread


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
