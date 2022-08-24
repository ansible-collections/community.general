# -*- coding: utf-8 -*-
# Copyright (c) 2021 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: xen_orchestra
    short_description: Xen Orchestra inventory source
    version_added: 4.1.0
    author:
        - Dom Del Nano (@ddelnano) <ddelnano@gmail.com>
        - Samori Gorse (@shinuza) <samorigorse@gmail.com>
    requirements:
        - websocket-client >= 1.0.0
    description:
        - Get inventory hosts from a Xen Orchestra deployment.
        - 'Uses a configuration file as an inventory source, it must end in C(.xen_orchestra.yml) or C(.xen_orchestra.yaml).'
    extends_documentation_fragment:
        - constructed
        - inventory_cache
    options:
        plugin:
            description: The name of this plugin, it should always be set to C(community.general.xen_orchestra) for this plugin to recognize it as its own.
            required: true
            choices: ['community.general.xen_orchestra']
            type: str
        api_host:
            description:
                - API host to XOA API.
                - If the value is not specified in the inventory configuration, the value of environment variable C(ANSIBLE_XO_HOST) will be used instead.
            type: str
            env:
                - name: ANSIBLE_XO_HOST
        user:
            description:
                - Xen Orchestra user.
                - If the value is not specified in the inventory configuration, the value of environment variable C(ANSIBLE_XO_USER) will be used instead.
            required: true
            type: str
            env:
                - name: ANSIBLE_XO_USER
        password:
            description:
                - Xen Orchestra password.
                - If the value is not specified in the inventory configuration, the value of environment variable C(ANSIBLE_XO_PASSWORD) will be used instead.
            required: true
            type: str
            env:
                - name: ANSIBLE_XO_PASSWORD
        validate_certs:
            description: Verify TLS certificate if using HTTPS.
            type: boolean
            default: true
        use_ssl:
            description: Use wss when connecting to the Xen Orchestra API
            type: boolean
            default: true
'''


EXAMPLES = '''
# file must be named xen_orchestra.yaml or xen_orchestra.yml
plugin: community.general.xen_orchestra
api_host: 192.168.1.255
user: xo
password: xo_pwd
validate_certs: true
use_ssl: true
groups:
    kube_nodes: "'kube_node' in tags"
compose:
    ansible_port: 2222

