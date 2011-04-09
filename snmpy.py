#! /usr/bin/env python

import sys
import os


class Snmpy(object):
    """
    Basic Class to consult SNMP
    """

    def __init__(self, dest_host, community, version="2c"):
        self.dest_host = dest_host
        self.community = community
        self.version = version

    def walk(self, oid):
        """
        Basic class to execute SNMPWALK
        """

        result = os.popen("snmpwalk -Os " + self.version + " -c " +
                self.community + " " + self.dest_host + " " + oid).read()
        return result


if __name__ = "__main__":
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-H", "--host", dest="host", help="Device address")
    parser.add_option("-C", "--community", dest="community", help="Community to be access")
    parser.add_option("-O", "--oid", dest="oid", help="OID to consult")
    (options, args) = parser.parse_args()
