"""
Tests for dhcp2nest.util
"""
from nose.tools import with_setup, eq_
from tempfile import TemporaryDirectory
import os.path
from time import sleep


from dhcp2nest.util import follow_file


TEMPDIR = None


def follow_setup():
    """
    Setup for follow_file tests
    """
    global TEMPDIR
    TEMPDIR = TemporaryDirectory()


def follow_teardown():
    """
    Teardown for follow_file tests
    """
    TEMPDIR.cleanup()


# #################
# follow_file tests
# #################
@with_setup(follow_setup, follow_teardown)
def test_basic_follow():
    tmp_fn = os.path.join(TEMPDIR.name, 'basic.log')
    with open(tmp_fn, 'w') as out_file:
        q = follow_file(tmp_fn)
        sleep(0.125)
        out_file.write('test line\n')
    eq_(q.get(timeout=5), 'test line\n')
