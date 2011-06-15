import unittest2

from snmpy import DiskStorage


class DiskStorageTest(unittest2.TestCase):
    def setUp(self):
        self.dest_host = '127.0.0.1'
        self.community = 'public'
        self.version = '2c'

        self.disk_storage = DiskStorage(self.dest_host, self.community,
            self.version)

    def test_snmpy_get_disk_storage(self):
        # TODO: Please, make this test an unit test
        self.assertEquals(type(self.disk_storage['/']), dict)
        self.assertTrue(self.disk_storage['Physical']['type'],
            'hrStorageRam')
