# -*- coding:utf-8 -*-
#! /usr/bin/env python

import time
import pickle
from sys import exit
from snmpy import DiskIO
from os import system

TMP_DIR = "/tmp/"
WINDOW_TIME = 20

class SnmpyDiskIO(DiskIO):
    """
    snmpy plugin to calculate the diskIO (MB AND IO)
    """

    def __init__(self, *args, **kwargs):
        super(SnmpyDiskIO, self).__init__(*args, **kwargs)

    def _update_file(self, disk, infs):
        disk_s = disk.replace(" ","_").replace("/","_")
        first = False
        infs["disk"] = disk
        infs["time"] = int(time.time())
        try:
            with open(TMP_DIR + 'history_diskIO_' + disk_s + '_' +
                    self._dest_host + '.pickle', 'rb') as f:
                try:
                    history = pickle.load(f)
                    del history[50:]
                except EOFError:
                    print "Error to load hitory file, restarting the process"
                    system("rm -f "+TMP_DIR+"history_diskIO_"+disk_s+"_"+
                            self._dest_host+".pickle")
                    exit(3)

        except IOError:
            history = []
            first = True
        else:
            f.close()

        history.insert(0,infs)
        with open(TMP_DIR + 'history_diskIO_' + disk_s + '_' +
                self._dest_host + '.pickle','wb') as f:
            pickle.dump(history,f)
            f.close()
        if first:
            print "store device disk history"
            exit(0)
        return history
                

    def get_disk(self, disk):
        try:
            infs = self.get_diskIO_infs(disk)
        except AttributeError:
            print "Device disk '%s' not found" % options.device
            exit(2)
        except ValueError:
            print "Destination device not found or SNMP is not present"
            exit(3)
        except:
            print "unknown error"
            exit(3)

        values = self._update_file(disk, infs)
        actual_value = values[0]
        old_value = None
        for v in values:
            if (actual_value["time"] - v["time"]) >= WINDOW_TIME:
                old_value = v
                break

        if not old_value:
            print "store device disk history"
            exit(0)
        
        return {"reads": float(actual_value["Reads"]) -
                float(old_value["Reads"]),
                "writes": float(actual_value["Writes"]) -
                float(old_value["Writes"]),
                "NRead": float(actual_value["NRead"]) - 
                float(old_value["NRead"]),
                "NWritten": float(actual_value["NWrite"]) -
                float(old_value["NWrite"]),
                "time": actual_value["time"] - old_value["time"]}

    def validate_args(self, warning, critical):
        warning_args = [int(i) for i in warning.split(",")]
        critical_args = [int(i) for i in critical.split(",")]
        TIO = True
        if len(warning_args) < 4 or len(warning_args) != len(critical_args):
            print "warning arguments not correspond with critical arguments"
            exit(3)
        elif len(warning_args) < 5:
            warning_args.insert(4,0)
            critical_args.insert(4,1)
            TIO = False

        for i in range(len(warning_args)):
            if warning_args[i] >= critical_args[i]:
                if i == 0:
                    print "Reads warning >= critical"
                elif i == 1:
                    print "writes warning >= critical"
                elif i == 2:
                    print "NRead warning >= critical"
                elif i == 3:
                    print "NWritten warning >= critical"
                elif i == 4 and not TIO:
                    print "Total IO warning >= critical"
                exit(3)
        return {"Reads" : {"warning": warning_args[0], "critical":
            critical_args[0]}, "Writes": {"warning": warning_args[1],
            "critical": critical_args[1]}, "NRead":{"warning":warning_args[2],
            "critical": critical_args[2]}, "NWritten": {"warning": 
            warning_args[3], "critical": critical_args[3]}, "TIO": {"warning":
            warning_args[4], "critical":critical_args[4]},"TIO_is_defined":TIO}

