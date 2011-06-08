#! /usr/bin/env python

import re
import subprocess
import sys


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

    def walk(self, oid):
        """
        Executes SNMPWALK to read values from SNMP.
        """
        result = self._subprocess(('snmpwalk', '-Os', '-v', self._version,
            '-c', self._community, self._dest_host, oid))

        return self._filter(result)
