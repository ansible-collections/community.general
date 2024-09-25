# -*- coding: utf-8 -*-
# Copyright (C) 2016 Guido Günther <agx@sigxcpu.org>, Daniel Lobato Garcia <dlobatog@redhat.com>
# Copyright (c) 2018 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
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
        - constructed
        - inventory_cache
    options:
      plugin:
        description: The name of this plugin, it should always be set to V(community.general.proxmox) for this plugin to recognize it as it's own.
        required: true
        choices: ['community.general.proxmox']
        type: str
      url:
        description:
          - URL to Proxmox cluster.
          - If the value is not specified in the inventory configuration, the value of environment variable E(PROXMOX_URL) will be used instead.
          - Since community.general 4.7.0 you can also use templating to specify the value of the O(url).
        default: 'http://localhost:8006'
        type: str
        env:
          - name: PROXMOX_URL
            version_added: 2.0.0
      user:
        description:
          - Proxmox authentication user.
          - If the value is not specified in the inventory configuration, the value of environment variable E(PROXMOX_USER) will be used instead.
          - Since community.general 4.7.0 you can also use templating to specify the value of the O(user).
        required: true
        type: str
        env:
          - name: PROXMOX_USER
            version_added: 2.0.0
      password:
        description:
          - Proxmox authentication password.
          - If the value is not specified in the inventory configuration, the value of environment variable E(PROXMOX_PASSWORD) will be used instead.
          - Since community.general 4.7.0 you can also use templating to specify the value of the O(password).
          - If you do not specify a password, you must set O(token_id) and O(token_secret) instead.
        type: str
        env:
          - name: PROXMOX_PASSWORD
            version_added: 2.0.0
      token_id:
        description:
          - Proxmox authentication token ID.
          - If the value is not specified in the inventory configuration, the value of environment variable E(PROXMOX_TOKEN_ID) will be used instead.
          - To use token authentication, you must also specify O(token_secret). If you do not specify O(token_id) and O(token_secret),
            you must set a password instead.
          - Make sure to grant explicit pve permissions to the token or disable 'privilege separation' to use the users' privileges instead.
        version_added: 4.8.0
        type: str
        env:
          - name: PROXMOX_TOKEN_ID
      token_secret:
        description:
          - Proxmox authentication token secret.
          - If the value is not specified in the inventory configuration, the value of environment variable E(PROXMOX_TOKEN_SECRET) will be used instead.
          - To use token authentication, you must also specify O(token_id). If you do not specify O(token_id) and O(token_secret),
            you must set a password instead.
        version_added: 4.8.0
        type: str
        env:
          - name: PROXMOX_TOKEN_SECRET
      validate_certs:
        description: Verify SSL certificate if using HTTPS.
        type: boolean
        default: true
      group_prefix:
        description: Prefix to apply to Proxmox groups.
        default: proxmox_
        type: str
      facts_prefix:
        description: Prefix to apply to LXC/QEMU config facts.
        default: proxmox_
        type: str
      want_facts:
        description:
          - Gather LXC/QEMU configuration facts.
          - When O(want_facts) is set to V(true) more details about QEMU VM status are possible, besides the running and stopped states.
            Currently if the VM is running and it is suspended, the status will be running and the machine will be in C(running) group,
            but its actual state will be paused. See O(qemu_extended_statuses) for how to retrieve the real status.
        default: false
        type: bool
      qemu_extended_statuses:
        description:
          - Requires O(want_facts) to be set to V(true) to function. This will allow you to differentiate between C(paused) and C(prelaunch)
            statuses of the QEMU VMs.
          - This introduces multiple groups [prefixed with O(group_prefix)] C(prelaunch) and C(paused).
        default: false
        type: bool
        version_added: 5.1.0
      want_proxmox_nodes_ansible_host:
        version_added: 3.0.0
        description:
          - Whether to set C(ansible_host) for proxmox nodes.
          - When set to V(true) (default), will use the first available interface. This can be different from what you expect.
          - The default of this option changed from V(true) to V(false) in community.general 6.0.0.
        type: bool
        default: false
      exclude_nodes:
        description: Exclude proxmox nodes and the nodes-group from the inventory output.
        type: bool
        default: false
        version_added: 8.1.0
      filters:
        version_added: 4.6.0
        description: A list of Jinja templates that allow filtering hosts.
        type: list
        elements: str
        default: []
      strict:
        version_added: 2.5.0
      compose:
        version_added: 2.5.0
      groups:
        version_added: 2.5.0
      keyed_groups:
        version_added: 2.5.0
