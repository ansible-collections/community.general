#!/usr/bin/python
#
# Copyright (c) 2019 Zim Kalinowski, (@zikalino)
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: azure_rm_devtestlabcustomimage_info
short_description: Get Azure DevTest Lab Custom Image facts
description:
    - Get facts of Azure Azure DevTest Lab Custom Image.

options:
    resource_group:
        description:
            - The name of the resource group.
        required: True
        type: str
    lab_name:
        description:
            - The name of the lab.
        required: True
        type: str
    name:
        description:
            - The name of the custom image.
        type: str
    tags:
        description:
            - Limit results by providing a list of tags. Format tags as 'key' or 'key:value'.
        type: list


author:
    - Zim Kalinowski (@zikalino)


extends_documentation_fragment:
- community.general.azure
'''

EXAMPLES = '''
  - name: Get instance of Custom Image
    azure_rm_devtestlabcustomimage_info:
      resource_group: myResourceGroup
      lab_name: myLab
      name: myImage

  - name: List instances of Custom Image in the lab
    azure_rm_devtestlabcustomimage_info:
      resource_group: myResourceGroup
      lab_name: myLab
      name: myImage
'''

RETURN = '''
custom_images:
    description:
        - A list of dictionaries containing facts for Custom Image.
    returned: always
    type: complex
    contains:
        id:
            description:
                - The identifier of the artifact source.
            returned: always
            type: str
            sample: "/subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxxx/resourceGroups/myResourceGroup/providers/Microsoft.DevTestLab/labs/myLab/cu
                     stomimages/myImage"
        resource_group:
            description:
                - Name of the resource group.
            returned: always
            type: str
            sample: myResourceGroup
        lab_name:
            description:
                - Name of the lab.
            returned: always
            type: str
            sample: myLab
        name:
            description:
                - The name of the image.
            returned: always
            type: str
            sample: myImage
        managed_shapshot_id:
            description:
                - Managed snapshot id.
            returned: always
            type: str
            sample: "/subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxxx/resourcegroups/myResourceGroup/providers/microsoft.compute/snapshots/myImage"
        source_vm_id:
            description:
                - Source VM id.
            returned: always
            type: str
            sample: "/subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxxx//resourcegroups/myResourceGroup/providers/microsoft.devtestlab/labs/myLab/v
                     irtualmachines/myLabVm"
        tags:
            description:
                - The tags of the resource.
            returned: always
            type: complex
            sample: "{ 'MyTag':'MyValue' }"
'''

from ansible_collections.azure.azcollection.plugins.module_utils.azure_rm_common import AzureRMModuleBase

try:
    from msrestazure.azure_exceptions import CloudError
    from azure.mgmt.devtestlabs import DevTestLabsClient
    from msrest.serialization import Model
except ImportError:
    # This is handled in azure_rm_common
    pass


class AzureRMDtlCustomImageInfo(AzureRMModuleBase):
    def __init__(self):
        # define user inputs into argument
        self.module_arg_spec = dict(
            resource_group=dict(
                type='str',
                required=True
            ),
            lab_name=dict(
                type='str',
                required=True
            ),
            name=dict(
                type='str',
                required=True
            ),
            tags=dict(
                type='list'
            )
        )
        # store the results of the module operation
        self.results = dict(
            changed=False
        )
        self.mgmt_client = None
        self.resource_group = None
        self.lab_name = None
        self.name = None
        self.tags = None
        super(AzureRMDtlCustomImageInfo, self).__init__(self.module_arg_spec, supports_tags=False)

    def exec_module(self, **kwargs):
        is_old_facts = self.module._name == 'azure_rm_devtestlabcustomimage_facts'
        if is_old_facts:
            self.module.deprecate("The 'azure_rm_devtestlabcustomimage_facts' module has been renamed to 'azure_rm_devtestlabcustomimage_info'", version='2.13')

        for key in self.module_arg_spec:
            setattr(self, key, kwargs[key])
        self.mgmt_client = self.get_mgmt_svc_client(DevTestLabsClient,
                                                    base_url=self._cloud_environment.endpoints.resource_manager)

        if self.name:
            self.results['custom_images'] = self.get()
        else:
            self.results['custom_images'] = self.list()
        return self.results

    def get(self):
        response = None
        results = []
        try:
            response = self.mgmt_client.custom_images.get(resource_group_name=self.resource_group,
                                                          lab_name=self.lab_name,
                                                          name=self.name)
            self.log("Response : {0}".format(response))
        except CloudError as e:
            self.log('Could not get facts for Custom Image.')

        if response and self.has_tags(response.tags, self.tags):
            results.append(self.format_response(response))

        return results

    def list(self):
        response = None
        results = []
        try:
            response = self.mgmt_client.custom_images.list(resource_group_name=self.resource_group,
                                                           lab_name=self.lab_name)
            self.log("Response : {0}".format(response))
        except CloudError as e:
            self.log('Could not get facts for Custom Image.')

        if response is not None:
            for item in response:
                if self.has_tags(item.tags, self.tags):
                    results.append(self.format_response(item))

        return results

    def format_response(self, item):
        d = item.as_dict()
        d = {
            'resource_group': self.resource_group,
            'lab_name': self.lab_name,
            'name': d.get('name'),
            'id': d.get('id'),
            'managed_snapshot_id': d.get('managed_snapshot_id'),
            'source_vm_id': d.get('vm', {}).get('source_vm_id'),
            'tags': d.get('tags')
        }
        return d


def main():
    AzureRMDtlCustomImageInfo()


if __name__ == '__main__':
    main()
