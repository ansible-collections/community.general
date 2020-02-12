# -*- coding: utf-8 -*-
# Copyright (C) 2016 Guido Günther <agx@sigxcpu.org>, Daniel Lobato Garcia <dlobatog@redhat.com>
# Copyright (c) 2018 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: foreman
    plugin_type: inventory
    short_description: foreman inventory source
    requirements:
        - requests >= 1.1
    description:
        - Get inventory hosts from the foreman service.
        - "Uses a configuration file as an inventory source, it must end in ``.foreman.yml`` or ``.foreman.yaml`` and has a ``plugin: foreman`` entry."
    options:
      plugin:
        description: the name of this plugin, it should always be set to 'foreman' for this plugin to recognize it as it's own.
        required: True
        choices: ['foreman']
      url:
        description: url to foreman
        default: 'http://localhost:3000'
        env:
            - name: FOREMAN_SERVER
      user:
        description: foreman authentication user
        required: True
        env:
            - name: FOREMAN_USER
      password:
        description: foreman authentication password
        required: True
        env:
            - name: FOREMAN_PASSWORD
      validate_certs:
        description: verify SSL certificate if using https
        type: boolean
        default: False
      group_prefix:
        description: prefix to apply to foreman groups
        default: foreman_
      vars_prefix:
        description: prefix to apply to host variables, does not include facts nor params
        default: foreman_
      want_facts:
        description: Toggle, if True the plugin will retrieve host facts from the server
        type: boolean
        default: False
      want_params:
        description: Toggle, if true the inventory will retrieve 'all_parameters' information as host vars
        type: boolean
        default: False
      want_hostcollections:
        description: Toggle, if true the plugin will create Ansible groups for host collections
        type: boolean
        default: False
      want_ansible_ssh_host:
        description: Toggle, if true the plugin will populate the ansible_ssh_host variable to explicitly specify the connection target
        type: boolean
        default: False