'''

EXAMPLES = '''
# Minimal example which will not gather additional facts for QEMU/LXC guests
# By not specifying a URL the plugin will attempt to connect to the controller host on port 8006
# my.proxmox.yml
plugin: community.general.proxmox
user: ansible@pve
password: secure
# Note that this can easily give you wrong values as ansible_host. See further below for
# an example where this is set to `false` and where ansible_host is set with `compose`.
want_proxmox_nodes_ansible_host: true

# Instead of login with password, proxmox supports api token authentication since release 6.2.
plugin: community.general.proxmox
user: ci@pve
token_id: gitlab-1
token_secret: fa256e9c-26ab-41ec-82da-707a2c079829

# The secret can also be a vault string or passed via the environment variable TOKEN_SECRET.
token_secret: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          62353634333163633336343265623632626339313032653563653165313262343931643431656138
          6134333736323265656466646539663134306166666237630a653363623262636663333762316136
          34616361326263383766366663393837626437316462313332663736623066656237386531663731
          3037646432383064630a663165303564623338666131353366373630656661333437393937343331
          32643131386134396336623736393634373936356332623632306561356361323737313663633633
          6231313333666361656537343562333337323030623732323833

# More complete example demonstrating the use of 'want_facts' and the constructed options
# Note that using facts returned by 'want_facts' in constructed options requires 'want_facts=true'
# my.proxmox.yml
plugin: community.general.proxmox
url: http://pve.domain.com:8006
user: ansible@pve
password: secure
want_facts: true
keyed_groups:
    # proxmox_tags_parsed is an example of a fact only returned when 'want_facts=true'
  - key: proxmox_tags_parsed
    separator: ""
    prefix: group
groups:
  webservers: "'web' in (proxmox_tags_parsed|list)"
  mailservers: "'mail' in (proxmox_tags_parsed|list)"
compose:
  ansible_port: 2222
# Note that this can easily give you wrong values as ansible_host. See further below for
# an example where this is set to `false` and where ansible_host is set with `compose`.
want_proxmox_nodes_ansible_host: true

# Using the inventory to allow ansible to connect via the first IP address of the VM / Container
# (Default is connection by name of QEMU/LXC guests)
# Note: my_inv_var demonstrates how to add a string variable to every host used by the inventory.
# my.proxmox.yml
plugin: community.general.proxmox
url: http://192.168.1.2:8006
user: ansible@pve
password: secure
validate_certs: false  # only do this when you trust the network!
want_facts: true
want_proxmox_nodes_ansible_host: false
compose:
  ansible_host: proxmox_ipconfig0.ip | default(proxmox_net0.ip) | ipaddr('address')
  my_inv_var_1: "'my_var1_value'"
  my_inv_var_2: >
    "my_var_2_value"

# Specify the url, user and password using templating
# my.proxmox.yml
plugin: community.general.proxmox
url: "{{ lookup('ansible.builtin.ini', 'url', section='proxmox', file='file.ini') }}"
user: "{{ lookup('ansible.builtin.env','PM_USER') | default('ansible@pve') }}"
password: "{{ lookup('community.general.random_string', base64=True) }}"
# Note that this can easily give you wrong values as ansible_host. See further up for
# an example where this is set to `false` and where ansible_host is set with `compose`.
want_proxmox_nodes_ansible_host: true

