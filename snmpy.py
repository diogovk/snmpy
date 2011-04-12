#! /usr/bin/env python

import sys
import os
import re

class Snmpy(object):
    """
    Basic Class to consult SNMP
    """

    def __init__(self, dest_host, community, version="2c"):
        self.dest_host = dest_host
        self.community = community
        self.version = version
    
    def _filter(self, text):
        """
        Regular expression to agregate the values
        """
        result = dict()
        pattern = re.compile('(?P<group>\w+)\.(?P<index>\d+) = (?P<type>\w+): (?P<value>\w+)')
        for i in range(len(text)):
            line_search = pattern.search(text[i])
            try:
                line_search = line_search.groupdict()
                result[i] = (line_search)  
            except AttributeError:
                pass

        return result


    def walk(self, oid):
        """
        Basic class to execute SNMPWALK
        """

        result = os.popen("snmpwalk -Os -v" + self.version + " -c " +
                self.community + " " + self.dest_host + " " +
                oid).read().split("\n")

        return self._filter(result)
                   


if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-H", "--host", dest="host", help="Device address")
    parser.add_option("-C", "--community", dest="community", help="Community to be access")
    parser.add_option("-O", "--oid", dest="oid", help="OID to consult")
    (options, args) = parser.parse_args()

    snmp = Snmpy(dest_host=options.host, community=options.community)

    s = snmp.walk("hrStorage");
    print s
