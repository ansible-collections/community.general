# -*- coding: utf-8 -*-
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
    name: linode
    author:
      - Luke Murphy (@decentral1se)
    short_description: Ansible dynamic inventory plugin for Linode.
    requirements:
        - python >= 2.7
        - linode_api4 >= 2.0.0
    description:
        - Reads inventories from the Linode API v4.
        - Uses a YAML configuration file that ends with linode.(yml|yaml).
        - Linode labels are used by default as the hostnames.
        - The default inventory groups are built from groups (deprecated by
          Linode) and not tags.
    extends_documentation_fragment:
        - constructed
    options:
        plugin:
            description: Marks this as an instance of the 'linode' plugin.
            required: true
            choices: ['linode', 'community.general.linode']
        ip_style:
            description: Populate hostvars with all information available from the Linode APIv4.
            type: string
            default: plain
            choices:
                - plain
                - api
            version_added: 3.6.0
        access_token:
            description: The Linode account personal access token.
            required: true
            env:
                - name: LINODE_ACCESS_TOKEN
        regions:
          description: Populate inventory with instances in this region.
          default: []
          type: list
        tags:
          description: Populate inventory only with instances which have at least one of the tags listed here.
          default: []
          type: list
          version_added: 2.0.0
        types:
          description: Populate inventory with instances with this type.
          default: []
          type: list
        strict:
          version_added: 2.0.0
        compose:
          version_added: 2.0.0
        groups:
          version_added: 2.0.0
        keyed_groups:
          version_added: 2.0.0
'''

EXAMPLES = r'''
# Minimal example. `LINODE_ACCESS_TOKEN` is exposed in environment.
plugin: community.general.linode

# Example with regions, types, groups and access token
plugin: community.general.linode
access_token: foobar
regions:
  - eu-west
types:
  - g5-standard-2

# Example with keyed_groups, groups, and compose
plugin: community.general.linode
access_token: foobar
keyed_groups:
  - key: tags
    separator: ''
  - key: region
    prefix: region
groups:
  webservers: "'web' in (tags|list)"
  mailservers: "'mail' in (tags|list)"
compose:
  # By default, Ansible tries to connect to the label of the instance.
  # Since that might not be a valid name to connect to, you can
  # replace it with the first IPv4 address of the linode as follows:
  ansible_ssh_host: ipv4[0]
  ansible_port: 2222

# Example where control traffic limited to internal network
plugin: community.general.linode
access_token: foobar
ip_style: api
compose:
  ansible_host: "ipv4 | community.general.json_query('[?public==`false`].address') | first"
