#! /usr/bin/env python

import sys
import subprocess
import re
from snmpy import NetworkInterfaces

class SnmpyIface(NetworkInterfaces):
    """
    snmpy plugin to get Network interfaces information
    """

    def __init__(self, *args, **kwargs):
        super(SnmpyIface, self).__init__(*args, **kwargs)
        

if __name__ == "__main__":
    """
    Get all parameters and math the result
    """

    from optparse import OptionParser
    parser = OptionParser(version="0.2")
    parser.add_option("-i","--iface", dest="iface", default="eth0", 
            help="Network Iface to be a consulted")
    parser.add_option("-H", "--host", dest="host",default="127.0.0.1", 
            help="Device address")
    parser.add_option("-C", "--community", dest="community", 
            help="SNMP community to consult", default="public")
    parser.add_option("-w", "--warning", dest="warning", 
            help="Waning values inW,outW,inDW,outDW,inEW,outEW", 
            default="80,75,20,20,20,20")
    parser.add_option("-c", "--critical", dest="critical", 
            help="Critical values inC,outC,inDC,outDC,inEC,outEC",
            default="90,85,40,40,40,40")
    parser.add_option("-r", "--real", dest="percent",
            action="store_false", default=True, 
            help="math values in real values")
    parser.add_option("-s", "--speed", dest="speed", type="int", 
            help="interface speed to calculate another value",
            default="10000000")
    (options, args) = parser.parse_args()

    r = SnmpyIface(dest_host=options.host, community=options.community)
    print r.get_iface_infs(options.iface)