extends_documentation_fragment:
- inventory_cache
- constructed
'''

EXAMPLES = '''
# my.foreman.yml
plugin: foreman
url: http://localhost:2222
user: ansible-tester
password: secure
validate_certs: False
'''

from distutils.version import LooseVersion

from ansible.errors import AnsibleError
from ansible.module_utils._text import to_bytes, to_native, to_text
from ansible.module_utils.common._collections_compat import MutableMapping
from ansible.plugins.inventory import BaseInventoryPlugin, Cacheable, to_safe_group_name, Constructable

# 3rd party imports
try:
    import requests
    if LooseVersion(requests.__version__) < LooseVersion('1.1.0'):
        raise ImportError
except ImportError:
    raise AnsibleError('This script requires python-requests 1.1 as a minimum version')

from requests.auth import HTTPBasicAuth


class InventoryModule(BaseInventoryPlugin, Cacheable, Constructable):
    ''' Host inventory parser for ansible using foreman as source. '''

    NAME = 'community.general.foreman'

    def __init__(self):

        super(InventoryModule, self).__init__()

        # from config
        self.foreman_url = None

        self.session = None
        self.cache_key = None
        self.use_cache = None

    def verify_file(self, path):

        valid = False
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(('foreman.yaml', 'foreman.yml')):
                valid = True
            else:
                self.display.vvv('Skipping due to inventory source not ending in "foreman.yaml" nor "foreman.yml"')
        return valid

    def _get_session(self):
        if not self.session:
            self.session = requests.session()
            self.session.auth = HTTPBasicAuth(self.get_option('user'), to_bytes(self.get_option('password')))
            self.session.verify = self.get_option('validate_certs')
        return self.session

    def _get_json(self, url, ignore_errors=None):

        if not self.use_cache or url not in self._cache.get(self.cache_key, {}):

            if self.cache_key not in self._cache:
                self._cache[self.cache_key] = {url: ''}

            results = []
            s = self._get_session()
            params = {'page': 1, 'per_page': 250}
            while True:
                ret = s.get(url, params=params)
                if ignore_errors and ret.status_code in ignore_errors:
                    break
                ret.raise_for_status()
                json = ret.json()

                # process results
                # FIXME: This assumes 'return type' matches a specific query,
                #        it will break if we expand the queries and they dont have different types
                if 'results' not in json:
                    # /hosts/:id dos not have a 'results' key
                    results = json
                    break
                elif isinstance(json['results'], MutableMapping):
                    # /facts are returned as dict in 'results'
                    results = json['results']
                    break
                else:
                    # /hosts 's 'results' is a list of all hosts, returned is paginated
                    results = results + json['results']

                    # check for end of paging
                    if len(results) >= json['subtotal']:
                        break
                    if len(json['results']) == 0:
                        self.display.warning("Did not make any progress during loop. expected %d got %d" % (json['subtotal'], len(results)))
                        break

                    # get next page
                    params['page'] += 1

            self._cache[self.cache_key][url] = results

        return self._cache[self.cache_key][url]

    def _get_hosts(self):
        return self._get_json("%s/api/v2/hosts" % self.foreman_url)

    def _get_all_params_by_id(self, hid):
        url = "%s/api/v2/hosts/%s" % (self.foreman_url, hid)
        ret = self._get_json(url, [404])
        if not ret or not isinstance(ret, MutableMapping) or not ret.get('all_parameters', False):
            return {}
        return ret.get('all_parameters')

    def _get_facts_by_id(self, hid):
        url = "%s/api/v2/hosts/%s/facts" % (self.foreman_url, hid)
        return self._get_json(url)

    def _get_host_data_by_id(self, hid):
        url = "%s/api/v2/hosts/%s" % (self.foreman_url, hid)
        return self._get_json(url)

    def _get_facts(self, host):
        """Fetch all host facts of the host"""

        ret = self._get_facts_by_id(host['id'])
        if len(ret.values()) == 0:
            facts = {}
        elif len(ret.values()) == 1:
            facts = list(ret.values())[0]
        else:
            raise ValueError("More than one set of facts returned for '%s'" % host)
        return facts

    def _populate(self):

        for host in self._get_hosts():

            if host.get('name'):
                host_name = self.inventory.add_host(host['name'])

                # create directly mapped groups
                group_name = host.get('hostgroup_title', host.get('hostgroup_name'))
                if group_name:
                    group_name = to_safe_group_name('%s%s' % (self.get_option('group_prefix'), group_name.lower().replace(" ", "")))
                    group_name = self.inventory.add_group(group_name)
                    self.inventory.add_child(group_name, host_name)

                # set host vars from host info
                try:
                    for k, v in host.items():
                        if k not in ('name', 'hostgroup_title', 'hostgroup_name'):
                            try:
                                self.inventory.set_variable(host_name, self.get_option('vars_prefix') + k, v)
                            except ValueError as e:
                                self.display.warning("Could not set host info hostvar for %s, skipping %s: %s" % (host, k, to_text(e)))
                except ValueError as e:
                    self.display.warning("Could not get host info for %s, skipping: %s" % (host_name, to_text(e)))

                # set host vars from params
                if self.get_option('want_params'):
                    for p in self._get_all_params_by_id(host['id']):
                        try:
                            self.inventory.set_variable(host_name, p['name'], p['value'])
                        except ValueError as e:
                            self.display.warning("Could not set hostvar %s to '%s' for the '%s' host, skipping:  %s" %
                                                 (p['name'], to_native(p['value']), host, to_native(e)))

                # set host vars from facts
                if self.get_option('want_facts'):
                    self.inventory.set_variable(host_name, 'foreman_facts', self._get_facts(host))

                # create group for host collections
                if self.get_option('want_hostcollections'):
                    host_data = self._get_host_data_by_id(host['id'])
                    hostcollections = host_data.get('host_collections')
                    if hostcollections:
                        # Create Ansible groups for host collections
                        for hostcollection in hostcollections:
                            try:
                                hostcollection_group = to_safe_group_name('%shostcollection_%s' % (self.get_option('group_prefix'),
                                                                          hostcollection['name'].lower().replace(" ", "")))
                                hostcollection_group = self.inventory.add_group(hostcollection_group)
                                self.inventory.add_child(hostcollection_group, host_name)
                            except ValueError as e:
                                self.display.warning("Could not create groups for host collections for %s, skipping: %s" % (host_name, to_text(e)))

                # put ansible_ssh_host as hostvar
                if self.get_option('want_ansible_ssh_host'):
                    if host.get('ip'):
                        try:
                            self.inventory.set_variable(host_name, 'ansible_ssh_host', host['ip'])
                        except ValueError as e:
                            self.display.warning("Could not set hostvar ansible_ssh_host to '%s' for the '%s' host, skipping: %s" %
                                                 (host['ip'], host_name, to_text(e)))

                strict = self.get_option('strict')

                hostvars = self.inventory.get_host(host_name).get_vars()
                self._set_composite_vars(self.get_option('compose'), hostvars, host_name, strict)
                self._add_host_to_composed_groups(self.get_option('groups'), hostvars, host_name, strict)
                self._add_host_to_keyed_groups(self.get_option('keyed_groups'), hostvars, host_name, strict)

    def parse(self, inventory, loader, path, cache=True):

        super(InventoryModule, self).parse(inventory, loader, path)

        # read config from file, this sets 'options'
        self._read_config_data(path)

        # get connection host
        self.foreman_url = self.get_option('url')
        self.cache_key = self.get_cache_key(path)
        self.use_cache = cache and self.get_option('cache')

        # actually populate inventory
        self._populate()
