#!/usr/bin/python
#
# Copyright (c) 2016 Matt Davis, <mdavis@ansible.com>
#                    Chris Houseknecht, <house@redhat.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: azure_rm_securitygroup_info


short_description: Get security group facts

description:
    - Get facts for a specific security group or all security groups within a resource group.

options:
    name:
        description:
            - Only show results for a specific security group.
    resource_group:
        description:
            - Name of the resource group to use.
        required: true
    tags:
        description:
            - Limit results by providing a list of tags. Format tags as 'key' or 'key:value'.


author:
    - Chris Houseknecht (@chouseknecht)
    - Matt Davis (@nitzmahone)


extends_documentation_fragment:
- community.general.azure
'''

EXAMPLES = '''
    - name: Get facts for one security group
      azure_rm_securitygroup_info:
        resource_group: myResourceGroup
        name: secgroup001

    - name: Get facts for all security groups
      azure_rm_securitygroup_info:
        resource_group: myResourceGroup

'''

RETURN = '''
securitygroups:
    description:
        - List containing security group dicts.
    returned: always
    type: complex
    contains:
        etag:
            description:
                - A unique read-only string that changes whenever the resource is updated.
            returned: always
            type: str
            sample:  'W/"d036f4d7-d977-429a-a8c6-879bc2523399"'
        id:
            description:
                - Resource ID.
            returned: always
            type: str
            sample: "/subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/resourceGroup/myResourceGroup/providers/Microsoft.Network/networkSecurityGroups/secgroup001"
        location:
            description:
                - Resource location.
            returned: always
            type: str
            sample: "eastus2"
        name:
            description:
                - Resource name.
            returned: always
            type: str
            sample: "secgroup001"
        properties:
            description:
                - List of security group's properties.
            returned: always
            type: dict
            sample: {
                    "defaultSecurityRules": [
                      {
                      "etag": 'W/"d036f4d7-d977-429a-a8c6-879bc2523399"',
                      "id": "/subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/resourceGroup/myResourceGroup/providers/Microsoft.Network/networkSecurityGroups/secgroup001/defaultSecurityRules/AllowVnetInBound",
                      "name": "AllowVnetInBound",
                      "properties": {
                        "access": "Allow",
                        "description": "Allow inbound traffic from all VMs in VNET",
                        "destinationAddressPrefix": "VirtualNetwork",
                        "destinationPortRange": "*",
                        "direction": "Inbound",
                        "priority": 65000,
                        "protocol": "*",
                        "provisioningState": "Succeeded",
                        "sourceAddressPrefix": "VirtualNetwork",
                        "sourcePortRange": "*"
                                    }
                         },
                         {
                         "etag": 'W/"d036f4d7-d977-429a-a8c6-879bc2523399"',
                         "id": "/subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/resourceGroup/myResourceGroup/providers/Microsoft.Network/networkSecurityGroups/secgroup001/defaultSecurityRules/AllowAzureLoadBalancerInBound",
                         "name": "AllowAzureLoadBalancerInBound",
                         "properties": {
                           "access": "Allow",
                           "description": "Allow inbound traffic from azure load balancer",
                           "destinationAddressPrefix": "*",
                           "destinationPortRange": "*",
                           "direction": "Inbound",
                           "priority": 65001,
                           "protocol": "*",
                           "provisioningState": "Succeeded",
                           "sourceAddressPrefix": "AzureLoadBalancer",
                           "sourcePortRange": "*"
                                     }
                         },
                         {
                         "etag": 'W/"d036f4d7-d977-429a-a8c6-879bc2523399"',
                         "id": "/subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/resourceGroup/myResourceGroup/providers/Microsoft.Network/networkSecurityGroups/secgroup001/defaultSecurityRules/DenyAllInBound",
                         "name": "DenyAllInBound",
                         "properties": {
                          "access": "Deny",
                          "description": "Deny all inbound traffic",
                          "destinationAddressPrefix": "*",
                          "destinationPortRange": "*",
                          "direction": "Inbound",
                          "priority": 65500,
                          "protocol": "*",
                          "provisioningState": "Succeeded",
                          "sourceAddressPrefix": "*",
                          "sourcePortRange": "*"
                                       }
                        },
                        {
                        "etag": 'W/"d036f4d7-d977-429a-a8c6-879bc2523399"',
                        "id": "/subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/resourceGroup/myResourceGroup/providers/Microsoft.Network/networkSecurityGroups/secgroup001/defaultSecurityRules/AllowVnetOutBound",
                        "name": "AllowVnetOutBound",
                        "properties": {
                          "access": "Allow",
                          "description": "Allow outbound traffic from all VMs to all VMs in VNET",
                          "destinationAddressPrefix": "VirtualNetwork",
                          "destinationPortRange": "*",
                          "direction": "Outbound",
                          "priority": 65000,
                          "protocol": "*",
                          "provisioningState": "Succeeded",
                          "sourceAddressPrefix": "VirtualNetwork",
                          "sourcePortRange": "*"
                                      }
                        },
                        {
                        "etag": 'W/"d036f4d7-d977-429a-a8c6-879bc2523399"',
                        "id": "/subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/resourceGroup/myResourceGroup/providers/Microsoft.Network/networkSecurityGroups/secgroup001/defaultSecurityRules/AllowInternetOutBound",
                        "name": "AllowInternetOutBound",
                        "properties": {
                          "access": "Allow",
                          "description": "Allow outbound traffic from all VMs to Internet",
                          "destinationAddressPrefix": "Internet",
                          "destinationPortRange": "*",
                          "direction": "Outbound",
                          "priority": 65001,
                          "protocol": "*",
                          "provisioningState": "Succeeded",
                          "sourceAddressPrefix": "*",
                          "sourcePortRange": "*"
                                     }
                        },
                        {
                        "etag": 'W/"d036f4d7-d977-429a-a8c6-879bc2523399"',
                        "id": "/subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/resourceGroup/myResourceGroup/providers/Microsoft.Network/networkSecurityGroups/secgroup001/defaultSecurityRules/DenyAllOutBound",
                        "name": "DenyAllOutBound",
                        "properties": {
                          "access": "Deny",
                          "description": "Deny all outbound traffic",
                          "destinationAddressPrefix": "*",
                          "destinationPortRange": "*",
                          "direction": "Outbound",
                          "priority": 65500,
                          "protocol": "*",
                          "provisioningState": "Succeeded",
                          "sourceAddressPrefix": "*",
                          "sourcePortRange": "*"
                                       }
                         }
                         ],
                    "networkInterfaces": [
                      {
                        "id": "/subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/resourceGroup/myResourceGroup/providers/Microsoft.Network/networkInterfaces/nic004"
                      }
                                    ],
                    "provisioningState": "Succeeded",
                    "resourceGuid": "ebd00afa-5dc8-446f-810a-50dd6f671588",
                    "securityRules": []
            }
        tags:
            description:
                - Tags to assign to the security group.
            returned: always
            type: dict
            sample: { 'tag': 'value' }
        type:
            description:
                - Type of the resource.
            returned: always
            type: str
            sample: "Microsoft.Network/networkSecurityGroups"

