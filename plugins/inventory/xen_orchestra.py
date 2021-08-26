# -*- coding: utf-8 -*-
# Copyright (c) 2021 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from jsonrpc_websocket import Server
from ansible.errors import AnsibleError
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable, Cacheable
import asyncio
import json
import os
import re


DOCUMENTATION = '''
    name: xen_orchestra
    short_description: Xen Orchestra inventory source
    version_added: 3.7.0
    author:
        - Dom Del Nano (@ddelnano) <ddelnano@gmail.com>
        - Samori Gorse (@shinuza) <samorigorse@gmail.com>
    requirements:
        - jsonrpc_websocket >= 3.0
    description:
        - Get inventory hosts from a Xen Orchestra deployment.
        - 'Uses a configuration file as an inventory source, it must end in C(.xen_orchestra.yml) or C(.xen_orchestra.yaml).'
    extends_documentation_fragment:
        - constructed
        - inventory_cache
    options:
        plugin:
            description: The name of this plugin, it should always be set to C(community.general.xen_orchestra) for this plugin to recognize it as it's own.
            required: yes
            choices: ['community.general.xen_orchestra']
            type: str
        api_host:
            description:
                - API host to XOA API.
                - If the value is not specified in the inventory configuration, the value of environment variable C(XO_API_HOST) will be used instead.
            default: '192.168.1.123'
            type: str
            env:
                - name: XO_API_HOST
        user:
            description:
                - Xen Orchestra user.
                - If the value is not specified in the inventory configuration, the value of environment variable C(XO_USER) will be used instead.
            required: yes
            type: str
            env:
                - name: XO_USER
        password:
            description:
                - Xen Orchestra password.
                - If the value is not specified in the inventory configuration, the value of environment variable C(XO_PASSWORD) will be used instead.
            required: yes
            type: str
            env:
                - name: XO_PASSWORD
        validate_certs:
            description: Verify SSL certificate if using HTTPS.
            type: boolean
            default: true
        use_ssl:
            description: Use wss when connecting to the Xen Orchestra API
            type: boolean
            default: true
'''


EXAMPLES = '''
# file must be named xen_orchestra.yaml or xen_orchestra.yml
simple_config_file:
    plugin: xen_orchestra
    api_host: 192.168.1.255
    user: xo
    password: xo_pwd
    validate_certs: true
    use_ssl: true
'''


HALTED = 'Halted'
PAUSED = 'Paused'
RUNNING = 'Running'
SUSPENDED = 'Suspended'
POWER_STATES = [RUNNING, HALTED, SUSPENDED, PAUSED]
HOST_GROUP = 'xo_hosts'
POOL_GROUP = 'xo_pools'


