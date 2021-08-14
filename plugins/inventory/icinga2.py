# -*- coding: utf-8 -*-
# Copyright (C) 2016 Guido Günther <agx@sigxcpu.org>, Daniel Lobato Garcia <dlobatog@redhat.com>
# Copyright (c) 2018 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: icinga2
    short_description: Icinga2 inventory source
    description: Returns Ansible inventory from CSV
    options:
      plugin:
          description: Name of the plugin
          required: true
          choices: ['icinga2', 'community.general.icinga2']
      url:
        description: Root URL of Icinga2 API 
        required: true
      user:
        description: API username
        required: true
      password:
        description: API password
        required: true
      validate_certs:
        description: Enable SSL certificate verification
        required: true
'''
EXAMPLES = '''
# my.icinga2.yml
plugin: community.general.icinga2
url: http://localhost:5665
user: ansible
password: secure
validate_certs: false
keyed_groups:
  - key: icinga2_tags_parsed
    separator: ""
    prefix: group
groups:
  webservers: "'web' in (icinga2_tags_parsed|list)"
  mailservers: "'mail' in (icinga2_tags_parsed|list)"
compose:
  ansible_port: 2222
'''
import re
import json

from ansible.module_utils.common._collections_compat import MutableMapping
from distutils.version import LooseVersion

from ansible.errors import AnsibleError, AnsibleParserError
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable, Cacheable
from ansible.module_utils.six.moves.urllib.parse import urlencode

# 3rd party imports
try:
    import requests
    if LooseVersion(requests.__version__) < LooseVersion('1.1.0'):
        raise ImportError
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):
    ''' Host inventory parser for ansible using Icinga2 as source. '''

    NAME = 'community.general.icinga2'

    def __init__(self):

        super(InventoryModule, self).__init__()

        # from config
        self.icinga2_url = None

        self.cache_key = None
        self.use_cache = None

    def verify_file(self, path):

        valid = False
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(('icinga2.yaml', 'icinga2.yml')):
                valid = True
            else:
                self.display.vvv('Skipping due to inventory source not ending in "icinga2.yaml" nor "icinga2.yml"')
        return valid

    def _api_connect(self):
        self.headers = {
                'User-Agent': "ansible-icinga2-inv",
                'Accept': "application/json",
                }
        api_status_url = self.icinga2_url + "/status"
        api_status = requests.get(api_status_url, 
                auth=(self.icinga2_user, self.icinga2_password), 
                verify=self.ssl_verify)
        api_status.raise_for_status()

    def _post_request(self, request_url, headers, data=None):
        #logging.debug("Requested URL: %s" % request_url)
        request_args = {
                'headers': self.headers,
                'auth': (self.icinga2_user, self.icinga2_password),
                'verify': self.ssl_verify
                }
        if data != None:
            request_args['data'] = json.dumps(data)
        #logging.debug("Request Args: %s" % request_args)
        response = requests.post(request_url, **request_args)
        if 200 <= response.status_code <= 299:
            if len(response.json()['results']) == 0:
                print("Query returned 0 results")
                sys.exit(0)
            else:
                return response.json()
        elif response.status_code == 404 and response.json()['status'] == "No objects found.":
            print("API was Unable to complete query -- Response: %s - %s" % (response.status_code, response.json()['status']))
            sys.exit(1)
        elif response.status_code == 401:
            print("API was Unable to complete query -- Response: %s - %s" % (response.status_code, response.json()['status']))
            sys.exit(1)
        elif response.status_code == 500:
            print("API Response - %s - %s" % (response.json()['status'], response.json()['errors']))
            sys.exit(1)
        else:
            #logging.debug("Returned Data: %s" % response.json())
            response.raise_for_status()

    def _query_hosts(self, hosts=None, attrs=None, joins=None, filter=None):
        query_hosts_url= "{}/objects/hosts".format(self.icinga2_url)
        self.headers['X-HTTP-Method-Override'] = 'GET'
        data_dict = dict()
        if hosts:
            if len(hosts) == 1:
                query_hosts_url += "/%s" % hosts[0]
            elif len(hosts) > 1:
                data_dict['hosts'] = hosts
        if attrs != None:
            data_dict['attrs'] = attrs
        if joins != None:
            data_dict['joins'] = joins
        if filter != None:
            data_dict['filter'] = filter
        host_dict = self._post_request(query_hosts_url, self.headers, data_dict)
        return host_dict

    def get_inventory_from_icinga(self):
        """Query for all hosts """
        #logging.info("Querying Icinga2 for inventory")
        query_args = {
            "attrs": ["address", "state_type", "state", "groups"],
        }
        # Icinga2 API Call
        results_json = self._query_hosts(**query_args)['results']
        ansible_inv = self._convert_inv(results_json)
        return ansible_inv
    
    def _populate(self):
        groups = self._to_json(self.get_inventory_from_icinga())
        return groups

    def _to_json(self, in_dict):
        """Convert dictionary to JSON"""
        return json.dumps(in_dict, sort_keys=True, indent=2)

    def _convert_inv(self, json_data):
        """Convert Icinga2 API data to JSON format for Ansible"""
        groups_dict = {"_meta": {"hostvars" : {}}}
        for entry in json_data:
            host_name = entry['name']
            host_attrs = entry['attrs']
            if host_attrs['state'] == 0:
                host_attrs['state'] = 'on'
            else:
                host_attrs['state'] = 'off'
            host_groups = host_attrs['groups']
            host_addr = host_attrs['address']
            self.inventory.add_host(host_addr)
            for group in host_groups:
                if group not in self.inventory.groups.keys():
                    self.inventory.add_group(group)
                self.inventory.add_child(group, host_addr)
            #self.inventory.set_variable(host_addr, 'ansible_host', host_attrs)
            self.inventory.set_variable(host_addr, 'address', host_addr)
            self.inventory.set_variable(host_addr, 'hostname', host_name)
            self.inventory.set_variable(host_addr, 'state', host_attrs['state'])
            self.inventory.set_variable(host_addr, 'state_type',
                    host_attrs['state_type'])
        return groups_dict
    
    def parse(self, inventory, loader, path, cache=True):
        if not HAS_REQUESTS:
            raise AnsibleError('This module requires Python Requests 1.1.0 or higher: '
                               'https://github.com/psf/requests.')

        super(InventoryModule, self).parse(inventory, loader, path)

        # read config from file, this sets 'options'
        self._read_config_data(path)
        try:
            # Store the options from the YAML file
            self.icinga2_url = self.get_option('url').rstrip('/') + '/v1'
            self.icinga2_user = self.get_option('user')
            self.icinga2_password = self.get_option('password')
            self.ssl_verify = self.get_option('validate_certs')
            ## Not currently enabled
            # self.host_filter = self.get_option('host_filter')
            # self.cache_key = self.get_cache_key(path)
            # self.use_cache = cache and self.get_option('cache')
        except Exception as e:
            raise AnsibleParserError(
                    'All correct options required: {}'.format(e))
        # Test connection to API
        self._api_connect()

        # Call our internal helper to populate the dynamic inventory
        self._populate()
