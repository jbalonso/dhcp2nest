"""
Tests for dhcp2nest.util
"""
from nose.tools import with_setup, eq_, raises
from tempfile import TemporaryDirectory
import os.path
from time import sleep
from os import rename
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
@async_test(timeout=1)
def test_basic_follow():
    tmp_fn = os.path.join(TEMPDIR.name, 'basic.log')
    with open(tmp_fn, 'w') as out_file:
        out_file.write('test line\n')
    q = follow_file(tmp_fn)
    eq_((yield from q.get()), 'test line\n')


@with_setup(follow_setup, follow_teardown)
@async_test(timeout=1)
def test_live_follow():
    tmp_fn = os.path.join(TEMPDIR.name, 'basic.log')
    q = follow_file(tmp_fn)
    with open(tmp_fn, 'w') as out_file:
        out_file.write('test line\n')
        out_file.flush()
        eq_((yield from q.get()), 'test line\n')
        out_file.write('another line\n')
        out_file.flush()
        eq_((yield from q.get()), 'another line\n')


@with_setup(follow_setup, follow_teardown)
@async_test(timeout=1)
def test_replacement_follow():
    tmp_fn = os.path.join(TEMPDIR.name, 'basic.log')
    q = follow_file(tmp_fn)

    with open(tmp_fn, 'w') as out_file:
        out_file.write('test line\n')
        out_file.flush()
        eq_((yield from q.get()), 'test line\n')

    with open(tmp_fn, 'w') as out_file:
        out_file.write('another line\n')
        out_file.flush()
        eq_((yield from q.get()), 'another line\n')


@with_setup(follow_setup, follow_teardown)
@async_test(timeout=2)
def test_rename_follow():
    tmp_fn = os.path.join(TEMPDIR.name, 'basic.log')
    new_fn = os.path.join(TEMPDIR.name, 'basic.log.aside')
    q = follow_file(tmp_fn)

    with open(tmp_fn, 'w') as out_file:
        out_file.write('test line\n')
        out_file.flush()
        eq_((yield from q.get()), 'test line\n')
        rename(tmp_fn, new_fn)
        out_file.write('lost line\n')
        out_file.flush()

    with open(tmp_fn, 'w') as out_file:
        out_file.write('another line\n')
        out_file.flush()
        eq_((yield from q.get()), 'another line\n')