'''

import json
import ssl

from ansible.errors import AnsibleError
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable, Cacheable

from ansible_collections.community.general.plugins.module_utils.version import LooseVersion

# 3rd party imports
try:
    HAS_WEBSOCKET = True
    import websocket
    from websocket import create_connection

    if LooseVersion(websocket.__version__) <= LooseVersion('1.0.0'):
        raise ImportError
except ImportError as e:
    HAS_WEBSOCKET = False


HALTED = 'Halted'
PAUSED = 'Paused'
RUNNING = 'Running'
SUSPENDED = 'Suspended'
POWER_STATES = [RUNNING, HALTED, SUSPENDED, PAUSED]
HOST_GROUP = 'xo_hosts'
POOL_GROUP = 'xo_pools'


def clean_group_name(label):
    return label.lower().replace(' ', '-').replace('-', '_')


class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):
    ''' Host inventory parser for ansible using XenOrchestra as source. '''

    NAME = 'community.general.xen_orchestra'

    def __init__(self):

        super(InventoryModule, self).__init__()

        # from config
        self.counter = -1
        self.session = None
        self.cache_key = None
        self.use_cache = None

    @property
    def pointer(self):
        self.counter += 1
        return self.counter

    def create_connection(self, xoa_api_host):
        validate_certs = self.get_option('validate_certs')
        use_ssl = self.get_option('use_ssl')
        proto = 'wss' if use_ssl else 'ws'

        sslopt = None if validate_certs else {'cert_reqs': ssl.CERT_NONE}
        self.conn = create_connection(
            '{0}://{1}/api/'.format(proto, xoa_api_host), sslopt=sslopt)

    def login(self, user, password):
        payload = {'id': self.pointer, 'jsonrpc': '2.0', 'method': 'session.signIn', 'params': {
            'username': user, 'password': password}}
        self.conn.send(json.dumps(payload))
        result = json.loads(self.conn.recv())

        if 'error' in result:
            raise AnsibleError(
                'Could not connect: {0}'.format(result['error']))

    def get_object(self, name):
        payload = {'id': self.pointer, 'jsonrpc': '2.0',
                   'method': 'xo.getAllObjects', 'params': {'filter': {'type': name}}}
        self.conn.send(json.dumps(payload))
        answer = json.loads(self.conn.recv())

        if 'error' in answer:
            raise AnsibleError(
                'Could not request: {0}'.format(answer['error']))

        return answer['result']

    def _get_objects(self):
        self.create_connection(self.xoa_api_host)
        self.login(self.xoa_user, self.xoa_password)

        return {
            'vms': self.get_object('VM'),
            'pools': self.get_object('pool'),
            'hosts': self.get_object('host'),
        }

    def _apply_constructable(self, name, variables):
        strict = self.get_option('strict')
        self._add_host_to_composed_groups(self.get_option('groups'), variables, name, strict=strict)
        self._add_host_to_keyed_groups(self.get_option('keyed_groups'), variables, name, strict=strict)
        self._set_composite_vars(self.get_option('compose'), variables, name, strict=strict)

    def _add_vms(self, vms, hosts, pools):
        for uuid, vm in vms.items():
            group = 'with_ip'
            ip = vm.get('mainIpAddress')
            entry_name = uuid
            power_state = vm['power_state'].lower()
            pool_name = self._pool_group_name_for_uuid(pools, vm['$poolId'])
            host_name = self._host_group_name_for_uuid(hosts, vm['$container'])

            self.inventory.add_host(entry_name)

            # Grouping by power state
            self.inventory.add_child(power_state, entry_name)

            # Grouping by host
            if host_name:
                self.inventory.add_child(host_name, entry_name)

            # Grouping by pool
            if pool_name:
                self.inventory.add_child(pool_name, entry_name)

            # Grouping VMs with an IP together
            if ip is None:
                group = 'without_ip'
            self.inventory.add_group(group)
            self.inventory.add_child(group, entry_name)

            # Adding meta
            self.inventory.set_variable(entry_name, 'uuid', uuid)
            self.inventory.set_variable(entry_name, 'ip', ip)
            self.inventory.set_variable(entry_name, 'ansible_host', ip)
            self.inventory.set_variable(entry_name, 'power_state', power_state)
            self.inventory.set_variable(
                entry_name, 'name_label', vm['name_label'])
            self.inventory.set_variable(entry_name, 'type', vm['type'])
            self.inventory.set_variable(
                entry_name, 'cpus', vm['CPUs']['number'])
            self.inventory.set_variable(entry_name, 'tags', vm['tags'])
            self.inventory.set_variable(
                entry_name, 'memory', vm['memory']['size'])
            self.inventory.set_variable(
                entry_name, 'has_ip', group == 'with_ip')
            self.inventory.set_variable(
                entry_name, 'is_managed', vm.get('managementAgentDetected', False))
            self.inventory.set_variable(
                entry_name, 'os_version', vm['os_version'])

            self._apply_constructable(entry_name, self.inventory.get_host(entry_name).get_vars())

    def _add_hosts(self, hosts, pools):
        for host in hosts.values():
            entry_name = host['uuid']
            group_name = 'xo_host_{0}'.format(
                clean_group_name(host['name_label']))
            pool_name = self._pool_group_name_for_uuid(pools, host['$poolId'])

            self.inventory.add_group(group_name)
            self.inventory.add_host(entry_name)
            self.inventory.add_child(HOST_GROUP, entry_name)
            self.inventory.add_child(pool_name, entry_name)

            self.inventory.set_variable(entry_name, 'enabled', host['enabled'])
            self.inventory.set_variable(
                entry_name, 'hostname', host['hostname'])
            self.inventory.set_variable(entry_name, 'memory', host['memory'])
            self.inventory.set_variable(entry_name, 'address', host['address'])
            self.inventory.set_variable(entry_name, 'cpus', host['cpus'])
            self.inventory.set_variable(entry_name, 'type', 'host')
            self.inventory.set_variable(entry_name, 'tags', host['tags'])
            self.inventory.set_variable(entry_name, 'version', host['version'])
            self.inventory.set_variable(
                entry_name, 'power_state', host['power_state'].lower())
            self.inventory.set_variable(
                entry_name, 'product_brand', host['productBrand'])

        for pool in pools.values():
            group_name = 'xo_pool_{0}'.format(
                clean_group_name(pool['name_label']))

            self.inventory.add_group(group_name)

    def _add_pools(self, pools):
        for pool in pools.values():
            group_name = 'xo_pool_{0}'.format(
                clean_group_name(pool['name_label']))

            self.inventory.add_group(group_name)

    # TODO: Refactor
    def _pool_group_name_for_uuid(self, pools, pool_uuid):
        for pool in pools:
            if pool == pool_uuid:
                return 'xo_pool_{0}'.format(
                    clean_group_name(pools[pool_uuid]['name_label']))

    # TODO: Refactor
    def _host_group_name_for_uuid(self, hosts, host_uuid):
        for host in hosts:
            if host == host_uuid:
                return 'xo_host_{0}'.format(
                    clean_group_name(hosts[host_uuid]['name_label']
                                     ))

    def _populate(self, objects):
        # Prepare general groups
        self.inventory.add_group(HOST_GROUP)
        self.inventory.add_group(POOL_GROUP)
        for group in POWER_STATES:
            self.inventory.add_group(group.lower())

        self._add_pools(objects['pools'])
        self._add_hosts(objects['hosts'], objects['pools'])
        self._add_vms(objects['vms'], objects['hosts'], objects['pools'])

    def verify_file(self, path):

        valid = False
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(('xen_orchestra.yaml', 'xen_orchestra.yml')):
                valid = True
            else:
                self.display.vvv(
                    'Skipping due to inventory source not ending in "xen_orchestra.yaml" nor "xen_orchestra.yml"')
        return valid

    def parse(self, inventory, loader, path, cache=True):
        if not HAS_WEBSOCKET:
            raise AnsibleError('This plugin requires websocket-client 1.0.0 or higher: '
                               'https://github.com/websocket-client/websocket-client.')

        super(InventoryModule, self).parse(inventory, loader, path)

        # read config from file, this sets 'options'
        self._read_config_data(path)
        self.inventory = inventory

        self.protocol = 'wss'
        self.xoa_api_host = self.get_option('api_host')
        self.xoa_user = self.get_option('user')
        self.xoa_password = self.get_option('password')
        self.cache_key = self.get_cache_key(path)
        self.use_cache = cache and self.get_option('cache')

        self.validate_certs = self.get_option('validate_certs')
        if not self.get_option('use_ssl'):
            self.protocol = 'ws'

        objects = self._get_objects()
        self._populate(objects)
