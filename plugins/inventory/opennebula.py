# -*- coding: utf-8 -*-
# Copyright (c) 2020, FELDSAM s.r.o. - FeldHost™ <support@feldhost.cz>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r'''
    name: opennebula
    author:
        - Kristian Feldsam (@feldsam)
    short_description: OpenNebula inventory source
    version_added: "3.8.0"
    extends_documentation_fragment:
        - constructed
    description:
        - Get inventory hosts from OpenNebula cloud.
        - Uses an YAML configuration file ending with either I(opennebula.yml) or I(opennebula.yaml)
          to set parameter values.
        - Uses I(api_authfile), C(~/.one/one_auth), or C(ONE_AUTH) pointing to a OpenNebula credentials file.
    options:
        plugin:
            description: Token that ensures this is a source file for the 'opennebula' plugin.
            type: string
            required: true
            choices: [ community.general.opennebula ]
        api_url:
            description:
              - URL of the OpenNebula RPC server.
              - It is recommended to use HTTPS so that the username/password are not
                transferred over the network unencrypted.
              - If not set then the value of the C(ONE_URL) environment variable is used.
            env:
              - name: ONE_URL
            required: true
            type: string
        api_username:
            description:
              - Name of the user to login into the OpenNebula RPC server. If not set
                then the value of the C(ONE_USERNAME) environment variable is used.
            env:
              - name: ONE_USERNAME
            type: string
        api_password:
            description:
              - Password or a token of the user to login into OpenNebula RPC server.
              - If not set, the value of the C(ONE_PASSWORD) environment variable is used.
            env:
              - name: ONE_PASSWORD
            required: false
            type: string
        api_authfile:
            description:
              - If both I(api_username) or I(api_password) are not set, then it will try
                authenticate with ONE auth file. Default path is C(~/.one/one_auth).
              - Set environment variable C(ONE_AUTH) to override this path.
            env:
              - name: ONE_AUTH
            required: false
            type: string
        hostname:
            description: Field to match the hostname. Note C(v4_first_ip) corresponds to the first IPv4 found on VM.
            type: string
            default: v4_first_ip
            choices:
                - v4_first_ip
                - v6_first_ip
                - name
        filter_by_label:
            description: Only return servers filtered by this label.
            type: string
        group_by_labels:
            description: Create host groups by vm labels
            type: bool
            default: true
'''

EXAMPLES = r'''
# inventory_opennebula.yml file in YAML format
# Example command line: ansible-inventory --list -i inventory_opennebula.yml

# Pass a label filter to the API
plugin: community.general.opennebula
api_url: https://opennebula:2633/RPC2
filter_by_label: Cache
'''

try:
    import pyone

    HAS_PYONE = True
except ImportError:
    HAS_PYONE = False

from ansible.errors import AnsibleError
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable
from ansible.module_utils.common.text.converters import to_native

from collections import namedtuple
import os


class InventoryModule(BaseInventoryPlugin, Constructable):
    NAME = 'community.general.opennebula'

    def verify_file(self, path):
        valid = False
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(('opennebula.yaml', 'opennebula.yml')):
                valid = True
        return valid

    def _get_connection_info(self):
        url = self.get_option('api_url')
        username = self.get_option('api_username')
        password = self.get_option('api_password')
        authfile = self.get_option('api_authfile')

        if not username and not password:
            if authfile is None:
                authfile = os.path.join(os.environ.get("HOME"), ".one", "one_auth")
            try:
                with open(authfile, "r") as fp:
                    authstring = fp.read().rstrip()
                username, password = authstring.split(":")
            except (OSError, IOError):
                raise AnsibleError("Could not find or read ONE_AUTH file at '{e}'".format(e=authfile))
            except Exception:
                raise AnsibleError("Error occurs when reading ONE_AUTH file at '{e}'".format(e=authfile))

        auth_params = namedtuple('auth', ('url', 'username', 'password'))

        return auth_params(url=url, username=username, password=password)

    def _get_vm_ipv4(self, vm):
        nic = vm.TEMPLATE.get('NIC')

        if isinstance(nic, dict):
            nic = [nic]

        for net in nic:
            return net['IP']

        return False

    def _get_vm_ipv6(self, vm):
        nic = vm.TEMPLATE.get('NIC')

        if isinstance(nic, dict):
            nic = [nic]

        for net in nic:
            if net.get('IP6_GLOBAL'):
                return net['IP6_GLOBAL']

        return False

    def _get_vm_pool(self):
        auth = self._get_connection_info()

        if not (auth.username and auth.password):
            raise AnsibleError('API Credentials missing. Check OpenNebula inventory file.')
        else:
            one_client = pyone.OneServer(auth.url, session=auth.username + ':' + auth.password)

        # get hosts (VMs)
        try:
            vm_pool = one_client.vmpool.infoextended(-2, -1, -1, 3)
        except Exception as e:
            raise AnsibleError("Something happened during XML-RPC call: {e}".format(e=to_native(e)))

        return vm_pool

    def _retrieve_servers(self, label_filter=None):
        vm_pool = self._get_vm_pool()

        result = []

        # iterate over hosts
        for vm in vm_pool.VM:
            server = vm.USER_TEMPLATE

            labels = []
            if vm.USER_TEMPLATE.get('LABELS'):
                labels = [s for s in vm.USER_TEMPLATE.get('LABELS') if s == ',' or s == '-' or s.isalnum() or s.isspace()]
                labels = ''.join(labels)
                labels = labels.replace(' ', '_')
                labels = labels.replace('-', '_')
                labels = labels.split(',')

            # filter by label
            if label_filter is not None:
                if label_filter not in labels:
                    continue

            server['name'] = vm.NAME
            server['LABELS'] = labels
            server['v4_first_ip'] = self._get_vm_ipv4(vm)
            server['v6_first_ip'] = self._get_vm_ipv6(vm)

            result.append(server)

        return result

    def _populate(self):
        hostname_preference = self.get_option('hostname')
        group_by_labels = self.get_option('group_by_labels')
        strict = self.get_option('strict')

        # Add a top group 'one'
        self.inventory.add_group(group='all')

        filter_by_label = self.get_option('filter_by_label')
        servers = self._retrieve_servers(filter_by_label)
        for server in servers:
            hostname = server['name']
            # check for labels
            if group_by_labels and server['LABELS']:
                for label in server['LABELS']:
                    self.inventory.add_group(group=label)
                    self.inventory.add_host(host=hostname, group=label)

            self.inventory.add_host(host=hostname, group='all')

            for attribute, value in server.items():
                self.inventory.set_variable(hostname, attribute, value)

            if hostname_preference != 'name':
                self.inventory.set_variable(hostname, 'ansible_host', server[hostname_preference])

            if server.get('SSH_PORT'):
                self.inventory.set_variable(hostname, 'ansible_port', server['SSH_PORT'])

            # handle construcable implementation: get composed variables if any
            self._set_composite_vars(self.get_option('compose'), server, hostname, strict=strict)

            # groups based on jinja conditionals get added to specific groups
            self._add_host_to_composed_groups(self.get_option('groups'), server, hostname, strict=strict)

            # groups based on variables associated with them in the inventory
            self._add_host_to_keyed_groups(self.get_option('keyed_groups'), server, hostname, strict=strict)

    def parse(self, inventory, loader, path, cache=True):
        if not HAS_PYONE:
            raise AnsibleError('OpenNebula Inventory plugin requires pyone to work!')

        super(InventoryModule, self).parse(inventory, loader, path)
        self._read_config_data(path=path)

        self._populate()
