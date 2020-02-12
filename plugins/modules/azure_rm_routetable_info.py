#!/usr/bin/python
#
# Copyright (c) 2018 Yuwei Zhou, <yuwzho@microsoft.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: azure_rm_routetable_info


short_description: Get route table facts

description:
    - Get facts for a specific route table or all route table in a resource group or subscription.

options:
    name:
        description:
            - Limit results to a specific route table.
    resource_group:
        description:
            - Limit results in a specific resource group.
    tags:
        description:
            - Limit results by providing a list of tags. Format tags as 'key' or 'key:value'.


author:
    - Yuwei Zhou (@yuwzho)


extends_documentation_fragment:
- community.general.azure
'''

EXAMPLES = '''
    - name: Get facts for one route table
      azure_rm_routetable_info:
        name: Testing
        resource_group: myResourceGroup

    - name: Get facts for all route tables
      azure_rm_routetable_info:
        resource_group: myResourceGroup

    - name: Get facts by tags
      azure_rm_routetable_info:
        tags:
          - testing
          - foo:bar
'''
RETURN = '''
id:
    description:
        - Resource ID.
    returned: success
    type: str
    sample: "/subscriptions/xxxx...xxxx/resourceGroups/v-xisuRG/providers/Microsoft.Network/routeTables/tableb57dc95236"
name:
    description:
        - Name of the resource.
    returned: success
    type: str
    sample: tableb57dc95236
resource_group:
    description:
        - Resource group of the route table.
    returned: success
    type: str
    sample: v-xisuRG
disable_bgp_route_propagation:
    description:
        - Whether the routes learned by BGP on that route table disabled.
    returned: success
    type: bool
    sample: false
tags:
    description:
        - Tags of the route table.
    returned: success
    type: dict
    sample: { 'key1':'value1', 'key2':'value2'}
routes:
    description:
        - Current routes of the route table.
    returned: success
    type: list
    sample: [
        {
          "id": "/subscriptions/xxx...xxx/resourceGroups/v-xisuRG/providers/Microsoft.Network/routeTables/tableb57dc95236/routes/routeb57dc95540",
          "name": "routeb57dc95540",
          "resource_group": "v-xisuRG",
          "route_table_name": "tableb57dc95236",
          "address_prefix": "10.1.0.0/24",
          "next_hop_type": "virtual_network_gateway",
          "next_hop_ip_address": null
        }
    ]
'''

try:
    from msrestazure.azure_exceptions import CloudError
except Exception:
    # This is handled in azure_rm_common
    pass

from ansible_collections.azure.azcollection.plugins.module_utils.azure_rm_common import AzureRMModuleBase, azure_id_to_dict
from ansible.module_utils.common.dict_transformations import _camel_to_snake


def route_to_dict(route):
    id_dict = azure_id_to_dict(route.id)
    return dict(
        id=route.id,
        name=route.name,
        resource_group=id_dict.get('resourceGroups'),
        route_table_name=id_dict.get('routeTables'),
        address_prefix=route.address_prefix,
        next_hop_type=_camel_to_snake(route.next_hop_type),
        next_hop_ip_address=route.next_hop_ip_address
    )


def instance_to_dict(table):
    return dict(
        id=table.id,
        name=table.name,
        resource_group=azure_id_to_dict(table.id).get('resourceGroups'),
        location=table.location,
        routes=[route_to_dict(i) for i in table.routes] if table.routes else [],
        disable_bgp_route_propagation=table.disable_bgp_route_propagation,
        tags=table.tags
    )


class AzureRMRouteTableInfo(AzureRMModuleBase):

    def __init__(self):

        self.module_arg_spec = dict(
            name=dict(type='str'),
            resource_group=dict(type='str'),
            tags=dict(type='list')
        )

        self.results = dict(
            changed=False,
            route_tables=[]
        )

        self.name = None
        self.resource_group = None
        self.tags = None

        super(AzureRMRouteTableInfo, self).__init__(self.module_arg_spec,
                                                    supports_tags=False,
                                                    facts_module=True)

    def exec_module(self, **kwargs):
        is_old_facts = self.module._name == 'azure_rm_routetable_facts'
        if is_old_facts:
            self.module.deprecate("The 'azure_rm_routetable_facts' module has been renamed to 'azure_rm_routetable_info'", version='2.13')

        for key in self.module_arg_spec:
            setattr(self, key, kwargs[key])

        response = []
        if self.name:
            response = self.get_item()
        elif self.resource_group:
            response = self.list_items()
        else:
            response = self.list_all_items()

        self.results['route_tables'] = [instance_to_dict(x) for x in response if self.has_tags(x.tags, self.tags)]
        return self.results

    def get_item(self):
        self.log('Get route table for {0}-{1}'.format(self.resource_group, self.name))
        try:
            item = self.network_client.route_tables.get(self.resource_group, self.name)
            return [item]
        except CloudError:
            pass
        return []

    def list_items(self):
        self.log('List all items in resource group')
        try:
            return self.network_client.route_tables.list(self.resource_group)
        except CloudError as exc:
            self.fail("Failed to list items - {0}".format(str(exc)))
        return []

    def list_all_items(self):
        self.log("List all items in subscription")
        try:
            return self.network_client.route_tables.list_all()
        except CloudError as exc:
            self.fail("Failed to list all items - {0}".format(str(exc)))
        return []


def main():
    AzureRMRouteTableInfo()


if __name__ == '__main__':
    main()
