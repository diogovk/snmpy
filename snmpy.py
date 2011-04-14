#! /usr/bin/env python

import sys
import subprocess
import re

class Snmpy(object):
    """
    Basic Class to consult SNMP
    """

    def __init__(self, dest_host, community, version="2c"):
            self._dest_host = dest_host
            self._community = community
            self._version = version
    

    def _filter(self, text, first_value=True):
        """
        Regular expression to agregate the values
        """
        result = dict()
        if first_value:
            pattern = re.compile('(?P<group>\w+)\.(?P<index>\d+) = (?P<type>\w+): (?P<value>[\:\/\w]+)')
        else:
            pattern = re.compile('(?P<group>\w+)\.(?P<index>\d+) = (?P<type>\w+): (?P<value>.+)')
    
        for i in range(len(text)):
            line_search = pattern.search(text[i])
            try:
                line_search = line_search.groupdict()
                result[i] = (line_search)  
            except AttributeError:
                pass

        return result


    def walk(self, oid, first_value=True):
        """
        Basic class to execute SNMPWALK
        """
        result = subprocess.Popen(("snmpwalk", "-Os", "-v", self._version, "-c",
                self._community, self._dest_host, oid), stdout=subprocess.PIPE,
                stderr=subprocess.PIPE).stdout.read().split("\n")
        
        return self._filter(result, first_value)


    def get(self, oid, first_value=True):
        """
        Basic class to execute SNMPGET
        """
        try:
            result = subprocess.Popen(("snmpget", "-OvQ", "-v", self._version,
                    "-c", self._community, self._dest_host, oid),
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.read().split("\n")
        except TypeError:
            return ()

        return tuple(result)

if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-H", "--host", dest="host", help="Device address")
    parser.add_option("-C", "--community", dest="community", help="Community to be access")
    parser.add_option("-O", "--oid", dest="oid", help="OID to consult")
    (options, args) = parser.parse_args()

    snmp = Snmpy(dest_host=options.host, community=options.community)

    s = snmp.walk(options.oid, first_value=True);
    print s
