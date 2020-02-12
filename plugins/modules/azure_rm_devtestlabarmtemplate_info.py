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
module: azure_rm_devtestlabarmtemplate_info
short_description: Get Azure DevTest Lab ARM Template facts
description:
    - Get facts of Azure DevTest Lab ARM Template.

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
    artifact_source_name:
        description:
            - The name of the artifact source.
        required: True
        type: str
    name:
        description:
            - The name of the ARM template.
        type: str


author:
    - Zim Kalinowski (@zikalino)


extends_documentation_fragment:
- community.general.azure
'''

EXAMPLES = '''
  - name: Get information on DevTest Lab ARM Template
    azure_rm_devtestlabarmtemplate_info:
      resource_group: myResourceGroup
      lab_name: myLab
      artifact_source_name: public environment repo
      name: WebApp
'''

RETURN = '''
arm_templates:
    description:
        - A list of dictionaries containing facts for DevTest Lab ARM Template.
    returned: always
    type: complex
    contains:
        id:
            description:
                - The identifier of the resource.
            returned: always
            type: str
            sample: "/subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/resourceGroups/myResourceGroup/providers/Microsoft.DevTestLab/labs/myLab/art
                     ifactSources/public environment repo/armTemplates/WebApp"
        resource_group:
            description:
                - Resource group name.
            returned: always
            sample: myResourceGroup
        lab_name:
            description:
                - DevTest Lab name.
            returned: always
            sample: myLab
        artifact_source_name:
            description:
                - Artifact source name.
            returned: always
            sample: public environment repo
        name:
            description:
                - ARM Template name.
            returned: always
            sample: WebApp
        display_name:
            description:
                - The tags of the resource.
            returned: always
            sample: Web App
        description:
            description:
                - The tags of the resource.
            returned: always
            sample: This template creates an Azure Web App without a data store.
        publisher:
            description:
                - The tags of the resource.
            returned: always
            sample: Microsoft
'''

from ansible_collections.azure.azcollection.plugins.module_utils.azure_rm_common import AzureRMModuleBase

try:
    from msrestazure.azure_exceptions import CloudError
    from azure.mgmt.devtestlabs import DevTestLabsClient
    from msrest.serialization import Model
except ImportError:
    # This is handled in azure_rm_common
    pass


class AzureRMDtlArmTemplateInfo(AzureRMModuleBase):
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
            artifact_source_name=dict(
                type='str',
                required=True
            ),
            name=dict(
                type='str'
            )
        )
        # store the results of the module operation
        self.results = dict(
            changed=False
        )
        self.mgmt_client = None
        self.resource_group = None
        self.lab_name = None
        self.artifact_source_name = None
        self.name = None
        super(AzureRMDtlArmTemplateInfo, self).__init__(self.module_arg_spec, supports_tags=False)

    def exec_module(self, **kwargs):
        is_old_facts = self.module._name == 'azure_rm_devtestlabarmtemplate_facts'
        if is_old_facts:
            self.module.deprecate("The 'azure_rm_devtestlabarmtemplate_facts' module has been renamed to 'azure_rm_devtestlabarmtemplate_info'", version='2.13')

        for key in self.module_arg_spec:
            setattr(self, key, kwargs[key])
        self.mgmt_client = self.get_mgmt_svc_client(DevTestLabsClient,
                                                    base_url=self._cloud_environment.endpoints.resource_manager)

        if self.name:
            self.results['armtemplates'] = self.get()
        else:
            self.results['armtemplates'] = self.list()

        return self.results

    def list(self):
        response = None
        results = []
        try:
            response = self.mgmt_client.arm_templates.list(resource_group_name=self.resource_group,
                                                           lab_name=self.lab_name,
                                                           artifact_source_name=self.artifact_source_name)
            self.log("Response : {0}".format(response))
        except CloudError as e:
            self.fail('Could not get facts for DTL ARM Template.')

        if response is not None:
            for item in response:
                results.append(self.format_response(item))

        return results

    def get(self):
        response = None
        results = []
        try:
            response = self.mgmt_client.arm_templates.get(resource_group_name=self.resource_group,
                                                          lab_name=self.lab_name,
                                                          artifact_source_name=self.artifact_source_name,
                                                          name=self.name)
            self.log("Response : {0}".format(response))
        except CloudError as e:
            self.fail('Could not get facts for DTL ARM Template.')

        if response:
            results.append(self.format_response(response))

        return results

    def format_response(self, item):
        d = item.as_dict()
        d = {
            'resource_group': self.parse_resource_to_dict(d.get('id')).get('resource_group'),
            'lab_name': self.parse_resource_to_dict(d.get('id')).get('name'),
            'artifact_source_name': self.parse_resource_to_dict(d.get('id')).get('child_name_1'),
            'id': d.get('id', None),
            'name': d.get('name'),
            'display_name': d.get('display_name'),
            'description': d.get('description'),
            'publisher': d.get('publisher')
        }
        return d


def main():
    AzureRMDtlArmTemplateInfo()


if __name__ == '__main__':
    main()
