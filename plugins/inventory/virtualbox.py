# -*- coding: utf-8 -*-
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    author: Unknown (!UNKNOWN)
    name: virtualbox
    short_description: virtualbox inventory source
    description:
        - Get inventory hosts from the local virtualbox installation.
        - Uses a YAML configuration file that ends with virtualbox.(yml|yaml) or vbox.(yml|yaml).
        - The inventory_hostname is always the 'Name' of the virtualbox instance.
    extends_documentation_fragment:
      - constructed
      - inventory_cache
    options:
        plugin:
            description: token that ensures this is a source file for the 'virtualbox' plugin
            required: true
            choices: ['virtualbox', 'community.general.virtualbox']
        running_only:
            description: toggles showing all vms vs only those currently running
            type: boolean
            default: false
        settings_password_file:
            description: provide a file containing the settings password (equivalent to --settingspwfile)
        network_info_path:
            description: property path to query for network information (ansible_host)
            default: "/VirtualBox/GuestInfo/Net/0/V4/IP"
        query:
            description: create vars from virtualbox properties
            type: dictionary
            default: {}
'''

EXAMPLES = '''
# file must be named vbox.yaml or vbox.yml
simple_config_file:
    plugin: community.general.virtualbox
    settings_password_file: /etc/virtulbox/secrets
    query:
      logged_in_users: /VirtualBox/GuestInfo/OS/LoggedInUsersList
    compose:
      ansible_connection: ('indows' in vbox_Guest_OS)|ternary('winrm', 'ssh')

# add hosts (all match with minishift vm) to the group container if any of the vms are in ansible_inventory'
plugin: community.general.virtualbox
groups:
  container: "'minis' in (inventory_hostname)"
