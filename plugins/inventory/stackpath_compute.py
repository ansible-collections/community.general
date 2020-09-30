# Copyright (c) 2020 Shay Rybak <shay.rybak@stackpath.com>
# Copyright (c) 2020 Ansible Project
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: stackpath_compute
    plugin_type: inventory
    short_description: StackPath Edge Computing inventory source
    version_added: 1.2.0
    extends_documentation_fragment:
        - inventory_cache
        - constructed
    description:
        - Get inventory hosts from StackPath Edge Computing.
        - Uses a YAML configuration file that ends with stackpath_compute.(yml|yaml).
    options:
        plugin:
            description:
                - A token that ensures this is a source file for the plugin.
            required: true
            choices: ['community.general.stackpath_compute']
        client_id:
            description:
                - An OAuth client ID generated from the API Management section of the StackPath customer portal
                  U(https://control.stackpath.net/api-management).
            required: true
            type: str
        client_secret:
            description:
                - An OAuth client secret generated from the API Management section of the StackPath customer portal
                  U(https://control.stackpath.net/api-management).
            required: true
            type: str
        stack_slugs:
            description:
                - A list of Stack slugs to query instances in. If no entry then get instances in all stacks on the account.
            type: list
            elements: str
        use_internal_ip:
            description:
                - Whether or not to use internal IP addresses, If false, uses external IP addresses, internal otherwise.
                - If an instance doesn't have an external IP it will not be returned when this option is set to false.
            type: bool
'''

EXAMPLES = '''
# Example using credentials to fetch all workload instances in a stack.
---
plugin: community.general.stackpath_compute
client_id: my_client_id
client_secret: my_client_secret
stack_slugs:
- my_first_stack_slug
- my_other_stack_slug
use_internal_ip: false
'''

import traceback
import json

from ansible.errors import AnsibleError
from ansible.module_utils.urls import open_url
from ansible.plugins.inventory import (
    BaseInventoryPlugin,
    Constructable,
    Cacheable
)
from ansible.utils.display import Display


display = Display()


class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):

    NAME = 'community.general.stackpath_compute'

    def __init__(self):
        super(InventoryModule, self).__init__()

        # credentials
        self.client_id = None
        self.client_secret = None
        self.stack_slug = None
        self.api_host = "https://gateway.stackpath.com"
        self.group_keys = [
            "stackSlug",
            "workloadId",
            "cityCode",
            "countryCode",
            "continent",
            "target",
            "name",
            "workloadSlug"
        ]

    def _validate_config(self, config):
        if config['plugin'] != 'community.general.stackpath_compute':
            raise AnsibleError("plugin doesn't match this plugin")
        try:
            client_id = config['client_id']
            if client_id != 32:
                raise AnsibleError("client_id must be 32 characters long")
        except KeyError:
            raise AnsibleError("config missing client_id, a required option")
        try:
            client_secret = config['client_secret']
            if client_secret != 64:
                raise AnsibleError("client_secret must be 64 characters long")
        except KeyError:
            raise AnsibleError("config missing client_id, a required option")
        return True

    def _set_credentials(self):
        '''
            :param config_data: contents of the inventory config file
        '''
        self.client_id = self.get_option('client_id')
        self.client_secret = self.get_option('client_secret')

    def _authenticate(self):
        payload = json.dumps(
            {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials",
            }
        )
        headers = {
            "Content-Type": "application/json",
        }
        resp = open_url(
            self.api_host + '/identity/v1/oauth2/token',
            headers=headers,
            data=payload,
            method="POST"
        )
        status_code = resp.code
        if status_code == 200:
            body = resp.read()
        self.auth_token = json.loads(body)["access_token"]

    def _query(self):
        results = []
        workloads = []
        self._authenticate()
        for stack_slug in self.stack_slugs:
            try:
                workloads = self._stackpath_query_get_list(self.api_host + '/workload/v1/stacks/' + stack_slug + '/workloads')
            except Exception:
                raise AnsibleError("Failed to get workloads from the StackPath API: %s" % traceback.format_exc())
            for workload in workloads:
                try:
                    workload_instances = self._stackpath_query_get_list(
                        self.api_host + '/workload/v1/stacks/' + stack_slug + '/workloads/' + workload["id"] + '/instances'
                    )
                except Exception:
                    raise AnsibleError("Failed to get workload instances from the StackPath API: %s" % traceback.format_exc())
                for instance in workload_instances:
                    if instance["phase"] == "RUNNING":
                        instance["stackSlug"] = stack_slug
                        instance["workloadId"] = workload["id"]
                        instance["workloadSlug"] = workload["slug"]
                        instance["cityCode"] = instance["location"]["cityCode"]
                        instance["countryCode"] = instance["location"]["countryCode"]
                        instance["continent"] = instance["location"]["continent"]
                        instance["target"] = instance["metadata"]["labels"]["workload.platform.stackpath.net/target-name"]
                        try:
                            if instance[self.hostname_key]:
                                results.append(instance)
                        except KeyError:
                            pass
        return results

    def _populate(self, instances):
        for instance in instances:
            for group_key in self.group_keys:
                group = group_key + "_" + instance[group_key]
                group = group.lower().replace(" ", "_").replace("-", "_")
                self.inventory.add_group(group)
                self.inventory.add_host(instance[self.hostname_key],
                                        group=group)

    def _stackpath_query_get_list(self, url):
        self._authenticate()
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.auth_token,
        }
        next_page = True
        result = []
        cursor = '-1'
        while next_page:
            resp = open_url(
                url + '?page_request.first=10&page_request.after=%s' % cursor,
                headers=headers,
                method="GET"
            )
            status_code = resp.code
            if status_code == 200:
                body = resp.read()
            body_json = json.loads(body)
            result.extend(body_json["results"])
            next_page = body_json["pageInfo"]["hasNextPage"]
            if next_page:
                cursor = body_json["pageInfo"]["endCursor"]
        return result

    def _get_stack_slugs(self, stacks):
        self.stack_slugs = [stack["slug"] for stack in stacks]

    def verify_file(self, path):
        '''
            :param loader: an ansible.parsing.dataloader.DataLoader object
            :param path: the path to the inventory config file
            :return the contents of the config file
        '''
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(('stackpath_compute.yml', 'stackpath_compute.yaml')):
                return True
        display.debug(
            "stackpath_compute inventory filename must end with \
            'stackpath_compute.yml' or 'stackpath_compute.yaml'"
        )
        return False

    def parse(self, inventory, loader, path, cache=True):

        super(InventoryModule, self).parse(inventory, loader, path)

        config = self._read_config_data(path)
        self._validate_config(config)
        self._set_credentials()

        # get user specifications
        self.use_internal_ip = self.get_option('use_internal_ip')
        if self.use_internal_ip:
            self.hostname_key = "ipAddress"
        else:
            self.hostname_key = "externalIpAddress"

        self.stack_slugs = self.get_option('stack_slugs')
        if not self.stack_slugs:
            try:
                stacks = self._stackpath_query_get_list(self.api_host + '/stack/v1/stacks')
                self._get_stack_slugs(stacks)
            except Exception:
                raise AnsibleError("Failed to get stack IDs from the Stackpath API: %s" % traceback.format_exc())

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
            results = self._query()

        self._populate(results)

        # If the cache has expired/doesn't exist or
        # if refresh_inventory/flush cache is used
        # when the user is using caching, update the cached inventory
        try:
            if cache_needs_update or (not cache and self.get_option('cache')):
                self._cache[cache_key] = results
        except Exception:
            raise AnsibleError("Failed to populate data: %s" % traceback.format_exc())
