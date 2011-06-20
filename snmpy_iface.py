# -*- coding:utf-8 -*-
#! /usr/bin/env python

import sys
import time
import pickle
from sys import exit
from snmpy import NetworkInterfaces
from os import system

TMP_DIR = "/tmp/"
WINDOW_TIME = 20

class SnmpyIface(NetworkInterfaces):
    """
    snmpy plugin to get Network interfaces information
    """

    def __init__(self, dest_host, community):
        self.ifaces = NetworkInterfaces(dest_host=dest_host, community=community)
        self._dest_host = dest_host
        self._community = community

    def _update_file(self, iface, infs):
        iface_s = iface.replace(" ","_").replace("/","_")        
        first = False;
        infs["name"] = iface
        infs["time"] = int(time.time())
        try:
            with open(TMP_DIR + 'history_'  + iface_s + '_' + self._dest_host + '.pickle',
                    'rb') as f:
                try:
                    history = pickle.load(f)
                    del history[50:]
                except EOFError:
                    print "Error to load history file, restarting the process"
                    system("rm -f "+TMP_DIR+"history_diskIO_"+disk_s+"_"+
                            self._dest_host+".pickle")
                    exit(3)

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
            print "store interface history"
            if infs["status"] == "up":
                exit(0)
            else:
                exit(3)
        return history
        
    def get_iface(self, iface):
        try:
            infs = self.ifaces[iface]
        except AttributeError:
            print "Interface not found"
            exit(2)
        except ValueError:
            print "Destination device not found or SNMP is not present"
            exit(3)
        except:
            print "unknown error"
            exit(3)
        
        values = self._update_file(iface, infs)
        actual_value = values[0];
        old_value = None;
        for v in values:
            if (values[0]["time"] - v["time"]) >= WINDOW_TIME:
                old_value = v
                break

        if not old_value:
            print "store interface history"
            if actual_value["status"] == "up":
                exit(0);
            else:
                exit(3);

        return {"in" :float(actual_value["in_oct"]) - float(old_value["in_oct"]), 
                "out" : float(values[0]["out_oct"])  - float(old_value["out_oct"]), 
                "in_discards" : float(actual_value["in_discards"]) - 
                float(old_value["in_discards"]),
                "out_discards" : float(actual_value["out_discards"]) -
                float(old_value["out_discards"]), 
                "in_errors" : float(actual_value["in_errors"]) - 
                float(old_value["in_errors"]), 
                "out_errors" : float(actual_value["out_errors"]) - 
                float(old_value["out_errors"]), 
                "time" : actual_value["time"] - old_value["time"],
                "speed" : float(actual_value["speed"]), 
                "name" : actual_value["name"], 
                "status" : infs["status"]}

                
    def validate_args(self, warning, critical):
        warning_args = [int(i) for i in warning.split(',')]
        critical_args = [int(i) for i in critical.split(',')]
        for i in range(len(warning_args)):
            if warning_args[i] >= critical_args[i]:
                if i == 0:
                    print "IN warning >= critical"
                elif i == 1:
                    print "OUT warning >= critical"
                elif i == 2:
                    print "ERRORS IN warning >= critical"
                elif i == 3:
                    print "ERRORS OUT warning >= critical"
                elif i == 4:
                    print "DISCARDS IN warning >= critical"
                elif i == 5:
                    print "Discards OUT warning >= critical"

                exit(3)

        return {"out" : {"warning" : warning_args[1], "critical" : critical_args[1]}, "in" : {"warning" : warning_args[0],
          "critical" : critical_args[0]}, "out_errors" : {"warning" : warning_args[3], "critical" : critical_args[3]},
          "in_errors" : {"warning" : warning_args[2], "critical" : critical_args[2]}, "out_discards" : {"warning" : warning_args[5],
          "critical" : critical_args[5]}, "in_discards" : {"warning" : warning_args[4], "critical" : critical_args[4]}}
            

        

if __name__ == "__main__":
    """
    Get all parameters and math the result
    """

    from optparse import OptionParser
    parser = OptionParser(usage = """
        in = In octets
        out = Out octets
        inD = In Discards
        outD = Out Discards
        inE = In Error
        outE = Out Error
        W = Warning values
        C = Critical values

        eg: %prog -i [device iface] -w inW,outW,inDW,outDW,inEW,outEW -c inC,outC,inDC,outDC,inEC,outEC -H [device address] -C [SNMP community]
    """,version="SNMPY version 0.2")
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
    
    try:
        snmp = SnmpyIface(dest_host=options.host, community=options.community)
    except:
        print "unknown error"
        exit(3)

    res = snmp.get_iface(options.iface)
    if res["status"] == "down":
        print "Iface down"
        exit(1)
    else:
        critical = False
        warning = False
        myiface = options.iface
        args = snmp.validate_args(warning = options.warning, critical = options.critical)  
        if res["speed"] == 0:
            res["speed"] = options.speed;

        val = {"in" : ((res["in"] / res["time"]) * 100) / res["speed"],
          "out" : ((res["out"] / res["time"]) * 100) / res["speed"],
          "in_discards" : res["in_discards"],
          "in_errors" : res["in_errors"],
          "out_discards" : res["out_discards"],
          "out_errors" : res["out_errors"]
          }
        result = ""
        if val["in"] > args["in"]["warning"] \
          and val["in"] < args["in"]["critical"]:
            warning = True        
        
        if val["in_discards"] > args["in_discards"]["warning"] \
          and val["in_discards"] < args["in_discards"]["critical"]:
            warning = True                

        if val["in_errors"] > args["in_errors"]["warning"] \
          and val["in_errors"] < args["in_errors"]["critical"]:
            warning = True        

        if val["out"] > args["out"]["warning"] \
          and val["in"] < args["in"]["critical"]:
            warning = True
        
        if val["out_discards"] > args["out_discards"]["warning"] \
          and val["out_discards"] < args["out_discards"]["critical"]:
            warning = True
            
        if val["out_errors"] > args["out_errors"]["warning"] \
          and val["out_errors"] < args["out_errors"]["critical"]:
            warning = True

        if val["in"] > args["in"]["critical"]:
            critical = True
        
        if val["in_discards"] > args["in_discards"]["critical"]:
            critical = True
            
        if val["in_errors"] > args["in_errors"]["critical"]:
            critical = True
            
        if val["out"] > args["out"]["critical"]:
            critical = True
        
        if val["out_discards"] > args["out_discards"]["critical"]:
            critical = True
            
        if val["out_errors"] > args["out_errors"]["critical"]:
            critical = True

        list_print = (val["in"], val["in_discards"], val["in_errors"], 
          val["out"], val["out_discards"], val["out_errors"],val["in"],
          args["in"]["warning"], args["in"]["critical"], val["out"],
          args["out"]["warning"], args["out"]["critical"], val["in_errors"],
          val["in_discards"], val["out_errors"], val["out_discards"])
        
        print "IN = %.2f%% ; d%.0f ; e%.0f  OUT = %.2f%% ; d%.0f ; e%.0f | 'iface_in_prct'=%.2f%%;%.0f;%.0f;0;100 'iface_out_prct'=%.2f%%;%.0f;%.0f;0;100 'iface_in_error'=%.0fc 'iface_in_discard'=%.0fc 'iface_out_error'=%.0fc 'iface_out_discard'=%.0fc"  % list_print

        if critical:
            exit(2)

        if warning:
            exit(1)

        exit(0)

