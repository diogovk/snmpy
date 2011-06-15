#! /usr/bin/env python

import re
import subprocess


class Snmpy(object):
    """
    Basic instructions to handle with SNMP.
    """

    def __init__(self, dest_host, community, version='2c'):
        self._dest_host = dest_host
        self._community = community
        self._version = version

    def _subprocess(self, cmd, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE):
        """
        Wraps subprocess calls.
        """
        response = subprocess.Popen(cmd, stdout=stdout, stderr=stderr)
        return response.stdout.read()

    def _filter(self, walk_result, first_value=True):
        """
        Gets a SNPWALK result and returns a dict.
        """
        walk_result = walk_result.split('\n')
        result = []
        pattern = '(?P<group>\w+)\.(?P<index>\d+) = (?P<type>\w+): '

        if first_value:
            pattern += '(?P<value>[\:\/\w]+)'
        else:
            pattern += '(?P<value>.+)'

        pattern = re.compile(pattern)

        for i in walk_result:
            line_search = pattern.search(i)
            try:
                line_search = line_search.groupdict()
                result.append(line_search)
            except AttributeError:
                pass

        return result

    def walk(self, oid, first_value=True):
        """
        Executes SNMPWALK to read values from SNMP.
        """
        result = self._subprocess(('snmpwalk', '-Os', '-v', self._version,
            '-c', self._community, self._dest_host, oid))

        return self._filter(result, first_value)

    def get(self, oid, first_value=True):
        """
        Executes SNMPGET to get values from SNMP.
        """
        try:
            result = self._subprocess(('snmpget', '-Os', '-v', self._version,
                '-c', self._community, self._dest_host, oid))
        except TypeError:
            return {}

        return self._filter(result, first_value)

    def get_all_elements(self, index):
        """
        get all information for specific object
        """
        values = {}
        for i in self._all_elements:
            value = self.get(self._all_elements[i] + "." + index)
            try:
                values[i] = value[0]['value']
            except KeyError:
                values[i] = 0

        return values


class SnmpyInterface(Snmpy):
    """
    Adds dict behavior to Snmpy's children.
    """
    oid = None
    elements = None
    _key_error_msg = "Undefined Index"
    _first_value = True

    def __init__(self, *args, **kwargs):
        if not self.oid or not self.elements:
            raise ValueError("Please, fill elements and oid attributes")

        super(SnmpyInterface, self).__init__(*args, **kwargs)

        # Executes SNMPWALK with specific OID to grab
        # information about elements
        self.walk_result = self.walk(self.oid, self._first_value)
        self._items = self._reorder_to_dict()

    def __getitem__(self, item):
        """
        Retrieve an element from _items with dict behaviour.
        """
        if type(item) != str or item not in self._items:
            raise KeyError(self._key_error_msg)

        return self._items[item]

    def _reorder_to_dict(self):
        """
        Regroups SNMPWALK result and get element details
        """
        response = {}

        for i in self.walk_result:
            elm = i['value']
            index = i['index']
            response.setdefault(elm, {})

            for j in self.elements:
                value = self.get(self.elements[j] + '.' + index)
                response[elm][j] = value[0]['value']

        return response


class NetworkInterfaces(SnmpyInterface):
    """
    Specific SNMP instructions to get iface informations.
    """
    oid = 'ifDescr'
    elements = {
        'status': 'ifOperStatus',
        'speed': 'ifSpeed',
        'in_oct': 'ifInOctets',
        'in_discards': 'ifInDiscards',
        'in_errors': 'ifInErrors',
        'out_oct': 'ifOutOctets',
        'out_discards': 'ifOutDiscards',
        'out_errors': 'ifOutErrors',
    }
    _key_error_msg = "Network interface not found"
    _first_value = False


class DiskIO(SnmpyInterface):
    """
    Specific SNMP instructions to get all information about diskIO.
    """
    oid = 'diskIODevice'
    elements = {
        'NRead': 'diskIONRead',
        'NWrite': 'diskIONWritten',
        'Reads': 'diskIOReads',
        'Writes': 'diskIOWrites',
    }
    _key_error_msg = "Disk label not found"


class DiskStorage(SnmpyInterface):
    """
    Specific SNMP instructions to get all information about storage.
    """
    oid = 'hrStorageDescr'
    elements = {
        'used': 'hrStorageUsed',
        'size': 'hrStorageSize',
        'units': 'hrStorageAllocationUnits',
        'type': 'hrStorageType',
    }
    _key_error_msg = "Storage label not found"
