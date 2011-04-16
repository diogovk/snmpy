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
        Method to execute SNMPWALK
        """
        result = subprocess.Popen(("snmpwalk", "-Os", "-v", self._version, "-c",
                self._community, self._dest_host, oid), stdout=subprocess.PIPE,
                stderr=subprocess.PIPE).stdout.read().split("\n")
        
        return self._filter(result, first_value)


    def get(self, oid, first_value=True):
        """
        Method to execute SNMPGET
        """
        try:
            result = subprocess.Popen(("snmpget", "-Os", "-v", self._version,
                    "-c", self._community, self._dest_host, oid),
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.read().split("\n")
        except TypeError:
            return {}
        
        return self._filter(result, first_value)

class NetworkInterfaces(Snmpy):
    """
    Class to get all the information to a specific interface
    """
    
    def __init__(self, *args, **kwargs):
        super(NetworkInterfaces, self).__init__(*args, **kwargs)
        self._ifaces = self.walk("ifDescr", first_value=False)
        self._all_elements = {'status' : 'ifOperStatus', 'speed' : 'ifSpeed',
                'in_oct' : 'ifInOctets', 'in_discards' : 'ifInDiscards',
                'in_errors' : 'ifInErrors', 'out_oct' : 'ifOutOctets',
                'out_discards' : 'ifOutDiscards', 'out_errors' : 'ifOutErrors'}
    
    def _get_the_iface(self, iface):
        """
        search the spefic interface
        """
        for i in self._ifaces:
            if self._ifaces[i]['value'] == iface:
                self._my_iface = self._ifaces[i]
                return True

        return False

    def _get_all_elements(self):
        """
        get all information from interface
        """
        iface = {}
        index = self._my_iface['index']
        for i in self._all_elements:
            value = self.get(self._all_elements[i] + "." + index)
            iface[i] = value[0]['value']
            
        return iface

    def get_iface_infs(self, iface):
        if not self._get_the_iface(iface):
            raise AttributeError("Interface not found")

        return self._get_all_elements()


if __name__ == "__main__":
    """ Main created to tests """

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-H", "--host", dest="host", help="Device address",
            default="127.0.0.1")
    parser.add_option("-C", "--community", dest="community", default="public",
            help="Community to be access")
    parser.add_option("-O", "--oid", dest="oid", help="OID to consult")
    (options, args) = parser.parse_args()

    snmp = NetworkInterfaces(dest_host=options.host, community=options.community)
    print snmp.get_iface_infs(options.oid)

