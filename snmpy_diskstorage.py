# -*- coding:utf-8 -*-
#! /usr/bin/env python

from sys import exit
from snmpy import DiskStorage
from os import system

class SnmpyDiskStorage(DiskStorage):
    """
    snmpy plugin to get partion storage used
    """

    def __init__(self, *args, **kwargs):
        super(SnmpyDiskStorage, self).__init__(*args, **kwargs)

