# -*- coding: utf-8 -*-
# Copyright (c) 2021, Cliff Hults <cliff.hlts@gmail.com>
# Copyright (c) 2021 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
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
    extends_documentation_fragment:
        - constructed
    options:
      strict:
        version_added: 4.4.0
      compose:
        version_added: 4.4.0
      groups:
        version_added: 4.4.0
      keyed_groups:
        version_added: 4.4.0
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
        description:
          - An Icinga2 API valid host filter. Leave blank for no filtering
        type: string
        required: false
      validate_certs:
        description: Enables or disables SSL certificate verification.
        type: boolean
        default: true
      inventory_attr:
        description:
          - Allows the override of the inventory name based on different attributes.
          - This allows for changing the way limits are used.
          - The current default, C(address), is sometimes not unique or present. We recommend to use C(name) instead.
        type: string
        default: address
        choices: ['name', 'display_name', 'address']
        version_added: 4.2.0
'''

EXAMPLES = r'''
# my.icinga2.yml
plugin: community.general.icinga2
url: http://localhost:5665
user: ansible
password: secure
host_filter: \"linux-servers\" in host.groups
validate_certs: false
inventory_attr: name
groups:
  # simple name matching
  webservers: inventory_hostname.startswith('web')

  # using icinga2 template
  databaseservers: "'db-template' in (icinga2_attributes.templates|list)"

compose:
  # set all icinga2 attributes to a host variable 'icinga2_attrs'
  icinga2_attrs: icinga2_attributes

  # set 'ansible_user' and 'ansible_port' from icinga2 host vars
  ansible_user: icinga2_attributes.vars.ansible_user
  ansible_port: icinga2_attributes.vars.ansible_port | default(22)
'''

import json

from ansible.errors import AnsibleParserError
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable
from ansible.module_utils.urls import open_url
from ansible.module_utils.six.moves.urllib.error import HTTPError


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
        self.inventory_attr = None

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
        try:
            response = open_url(request_url, **request_args)
        except HTTPError as e:
            try:
                error_body = json.loads(e.read().decode())
                self.display.vvv("Error returned: {0}".format(error_body))
            except Exception:
                error_body = {"status": None}
            if e.code == 404 and error_body.get('status') == "No objects found.":
                raise AnsibleParserError("Host filter returned no data. Please confirm your host_filter value is valid")
            raise AnsibleParserError("Unexpected data returned: {0} -- {1}".format(e, error_body))

        response_body = response.read()
        json_data = json.loads(response_body.decode('utf-8'))
        self.display.vvv("Returned Data: %s" % json.dumps(json_data, indent=4, sort_keys=True))
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
            "attrs": ["address", "address6", "name", "display_name", "state_type", "state", "templates", "groups", "vars", "zone"],
        }
        if self.host_filter is not None:
            query_args['host_filter'] = self.host_filter
        # Icinga2 API Call
        results_json = self._query_hosts(**query_args)
        # Manipulate returned API data to Ansible inventory spec
        ansible_inv = self._convert_inv(results_json)
        return ansible_inv

    def _apply_constructable(self, name, variables):
        strict = self.get_option('strict')
        self._add_host_to_composed_groups(self.get_option('groups'), variables, name, strict=strict)
        self._add_host_to_keyed_groups(self.get_option('keyed_groups'), variables, name, strict=strict)
        self._set_composite_vars(self.get_option('compose'), variables, name, strict=strict)

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
            host_attrs = entry['attrs']
            if self.inventory_attr == "name":
                host_name = entry.get('name')
            if self.inventory_attr == "address":
                # When looking for address for inventory, if missing fallback to object name
                if host_attrs.get('address', '') != '':
                    host_name = host_attrs.get('address')
                else:
                    host_name = entry.get('name')
            if self.inventory_attr == "display_name":
                host_name = host_attrs.get('display_name')
            if host_attrs['state'] == 0:
                host_attrs['state'] = 'on'
            else:
                host_attrs['state'] = 'off'
            host_groups = host_attrs.get('groups')
            self.inventory.add_host(host_name)
            for group in host_groups:
                if group not in self.inventory.groups.keys():
                    self.inventory.add_group(group)
                self.inventory.add_child(group, host_name)
            # If the address attribute is populated, override ansible_host with the value
            if host_attrs.get('address') != '':
                self.inventory.set_variable(host_name, 'ansible_host', host_attrs.get('address'))
            self.inventory.set_variable(host_name, 'hostname', entry.get('name'))
            self.inventory.set_variable(host_name, 'display_name', host_attrs.get('display_name'))
            self.inventory.set_variable(host_name, 'state',
                                        host_attrs['state'])
            self.inventory.set_variable(host_name, 'state_type',
                                        host_attrs['state_type'])
            # Adds all attributes to a variable 'icinga2_attributes'
            construct_vars = dict(self.inventory.get_host(host_name).get_vars())
            construct_vars['icinga2_attributes'] = host_attrs
            self._apply_constructable(host_name, construct_vars)
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
        self.inventory_attr = self.get_option('inventory_attr')
        # Not currently enabled
        # self.cache_key = self.get_cache_key(path)
        # self.use_cache = cache and self.get_option('cache')

        # Test connection to API
        self._api_connect()

        # Call our internal helper to populate the dynamic inventory
        self._populate()
