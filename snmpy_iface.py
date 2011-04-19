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
    parser = OptionParser()
    parser.add_option("-i","--iface", dest="iface", help="Network Iface to be a
    consulted", default="eth0")
    parser.add_option("-H", "--host", dest="host", help="Device address",
            default="127.0.0.1")
    parser

