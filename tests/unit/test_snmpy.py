import fudge
import unittest2

from snmpy import Snmpy


class SnmpyTest(unittest2.TestCase):
    def setUp(self):
        self.dest_host = '127.0.0.1'
        self.community = 'public'
        self.version = '2c'

        self.snmpy = Snmpy(self.dest_host, self.community, self.version)

    def _fake_subprocess(self, Class_, snmp_command, version, community,
            dest_host, oid, returns):
        fake_response = fudge.Fake('response').is_a_stub()
        fake_response.stdout = (fudge.Fake('stdout')
            .provides('read')
            .returns(returns)
        )

        (Class_.expects_call()
            .with_args((snmp_command, '-Os', '-v', version, '-c', community,
                dest_host, oid), stdout=-1, stderr=-1)
            .returns(fake_response)
        )

    @fudge.patch('subprocess.Popen')
    def test_walk_with_ifdescr(self, FakePopen):
        oid = 'ifDescr'

        # Fake subprocess command
        self._fake_subprocess(FakePopen, 'snmpwalk', self.version,
            self.community, self.dest_host, oid, """ifDescr.1 = STRING: lo
            ifDescr.2 = STRING: eth0
            ifDescr.3 = STRING: wlan0
        """)

        response = self.snmpy.walk(oid)
        snmpwalk = [
            {'group': 'ifDescr', 'index': '1', 'type': 'STRING',
                'value': 'lo'},
            {'group': 'ifDescr', 'index': '2', 'type': 'STRING',
                'value': 'eth0'},
            {'group': 'ifDescr', 'index': '3', 'type': 'STRING',
                'value': 'wlan0'},
        ]

        self.assertEquals(response, snmpwalk)

    @fudge.patch('subprocess.Popen')
    def test_get_with_ifdescr(self, FakePopen):
        oid = 'ifDescr.1'

        # Fake subprocess command
        self._fake_subprocess(FakePopen, 'snmpget', self.version,
            self.community, self.dest_host, oid, 'ifDescr.1 = STRING: lo')

        response = self.snmpy.get(oid)
        snmpget = [{
            'index': '1',
            'group': 'ifDescr',
            'value': 'lo',
            'type': 'STRING',
        }]

        self.assertEquals(response, snmpget)
