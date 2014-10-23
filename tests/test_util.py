"""
Tests for dhcp2nest.util
"""
from nose.tools import with_setup, eq_, raises
from tempfile import TemporaryDirectory
import os.path
from time import sleep
import asyncio


from dhcp2nest.util import run_until_complete, async_test, follow_file


TEMPDIR = None

# ########################
# run_until_complete tests
# ########################


def test_run_until_complete_basic():
    eq_(run_until_complete(asyncio.sleep(0.5, 'done'), timeout=2), 'done')


@raises(asyncio.TimeoutError)
def test_run_until_complete_timeout():
   run_until_complete(asyncio.sleep(2), timeout=0.5)


@async_test(timeout=2)
def test_async_test_basic():
    result = yield from asyncio.sleep(0.5, 'done')
    eq_(result, 'done')


@raises(asyncio.TimeoutError)
@async_test(timeout=0.5)
def test_async_test_basic():
    result = yield from asyncio.sleep(2.0, 'done')
    eq_(result, 'done')


# #################
# follow_file tests
# #################


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


@with_setup(follow_setup, follow_teardown)
def test_basic_follow():
    tmp_fn = os.path.join(TEMPDIR.name, 'basic.log')
    with open(tmp_fn, 'w') as out_file:
        q = follow_file(tmp_fn)
        sleep(0.125)
        out_file.write('test line\n')
    eq_(q.get(timeout=2), 'test line\n')