class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):
    ''' Host inventory parser for ansible using XenOrchestra as source. '''

    NAME = 'community.general.xen_orchestra'

    def __init__(self):

        super(InventoryModule, self).__init__()

        # from config
        self.session = None
        self.cache_key = None
        self.use_cache = None

    def _get_objects(self):
        async def req():
            server = Server(
                f'{self.protocol}://{self.xoa_api_host}/api/', ssl=self.validate_certs)

            await server.ws_connect()
            await server.session.signIn(username=self.xoa_user, password=self.xoa_password)

            vms = await server.xo.getAllObjects(filter={'type': 'VM'})
            pools = await server.xo.getAllObjects(filter={'type': 'pool'})
            hosts = await server.xo.getAllObjects(filter={'type': 'host'})

            return {
                'vms': vms,
                'pools': pools,
                'hosts': hosts,
            }

        return asyncio.get_event_loop().run_until_complete(req())

    def _add_vms(self, vms, hosts, pools):
        for uuid, vm in vms.items():
            group = 'with_ip'
            ip = vm.get('mainIpAddress')
            host = uuid
            power_state = vm['power_state'].lower()
            pool_name = self._pool_group_name_for_uuid(pools, vm['$poolId'])
            host_name = self._host_group_name_for_uuid(hosts, vm['$container'])

            self.inventory.add_host(host)

            # Grouping by power state
            self.inventory.add_child(power_state, host)

            # Grouping by host
            if host_name:
                self.inventory.add_child(host_name, host)

            # Grouping by pool
            if pool_name:
                self.inventory.add_child(pool_name, host)

            # Grouping VMs with an IP together
            if ip is None:
                group = 'without_ip'
            self.inventory.add_group(group)
            self.inventory.add_child(group, host)

            # Adding meta
            self.inventory.set_variable(host, 'uuid', uuid)
            self.inventory.set_variable(host, 'ip', ip)
            self.inventory.set_variable(host, 'ansible_host', ip)
            self.inventory.set_variable(host, 'name_label', vm['name_label'])
            self.inventory.set_variable(host, 'type', vm['type'])
            self.inventory.set_variable(host, 'power_state', power_state)
            self.inventory.set_variable(host, 'cpus', vm["CPUs"]["number"])
            self.inventory.set_variable(host, 'tags', vm["tags"])
            self.inventory.set_variable(host, 'memory', vm["memory"]["size"])
            self.inventory.set_variable(host, 'has_ip', group == 'with_ip')
            self.inventory.set_variable(
                host, 'is_managed', vm.get('managementAgentDetected', False))
            self.inventory.set_variable(
                host, 'os_version', vm["os_version"])

    def _add_hosts(self, hosts, pools):
        for host in hosts.values():
            address = host['address']
            group_name = self.to_safe("xo_host_{}".format(host['name_label']))
            pool_name = self._pool_group_name_for_uuid(pools, host['$poolId'])

            self.inventory.add_group(group_name)
            self.inventory.add_host(address)
            self.inventory.add_child(HOST_GROUP, address)
            self.inventory.add_child(pool_name, address)

            self.inventory.set_variable(address, 'enabled', host['enabled'])
            self.inventory.set_variable(address, 'hostname', host['hostname'])
            self.inventory.set_variable(address, 'memory', host['memory'])
            self.inventory.set_variable(address, 'cpus', host['cpus'])
            self.inventory.set_variable(address, 'type', 'host')
            self.inventory.set_variable(address, 'tags', host['tags'])
            self.inventory.set_variable(address, 'version', host['version'])
            self.inventory.set_variable(
                address, 'power_state', host['power_state'].lower())
            self.inventory.set_variable(
                address, 'product_brand', host['productBrand'])

    def _add_pools(self, pools):
        for pool in pools.values():
            group_name = self.to_safe("xo_pool_{}".format(pool['name_label']))

            self.inventory.add_group(group_name)

    # TODO: Refactor
    def _pool_group_name_for_uuid(self, pools, pool_uuid) -> str:
        for pool in pools:
            if pool == pool_uuid:
                return self.to_safe("xo_pool_{}".format(pools[pool_uuid]['name_label']))

    # TODO: Refactor
    def _host_group_name_for_uuid(self, hosts, host_uuid) -> str:
        for host in hosts:
            if host == host_uuid:
                return self.to_safe("xo_host_{}".format(hosts[host_uuid]['name_label']))

    def _populate(self, objects):
        # Prepare general groups
        self.inventory.add_group(HOST_GROUP)
        self.inventory.add_group(POOL_GROUP)
        for group in POWER_STATES:
            self.inventory.add_group(group.lower())

        self._add_pools(objects['pools'])
        self._add_hosts(objects['hosts'], objects['pools'])
        self._add_vms(objects['vms'], objects['hosts'], objects['pools'])

    def to_safe(self, word) -> str:
        '''Converts 'bad' characters in a string to underscores so they can be used as Ansible groups
        #> InventoryModule.to_safe("foo-bar baz")
        'foo_barbaz'
        '''
        regex = r"[^A-Za-z0-9\_]"
        return re.sub(regex, "_", word.replace(" ", "")).lower()

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
