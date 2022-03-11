# -*- coding: utf-8 -*-
# Copyright (C) 2020 Orion Poplawski <orion@nwra.com>
# Copyright (c) 2020 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    author: Orion Poplawski (@opoplawski)
    name: cobbler
    short_description: Cobbler inventory source
    version_added: 1.0.0
    description:
        - Get inventory hosts from the cobbler service.
        - "Uses a configuration file as an inventory source, it must end in C(.cobbler.yml) or C(.cobbler.yaml) and has a C(plugin: cobbler) entry."
    extends_documentation_fragment:
        - inventory_cache
    options:
      plugin:
        description: The name of this plugin, it should always be set to C(community.general.cobbler) for this plugin to recognize it as it's own.
        required: yes
        choices: [ 'cobbler', 'community.general.cobbler' ]
      url:
        description: URL to cobbler.
        default: 'http://cobbler/cobbler_api'
        env:
            - name: COBBLER_SERVER
      user:
        description: Cobbler authentication user.
        required: no
        env:
            - name: COBBLER_USER
      password:
        description: Cobbler authentication password
        required: no
        env:
            - name: COBBLER_PASSWORD
      cache_fallback:
        description: Fallback to cached results if connection to cobbler fails
        type: boolean
        default: no
      exclude_profiles:
        description:
          - Profiles to exclude from inventory.
          - Ignored if I(include_profiles) is specified.
        type: list
        default: []
        elements: str
      include_profiles:
        description:
          - Profiles to include from inventory.
          - If specified, all other profiles will be excluded.
          - I(exclude_profiles) is ignored if I(include_profiles) is specified.
        type: list
        default: []
        elements: str
        version_added: 4.4.0
      group_by:
        description: Keys to group hosts by
        type: list
        elements: string
        default: [ 'mgmt_classes', 'owners', 'status' ]
      group:
        description: Group to place all hosts into
        default: cobbler
      group_prefix:
        description: Prefix to apply to cobbler groups
        default: cobbler_
      want_facts:
        description: Toggle, if C(true) the plugin will retrieve host facts from the server
        type: boolean
        default: yes
