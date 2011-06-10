import unittest2

from snmpy import DiskIO


class DiskOITest(unittest2.TestCase):
    def setUp(self):
        self.dest_host = '127.0.0.1'
        self.community = 'public'
        self.version = '2c'

        self.diskio = DiskIO(self.dest_host, self.community, self.version)

    def test_snmpy_get_diskio(self):
        # TODO: Please, make test test an unit test
        self.assertEquals(type(self.diskio['sda1']), dict)
        self.assertTrue('Reads' in self.diskio['sda1'])
