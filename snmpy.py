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

    def _reorder_to_dict(self, elements):
        """
        Regroups SNMPWALK result and get element details
        """
        response = {}

        for i in self.walk:
            elm = i['value']
            index = i['index']
            response.setdefault(elm, {})

            for j in elements:
                value = self.get(elements[j] + '.' + index)
                response[elm][j] = value[0]['value']

        return response

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


class NetworkInterfaces(Snmpy):
    """
    Specific SNMP instructions to get iface informations.
    """
    oid = 'ifDescr'
    _all_elements = {
        'status': 'ifOperStatus',
        'speed': 'ifSpeed',
        'in_oct': 'ifInOctets',
        'in_discards': 'ifInDiscards',
        'in_errors': 'ifInErrors',
        'out_oct': 'ifOutOctets',
        'out_discards': 'ifOutDiscards',
        'out_errors': 'ifOutErrors',
    }

    def __init__(self, *args, **kwargs):
        super(NetworkInterfaces, self).__init__(*args, **kwargs)

        # Executes SNMPWALK with specific OID to grab ifaces information
        self.walk = self.walk(self.oid, first_value=False)
        self._ifaces = self._reorder_to_dict(self._all_elements)

    def __getitem__(self, items):
        """
        Adds dict behaviour to NetworkInterfaces instances.
        """
        if type(items) != str or items not in self._ifaces:
            raise KeyError('Network interface not found')

        return self._ifaces[items]


class DiskIO(Snmpy):
    """
    Specific SNMP instructions to get all information about diskIO.
    """
    oid = 'diskIODevice'
    _all_elements = {
        'NRead': 'diskIONRead',
        'NWrite': 'diskIONWritten',
        'Reads': 'diskIOReads',
        'Writes': 'diskIOWrites',
    }

    def __init__(self, *args, **kwargs):
        super(DiskIO, self).__init__(*args, **kwargs)

        # Executes SNMPWALK with specific OID to grab diskio information
        self.walk = self.walk(self.oid)
        self._disksio = self._reorder_to_dict(self._all_elements)

    def __getitem__(self, items):
        """
        Adds dict behaviour to DiskIO instances.
        """
        if type(items) != str or items not in self._disksio:
            raise KeyError('Disk label not found')

        return self._disksio[items]
