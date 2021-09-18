# -*- coding: utf-8 -*-
# Copyright (c) 2021, Cliff Hults <cliff.hlts@gmail.com>
# Copyright (c) 2021 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = '''
    name: icinga2
    short_description: Icinga2 inventory source
    version_added: 3.7.0
    author:
        - Cliff Hults (@BongoEADGC6) <cliff.hults@gmail.com>
    description:
        - Get inventory hosts from the Icinga2 API.
        - "Uses a configuration file as an inventory source, it must end in
          C(.icinga2.yml) or C(.icinga2.yaml)."
    options:
      plugin:
        description: Name of the plugin.
        required: true
        type: string
        choices: ['community.general.icinga2']
      url:
        description: Root URL of Icinga2 API.
        type: string
        required: true
      user:
        description: Username to query the API.
        type: string
        required: true
      password:
        description: Password to query the API.
        type: string
        required: true
      host_filter:
        description: An Icinga2 API valid host filter.
        type: string
        required: false
      validate_certs:
        description: Enables or disables SSL certificate verification.
        type: boolean
        default: true
'''

EXAMPLES = r'''
# my.icinga2.yml
plugin: community.general.icinga2
url: http://localhost:5665
user: ansible
password: secure
host_filter: \"linux-servers\" in host.groups
validate_certs: false
'''

import json

from ansible.errors import AnsibleParserError
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable
from ansible.module_utils.urls import open_url


class InventoryModule(BaseInventoryPlugin, Constructable):
    ''' Host inventory parser for ansible using Icinga2 as source. '''

    NAME = 'community.general.icinga2'

    def __init__(self):

        super(InventoryModule, self).__init__()

        # from config
        self.icinga2_url = None
        self.icinga2_user = None
        self.icinga2_password = None
        self.ssl_verify = None
        self.host_filter = None

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
        request_args = {
            'headers': self.headers,
            'url_username': self.icinga2_user,
            'url_password': self.icinga2_password,
            'validate_certs': self.ssl_verify
        }
        open_url(api_status_url, **request_args)

    def _post_request(self, request_url, data=None):
        self.display.vvv("Requested URL: %s" % request_url)
        request_args = {
            'headers': self.headers,
            'url_username': self.icinga2_user,
            'url_password': self.icinga2_password,
            'validate_certs': self.ssl_verify
        }
        if data is not None:
            request_args['data'] = json.dumps(data)
        self.display.vvv("Request Args: %s" % request_args)
        response = open_url(request_url, **request_args)
        response_body = response.read()
        json_data = json.loads(response_body.decode('utf-8'))
        if 200 <= response.status <= 299:
            return json_data
        if response.status == 404 and json_data['status'] == "No objects found.":
            raise AnsibleParserError(
                "API returned no data -- Response: %s - %s"
                % (response.status, json_data['status']))
        if response.status == 401:
            raise AnsibleParserError(
                "API was unable to complete query -- Response: %s - %s"
                % (response.status, json_data['status']))
        if response.status == 500:
            raise AnsibleParserError(
                "API Response - %s - %s"
                % (json_data['status'], json_data['errors']))
        raise AnsibleParserError(
            "Unexpected data returned - %s - %s"
            % (json_data['status'], json_data['errors']))

    def _query_hosts(self, hosts=None, attrs=None, joins=None, host_filter=None):
        query_hosts_url = "{0}/objects/hosts".format(self.icinga2_url)
        self.headers['X-HTTP-Method-Override'] = 'GET'
        data_dict = dict()
        if hosts:
            data_dict['hosts'] = hosts
        if attrs is not None:
            data_dict['attrs'] = attrs
        if joins is not None:
            data_dict['joins'] = joins
        if host_filter is not None:
            data_dict['filter'] = host_filter.replace("\\\"", "\"")
            self.display.vvv(host_filter)
        host_dict = self._post_request(query_hosts_url, data_dict)
        return host_dict['results']

    def get_inventory_from_icinga(self):
        """Query for all hosts """
        self.display.vvv("Querying Icinga2 for inventory")
        query_args = {
            "attrs": ["address", "state_type", "state", "groups"],
        }
        if self.host_filter is not None:
            query_args['host_filter'] = self.host_filter
        # Icinga2 API Call
        results_json = self._query_hosts(**query_args)
        # Manipulate returned API data to Ansible inventory spec
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
        groups_dict = {"_meta": {"hostvars": {}}}
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
            self.inventory.set_variable(host_addr, 'address', host_addr)
            self.inventory.set_variable(host_addr, 'hostname', host_name)
            self.inventory.set_variable(host_addr, 'state',
                                        host_attrs['state'])
            self.inventory.set_variable(host_addr, 'state_type',
                                        host_attrs['state_type'])
        return groups_dict

    def parse(self, inventory, loader, path, cache=True):

        super(InventoryModule, self).parse(inventory, loader, path)

        # read config from file, this sets 'options'
        self._read_config_data(path)

        # Store the options from the YAML file
        self.icinga2_url = self.get_option('url').rstrip('/') + '/v1'
        self.icinga2_user = self.get_option('user')
        self.icinga2_password = self.get_option('password')
        self.ssl_verify = self.get_option('validate_certs')
        self.host_filter = self.get_option('host_filter')
        # Not currently enabled
        # self.cache_key = self.get_cache_key(path)
        # self.use_cache = cache and self.get_option('cache')

        # Test connection to API
        self._api_connect()

        # Call our internal helper to populate the dynamic inventory
        self._populate()