'''

import os

from subprocess import Popen, PIPE

from ansible.errors import AnsibleParserError
from ansible.module_utils.common.text.converters import to_bytes, to_native, to_text
from ansible.module_utils.common._collections_compat import MutableMapping
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable, Cacheable
from ansible.module_utils.common.process import get_bin_path


class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):
    ''' Host inventory parser for ansible using local virtualbox. '''

    NAME = 'community.general.virtualbox'
    VBOX = "VBoxManage"

    def __init__(self):
        self._vbox_path = None
        super(InventoryModule, self).__init__()

    def _query_vbox_data(self, host, property_path):
        ret = None
        try:
            cmd = [self._vbox_path, b'guestproperty', b'get',
                   to_bytes(host, errors='surrogate_or_strict'),
                   to_bytes(property_path, errors='surrogate_or_strict')]
            x = Popen(cmd, stdout=PIPE)
            ipinfo = to_text(x.stdout.read(), errors='surrogate_or_strict')
            if 'Value' in ipinfo:
                a, ip = ipinfo.split(':', 1)
                ret = ip.strip()
        except Exception:
            pass
        return ret

    def _set_variables(self, hostvars):

        # set vars in inventory from hostvars
        for host in hostvars:

            query = self.get_option('query')
            # create vars from vbox properties
            if query and isinstance(query, MutableMapping):
                for varname in query:
                    hostvars[host][varname] = self._query_vbox_data(host, query[varname])

            strict = self.get_option('strict')

            # create composite vars
            self._set_composite_vars(self.get_option('compose'), hostvars[host], host, strict=strict)

            # actually update inventory
            for key in hostvars[host]:
                self.inventory.set_variable(host, key, hostvars[host][key])

            # constructed groups based on conditionals
            self._add_host_to_composed_groups(self.get_option('groups'), hostvars[host], host, strict=strict)

            # constructed keyed_groups
            self._add_host_to_keyed_groups(self.get_option('keyed_groups'), hostvars[host], host, strict=strict)

    def _populate_from_cache(self, source_data):
        hostvars = source_data.pop('_meta', {}).get('hostvars', {})
        for group in source_data:
            if group == 'all':
                continue
            else:
                group = self.inventory.add_group(group)
                hosts = source_data[group].get('hosts', [])
                for host in hosts:
                    self._populate_host_vars([host], hostvars.get(host, {}), group)
                self.inventory.add_child('all', group)
        if not source_data:
            for host in hostvars:
                self.inventory.add_host(host)
                self._populate_host_vars([host], hostvars.get(host, {}))

    def _populate_from_source(self, source_data, using_current_cache=False):
        if using_current_cache:
            self._populate_from_cache(source_data)
            return source_data

        cacheable_results = {'_meta': {'hostvars': {}}}

        hostvars = {}
        prevkey = pref_k = ''
        current_host = None

        # needed to possibly set ansible_host
        netinfo = self.get_option('network_info_path')

        for line in source_data:
            line = to_text(line)
            if ':' not in line:
                continue
            try:
                k, v = line.split(':', 1)
            except Exception:
                # skip non splitable
                continue

            if k.strip() == '':
                # skip empty
                continue

            v = v.strip()
            # found host
            if k.startswith('Name') and ',' not in v:  # some setting strings appear in Name
                current_host = v
                if current_host not in hostvars:
                    hostvars[current_host] = {}
                    self.inventory.add_host(current_host)

                # try to get network info
                netdata = self._query_vbox_data(current_host, netinfo)
                if netdata:
                    self.inventory.set_variable(current_host, 'ansible_host', netdata)

            # found groups
            elif k == 'Groups':
                for group in v.split('/'):
                    if group:
                        group = self.inventory.add_group(group)
                        self.inventory.add_child(group, current_host)
                        if group not in cacheable_results:
                            cacheable_results[group] = {'hosts': []}
                        cacheable_results[group]['hosts'].append(current_host)
                continue

            else:
                # found vars, accumulate in hostvars for clean inventory set
                pref_k = 'vbox_' + k.strip().replace(' ', '_')
                leading_spaces = len(k) - len(k.lstrip(' '))
                if 0 < leading_spaces <= 2:
                    if prevkey not in hostvars[current_host] or not isinstance(hostvars[current_host][prevkey], dict):
                        hostvars[current_host][prevkey] = {}
                    hostvars[current_host][prevkey][pref_k] = v
                elif leading_spaces > 2:
                    continue
                else:
                    if v != '':
                        hostvars[current_host][pref_k] = v
                if self._ungrouped_host(current_host, cacheable_results):
                    if 'ungrouped' not in cacheable_results:
                        cacheable_results['ungrouped'] = {'hosts': []}
                    cacheable_results['ungrouped']['hosts'].append(current_host)

                prevkey = pref_k

        self._set_variables(hostvars)
        for host in hostvars:
            h = self.inventory.get_host(host)
            cacheable_results['_meta']['hostvars'][h.name] = h.vars

        return cacheable_results

    def _ungrouped_host(self, host, inventory):
        def find_host(host, inventory):
            for k, v in inventory.items():
                if k == '_meta':
                    continue
                if isinstance(v, dict):
                    yield self._ungrouped_host(host, v)
                elif isinstance(v, list):
                    yield host not in v
            yield True

        return all(find_host(host, inventory))

    def verify_file(self, path):

        valid = False
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(('virtualbox.yaml', 'virtualbox.yml', 'vbox.yaml', 'vbox.yml')):
                valid = True
        return valid

    def parse(self, inventory, loader, path, cache=True):

        try:
            self._vbox_path = get_bin_path(self.VBOX)
        except ValueError as e:
            raise AnsibleParserError(e)

        super(InventoryModule, self).parse(inventory, loader, path)

        cache_key = self.get_cache_key(path)

        config_data = self._read_config_data(path)

        # set _options from config data
        self._consume_options(config_data)

        source_data = None
        if cache:
            cache = self.get_option('cache')

        update_cache = False
        if cache:
            try:
                source_data = self._cache[cache_key]
            except KeyError:
                update_cache = True

        if not source_data:
            b_pwfile = to_bytes(self.get_option('settings_password_file'), errors='surrogate_or_strict', nonstring='passthru')
            running = self.get_option('running_only')

            # start getting data
            cmd = [self._vbox_path, b'list', b'-l']
            if running:
                cmd.append(b'runningvms')
            else:
                cmd.append(b'vms')

            if b_pwfile and os.path.exists(b_pwfile):
                cmd.append(b'--settingspwfile')
                cmd.append(b_pwfile)

            try:
                p = Popen(cmd, stdout=PIPE)
            except Exception as e:
                raise AnsibleParserError(to_native(e))

            source_data = p.stdout.read().splitlines()

        using_current_cache = cache and not update_cache
        cacheable_results = self._populate_from_source(source_data, using_current_cache)

        if update_cache:
            self._cache[cache_key] = cacheable_results
