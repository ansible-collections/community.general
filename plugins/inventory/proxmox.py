# -*- coding: utf-8 -*-
# Copyright (C) 2016 Guido Günther <agx@sigxcpu.org>, Daniel Lobato Garcia <dlobatog@redhat.com>
# Copyright (c) 2018 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: proxmox
    short_description: Proxmox inventory source
    version_added: "1.2.0"
    author:
        - Jeffrey van Pelt (@Thulium-Drake) <jeff@vanpelt.one>
    requirements:
        - requests >= 1.1
    description:
        - Get inventory hosts from a Proxmox PVE cluster.
        - "Uses a configuration file as an inventory source, it must end in C(.proxmox.yml) or C(.proxmox.yaml)"
        - Will retrieve the first network interface with an IP for Proxmox nodes.
        - Can retrieve LXC/QEMU configuration as facts.
    extends_documentation_fragment:
        - inventory_cache
    options:
      plugin:
        description: The name of this plugin, it should always be set to C(community.general.proxmox) for this plugin to recognize it as it's own.
        required: yes
        choices: ['community.general.proxmox']
        type: str
      url:
        description:
          - URL to Proxmox cluster.
          - If the value is not specified in the inventory configuration, the value of environment variable C(PROXMOX_URL) will be used instead.
        default: 'http://localhost:8006'
        type: str
        env:
          - name: PROXMOX_URL
            version_added: 2.0.0
      user:
        description:
          - Proxmox authentication user.
          - If the value is not specified in the inventory configuration, the value of environment variable C(PROXMOX_USER) will be used instead.
        required: yes
        type: str
        env:
          - name: PROXMOX_USER
            version_added: 2.0.0
      password:
        description:
          - Proxmox authentication password.
          - If the value is not specified in the inventory configuration, the value of environment variable C(PROXMOX_PASSWORD) will be used instead.
        required: yes
        type: str
        env:
          - name: PROXMOX_PASSWORD
            version_added: 2.0.0
      validate_certs:
        description: Verify SSL certificate if using HTTPS.
        type: boolean
        default: yes
      group_prefix:
        description: Prefix to apply to Proxmox groups.
        default: proxmox_
        type: str
      facts_prefix:
        description: Prefix to apply to LXC/QEMU config facts.
        default: proxmox_
        type: str
      want_facts:
        description: Gather LXC/QEMU configuration facts.
        default: no
        type: bool
