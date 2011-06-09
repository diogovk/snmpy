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
        self._ifaces = self._get_ifaces()

    def _get_ifaces(self):
        """
        Regroups SNMPWALK result and get iface details.
        """

        ifaces = {}

        for i in self.walk:
            iface = i['value']
            index = i['index']
            ifaces.setdefault(iface, {})

            for j in self._all_elements:
                value = self.get(self._all_elements[j] + '.' + index)
                ifaces[iface][j] = value[0]['value']

        return ifaces

    def __getitem__(self, items):
        """
        Adds dict behaviour to NetworkInterfaces instances.
        """

        if type(items) != str or items not in self._ifaces:
            raise KeyError

        return self._ifaces[items]