'''

import itertools
import re

from ansible.module_utils.common._collections_compat import MutableMapping

from ansible.errors import AnsibleError
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable, Cacheable
from ansible.module_utils.common.text.converters import to_native
from ansible.module_utils.six import string_types
from ansible.module_utils.six.moves.urllib.parse import urlencode
from ansible.utils.display import Display

from ansible_collections.community.general.plugins.module_utils.version import LooseVersion
from ansible_collections.community.general.plugins.plugin_utils.unsafe import make_unsafe

# 3rd party imports
try:
    import requests
    if LooseVersion(requests.__version__) < LooseVersion('1.1.0'):
        raise ImportError
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

display = Display()


class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):
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

        if self.proxmox_password:

            credentials = urlencode({'username': self.proxmox_user, 'password': self.proxmox_password})

            a = self._get_session()

            if a.verify is False:
                from requests.packages.urllib3 import disable_warnings
                disable_warnings()

            ret = a.post('%s/api2/json/access/ticket' % self.proxmox_url, data=credentials)

            json = ret.json()

            self.headers = {
                # only required for POST/PUT/DELETE methods, which we are not using currently
                # 'CSRFPreventionToken': json['data']['CSRFPreventionToken'],
                'Cookie': 'PVEAuthCookie={0}'.format(json['data']['ticket'])
            }

        else:

            self.headers = {'Authorization': 'PVEAPIToken={0}!{1}={2}'.format(self.proxmox_user, self.proxmox_token_id, self.proxmox_token_secret)}

    def _get_json(self, url, ignore_errors=None):

        if not self.use_cache or url not in self._cache.get(self.cache_key, {}):

            if self.cache_key not in self._cache:
                self._cache[self.cache_key] = {'url': ''}

            data = []
            s = self._get_session()
            while True:
                ret = s.get(url, headers=self.headers)
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
                    if json['data']:
                        # /hosts 's 'results' is a list of all hosts, returned is paginated
                        data = data + json['data']
                    break

            self._cache[self.cache_key][url] = data

        return make_unsafe(self._cache[self.cache_key][url])

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

    def _get_lxc_interfaces(self, properties, node, vmid):
        status_key = self._fact('status')

        if status_key not in properties or not properties[status_key] == 'running':
            return

        ret = self._get_json("%s/api2/json/nodes/%s/lxc/%s/interfaces" % (self.proxmox_url, node, vmid), ignore_errors=[501])
        if not ret:
            return

        result = []

        for iface in ret:
            result_iface = {
                'name': iface['name'],
                'hwaddr': iface['hwaddr']
            }

            if 'inet' in iface:
                result_iface['inet'] = iface['inet']

            if 'inet6' in iface:
                result_iface['inet6'] = iface['inet6']

            result.append(result_iface)

        properties[self._fact('lxc_interfaces')] = result

    def _get_agent_network_interfaces(self, node, vmid, vmtype):
        result = []

        try:
            ifaces = self._get_json(
                "%s/api2/json/nodes/%s/%s/%s/agent/network-get-interfaces" % (
                    self.proxmox_url, node, vmtype, vmid
                )
            )['result']

            if "error" in ifaces:
                if "class" in ifaces["error"]:
                    # This happens on Windows, even though qemu agent is running, the IP address
                    # cannot be fetched, as it's unsupported, also a command disabled can happen.
                    errorClass = ifaces["error"]["class"]
                    if errorClass in ["Unsupported"]:
                        self.display.v("Retrieving network interfaces from guest agents on windows with older qemu-guest-agents is not supported")
                    elif errorClass in ["CommandDisabled"]:
                        self.display.v("Retrieving network interfaces from guest agents has been disabled")
                return result

            for iface in ifaces:
                result.append({
                    'name': iface['name'],
                    'mac-address': iface['hardware-address'] if 'hardware-address' in iface else '',
                    'ip-addresses': ["%s/%s" % (ip['ip-address'], ip['prefix']) for ip in iface['ip-addresses']] if 'ip-addresses' in iface else []
                })
        except requests.HTTPError:
            pass

        return result

    def _get_vm_config(self, properties, node, vmid, vmtype, name):
        ret = self._get_json("%s/api2/json/nodes/%s/%s/%s/config" % (self.proxmox_url, node, vmtype, vmid))

        properties[self._fact('node')] = node
        properties[self._fact('vmid')] = vmid
        properties[self._fact('vmtype')] = vmtype

        plaintext_configs = [
            'description',
        ]

        for config in ret:
            key = self._fact(config)
            value = ret[config]
            try:
                # fixup disk images as they have no key
                if config == 'rootfs' or config.startswith(('virtio', 'sata', 'ide', 'scsi')):
                    value = ('disk_image=' + value)

                # Additional field containing parsed tags as list
                if config == 'tags':
                    stripped_value = value.strip()
                    if stripped_value:
                        parsed_key = key + "_parsed"
                        properties[parsed_key] = [tag.strip() for tag in stripped_value.replace(',', ';').split(";")]

                # The first field in the agent string tells you whether the agent is enabled
                # the rest of the comma separated string is extra config for the agent.
                # In some (newer versions of proxmox) instances it can be 'enabled=1'.
                if config == 'agent':
                    agent_enabled = 0
                    try:
                        agent_enabled = int(value.split(',')[0])
                    except ValueError:
                        if value.split(',')[0] == "enabled=1":
                            agent_enabled = 1
                    if agent_enabled:
                        agent_iface_value = self._get_agent_network_interfaces(node, vmid, vmtype)
                        if agent_iface_value:
                            agent_iface_key = self.to_safe('%s%s' % (key, "_interfaces"))
                            properties[agent_iface_key] = agent_iface_value

                if config == 'lxc':
                    out_val = {}
                    for k, v in value:
                        if k.startswith('lxc.'):
                            k = k[len('lxc.'):]
                        out_val[k] = v
                    value = out_val

                if config not in plaintext_configs and isinstance(value, string_types) \
                        and all("=" in v for v in value.split(",")):
                    # split off strings with commas to a dict
                    # skip over any keys that cannot be processed
                    try:
                        value = dict(key.split("=", 1) for key in value.split(","))
                    except Exception:
                        continue

                properties[key] = value
            except NameError:
                return None

    def _get_vm_status(self, properties, node, vmid, vmtype, name):
        ret = self._get_json("%s/api2/json/nodes/%s/%s/%s/status/current" % (self.proxmox_url, node, vmtype, vmid))
        properties[self._fact('status')] = ret['status']
        if vmtype == 'qemu':
            properties[self._fact('qmpstatus')] = ret['qmpstatus']

    def _get_vm_snapshots(self, properties, node, vmid, vmtype, name):
        ret = self._get_json("%s/api2/json/nodes/%s/%s/%s/snapshot" % (self.proxmox_url, node, vmtype, vmid))
        snapshots = [snapshot['name'] for snapshot in ret if snapshot['name'] != 'current']
        properties[self._fact('snapshots')] = snapshots

    def to_safe(self, word):
        '''Converts 'bad' characters in a string to underscores so they can be used as Ansible groups
        #> ProxmoxInventory.to_safe("foo-bar baz")
        'foo_barbaz'
        '''
        regex = r"[^A-Za-z0-9\_]"
        return re.sub(regex, "_", word.replace(" ", ""))

    def _fact(self, name):
        '''Generate a fact's full name from the common prefix and a name.'''
        return self.to_safe('%s%s' % (self.facts_prefix, name.lower()))

    def _group(self, name):
        '''Generate a group's full name from the common prefix and a name.'''
        return self.to_safe('%s%s' % (self.group_prefix, name.lower()))

    def _can_add_host(self, name, properties):
        '''Ensure that a host satisfies all defined hosts filters. If strict mode is
        enabled, any error during host filter compositing will lead to an AnsibleError
        being raised, otherwise the filter will be ignored.
        '''
        for host_filter in self.host_filters:
            try:
                if not self._compose(host_filter, properties):
                    return False
            except Exception as e:  # pylint: disable=broad-except
                message = "Could not evaluate host filter %s for host %s - %s" % (host_filter, name, to_native(e))
                if self.strict:
                    raise AnsibleError(message)
                display.warning(message)
        return True

    def _add_host(self, name, variables):
        self.inventory.add_host(name)
        for k, v in variables.items():
            self.inventory.set_variable(name, k, v)
        variables = self.inventory.get_host(name).get_vars()
        self._set_composite_vars(self.get_option('compose'), variables, name, strict=self.strict)
        self._add_host_to_composed_groups(self.get_option('groups'), variables, name, strict=self.strict)
        self._add_host_to_keyed_groups(self.get_option('keyed_groups'), variables, name, strict=self.strict)

    def _handle_item(self, node, ittype, item):
        '''Handle an item from the list of LXC containers and Qemu VM. The
        return value will be either None if the item was skipped or the name of
        the item if it was added to the inventory.'''
        if item.get('template'):
            return None

        properties = dict()
        name, vmid = item['name'], item['vmid']

        # get status, config and snapshots if want_facts == True
        want_facts = self.get_option('want_facts')
        if want_facts:
            self._get_vm_status(properties, node, vmid, ittype, name)
            self._get_vm_config(properties, node, vmid, ittype, name)
            self._get_vm_snapshots(properties, node, vmid, ittype, name)

            if ittype == 'lxc':
                self._get_lxc_interfaces(properties, node, vmid)

        # ensure the host satisfies filters
        if not self._can_add_host(name, properties):
            return None

        # add the host to the inventory
        self._add_host(name, properties)
        node_type_group = self._group('%s_%s' % (node, ittype))
        self.inventory.add_child(self._group('all_' + ittype), name)
        self.inventory.add_child(node_type_group, name)

        item_status = item['status']
        if item_status == 'running':
            if want_facts and ittype == 'qemu' and self.get_option('qemu_extended_statuses'):
                # get more details about the status of the qemu VM
                item_status = properties.get(self._fact('qmpstatus'), item_status)
        self.inventory.add_child(self._group('all_%s' % (item_status, )), name)

        return name

    def _populate_pool_groups(self, added_hosts):
        '''Generate groups from Proxmox resource pools, ignoring VMs and
        containers that were skipped.'''
        for pool in self._get_pools():
            poolid = pool.get('poolid')
            if not poolid:
                continue
            pool_group = self._group('pool_' + poolid)
            self.inventory.add_group(pool_group)

            for member in self._get_members_per_pool(poolid):
                name = member.get('name')
                if name and name in added_hosts:
                    self.inventory.add_child(pool_group, name)

    def _populate(self):

        # create common groups
        default_groups = ['lxc', 'qemu', 'running', 'stopped']

        if self.get_option('qemu_extended_statuses'):
            default_groups.extend(['prelaunch', 'paused'])

        for group in default_groups:
            self.inventory.add_group(self._group('all_%s' % (group)))
        nodes_group = self._group('nodes')
        if not self.exclude_nodes:
            self.inventory.add_group(nodes_group)

        want_proxmox_nodes_ansible_host = self.get_option("want_proxmox_nodes_ansible_host")

        # gather vm's on nodes
        self._get_auth()
        hosts = []
        for node in self._get_nodes():
            if not node.get('node'):
                continue
            if not self.exclude_nodes:
                self.inventory.add_host(node['node'])
            if node['type'] == 'node' and not self.exclude_nodes:
                self.inventory.add_child(nodes_group, node['node'])

            if node['status'] == 'offline':
                continue

            # get node IP address
            if want_proxmox_nodes_ansible_host and not self.exclude_nodes:
                ip = self._get_node_ip(node['node'])
                self.inventory.set_variable(node['node'], 'ansible_host', ip)

            # Setting composite variables
            if not self.exclude_nodes:
                variables = self.inventory.get_host(node['node']).get_vars()
                self._set_composite_vars(self.get_option('compose'), variables, node['node'], strict=self.strict)

            # add LXC/Qemu groups for the node
            for ittype in ('lxc', 'qemu'):
                node_type_group = self._group('%s_%s' % (node['node'], ittype))
                self.inventory.add_group(node_type_group)

            # get LXC containers and Qemu VMs for this node
            lxc_objects = zip(itertools.repeat('lxc'), self._get_lxc_per_node(node['node']))
            qemu_objects = zip(itertools.repeat('qemu'), self._get_qemu_per_node(node['node']))
            for ittype, item in itertools.chain(lxc_objects, qemu_objects):
                name = self._handle_item(node['node'], ittype, item)
                if name is not None:
                    hosts.append(name)

        # gather vm's in pools
        self._populate_pool_groups(hosts)

    def parse(self, inventory, loader, path, cache=True):
        if not HAS_REQUESTS:
            raise AnsibleError('This module requires Python Requests 1.1.0 or higher: '
                               'https://github.com/psf/requests.')

        super(InventoryModule, self).parse(inventory, loader, path)

        # read config from file, this sets 'options'
        self._read_config_data(path)

        # read and template auth options
        for o in ('url', 'user', 'password', 'token_id', 'token_secret'):
            v = self.get_option(o)
            if self.templar.is_template(v):
                v = self.templar.template(v, disable_lookups=False)
            setattr(self, 'proxmox_%s' % o, v)

        # some more cleanup and validation
        self.proxmox_url = self.proxmox_url.rstrip('/')

        if self.proxmox_password is None and (self.proxmox_token_id is None or self.proxmox_token_secret is None):
            raise AnsibleError('You must specify either a password or both token_id and token_secret.')

        if self.get_option('qemu_extended_statuses') and not self.get_option('want_facts'):
            raise AnsibleError('You must set want_facts to True if you want to use qemu_extended_statuses.')
        # read rest of options
        self.exclude_nodes = self.get_option('exclude_nodes')
        self.cache_key = self.get_cache_key(path)
        self.use_cache = cache and self.get_option('cache')
        self.host_filters = self.get_option('filters')
        self.group_prefix = self.get_option('group_prefix')
        self.facts_prefix = self.get_option('facts_prefix')
        self.strict = self.get_option('strict')

        # actually populate inventory
        self._populate()
