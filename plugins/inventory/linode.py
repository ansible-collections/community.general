# -*- coding: utf-8 -*-
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
    name: linode
    author:
      - Luke Murphy (@decentral1se)
    short_description: Ansible dynamic inventory plugin for Linode.
    requirements:
        - linode_api4 >= 2.0.0
    description:
        - Reads inventories from the Linode API v4.
        - Uses a YAML configuration file that ends with linode.(yml|yaml).
        - Linode labels are used by default as the hostnames.
        - The default inventory groups are built from groups (deprecated by
          Linode) and not tags.
    extends_documentation_fragment:
        - constructed
        - inventory_cache
    options:
        cache:
            version_added: 4.5.0
        cache_plugin:
            version_added: 4.5.0
        cache_timeout:
            version_added: 4.5.0
        cache_connection:
            version_added: 4.5.0
        cache_prefix:
            version_added: 4.5.0
        plugin:
            description: Marks this as an instance of the 'linode' plugin.
            type: string
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
            type: string
            required: true
            env:
                - name: LINODE_ACCESS_TOKEN
        regions:
          description: Populate inventory with instances in this region.
          default: []
          type: list
          elements: string
        tags:
          description: Populate inventory only with instances which have at least one of the tags listed here.
          default: []
          type: list
          elements: string
          version_added: 2.0.0
        types:
          description: Populate inventory with instances with this type.
          default: []
          type: list
          elements: string
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

# You can use Jinja to template the access token.
plugin: community.general.linode
access_token: "{{ lookup('ini', 'token', section='your_username', file='~/.config/linode-cli') }}"
# For older Ansible versions, you need to write this as:
# access_token: "{{ lookup('ini', 'token section=your_username file=~/.config/linode-cli') }}"

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

from ansible.errors import AnsibleError
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable, Cacheable

from ansible_collections.community.general.plugins.plugin_utils.unsafe import make_unsafe


try:
    from linode_api4 import LinodeClient
    from linode_api4.objects.linode import Instance
    from linode_api4.errors import ApiError as LinodeApiError
    HAS_LINODE = True
except ImportError:
    HAS_LINODE = False


class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):

    NAME = 'community.general.linode'

    def _build_client(self, loader):
        """Build the Linode client."""

        access_token = self.get_option('access_token')
        if self.templar.is_template(access_token):
            access_token = self.templar.template(variable=access_token, disable_lookups=False)

        if access_token is None:
            raise AnsibleError((
                'Could not retrieve Linode access token '
                'from plugin configuration sources'
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

    def _filter_by_config(self):
        """Filter instances by user specified configuration."""
        regions = self.get_option('regions')
        if regions:
            self.instances = [
                instance for instance in self.instances
                if instance.region.id in regions
            ]

        types = self.get_option('types')
        if types:
            self.instances = [
                instance for instance in self.instances
                if instance.type.id in types
            ]

        tags = self.get_option('tags')
        if tags:
            self.instances = [
                instance for instance in self.instances
                if any(tag in instance.tags for tag in tags)
            ]

    def _add_instances_to_groups(self):
        """Add instance names to their dynamic inventory groups."""
        for instance in self.instances:
            self.inventory.add_host(make_unsafe(instance.label), group=instance.group)

    def _add_hostvars_for_instances(self):
        """Add hostvars for instances in the dynamic inventory."""
        ip_style = self.get_option('ip_style')
        for instance in self.instances:
            hostvars = instance._raw_json
            hostname = make_unsafe(instance.label)
            for hostvar_key in hostvars:
                if ip_style == 'api' and hostvar_key in ['ipv4', 'ipv6']:
                    continue
                self.inventory.set_variable(
                    hostname,
                    hostvar_key,
                    make_unsafe(hostvars[hostvar_key])
                )
            if ip_style == 'api':
                ips = instance.ips.ipv4.public + instance.ips.ipv4.private
                ips += [instance.ips.ipv6.slaac, instance.ips.ipv6.link_local]
                ips += instance.ips.ipv6.pools

                for ip_type in set(ip.type for ip in ips):
                    self.inventory.set_variable(
                        hostname,
                        ip_type,
                        make_unsafe(self._ip_data([ip for ip in ips if ip.type == ip_type]))
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

    def _cacheable_inventory(self):
        return [i._raw_json for i in self.instances]

    def populate(self):
        strict = self.get_option('strict')

        self._filter_by_config()

        self._add_groups()
        self._add_instances_to_groups()
        self._add_hostvars_for_instances()
        for instance in self.instances:
            hostname = make_unsafe(instance.label)
            variables = self.inventory.get_host(hostname).get_vars()
            self._add_host_to_composed_groups(
                self.get_option('groups'),
                variables,
                hostname,
                strict=strict)
            self._add_host_to_keyed_groups(
                self.get_option('keyed_groups'),
                variables,
                hostname,
                strict=strict)
            self._set_composite_vars(
                self.get_option('compose'),
                variables,
                hostname,
                strict=strict)

    def verify_file(self, path):
        """Verify the Linode configuration file.

        Return true/false if the config-file is valid for this plugin

        Args:
            str(path): path to the config
        Kwargs:
            None
        Raises:
            None
        Returns:
            bool(valid): is valid config file"""
        valid = False
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(("linode.yaml", "linode.yml")):
                valid = True
            else:
                self.display.vvv('Inventory source not ending in "linode.yaml" or "linode.yml"')
        return valid

    def parse(self, inventory, loader, path, cache=True):
        """Dynamically parse Linode the cloud inventory."""
        super(InventoryModule, self).parse(inventory, loader, path)
        self.instances = None

        if not HAS_LINODE:
            raise AnsibleError('the Linode dynamic inventory plugin requires linode_api4.')

        self._read_config_data(path)

        cache_key = self.get_cache_key(path)

        if cache:
            cache = self.get_option('cache')

        update_cache = False
        if cache:
            try:
                self.instances = [Instance(None, i["id"], i) for i in self._cache[cache_key]]
            except KeyError:
                update_cache = True

        # Check for None rather than False in order to allow
        # for empty sets of cached instances
        if self.instances is None:
            self._build_client(loader)
            self._get_instances_inventory()

        if update_cache:
            self._cache[cache_key] = self._cacheable_inventory()

        self.populate()
