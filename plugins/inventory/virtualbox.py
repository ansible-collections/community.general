# -*- coding: utf-8 -*-
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
author: Unknown (!UNKNOWN)
name: virtualbox
short_description: Virtualbox inventory source
description:
  - Get inventory hosts from the local virtualbox installation.
  - Uses a YAML configuration file that ends with virtualbox.(yml|yaml) or vbox.(yml|yaml).
  - The inventory_hostname is always the 'Name' of the virtualbox instance.
  - Groups can be assigned to the VMs using C(VBoxManage). Multiple groups can be assigned by using V(/) as a delimeter.
  - A separate parameter, O(enable_advanced_group_parsing) is exposed to change grouping behaviour. See the parameter documentation
    for details.
extends_documentation_fragment:
  - constructed
  - inventory_cache
options:
  plugin:
    description: Token that ensures this is a source file for the P(community.general.virtualbox#inventory) plugin.
    type: string
    required: true
    choices: ['virtualbox', 'community.general.virtualbox']
  running_only:
    description: Toggles showing all VMs instead of only those currently running.
    type: boolean
    default: false
  settings_password_file:
    description: Provide a file containing the settings password (equivalent to C(--settingspwfile)).
    type: string
  network_info_path:
    description: Property path to query for network information (C(ansible_host)).
    type: string
    default: "/VirtualBox/GuestInfo/Net/0/V4/IP"
  query:
    description: Create vars from virtualbox properties.
    type: dictionary
    default: {}
  enable_advanced_group_parsing:
    description:
      - The default group parsing rule (when this setting is set to V(false)) is to split the VirtualBox VM's group based
        on the V(/) character and assign the resulting list elements as an Ansible Group.
      - Setting O(enable_advanced_group_parsing=true) changes this behaviour to match VirtualBox's interpretation of groups
        according to U(https://www.virtualbox.org/manual/UserManual.html#gui-vmgroups). Groups are now split using the V(,)
        character, and the V(/) character indicates nested groups.
      - When enabled, a VM that's been configured using V(VBoxManage modifyvm "vm01" --groups "/TestGroup/TestGroup2,/TestGroup3")
        results in the group C(TestGroup2) being a child group of C(TestGroup); and the VM being a part of C(TestGroup2)
        and C(TestGroup3).
    default: false
    type: bool
    version_added: 9.2.0
"""

EXAMPLES = r"""
---
# file must be named vbox.yaml or vbox.yml
plugin: community.general.virtualbox
settings_password_file: /etc/virtualbox/secrets
query:
  logged_in_users: /VirtualBox/GuestInfo/OS/LoggedInUsersList
compose:
  ansible_connection: ('indows' in vbox_Guest_OS)|ternary('winrm', 'ssh')

---
# add hosts (all match with minishift vm) to the group container if any of the vms are in ansible_inventory'
plugin: community.general.virtualbox
groups:
  container: "'minis' in (inventory_hostname)"
"""

import os

from subprocess import Popen, PIPE

from ansible.errors import AnsibleParserError
from ansible.module_utils.common.text.converters import to_bytes, to_text
from collections.abc import MutableMapping
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable, Cacheable
from ansible.module_utils.common.process import get_bin_path

from ansible_collections.community.general.plugins.plugin_utils.unsafe import make_unsafe


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
        source_data = make_unsafe(source_data)
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
                current_host = make_unsafe(v)
                if current_host not in hostvars:
                    hostvars[current_host] = {}
                    self.inventory.add_host(current_host)

                # try to get network info
                netdata = self._query_vbox_data(current_host, netinfo)
                if netdata:
                    self.inventory.set_variable(current_host, 'ansible_host', make_unsafe(netdata))

            # found groups
            elif k == 'Groups':
                if self.get_option('enable_advanced_group_parsing'):
                    self._handle_vboxmanage_group_string(v, current_host, cacheable_results)
                else:
                    self._handle_group_string(v, current_host, cacheable_results)
                continue

            else:
                # found vars, accumulate in hostvars for clean inventory set
                pref_k = make_unsafe(f"vbox_{k.strip().replace(' ', '_')}")
                leading_spaces = len(k) - len(k.lstrip(' '))
                if 0 < leading_spaces <= 2:
                    if prevkey not in hostvars[current_host] or not isinstance(hostvars[current_host][prevkey], dict):
                        hostvars[current_host][prevkey] = {}
                    hostvars[current_host][prevkey][pref_k] = make_unsafe(v)
                elif leading_spaces > 2:
                    continue
                else:
                    if v != '':
                        hostvars[current_host][pref_k] = make_unsafe(v)
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

    def _handle_group_string(self, vboxmanage_group, current_host, cacheable_results):
        '''Handles parsing the VM's Group assignment from VBoxManage according to this inventory's initial implementation.'''
        # The original implementation of this inventory plugin treated `/` as
        # a delimeter to split and use as Ansible Groups.
        for group in vboxmanage_group.split('/'):
            if group:
                group = make_unsafe(group)
                group = self.inventory.add_group(group)
                self.inventory.add_child(group, current_host)
                if group not in cacheable_results:
                    cacheable_results[group] = {'hosts': []}
                cacheable_results[group]['hosts'].append(current_host)

    def _handle_vboxmanage_group_string(self, vboxmanage_group, current_host, cacheable_results):
        '''Handles parsing the VM's Group assignment from VBoxManage according to VirtualBox documentation.'''
        # Per the VirtualBox documentation, a VM can be part of many groups,
        # and it is possible to have nested groups.
        # Many groups are separated by commas ",", and nested groups use
        # slash "/".
        # https://www.virtualbox.org/manual/UserManual.html#gui-vmgroups
        # Multi groups: VBoxManage modifyvm "vm01" --groups "/TestGroup,/TestGroup2"
        # Nested groups: VBoxManage modifyvm "vm01" --groups "/TestGroup/TestGroup2"

        for group in vboxmanage_group.split(','):
            if not group:
                # We could get an empty element due how to split works, and
                # possible assignments from VirtualBox. e.g. ,/Group1
                continue

            if group == "/":
                # This is the "root" group. We get here if the VM was not
                # assigned to a particular group. Consider the host to be
                # unassigned to a group.
                continue

            parent_group = None
            for subgroup in group.split('/'):
                if not subgroup:
                    # Similarly to above, we could get an empty element.
                    # e.g //Group1
                    continue

                if subgroup == '/':
                    # "root" group.
                    # Consider the host to be unassigned
                    continue

                subgroup = make_unsafe(subgroup)
                subgroup = self.inventory.add_group(subgroup)
                if parent_group is not None:
                    self.inventory.add_child(parent_group, subgroup)
                self.inventory.add_child(subgroup, current_host)
                if subgroup not in cacheable_results:
                    cacheable_results[subgroup] = {'hosts': []}
                cacheable_results[subgroup]['hosts'].append(current_host)

                parent_group = subgroup

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
                raise AnsibleParserError(str(e))

            source_data = p.stdout.read().splitlines()

        using_current_cache = cache and not update_cache
        cacheable_results = self._populate_from_source(source_data, using_current_cache)

        if update_cache:
            self._cache[cache_key] = cacheable_results
