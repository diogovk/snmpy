import unittest

from snmpy import Snmpy

class SnmpyTest(unittest.TestCase):
    def setUp(self):
        self.snmpy = Snmpy(dest_host='127.0.0.1', community='public')

    def test_walk(self):
        response = self.snmpy.walk('ifDescr')
        snmpwalk = [
            {'group': 'ifDescr', 'index': '1', 'type': 'STRING',
                'value': 'lo'},
            {'group': 'ifDescr', 'index': '2', 'type': 'STRING',
                'value': 'eth0'},
            {'group': 'ifDescr', 'index': '3', 'type': 'STRING',
                'value': 'wlan0'},
        ]

        self.assertEquals(response, snmpwalk)
