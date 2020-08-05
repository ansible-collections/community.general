# -*- coding: utf-8 -*-
# Copyright (c) 2014, Mathieu GAUTHIER-LAFAYE <gauthierl@lapth.cnrs.fr>
# Copyright (c) 2016, Matt Harris <matthaeus.harris@gmail.com>
# Copyright (c) 2020, Robert Kaussow <mail@thegeeklab.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
    name: proxmox
    plugin_type: inventory
    short_description: Proxmox VE inventory source
    version_added: 1.0.0
    description:
        - Get inventory hosts from the proxmox service.
        - "Uses a configuration file as an inventory source, it must end in C(.proxmox.yml) or C(.proxmox.yaml) and has a C(plugin: proxmox) entry."
    extends_documentation_fragment:
        - inventory_cache
    options:
      plugin:
        description: The name of this plugin, it should always be set to C(proxmox) for this plugin to recognize it as it's own.
        required: yes
        choices: ['proxmox']
      server:
        description: Proxmox VE server url.
        default: 'pve.example.com'
        required: yes
        env:
            - name: PROXMOX_SERVER
      user:
        description: Proxmox VE authentication user.
        required: yes
        env:
            - name: PROXMOX_USER
      password:
        description: Proxmox VE authentication password
        required: yes
        env:
            - name: PROXMOX_PASSWORD
      exclude_vmid:
        description: VMID's to exclude from inventory
        type: list
        default: []
        elements: str
      exclude_state:
        description: VM states to exclude from inventory
        type: list
        default: []
        elements: str
      group:
        description: Group to place all hosts into
        default: proxmox
      want_facts:
        description: Toggle, if C(true) the plugin will retrieve host facts from the server
        type: boolean
        default: yes