'''

EXAMPLES = '''
# my.proxmox.yml
plugin: community.general.proxmox
url: http://localhost:8006
user: ansible@pve
password: secure
validate_certs: no
'''

import re

from ansible.module_utils.common._collections_compat import MutableMapping
from distutils.version import LooseVersion

from ansible.errors import AnsibleError
from ansible.plugins.inventory import BaseInventoryPlugin, Cacheable
from ansible.module_utils.six.moves.urllib.parse import urlencode

# 3rd party imports
try:
    import requests
    if LooseVersion(requests.__version__) < LooseVersion('1.1.0'):
        raise ImportError
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class InventoryModule(BaseInventoryPlugin, Cacheable):
    ''' Host inventory parser for ansible using Proxmox as source. '''

    NAME = 'community.general.proxmox'

    def __init__(self):

        super(InventoryModule, self).__init__()

        # from config
        self.proxmox_url = None

        self.session = None
        self.cache_key = None
        self.use_cache = None

    def verify_file(self, path):

        valid = False
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(('proxmox.yaml', 'proxmox.yml')):
                valid = True
            else:
                self.display.vvv('Skipping due to inventory source not ending in "proxmox.yaml" nor "proxmox.yml"')
        return valid

    def _get_session(self):
        if not self.session:
            self.session = requests.session()
            self.session.verify = self.get_option('validate_certs')
        return self.session

    def _get_auth(self):
        credentials = urlencode({'username': self.proxmox_user, 'password': self.proxmox_password, })

        a = self._get_session()
        ret = a.post('%s/api2/json/access/ticket' % self.proxmox_url, data=credentials)

        json = ret.json()

        self.credentials = {
            'ticket': json['data']['ticket'],
            'CSRFPreventionToken': json['data']['CSRFPreventionToken'],
        }

    def _get_json(self, url, ignore_errors=None):

        if not self.use_cache or url not in self._cache.get(self.cache_key, {}):

            if self.cache_key not in self._cache:
                self._cache[self.cache_key] = {'url': ''}

            data = []
            s = self._get_session()
            while True:
                headers = {'Cookie': 'PVEAuthCookie={0}'.format(self.credentials['ticket'])}
                ret = s.get(url, headers=headers)
                if ignore_errors and ret.status_code in ignore_errors:
                    break
                ret.raise_for_status()
                json = ret.json()

                # process results
                # FIXME: This assumes 'return type' matches a specific query,
                #        it will break if we expand the queries and they dont have different types
                if 'data' not in json:
                    # /hosts/:id does not have a 'data' key
                    data = json
                    break
                elif isinstance(json['data'], MutableMapping):
                    # /facts are returned as dict in 'data'
                    data = json['data']
                    break
                else:
                    # /hosts 's 'results' is a list of all hosts, returned is paginated
                    data = data + json['data']
                    break

            self._cache[self.cache_key][url] = data

        return self._cache[self.cache_key][url]

    def _get_nodes(self):
        return self._get_json("%s/api2/json/nodes" % self.proxmox_url)

    def _get_pools(self):
        return self._get_json("%s/api2/json/pools" % self.proxmox_url)

    def _get_lxc_per_node(self, node):
        return self._get_json("%s/api2/json/nodes/%s/lxc" % (self.proxmox_url, node))

    def _get_qemu_per_node(self, node):
        return self._get_json("%s/api2/json/nodes/%s/qemu" % (self.proxmox_url, node))

    def _get_members_per_pool(self, pool):
        ret = self._get_json("%s/api2/json/pools/%s" % (self.proxmox_url, pool))
        return ret['members']

    def _get_node_ip(self, node):
        ret = self._get_json("%s/api2/json/nodes/%s/network" % (self.proxmox_url, node))

        for iface in ret:
            try:
                return iface['address']
            except Exception:
                return None

    def _get_vm_config(self, node, vmid, vmtype, name):
        ret = self._get_json("%s/api2/json/nodes/%s/%s/%s/config" % (self.proxmox_url, node, vmtype, vmid))

        vmid_key = 'vmid'
        vmid_key = self.to_safe('%s%s' % (self.get_option('facts_prefix'), vmid_key.lower()))
        self.inventory.set_variable(name, vmid_key, vmid)

        vmtype_key = 'vmtype'
        vmtype_key = self.to_safe('%s%s' % (self.get_option('facts_prefix'), vmtype_key.lower()))
        self.inventory.set_variable(name, vmtype_key, vmtype)

        for config in ret:
            key = config
            key = self.to_safe('%s%s' % (self.get_option('facts_prefix'), key.lower()))
            value = ret[config]
            try:
                # fixup disk images as they have no key
                if config == 'rootfs' or config.startswith(('virtio', 'sata', 'ide', 'scsi')):
                    value = ('disk_image=' + value)

                if isinstance(value, int) or ',' not in value:
                    value = value
                # split off strings with commas to a dict
                else:
                    # skip over any keys that cannot be processed
                    try:
                        value = dict(key.split("=") for key in value.split(","))
                    except Exception:
                        continue

                self.inventory.set_variable(name, key, value)
            except NameError:
                return None

    def _get_vm_status(self, node, vmid, vmtype, name):
        ret = self._get_json("%s/api2/json/nodes/%s/%s/%s/status/current" % (self.proxmox_url, node, vmtype, vmid))

        status = ret['status']
        status_key = 'status'
        status_key = self.to_safe('%s%s' % (self.get_option('facts_prefix'), status_key.lower()))
        self.inventory.set_variable(name, status_key, status)

    def to_safe(self, word):
        '''Converts 'bad' characters in a string to underscores so they can be used as Ansible groups
        #> ProxmoxInventory.to_safe("foo-bar baz")
        'foo_barbaz'
        '''
        regex = r"[^A-Za-z0-9\_]"
        return re.sub(regex, "_", word.replace(" ", ""))

    def _populate(self):

        self._get_auth()

        # gather vm's on nodes
        for node in self._get_nodes():
            # FIXME: this can probably be cleaner
            # create groups
            lxc_group = 'all_lxc'
            lxc_group = self.to_safe('%s%s' % (self.get_option('group_prefix'), lxc_group.lower()))
            self.inventory.add_group(lxc_group)
            qemu_group = 'all_qemu'
            qemu_group = self.to_safe('%s%s' % (self.get_option('group_prefix'), qemu_group.lower()))
            self.inventory.add_group(qemu_group)
            nodes_group = 'nodes'
            nodes_group = self.to_safe('%s%s' % (self.get_option('group_prefix'), nodes_group.lower()))
            self.inventory.add_group(nodes_group)
            running_group = 'all_running'
            running_group = self.to_safe('%s%s' % (self.get_option('group_prefix'), running_group.lower()))
            self.inventory.add_group(running_group)
            stopped_group = 'all_stopped'
            stopped_group = self.to_safe('%s%s' % (self.get_option('group_prefix'), stopped_group.lower()))
            self.inventory.add_group(stopped_group)

            if node.get('node'):
                self.inventory.add_host(node['node'])

                if node['type'] == 'node':
                    self.inventory.add_child(nodes_group, node['node'])

                # get node IP address
                ip = self._get_node_ip(node['node'])
                self.inventory.set_variable(node['node'], 'ansible_host', ip)

                # get LXC containers for this node
                node_lxc_group = self.to_safe('%s%s' % (self.get_option('group_prefix'), ('%s_lxc' % node['node']).lower()))
                self.inventory.add_group(node_lxc_group)
                for lxc in self._get_lxc_per_node(node['node']):
                    self.inventory.add_host(lxc['name'])
                    self.inventory.add_child(lxc_group, lxc['name'])
                    self.inventory.add_child(node_lxc_group, lxc['name'])

                    # get LXC status when want_facts == True
                    if self.get_option('want_facts'):
                        self._get_vm_status(node['node'], lxc['vmid'], 'lxc', lxc['name'])
                        if lxc['status'] == 'stopped':
                            self.inventory.add_child(stopped_group, lxc['name'])
                        elif lxc['status'] == 'running':
                            self.inventory.add_child(running_group, lxc['name'])

                    # get LXC config for facts
                    if self.get_option('want_facts'):
                        self._get_vm_config(node['node'], lxc['vmid'], 'lxc', lxc['name'])

                # get QEMU vm's for this node
                node_qemu_group = self.to_safe('%s%s' % (self.get_option('group_prefix'), ('%s_qemu' % node['node']).lower()))
                self.inventory.add_group(node_qemu_group)
                for qemu in self._get_qemu_per_node(node['node']):
                    if qemu['template']:
                        continue

                    self.inventory.add_host(qemu['name'])
                    self.inventory.add_child(qemu_group, qemu['name'])
                    self.inventory.add_child(node_qemu_group, qemu['name'])

                    # get QEMU status
                    self._get_vm_status(node['node'], qemu['vmid'], 'qemu', qemu['name'])
                    if qemu['status'] == 'stopped':
                        self.inventory.add_child(stopped_group, qemu['name'])
                    elif qemu['status'] == 'running':
                        self.inventory.add_child(running_group, qemu['name'])

                    # get QEMU config for facts
                    if self.get_option('want_facts'):
                        self._get_vm_config(node['node'], qemu['vmid'], 'qemu', qemu['name'])

        # gather vm's in pools
        for pool in self._get_pools():
            if pool.get('poolid'):
                pool_group = 'pool_' + pool['poolid']
                pool_group = self.to_safe('%s%s' % (self.get_option('group_prefix'), pool_group.lower()))
                self.inventory.add_group(pool_group)

                for member in self._get_members_per_pool(pool['poolid']):
                    if member.get('name'):
                        self.inventory.add_child(pool_group, member['name'])

    def parse(self, inventory, loader, path, cache=True):
        if not HAS_REQUESTS:
            raise AnsibleError('This module requires Python Requests 1.1.0 or higher: '
                               'https://github.com/psf/requests.')

        super(InventoryModule, self).parse(inventory, loader, path)

        # read config from file, this sets 'options'
        self._read_config_data(path)

        # get connection host
        self.proxmox_url = self.get_option('url')
        self.proxmox_user = self.get_option('user')
        self.proxmox_password = self.get_option('password')
        self.cache_key = self.get_cache_key(path)
        self.use_cache = cache and self.get_option('cache')

        # actually populate inventory
        self._populate()