'''  # NOQA

try:
    from msrestazure.azure_exceptions import CloudError
except Exception:
    # This is handled in azure_rm_common
    pass

from ansible_collections.azure.azcollection.plugins.module_utils.azure_rm_common import AzureRMModuleBase


AZURE_OBJECT_CLASS = 'NetworkSecurityGroup'


class AzureRMSecurityGroupInfo(AzureRMModuleBase):

    def __init__(self):

        self.module_arg_spec = dict(
            name=dict(type='str'),
            resource_group=dict(required=True, type='str'),
            tags=dict(type='list'),
        )

        self.results = dict(
            changed=False,
        )

        self.name = None
        self.resource_group = None
        self.tags = None

        super(AzureRMSecurityGroupInfo, self).__init__(self.module_arg_spec,
                                                       supports_tags=False,
                                                       facts_module=True)

    def exec_module(self, **kwargs):

        is_old_facts = self.module._name == 'azure_rm_securitygroup_facts'
        if is_old_facts:
            self.module.deprecate("The 'azure_rm_securitygroup_facts' module has been renamed to 'azure_rm_securitygroup_info'", version='2.13')

        for key in self.module_arg_spec:
            setattr(self, key, kwargs[key])

        if self.name is not None:
            info = self.get_item()
        else:
            info = self.list_items()

        if is_old_facts:
            self.results['ansible_facts'] = {
                'azure_securitygroups': info
            }
        self.results['securitygroups'] = info

        return self.results

    def get_item(self):
        self.log('Get properties for {0}'.format(self.name))
        item = None
        result = []

        try:
            item = self.network_client.network_security_groups.get(self.resource_group, self.name)
        except CloudError:
            pass

        if item and self.has_tags(item.tags, self.tags):
            grp = self.serialize_obj(item, AZURE_OBJECT_CLASS)
            grp['name'] = item.name
            result = [grp]

        return result

    def list_items(self):
        self.log('List all items')
        try:
            response = self.network_client.network_security_groups.list(self.resource_group)
        except Exception as exc:
            self.fail("Error listing all items - {0}".format(str(exc)))

        results = []
        for item in response:
            if self.has_tags(item.tags, self.tags):
                grp = self.serialize_obj(item, AZURE_OBJECT_CLASS)
                grp['name'] = item.name
                results.append(grp)
        return results


def main():
    AzureRMSecurityGroupInfo()


if __name__ == '__main__':
    main()