'''

EXAMPLES = '''
# proxmox.yml
plugin: community.general.proxmox
server: pve.example.com
user: admin@pve
password: secure
'''

import json
import re
import socket

from ansible.errors import AnsibleError
from ansible.module_utils._text import to_native
from ansible.module_utils.six import iteritems
from ansible.plugins.inventory import BaseInventoryPlugin
from collections import defaultdict
from distutils.version import LooseVersion

try:
    from proxmoxer import ProxmoxAPI
    HAS_PROXMOXER = True
except ImportError:
    HAS_PROXMOXER = False


class InventoryModule(BaseInventoryPlugin):
    NAME = 'community.general.proxmox'

    def _auth(self):
        return ProxmoxAPI(self.get_option('server'),
                          user=self.get_option('user'),
                          password=self.get_option('password'),
                          verify_ssl=False)

    def _get_version(self):
        return LooseVersion(self.client.version.get()['version'])

    def _get_major(self):
        return LooseVersion(self.client.version.get()['release'])

    def _get_names(self, pve_list, pve_type):
        names = []

        if pve_type == 'node':
            names = [node['node'] for node in pve_list]
        elif pve_type == 'pool':
            names = [pool['poolid'] for pool in pve_list]
        elif pve_type in ['qemu', 'container']:
            names = [vm['name'] for vm in pve_list]

        return names

    def _get_variables(self, pve_list, pve_type):
        variables = {}

        if pve_type in ['qemu', 'container']:
            for vm in pve_list:
                nested = {}
                for key, value in iteritems(vm):
                    nested['proxmox_' + key] = value
                variables[vm['name']] = nested

        return variables

    def _get_by_name(self, pve_list, pve_name):
        results = [vm for vm in pve_list if vm['name'] == pve_name]
        return results[0] if len(results) > 0 else None

    def _get_ip_address(self, pve_type, pve_node, vmid):
        def validate(address):
            try:
                # IP address validation
                if socket.inet_aton(address):
                    # Ignore localhost
                    if address != '127.0.0.1':
                        return address
            except socket.error:
                return False

        address = False
        networks = False
        if pve_type == 'qemu':
            # If qemu agent is enabled, try to gather the IP address
            try:
                if self.client.nodes(pve_node).get(pve_type, vmid, 'agent',
                                                   'info') is not None:
                    networks = self.client.nodes(pve_node).get(
                        'qemu', vmid, 'agent',
                        'network-get-interfaces')['result']
            except Exception:
                pass

            if networks:
                if type(networks) is list:
                    for network in networks:
                        for ip_address in network['ip-addresses']:
                            address = validate(ip_address['ip-address'])
        else:
            try:
                config = self.client.nodes(pve_node).get(
                    pve_type, vmid, 'config')
                address = re.search(r'ip=(\d*\.\d*\.\d*\.\d*)',
                                    config['net0']).group(1)
            except Exception:
                pass

        return address

    def _exclude(self, pve_list):
        filtered = []
        for item in pve_list:
            obj = defaultdict(dict, item)
            if obj['template'] == 1:
                continue

            if obj['status'] in self.get_option('exclude_state'):
                continue

            if obj['vmid'] in self.get_option('exclude_vmid'):
                continue

            filtered.append(item.copy())
        return filtered

    def _propagate(self):
        for node in self._get_names(self.client.nodes.get(), 'node'):
            try:
                qemu_list = self._exclude(self.client.nodes(node).qemu.get())
                container_list = self._exclude(
                    self.client.nodes(node).lxc.get())
            except Exception as e:
                raise AnsibleError('Proxmoxer API error: {}'.format(
                    to_native(e)))

            # Merge QEMU and Containers lists from this node
            instances = self._get_variables(qemu_list.copy(), 'qemu')
            instances.update(self._get_variables(container_list, 'container'))

            for host in instances:
                vmid = instances[host]['proxmox_vmid']

                try:
                    pve_type = instances[host]['proxmox_type']
                except KeyError:
                    pve_type = 'qemu'

                try:
                    description = self.client.nodes(node).get(
                        pve_type, vmid, 'config')['description']
                except KeyError:
                    description = None
                except Exception as e:
                    raise AnsibleError('Proxmoxer API error: {}'.format(
                        to_native(e)))

                try:
                    metadata = json.loads(description)
                except TypeError:
                    metadata = {}
                except ValueError:
                    metadata = {'notes': description}

                # Add hosts to default group
                self.inventory.add_group(group=self.get_option('group'))
                self.inventory.add_host(group=self.get_option('group'),
                                        host=host)

                # Group hosts by status
                self.inventory.add_group(
                    group=instances[host]['proxmox_status'])
                self.inventory.add_host(
                    group=instances[host]['proxmox_status'], host=host)

                if 'groups' in metadata:
                    for group in metadata['groups']:
                        self.inventory.add_group(group=group)
                        self.inventory.add_host(group=group, host=host)

                if self.get_option('want_facts'):
                    for attr in instances[host]:
                        if attr not in ['proxmox_template']:
                            self.inventory.set_variable(
                                host, attr, instances[host][attr])

                address = self._get_ip_address(pve_type, node, vmid)
                if address:
                    self.inventory.set_variable(host, 'ansible_host', address)

        for pool in self._get_names(self.client.pools.get(), 'pool'):
            try:
                pool_list = self._exclude(
                    self.client.pool(pool).get()['members'])
            except Exception as e:
                raise AnsibleError('Proxmoxer API error: {}'.format(
                    to_native(e)))

            members = [
                member['name'] for member in pool_list
                if (member['type'] == 'qemu' or member['type'] == 'lxc')
            ]

            for member in members:
                self.inventory.add_host(group=pool, host=member)

    def verify_file(self, path):
        """Verify the Proxmox VE configuration file."""
        if super(InventoryModule, self).verify_file(path):
            endings = ('proxmox.yaml', 'proxmox.yml')
            if any((path.endswith(ending) for ending in endings)):
                return True
        return False

    def parse(self, inventory, loader, path, cache=True):
        """Dynamically parse the Proxmox VE cloud inventory."""
        if not HAS_PROXMOXER:
            raise AnsibleError(
                'The Proxmox VE dynamic inventory plugin requires proxmoxer: '
                'https://pypi.org/project/proxmoxer/')

        super(InventoryModule, self).parse(inventory, loader, path)

        self._read_config_data(path)
        self.client = self._auth()
        self._propagate()
