import fudge
import unittest2

from snmpy import Snmpy


class SnmpyTest(unittest2.TestCase):
    def setUp(self):
        self.dest_host = '127.0.0.1'
        self.community = 'public'
        self.version = '2c'
        self.snmpy = Snmpy(self.dest_host, self.community, self.version)

    @fudge.patch('subprocess.Popen')
    def test_walk_with_ifdescr(self, FakePopen):
        oid = 'ifDescr'

        # Fake subprocess command
        fake_response = fudge.Fake('response').is_a_stub()
        fake_response.stdout = (fudge.Fake('stdout')
            .provides('read')
           .returns("""ifDescr.1 = STRING: lo
           ifDescr.2 = STRING: eth0
           ifDescr.3 = STRING: wlan0
           """)
        )
        (FakePopen.expects_call()
            .with_args(('snmpwalk', '-Os', '-v', self.version, '-c',
                self.community, self.dest_host, oid), stdout=-1, stderr=-1)
            .returns(fake_response)
        )

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
