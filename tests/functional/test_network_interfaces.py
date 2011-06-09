import fudge
import unittest2

from snmpy import NetworkInterfaces


class NetworkInterfacesTest(unittest2.TestCase):
    def setUp(self):
        self.dest_host = '127.0.0.1'
        self.community = 'public'
        self.version = '2c'

        self.network_interfaces = NetworkInterfaces(self.dest_host,
            self.community, self.version)

    def test_snmpt_get_iface(self):
        # TODO: Please, make this test an unit test
        self.assertEquals(type(self.network_interfaces['lo']), dict)
        self.assertEquals(self.network_interfaces['lo']['status'], 'up')
