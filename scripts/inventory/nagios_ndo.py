#!/usr/bin/env python

# (c) 2014, Jonathan Lestrelin <jonathan.lestrelin@gmail.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

"""
Nagios NDO external inventory script.
========================================

Returns hosts and hostgroups from Nagios NDO.

Configuration is read from `nagios_ndo.ini`.
"""

import os
import argparse
import sys
from ansible.module_utils.six.moves import configparser
import json

try:
    from sqlalchemy import text
    from sqlalchemy.engine import create_engine
except ImportError:
    sys.exit("Error: SQLAlchemy is needed. Try something like: pip install sqlalchemy")


class NagiosNDOInventory(object):

    def read_settings(self):
        config = configparser.SafeConfigParser()
        config.read(os.path.dirname(os.path.realpath(__file__)) + '/nagios_ndo.ini')
        if config.has_option('ndo', 'database_uri'):
            self.ndo_database_uri = config.get('ndo', 'database_uri')

    def read_cli(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--host', nargs=1)
        parser.add_argument('--list', action='store_true')
        self.options = parser.parse_args()

    def get_hosts(self):
        engine = create_engine(self.ndo_database_uri)
        connection = engine.connect()
        select_hosts = text("SELECT display_name \
                            FROM nagios_hosts")
        select_hostgroups = text("SELECT alias \
                                 FROM nagios_hostgroups")
        select_hostgroup_hosts = text("SELECT h.display_name \
                                       FROM nagios_hostgroup_members hgm, nagios_hosts h, nagios_hostgroups hg \
                                       WHERE hgm.hostgroup_id = hg.hostgroup_id \
                                       AND hgm.host_object_id = h.host_object_id \
                                       AND hg.alias =:hostgroup_alias")

        hosts = connection.execute(select_hosts)
        self.result['all']['hosts'] = [host['display_name'] for host in hosts]

        for hostgroup in connection.execute(select_hostgroups):
            hostgroup_alias = hostgroup['alias']
            self.result[hostgroup_alias] = {}
            hosts = connection.execute(select_hostgroup_hosts, hostgroup_alias=hostgroup_alias)
            self.result[hostgroup_alias]['hosts'] = [host['display_name'] for host in hosts]

    def __init__(self):

        self.defaultgroup = 'group_all'
        self.ndo_database_uri = None
        self.options = None

        self.read_settings()
        self.read_cli()

        self.result = {}
        self.result['all'] = {}
        self.result['all']['hosts'] = []
        self.result['_meta'] = {}
        self.result['_meta']['hostvars'] = {}

        if self.ndo_database_uri:
            self.get_hosts()
            if self.options.host:
                print(json.dumps({}))
            elif self.options.list:
                print(json.dumps(self.result))
            else:
                sys.exit("usage: --list or --host HOSTNAME")
        else:
            sys.exit("Error: Database configuration is missing. See nagios_ndo.ini.")


NagiosNDOInventory()