if __name__ == "__main__":
    """
    Get all parameters and calculates the result
    """

    from optparse import OptionParser
    parser = OptionParser(usage = """
        R = Reads 
        W = Writes 
        NR = MB/s Read 
        NW = MB/s written 
        TIO = Total IO 
        
        eg: %prog -d [device disk] -w R,W,NR,NW[,TIO] -c R,W,MR,NW[,TIO] -H [device address] -C [SNMP community]
    """,version="SNMPY version 0.3")
    parser.add_option("-d","--device", dest="device", default="sda",
            help="device disk to be constulted")
    parser.add_option("-H","--host", dest="host", default="127.0.0.1",
            help="device address")
    parser.add_option("-C", "--community", dest="community", default="public",
            help="SNMP community to be consulted")
    parser.add_option("-w", "--warning", dest="warning",
            default="20,20,20,20,80,80", help="Warning value R,W,NR,NW[,TIO]")
    parser.add_option("-c", "--critical", dest="critical",
            default="30,30,30,30,100,100", 
            help="Critical value R,W,NR,NW[,TIO]")
    (options, args) = parser.parse_args()
    
    try:
        snmp = SnmpyDiskIO(dest_host=options.host, community=options.community) 
    except:
        print "unknown error"
        exit(3)
    
    critical = False
    warning = False
    res = snmp.get_disk(options.device)
    args = snmp.validate_args(warning=options.warning,
            critical=options.critical)
    val = { "NRead" : ((res["NRead"] / res["time"]) / 1024) / 1024,
            "NWritten": ((res["NWritten"] / res["time"]) / 1024) / 1024,
            "Reads": res["reads"] / res["time"],
            "Writes": res["writes"] / res["time"],
            "TIO": (res["reads"] +  res["writes"]) / res["time"]}
    
    if val["Reads"] >= args["Reads"]["warning"] \
        and val["Reads"] < args["Reads"]["critical"]:
        warning = True

    if val["Writes"] >= args["Writes"]["warning"] \
        and val["Writes"] < args["Writes"]["critical"]:
        warning = True

    if val["NRead"] >= args["NRead"]["warning"] \
        and val["NRead"] < args["NRead"]["critical"]:
        warning = True

    if val["NWritten"] >= args["NWritten"]["warning"] \
        and val["NWritten"] < args["NWritten"]["critical"]:
        warning = True

    if args["TIO_is_defined"] and val["TIO"] >= args["TIO"]["warning"]\
        and val["TIO"] < args["TIO"]["critical"]:
        warning = True

    if val["Reads"] >= args["Reads"]["critical"]:
        critical = True
        
    if val["Writes"] >= args["Writes"]["critical"]:
        critical = True

    if val["NRead"] >= args["NRead"]["critical"]:
        critical = True

    if val["NWritten"] >= args["NWritten"]["critical"]:
        critical = True

    if args["TIO_is_defined"] and val["TIO"] >= args["TIO"]["critical"]:
        critical = True

    if args["TIO_is_defined"]:
        print "READ = IO: %.2f, MB/s: %.2f - WRITE = IO: %.2f, MB/s: %.2f - TIO = %.2f | 'reads_io'=%.2f 'NRead'=%.2f 'writes_io'=%.2f 'NWritten'=%.2f 'total_io'=%.2f" % (val["Reads"], val["NRead"], val["Writes"], val["NWritten"], val["TIO"], val["Reads"], val["NRead"], val["Writes"], val["NWritten"], val["TIO"])
    else:
        print "READ = IO: %.2f, MB/s: %.2f - WRITE = IO: %.2f, MB/s: %.2f | 'reads_io'=%.2f 'NRead'=%.2f 'writes_io'=%.2f 'NWritten'=%.2f 'total_io'=0.00" % (val["Reads"], val["NRead"], val["Writes"], val["NWritten"], val["Reads"], val["NRead"], val["Writes"], val["NWritten"])

    if critical:
        exit(2)

    if warning:
        exit(1)

    exit(0)