'''

import os

from ansible.errors import AnsibleError, AnsibleParserError
from ansible.module_utils.six import string_types
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable


try:
    from linode_api4 import LinodeClient
    from linode_api4.errors import ApiError as LinodeApiError
    HAS_LINODE = True
except ImportError:
    HAS_LINODE = False


class InventoryModule(BaseInventoryPlugin, Constructable):

    NAME = 'community.general.linode'

    def _build_client(self):
        """Build the Linode client."""

        access_token = self.get_option('access_token')

        if access_token is None:
            try:
                access_token = os.environ['LINODE_ACCESS_TOKEN']
            except KeyError:
                pass

        if access_token is None:
            raise AnsibleError((
                'Could not retrieve Linode access token '
                'from plugin configuration or environment'
            ))

        self.client = LinodeClient(access_token)

    def _get_instances_inventory(self):
        """Retrieve Linode instance information from cloud inventory."""
        try:
            self.instances = self.client.linode.instances()
        except LinodeApiError as exception:
            raise AnsibleError('Linode client raised: %s' % exception)

    def _add_groups(self):
        """Add Linode instance groups to the dynamic inventory."""
        self.linode_groups = set(
            filter(None, [
                instance.group
                for instance
                in self.instances
            ])
        )

        for linode_group in self.linode_groups:
            self.inventory.add_group(linode_group)

    def _filter_by_config(self, regions, types, tags):
        """Filter instances by user specified configuration."""
        if regions:
            self.instances = [
                instance for instance in self.instances
                if instance.region.id in regions
            ]

        if types:
            self.instances = [
                instance for instance in self.instances
                if instance.type.id in types
            ]

        if tags:
            self.instances = [
                instance for instance in self.instances
                if any(tag in instance.tags for tag in tags)
            ]

    def _add_instances_to_groups(self):
        """Add instance names to their dynamic inventory groups."""
        for instance in self.instances:
            self.inventory.add_host(instance.label, group=instance.group)

    def _add_hostvars_for_instances(self):
        """Add hostvars for instances in the dynamic inventory."""
        ip_style = self.get_option('ip_style')
        for instance in self.instances:
            hostvars = instance._raw_json
            for hostvar_key in hostvars:
                if ip_style == 'api' and hostvar_key in ['ipv4', 'ipv6']:
                    continue
                self.inventory.set_variable(
                    instance.label,
                    hostvar_key,
                    hostvars[hostvar_key]
                )
            if ip_style == 'api':
                ips = instance.ips.ipv4.public + instance.ips.ipv4.private
                ips += [instance.ips.ipv6.slaac, instance.ips.ipv6.link_local]
                ips += instance.ips.ipv6.pools

                for ip_type in set(ip.type for ip in ips):
                    self.inventory.set_variable(
                        instance.label,
                        ip_type,
                        self._ip_data([ip for ip in ips if ip.type == ip_type])
                    )

    def _ip_data(self, ip_list):
        data = []
        for ip in list(ip_list):
            data.append(
                {
                    'address': ip.address,
                    'subnet_mask': ip.subnet_mask,
                    'gateway': ip.gateway,
                    'public': ip.public,
                    'prefix': ip.prefix,
                    'rdns': ip.rdns,
                    'type': ip.type
                }
            )
        return data

    def _validate_option(self, name, desired_type, option_value):
        """Validate user specified configuration data against types."""
        if isinstance(option_value, string_types) and desired_type == list:
            option_value = [option_value]

        if option_value is None:
            option_value = desired_type()

        if not isinstance(option_value, desired_type):
            raise AnsibleParserError(
                'The option %s (%s) must be a %s' % (
                    name, option_value, desired_type
                )
            )

        return option_value

    def _get_query_options(self, config_data):
        """Get user specified query options from the configuration."""
        options = {
            'regions': {
                'type_to_be': list,
                'value': config_data.get('regions', [])
            },
            'types': {
                'type_to_be': list,
                'value': config_data.get('types', [])
            },
            'tags': {
                'type_to_be': list,
                'value': config_data.get('tags', [])
            },
        }

        for name in options:
            options[name]['value'] = self._validate_option(
                name,
                options[name]['type_to_be'],
                options[name]['value']
            )

        regions = options['regions']['value']
        types = options['types']['value']
        tags = options['tags']['value']

        return regions, types, tags

    def verify_file(self, path):
        """Verify the Linode configuration file."""
        if super(InventoryModule, self).verify_file(path):
            endings = ('linode.yaml', 'linode.yml')
            if any((path.endswith(ending) for ending in endings)):
                return True
        return False

    def parse(self, inventory, loader, path, cache=True):
        """Dynamically parse Linode the cloud inventory."""
        super(InventoryModule, self).parse(inventory, loader, path)

        if not HAS_LINODE:
            raise AnsibleError('the Linode dynamic inventory plugin requires linode_api4.')

        config_data = self._read_config_data(path)
        self._build_client()

        self._get_instances_inventory()

        strict = self.get_option('strict')
        regions, types, tags = self._get_query_options(config_data)
        self._filter_by_config(regions, types, tags)

        self._add_groups()
        self._add_instances_to_groups()
        self._add_hostvars_for_instances()
        for instance in self.instances:
            variables = self.inventory.get_host(instance.label).get_vars()
            self._add_host_to_composed_groups(
                self.get_option('groups'),
                variables,
                instance.label,
                strict=strict)
            self._add_host_to_keyed_groups(
                self.get_option('keyed_groups'),
                variables,
                instance.label,
                strict=strict)
            self._set_composite_vars(
                self.get_option('compose'),
                variables,
                instance.label,
                strict=strict)
