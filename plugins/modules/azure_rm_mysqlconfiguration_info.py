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
module: azure_rm_mysqlconfiguration_info
short_description: Get Azure MySQL Configuration facts
description:
    - Get facts of Azure MySQL Configuration.

options:
    resource_group:
        description:
            - The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.
        required: True
        type: str
    server_name:
        description:
            - The name of the server.
        required: True
        type: str
    name:
        description:
            - Setting name.
        type: str


author:
    - Zim Kalinowski (@zikalino)


extends_documentation_fragment:
- community.general.azure
'''

EXAMPLES = '''
  - name: Get specific setting of MySQL Server
    azure_rm_mysqlconfiguration_info:
      resource_group: myResourceGroup
      server_name: testmysqlserver
      name: deadlock_timeout

  - name: Get all settings of MySQL Server
    azure_rm_mysqlconfiguration_info:
      resource_group: myResourceGroup
      server_name: server_name
'''

RETURN = '''
settings:
    description:
        - A list of dictionaries containing MySQL Server settings.
    returned: always
    type: complex
    contains:
        id:
            description:
                - Setting resource ID.
            returned: always
            type: str
            sample: "/subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/resourceGroups/myResourceGroup/providers/Microsoft.DBforMySQL/servers/testmysqlser
                     ver/configurations/deadlock_timeout"
        name:
            description:
                - Setting name.
            returned: always
            type: str
            sample: deadlock_timeout
        value:
            description:
                - Setting value.
            returned: always
            type: raw
            sample: 1000
        description:
            description:
                - Description of the configuration.
            returned: always
            type: str
            sample: Deadlock timeout.
        source:
            description:
                - Source of the configuration.
            returned: always
            type: str
            sample: system-default
'''

from ansible_collections.azure.azcollection.plugins.module_utils.azure_rm_common import AzureRMModuleBase

try:
    from msrestazure.azure_exceptions import CloudError
    from msrestazure.azure_operation import AzureOperationPoller
    from azure.mgmt.rdbms.mysql import MySQLManagementClient
    from msrest.serialization import Model
except ImportError:
    # This is handled in azure_rm_common
    pass


class AzureRMMySqlConfigurationInfo(AzureRMModuleBase):
    def __init__(self):
        # define user inputs into argument
        self.module_arg_spec = dict(
            resource_group=dict(
                type='str',
                required=True
            ),
            server_name=dict(
                type='str',
                required=True
            ),
            name=dict(
                type='str'
            )
        )
        # store the results of the module operation
        self.results = dict(changed=False)
        self.mgmt_client = None
        self.resource_group = None
        self.server_name = None
        self.name = None
        super(AzureRMMySqlConfigurationInfo, self).__init__(self.module_arg_spec, supports_tags=False)

    def exec_module(self, **kwargs):
        is_old_facts = self.module._name == 'azure_rm_mysqlconfiguration_facts'
        if is_old_facts:
            self.module.deprecate("The 'azure_rm_mysqlconfiguration_facts' module has been renamed to 'azure_rm_mysqlconfiguration_info'", version='2.13')

        for key in self.module_arg_spec:
            setattr(self, key, kwargs[key])
        self.mgmt_client = self.get_mgmt_svc_client(MySQLManagementClient,
                                                    base_url=self._cloud_environment.endpoints.resource_manager)

        if self.name is not None:
            self.results['settings'] = self.get()
        else:
            self.results['settings'] = self.list_by_server()
        return self.results

    def get(self):
        '''
        Gets facts of the specified MySQL Configuration.

        :return: deserialized MySQL Configurationinstance state dictionary
        '''
        response = None
        results = []
        try:
            response = self.mgmt_client.configurations.get(resource_group_name=self.resource_group,
                                                           server_name=self.server_name,
                                                           configuration_name=self.name)
            self.log("Response : {0}".format(response))
        except CloudError as e:
            self.log('Could not get facts for Configurations.')

        if response is not None:
            results.append(self.format_item(response))

        return results

    def list_by_server(self):
        '''
        Gets facts of the specified MySQL Configuration.

        :return: deserialized MySQL Configurationinstance state dictionary
        '''
        response = None
        results = []
        try:
            response = self.mgmt_client.configurations.list_by_server(resource_group_name=self.resource_group,
                                                                      server_name=self.server_name)
            self.log("Response : {0}".format(response))
        except CloudError as e:
            self.log('Could not get facts for Configurations.')

        if response is not None:
            for item in response:
                results.append(self.format_item(item))

        return results

    def format_item(self, item):
        d = item.as_dict()
        d = {
            'resource_group': self.resource_group,
            'server_name': self.server_name,
            'id': d['id'],
            'name': d['name'],
            'value': d['value'],
            'description': d['description'],
            'source': d['source']
        }
        return d


def main():
    AzureRMMySqlConfigurationInfo()


if __name__ == '__main__':
    main()