'''

EXAMPLES = '''
# my.cobbler.yml
plugin: community.general.cobbler
url: http://cobbler/cobbler_api
user: ansible-tester
password: secure
'''

import socket

from ansible.errors import AnsibleError
from ansible.module_utils.common.text.converters import to_text
from ansible.module_utils.six import iteritems
from ansible.plugins.inventory import BaseInventoryPlugin, Cacheable, to_safe_group_name

# xmlrpc
try:
    import xmlrpclib as xmlrpc_client
    HAS_XMLRPC_CLIENT = True
except ImportError:
    try:
        import xmlrpc.client as xmlrpc_client
        HAS_XMLRPC_CLIENT = True
    except ImportError:
        HAS_XMLRPC_CLIENT = False


class InventoryModule(BaseInventoryPlugin, Cacheable):
    ''' Host inventory parser for ansible using cobbler as source. '''

    NAME = 'community.general.cobbler'

    def __init__(self):
        super(InventoryModule, self).__init__()
        self.cache_key = None
        self.connection = None

    def verify_file(self, path):
        valid = False
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(('cobbler.yaml', 'cobbler.yml')):
                valid = True
            else:
                self.display.vvv('Skipping due to inventory source not ending in "cobbler.yaml" nor "cobbler.yml"')
        return valid

    def _get_connection(self):
        if not HAS_XMLRPC_CLIENT:
            raise AnsibleError('Could not import xmlrpc client library')

        if self.connection is None:
            self.display.vvvv('Connecting to %s\n' % self.cobbler_url)
            self.connection = xmlrpc_client.Server(self.cobbler_url, allow_none=True)
            self.token = None
            if self.get_option('user') is not None:
                self.token = self.connection.login(self.get_option('user'), self.get_option('password'))
        return self.connection

    def _init_cache(self):
        if self.cache_key not in self._cache:
            self._cache[self.cache_key] = {}

    def _reload_cache(self):
        if self.get_option('cache_fallback'):
            self.display.vvv('Cannot connect to server, loading cache\n')
            self._options['cache_timeout'] = 0
            self.load_cache_plugin()
            self._cache.get(self.cache_key, {})

    def _get_profiles(self):
        if not self.use_cache or 'profiles' not in self._cache.get(self.cache_key, {}):
            c = self._get_connection()
            try:
                if self.token is not None:
                    data = c.get_profiles(self.token)
                else:
                    data = c.get_profiles()
            except (socket.gaierror, socket.error, xmlrpc_client.ProtocolError):
                self._reload_cache()
            else:
                self._init_cache()
                self._cache[self.cache_key]['profiles'] = data

        return self._cache[self.cache_key]['profiles']

    def _get_systems(self):
        if not self.use_cache or 'systems' not in self._cache.get(self.cache_key, {}):
            c = self._get_connection()
            try:
                if self.token is not None:
                    data = c.get_systems(self.token)
                else:
                    data = c.get_systems()
            except (socket.gaierror, socket.error, xmlrpc_client.ProtocolError):
                self._reload_cache()
            else:
                self._init_cache()
                self._cache[self.cache_key]['systems'] = data

        return self._cache[self.cache_key]['systems']

    def _add_safe_group_name(self, group, child=None):
        group_name = self.inventory.add_group(to_safe_group_name('%s%s' % (self.get_option('group_prefix'), group.lower().replace(" ", ""))))
        if child is not None:
            self.inventory.add_child(group_name, child)
        return group_name

    def _exclude_profile(self, profile):
        if self.include_profiles:
            return profile not in self.include_profiles
        else:
            return profile in self.exclude_profiles

    def parse(self, inventory, loader, path, cache=True):

        super(InventoryModule, self).parse(inventory, loader, path)

        # read config from file, this sets 'options'
        self._read_config_data(path)

        # get connection host
        self.cobbler_url = self.get_option('url')
        self.cache_key = self.get_cache_key(path)
        self.use_cache = cache and self.get_option('cache')

        self.exclude_profiles = self.get_option('exclude_profiles')
        self.include_profiles = self.get_option('include_profiles')
        self.group_by = self.get_option('group_by')

        for profile in self._get_profiles():
            if profile['parent']:
                self.display.vvvv('Processing profile %s with parent %s\n' % (profile['name'], profile['parent']))
                if not self._exclude_profile(profile['parent']):
                    parent_group_name = self._add_safe_group_name(profile['parent'])
                    self.display.vvvv('Added profile parent group %s\n' % parent_group_name)
                    if not self._exclude_profile(profile['name']):
                        group_name = self._add_safe_group_name(profile['name'])
                        self.display.vvvv('Added profile group %s\n' % group_name)
                        self.inventory.add_child(parent_group_name, group_name)
            else:
                self.display.vvvv('Processing profile %s without parent\n' % profile['name'])
                # Create a heirarchy of profile names
                profile_elements = profile['name'].split('-')
                i = 0
                while i < len(profile_elements) - 1:
                    profile_group = '-'.join(profile_elements[0:i + 1])
                    profile_group_child = '-'.join(profile_elements[0:i + 2])
                    if self._exclude_profile(profile_group):
                        self.display.vvvv('Excluding profile %s\n' % profile_group)
                        break
                    group_name = self._add_safe_group_name(profile_group)
                    self.display.vvvv('Added profile group %s\n' % group_name)
                    child_group_name = self._add_safe_group_name(profile_group_child)
                    self.display.vvvv('Added profile child group %s to %s\n' % (child_group_name, group_name))
                    self.inventory.add_child(group_name, child_group_name)
                    i = i + 1

        # Add default group for this inventory if specified
        self.group = to_safe_group_name(self.get_option('group'))
        if self.group is not None and self.group != '':
            self.inventory.add_group(self.group)
            self.display.vvvv('Added site group %s\n' % self.group)

        for host in self._get_systems():
            # Get the FQDN for the host and add it to the right groups
            hostname = host['hostname']  # None
            interfaces = host['interfaces']

            if self._exclude_profile(host['profile']):
                self.display.vvvv('Excluding host %s in profile %s\n' % (host['name'], host['profile']))
                continue

            # hostname is often empty for non-static IP hosts
            if hostname == '':
                for (iname, ivalue) in iteritems(interfaces):
                    if ivalue['management'] or not ivalue['static']:
                        this_dns_name = ivalue.get('dns_name', None)
                        if this_dns_name is not None and this_dns_name != "":
                            hostname = this_dns_name
                            self.display.vvvv('Set hostname to %s from %s\n' % (hostname, iname))

            if hostname == '':
                self.display.vvvv('Cannot determine hostname for host %s, skipping\n' % host['name'])
                continue

            self.inventory.add_host(hostname)
            self.display.vvvv('Added host %s hostname %s\n' % (host['name'], hostname))

            # Add host to profile group
            group_name = self._add_safe_group_name(host['profile'], child=hostname)
            self.display.vvvv('Added host %s to profile group %s\n' % (hostname, group_name))

            # Add host to groups specified by group_by fields
            for group_by in self.group_by:
                if host[group_by] == '<<inherit>>':
                    groups = []
                else:
                    groups = [host[group_by]] if isinstance(host[group_by], str) else host[group_by]
                for group in groups:
                    group_name = self._add_safe_group_name(group, child=hostname)
                    self.display.vvvv('Added host %s to group_by %s group %s\n' % (hostname, group_by, group_name))

            # Add to group for this inventory
            if self.group is not None:
                self.inventory.add_child(self.group, hostname)

            # Add host variables
            if self.get_option('want_facts'):
                try:
                    self.inventory.set_variable(hostname, 'cobbler', host)
                except ValueError as e:
                    self.display.warning("Could not set host info for %s: %s" % (hostname, to_text(e)))
