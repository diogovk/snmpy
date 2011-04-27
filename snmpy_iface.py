#! /usr/bin/env python

import sys
import time
import pickle
from sys import exit
from snmpy import NetworkInterfaces

TMP_DIR = "/tmp/"

class SnmpyIface(NetworkInterfaces):
    """
    snmpy plugin to get Network interfaces information
    """

    def __init__(self, *args, **kwargs):
        super(SnmpyIface, self).__init__(*args, **kwargs)

    def _update_file(self, iface, infs):
        iface_s = iface.replace(" ","_").replace("/","_")        
        first = False;
        infs["name"] = iface
        infs["time"] = int(time.time())
        try:
            with open(TMP_DIR + 'history_'  + iface_s + '_' + self._dest_host + '.pickle',
                    'rb') as f:
                history = pickle.load(f)
                del history[5:]
        except IOError:
            history = []
            first = True
        else:
            f.close()

        history.insert(0,infs)
        with open(TMP_DIR + 'history_' + iface_s + '_' + self._dest_host +
                '.pickle', 'wb') as f:
            pickle.dump(history,f)
        if first:
            print "store history of iface"
            if infs["status"] == "up":
                exit(0)
            else:
                exit(3)
        return history
        
    def get_iface(self, iface):
        infs = self.get_iface_infs(iface)
        values = self._update_file(iface, infs)
        return {"in" :float(values[0]["in_oct"]) - float(values[1]["in_oct"]), 
                "out" : float(values[0]["out_oct"])  - float(values[1]["out_oct"]), 
                "in_discards" : float(values[0]["in_discards"]) - 
                float(values[1]["in_discards"]),
                "out_discards" : float(values[0]["out_discards"]) -
                float(values[1]["out_discards"]), 
                "in_errors" : float(values[0]["in_errors"]) - 
                float(values[1]["in_errors"]), 
                "out_errors" : float(values[0]["out_errors"]) - 
                float(values[1]["out_errors"]), 
                "speed" : values[0]["speed"], 
                "name" : values[0]["name"] }
        
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
    print r.get_iface(options.iface)
