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
module: azure_rm_aks_info


short_description: Get Azure Kubernetes Service facts

description:
    - Get facts for a specific Azure Kubernetes Service or all Azure Kubernetes Services.

options:
    name:
        description:
            - Limit results to a specific resource group.
    resource_group:
        description:
            - The resource group to search for the desired Azure Kubernetes Service
    tags:
        description:
            - Limit results by providing a list of tags. Format tags as 'key' or 'key:value'.
    show_kubeconfig:
        description:
            - Show kubeconfig of the AKS cluster.
            - Note the operation will cost more network overhead, not recommended when listing AKS.
        choices:
            - user
            - admin


author:
    - Yuwei Zhou (@yuwzho)

extends_documentation_fragment:
- community.general.azure
'''

EXAMPLES = '''
    - name: Get facts for one Azure Kubernetes Service
      azure_rm_aks_info:
        name: Testing
        resource_group: myResourceGroup

    - name: Get facts for all Azure Kubernetes Services
      azure_rm_aks_info:

    - name: Get facts by tags
      azure_rm_aks_info:
        tags:
          - testing
'''

RETURN = '''
azure_aks:
    description: List of Azure Kubernetes Service dicts.
    returned: always
    type: list
'''

from ansible_collections.azure.azcollection.plugins.module_utils.azure_rm_common import AzureRMModuleBase

try:
    from msrestazure.azure_exceptions import CloudError
    from azure.common import AzureHttpError
except Exception:
    # handled in azure_rm_common
    pass

AZURE_OBJECT_CLASS = 'managedClusters'


class AzureRMManagedClusterInfo(AzureRMModuleBase):
    """Utility class to get Azure Kubernetes Service facts"""

    def __init__(self):

        self.module_args = dict(
            name=dict(type='str'),
            resource_group=dict(type='str'),
            tags=dict(type='list'),
            show_kubeconfig=dict(type='str', choices=['user', 'admin']),
        )

        self.results = dict(
            changed=False,
            aks=[],
            available_versions=[]
        )

        self.name = None
        self.resource_group = None
        self.tags = None
        self.show_kubeconfig = None

        super(AzureRMManagedClusterInfo, self).__init__(
            derived_arg_spec=self.module_args,
            supports_tags=False,
            facts_module=True
        )

    def exec_module(self, **kwargs):

        is_old_facts = self.module._name == 'azure_rm_aks_facts'
        if is_old_facts:
            self.module.deprecate("The 'azure_rm_aks_facts' module has been renamed to 'azure_rm_aks_info'", version='2.13')

        for key in self.module_args:
            setattr(self, key, kwargs[key])

        self.results['aks'] = (
            self.get_item() if self.name
            else self.list_items()
        )

        return self.results

    def get_item(self):
        """Get a single Azure Kubernetes Service"""

        self.log('Get properties for {0}'.format(self.name))

        item = None
        result = []

        try:
            item = self.managedcluster_client.managed_clusters.get(self.resource_group, self.name)
        except CloudError:
            pass

        if item and self.has_tags(item.tags, self.tags):
            result = [self.serialize_obj(item, AZURE_OBJECT_CLASS)]
            if self.show_kubeconfig:
                result[0]['kube_config'] = self.get_aks_kubeconfig(self.resource_group, self.name)

        return result

    def list_items(self):
        """Get all Azure Kubernetes Services"""

        self.log('List all Azure Kubernetes Services')

        try:
            response = self.managedcluster_client.managed_clusters.list(self.resource_group)
        except AzureHttpError as exc:
            self.fail('Failed to list all items - {0}'.format(str(exc)))

        results = []
        for item in response:
            if self.has_tags(item.tags, self.tags):
                item_dict = self.serialize_obj(item, AZURE_OBJECT_CLASS)
                if self.show_kubeconfig:
                    item_dict['kube_config'] = self.get_aks_kubeconfig(self.resource_group, item.name)
                results.append(item_dict)

        return results

    def get_aks_kubeconfig(self, resource_group, name):
        '''
        Gets kubeconfig for the specified AKS instance.

        :return: AKS instance kubeconfig
        '''
        if not self.show_kubeconfig:
            return ''
        role_name = 'cluster{0}'.format(str.capitalize(self.show_kubeconfig))
        access_profile = self.managedcluster_client.managed_clusters.get_access_profile(resource_group, name, role_name)
        return access_profile.kube_config.decode('utf-8')


def main():
    """Main module execution code path"""

    AzureRMManagedClusterInfo()


if __name__ == '__main__':
    main()
