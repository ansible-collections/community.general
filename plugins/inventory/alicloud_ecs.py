# Copyright (c) 2017-present Alibaba Group Holding Limited. He Guimin <heguimin36@163.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = '''
name: alicloud_ecs
plugin_type: inventory
short_description: ECS inventory source
requirements:
    - python3
    - footmark
extends_documentation_fragment:
    - inventory_cache
    - constructed
    - community.general.alicloud
description:
    - Get inventory hosts from Alicloud ECS.
    - Uses a yaml configuration file that ends with C(alicloud.(yml|yaml)).
author:
    - "He Guimin (@xiaozhu36)"
    - "Li Xue (@lixue323)"
options:
    plugin:
        description: Token that ensures this is a source file for the plugin.
        required: True
        choices: ['alicloud_ecs']
    regions:
      description:
          - A list of regions in which to describe ECS instances.
          - If empty (the default) default this will include all regions, except possibly restricted ones like cn-beijing
      type: list
      default: []
    hostnames:
      description:
          - A list in order of precedence for hostname variables.
          - You can use the options specified in U(https://www.alibabacloud.com/help/doc-detail/25506.htm).
      type: list
      default: []
    filters:
      description:
          - A dictionary of filter value pairs.
          - Available filters are listed here U(https://www.alibabacloud.com/help/doc-detail/25506.htm).
      type: dict
      default: {}
'''

EXAMPLES = '''
# Fetch all hosts in cn-beijing
plugin: alicloud_ecs
regions:
  - cn-beijing

# Example using filters and specifying the hostname precedence
plugin: alicloud_ecs
regions:
  - cn-beijing
  - cn-qingdao
filters:
  instance_type: ecs.g6.4xlarge

hostnames:
  - instance_id
  - public_ip_address


# Example using constructed features to create groups and set ansible_host
plugin: alicloud_ecs

# If true make invalid entries a fatal error, otherwise skip and continue
# Since it is possible to use facts in the expressions they might not always be available and we ignore those errors by default.
strict: False

# Add hosts to group based on the values of a variable
keyed_groups:
  - key: instance_name
    prefix: name

# Set individual variables with compose
# Create vars from jinja2 expressions
compose:
  # Use the public ip address to connect to the host
  # (note: this does not modify inventory_hostname, which is set via I(hostnames))
  ansible_host: public_ip_address

# Example of enabling caching for an individual YAML configuration file
plugin: alicloud_ecs
cache: yes
cache_plugin: jsonfile
cache_timeout: 7200
cache_connection: /tmp/alicloud_inventory
cache_prefix: alicloud_ecs
'''

import os
from ansible.errors import AnsibleError
from ansible.module_utils._text import to_native, to_text
from ansible.module_utils.alicloud_ecs import connect_to_acs, get_profile
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable, Cacheable
from ansible.utils.display import Display

try:
    import footmark
    import footmark.ecs
    import footmark.regioninfo
    HAS_FOOTMARK = True
except ImportError:
    raise AnsibleError('The ecs dynamic inventory plugin requires footmark.')

display = Display()


class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):

    NAME = 'alicloud_ecs'

    def __init__(self):
        super(InventoryModule, self).__init__()

        self.group_prefix = 'alicloud_ecs_'

    def _set_credentials(self):
        ''' Reads the settings from the file '''

        access_key = os.environ.get('ALICLOUD_ACCESS_KEY', os.environ.get('ALICLOUD_ACCESS_KEY_ID', None))
        if not access_key:
            access_key = self.get_option('alicloud_access_key')

        secret_key = os.environ.get('ALICLOUD_SECRET_KEY', os.environ.get('ALICLOUD_SECRET_ACCESS_KEY', None))
        if not secret_key:
            secret_key = self.get_option('alicloud_secret_key')

        security_token = os.environ.get('ALICLOUD_SECURITY_TOKEN', None)
        if not security_token:
            self.security_token = self.get_option('alicloud_security_token')

        alicloud_region = os.environ.get('ALICLOUD_REGION', None)
        if not alicloud_region:
            alicloud_region = self.get_option('alicloud_region')

        ecs_role_name = os.environ.get('ALICLOUD_ECS_ROLE_NAME', None)
        if not ecs_role_name:
            ecs_role_name = self.get_option('ecs_role_name')

        profile = os.environ.get('ALICLOUD_PROFILE', None)
        if not profile:
            profile = self.get_option('profile')

        shared_credentials_file = os.environ.get('ALICLOUD_SHARED_CREDENTIALS_FILE', None)
        if not shared_credentials_file:
            shared_credentials_file = self.get_option('shared_credentials_file')

        assume_role = self.get_option('alicloud_assume_role')
        assume_role_params = {}

        role_arn = os.environ.get('ALICLOUD_ASSUME_ROLE_ARN', None)
        if not role_arn and assume_role:
            assume_role_params['role_arn'] = assume_role.get('role_arn')

        session_name = os.environ.get('ALICLOUD_ASSUME_ROLE_SESSION_NAME', None)
        if not session_name and assume_role:
            assume_role_params['session_name'] = assume_role.get('session_name')

        session_expiration = os.environ.get('ALICLOUD_ASSUME_ROLE_SESSION_EXPIRATION', None)
        if not session_expiration and assume_role:
            assume_role_params['session_expiration'] = assume_role.get('session_expiration')

        if assume_role:
            assume_role_params['policy'] = assume_role.get('policy')

        credentials = {
            'alicloud_access_key': access_key,
            'alicloud_secret_key': secret_key,
            'security_token': security_token,
            'ecs_role_name': ecs_role_name,
            'profile': profile,
            'shared_credentials_file': shared_credentials_file,
            'assume_role': assume_role_params,
            'alicloud_region': alicloud_region
        }
        self.credentials = get_profile(credentials)

    def connect_to_ecs(self, module, region):

        # Check module args for credentials, then check environment vars access key pair and region
        connect_args = self.credentials
        connect_args['user_agent'] = 'Ansible-Provider-Alicloud/Dynamic-Inventory'
        conn = connect_to_acs(module, region, **connect_args)
        if conn is None:
            self.fail_with_error("region name: %s likely not supported. Connection to region failed." % region)
        return conn

    def _get_instances_by_region(self, regions, filters):
        '''
           :param regions: a list of regions in which to describe instances
           :param filters: a list of ECS filter dictionaries
           :return A list of instance dictionaries
        '''
        all_instances = []
        if not regions:
            try:
                regions = list(map(lambda x: x.id, self.connect_to_ecs(footmark.ecs, "cn-beijing").describe_regions()))
            except Exception as e:
                raise AnsibleError('Unable to get regions list from available methods, you must specify the "regions" option to continue.')

        for region in regions:
            try:
                conn = connect_to_acs(footmark.ecs, region, **self.credentials)
                insts = conn.describe_instances(**filters)
                all_instances.extend(map(lambda x: x.read(), insts))
            except Exception as e:
                raise AnsibleError("Failed to describe instances: %s" % to_native(e))
        return sorted(all_instances, key=lambda x: x['instance_id'])

    def _query(self, regions, filters):
        '''
            :param regions: a list of regions to query
            :param filters: a dict of ECS filter params
            :param hostnames: a list of hostname destination variables in order of preference
        '''
        return {'alicloud': self._get_instances_by_region(regions, filters)}

    def _populate(self, groups, hostnames):
        for group in groups:
            group = self.inventory.add_group(group)
            self._add_hosts(hosts=groups[group], group=group, hostnames=hostnames)
            self.inventory.add_child('all', group)

    def _get_tag_hostname(self, preference, instance):
        tag_hostnames = preference['tags']
        if ',' in tag_hostnames:
            tag_hostnames = tag_hostnames.split(',')
        else:
            tag_hostnames = [tag_hostnames]
        tags = instance.get('tags', {})
        for v in tag_hostnames:
            if '=' in v:
                tag_name, tag_value = v.split('=')
                if tags.get(tag_name) == tag_value:
                    return to_text(tag_name) + "_" + to_text(tag_value)
            else:
                tag_value = tags.get(v)
                if tag_value:
                    return to_text(tag_value)
        return None

    def _get_instance_attr(self, filter_name, instance):
        '''
            :param filter_name: The filter
            :param instance: instance dict returned by  describe_instances()
        '''
        if filter_name not in instance:
            raise AnsibleError("Invalid filter '%s' provided" % filter_name)
        return instance[filter_name]

    def _get_hostname(self, instance, hostnames):
        '''
            :param instance: an instance dict returned by describe_instances()
            :param hostnames: a list of hostname destination variables in order of preference
            :return the preferred identifer for the host
        '''
        if not hostnames:
            hostnames = ['instance_id', 'instance_name']

        hostname = None
        for preference in hostnames:
            if 'tag' in preference:
                hostname = self._get_tag_hostname(preference, instance)
            else:
                hostname = self._get_instance_attr(preference, instance)
            if hostname:
                break
        if hostname:
            if ':' in to_text(hostname):
                return self._sanitize_group_name((to_text(hostname)))
            else:
                return to_text(hostname)

    def _add_hosts(self, hosts, group, hostnames):
        '''
            :param hosts: a list of hosts to be added to a group
            :param group: the name of the group to which the hosts belong
            :param hostnames: a list of hostname destination variables in order of preference
        '''
        for host in hosts:
            hostname = self._get_hostname(host, hostnames)

            # Allow easier grouping by region
            host['region'] = host['availability_zone']

            if not hostname:
                continue
            self.inventory.add_host(hostname, group=group)
            for hostvar, hostval in host.items():
                self.inventory.set_variable(hostname, hostvar, hostval)

            strict = self.get_option('strict')

            # Composed variables
            self._set_composite_vars(self.get_option('compose'), host, hostname, strict=strict)

            # Complex groups based on jinja2 conditionals, hosts that meet the conditional are added to group
            self._add_host_to_composed_groups(self.get_option('groups'), host, hostname, strict=strict)

            # Create groups based on variable values and add the corresponding hosts to it
            self._add_host_to_keyed_groups(self.get_option('keyed_groups'), host, hostname, strict=strict)

    def verify_file(self, path):
        '''
            :param loader: an ansible.parsing.dataloader.DataLoader object
            :param path: the path to the inventory config file
            :return the contents of the config file
        '''
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(('alicloud.yaml', 'alicloud.yml')):
                return True
        display.debug("alicloud inventory filename must end with 'alicloud.yaml' or 'alicloud.yml'")
        return False

    def parse(self, inventory, loader, path, cache=True):

        super(InventoryModule, self).parse(inventory, loader, path)

        self._read_config_data(path)
        self._set_credentials()

        # get user specifications
        regions = self.get_option('regions')
        filters = self.get_option('filters')
        hostnames = self.get_option('hostnames')

        cache_key = self.get_cache_key(path)
        # false when refresh_cache or --flush-cache is used
        if cache:
            # get the user-specified directive
            cache = self.get_option('cache')

        # Generate inventory
        cache_needs_update = False
        if cache:
            try:
                results = self._cache[cache_key]
            except KeyError:
                # if cache expires or cache file doesn't exist
                cache_needs_update = True

        if not cache or cache_needs_update:
            results = self._query(regions, filters)

        self._populate(results, hostnames)

        # If the cache has expired/doesn't exist or if refresh_inventory/flush cache is used
        # when the user is using caching, update the cached inventory
        if cache_needs_update or (not cache and self.get_option('cache')):
            self._cache[cache_key] = results
