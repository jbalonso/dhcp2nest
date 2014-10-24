"""
Tests for dhcp2net.dhcp
"""

from asyncio import Queue, TimeoutError
from nose.tools import eq_, raises
from dhcp2nest.util import async_test
from dhcp2nest.dhcp import DhcpEvent, find_events


MATCHING_TESTS = (
    (('Oct 23 17:57:13 charon dhcpd: DHCPREQUEST for 192.168.100.83 '
      '(192.168.100.1) from a0:0b:ba:21:fc:ca '
      '(android-3c91e7e99798cb2b) via vlan5\n'),
     DhcpEvent(event='DHCPREQUEST', mac='a0:0b:ba:21:fc:ca',
         ip='192.168.100.83', name='android-3c91e7e99798cb2b', iface='vlan5')),
    (('Oct 23 02:45:00 charon dhcpd: DHCPACK on 192.168.100.104 '
      'to ec:55:f9:54:a9:64 (NPI7CC6A7) via vlan5\n'),
     DhcpEvent(event='DHCPACK', mac='ec:55:f9:54:a9:64', ip='192.168.100.104',
         name='NPI7CC6A7', iface='vlan5')),
     (('Oct 22 22:53:55 charon dhcpd: DHCPDISCOVER from 88:53:2e:99:5c:dc '
       'via vlan5'),
      DhcpEvent(event='DHCPDISCOVER', mac='88:53:2e:99:5c:dc', ip=None,
         name=None, iface='vlan5')),
)


NONMATCHING_TESTS = (
    'Oct 23 13:45:37 charon dhcpd: Can\'t create new lease file: '
    'Permission denied ',
    'Oct 23 00:20:36 charon dhcpd: Removed forward map from '
    'CatherinesMBP3.jayst to 192.168.100.75',
    'This has nothing to do with dhcp',
)


@async_test(timeout=4)
def test_matching():
    i_queue = Queue()
    o_queue = find_events(i_queue)

    for in_string, event in MATCHING_TESTS:
        yield from i_queue.put(in_string)
        ev = yield from o_queue.get()
        eq_(ev, event)


@raises(TimeoutError)
@async_test(timeout=4)
def test_nonmatching():
    i_queue = Queue()
    o_queue = find_events(i_queue)

    for in_string in NONMATCHING_TESTS:
        yield from i_queue.put(in_string)

    yield from o_queue.get()
