#!/usr/bin/python
#
# Copyright (c) 2019 Yuwei Zhou, <yuwzho@microsoft.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: azure_rm_iotdevicemodule
short_description: Manage Azure IoT hub device module
description:
    - Create, delete an Azure IoT hub device module.
options:
    hub:
        description:
            - Name of IoT Hub.
        type: str
        required: true
    hub_policy_name:
        description:
            - Policy name of the IoT Hub which will be used to query from IoT hub.
            - This policy should have at least 'Registry Read' access.
        type: str
        required: true
    hub_policy_key:
        description:
            - Key of the I(hub_policy_name).
        type: str
        required: true
    name:
        description:
            - Name of the IoT hub device identity.
        type: str
        required: true
    device:
        description:
            - Device name the module associate with.
        required: true
        type: str
    state:
        description:
            - State of the IoT hub. Use C(present) to create or update an IoT hub device and C(absent) to delete an IoT hub device.
        type: str
        default: present
        choices:
            - absent
            - present
    auth_method:
        description:
            - The authorization type an entity is to be created with.
        type: str
        choices:
            - sas
            - certificate_authority
            - self_signed
        default: sas
    primary_key:
        description:
            - Explicit self-signed certificate thumbprint to use for primary key.
            - Explicit Shared Private Key to use for primary key.
        type: str
        aliases:
            - primary_thumbprint
    secondary_key:
        description:
            - Explicit self-signed certificate thumbprint to use for secondary key.
            - Explicit Shared Private Key to use for secondary key.
        type: str
        aliases:
            - secondary_thumbprint
    twin_tags:
        description:
            - A section that the solution back end can read from and write to.
            - Tags are not visible to device apps.
            - "The tag can be nested dictionary, '.', '$', '#', ' ' is not allowed in the key."
            - List is not supported.
        type: dict
    desired:
        description:
            - Used along with reported properties to synchronize device configuration or conditions.
            - "The tag can be nested dictionary, '.', '$', '#', ' ' is not allowed in the key."
            - List is not supported.
        type: dict

author:
    - Yuwei Zhou (@yuwzho)


extends_documentation_fragment:
- community.general.azure
- community.general.azure_tags
'''

EXAMPLES = '''
- name: Create simplest Azure IoT Hub device module
  azure_rm_iotdevicemodule:
    hub: myHub
    name: Testing
    device: mydevice
    hub_policy_name: iothubowner
    hub_policy_key: "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

- name: Create Azure IoT Edge device module
  azure_rm_iotdevice:
    hub: myHub
    device: mydevice
    name: Testing
    hub_policy_name: iothubowner
    hub_policy_key: "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    edge_enabled: yes

- name: Create Azure IoT Hub device module with module twin properties and tag
  azure_rm_iotdevice:
    hub: myHub
    name: Testing
    device: mydevice
    hub_policy_name: iothubowner
    hub_policy_key: "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    twin_tags:
        location:
            country: US
            city: Redmond
        sensor: humidity
    desired:
        period: 100
'''

RETURN = '''
module:
    description:
        - IoT Hub device.
    returned: always
    type: dict
    sample: {
        "authentication": {
            "symmetricKey": {
                "primaryKey": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                "secondaryKey": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
            },
            "type": "sas",
            "x509Thumbprint": {
                "primaryThumbprint": null,
                "secondaryThumbprint": null
            }
        },
        "cloudToDeviceMessageCount": 0,
        "connectionState": "Disconnected",
        "connectionStateUpdatedTime": "0001-01-01T00:00:00",
        "deviceId": "mydevice",
        "etag": "ODM2NjI3ODg=",
        "generationId": "636904759703045768",
        "lastActivityTime": "0001-01-01T00:00:00",
        "managedBy": null,
        "moduleId": "Testing"
    }
'''  # NOQA

import json
import copy
import re

from ansible_collections.azure.azcollection.plugins.module_utils.azure_rm_common import AzureRMModuleBase, format_resource_id
from ansible.module_utils.common.dict_transformations import _snake_to_camel

try:
    from msrestazure.tools import parse_resource_id
    from msrestazure.azure_exceptions import CloudError
except ImportError:
    # This is handled in azure_rm_common
    pass


class AzureRMIoTDeviceModule(AzureRMModuleBase):

    def __init__(self):

        self.module_arg_spec = dict(
            name=dict(type='str', required=True),
            hub_policy_name=dict(type='str', required=True),
            hub_policy_key=dict(type='str', required=True),
            hub=dict(type='str', required=True),
            device=dict(type='str', required=True),
            state=dict(type='str', default='present', choices=['present', 'absent']),
            twin_tags=dict(type='dict'),
            desired=dict(type='dict'),
            auth_method=dict(type='str', choices=['self_signed', 'sas', 'certificate_authority'], default='sas'),
            primary_key=dict(type='str', no_log=True, aliases=['primary_thumbprint']),
            secondary_key=dict(type='str', no_log=True, aliases=['secondary_thumbprint'])
        )

        self.results = dict(
            changed=False,
            id=None
        )

        self.name = None
        self.hub = None
        self.device = None
        self.hub_policy_key = None
        self.hub_policy_name = None
        self.state = None
        self.twin_tags = None
        self.desired = None
        self.auth_method = None
        self.primary_key = None
        self.secondary_key = None

        required_if = [
            ['auth_method', 'self_signed', ['certificate_authority']]
        ]

        self._base_url = None
        self._mgmt_client = None
        self.query_parameters = {
            'api-version': '2018-06-30'
        }
        self.header_parameters = {
            'Content-Type': 'application/json; charset=utf-8',
            'accept-language': 'en-US'
        }
        super(AzureRMIoTDeviceModule, self).__init__(self.module_arg_spec, supports_check_mode=True, required_if=required_if)

    def exec_module(self, **kwargs):

        for key in self.module_arg_spec.keys():
            setattr(self, key, kwargs[key])

        self._base_url = '{0}.azure-devices.net'.format(self.hub)
        config = {
            'base_url': self._base_url,
            'key': self.hub_policy_key,
            'policy': self.hub_policy_name
        }
        self._mgmt_client = self.get_data_svc_client(**config)

        changed = False

        module = self.get_module()
        if self.state == 'present':
            if not module:
                changed = True
                auth = {'type': _snake_to_camel(self.auth_method)}
                if self.auth_method == 'self_signed':
                    auth['x509Thumbprint'] = {
                        'primaryThumbprint': self.primary_key,
                        'secondaryThumbprint': self.secondary_key
                    }
                elif self.auth_method == 'sas':
                    auth['symmetricKey'] = {
                        'primaryKey': self.primary_key,
                        'secondaryKey': self.secondary_key
                    }
                module = {
                    'deviceId': self.device,
                    'moduleId': self.name,
                    'authentication': auth
                }
            if changed and not self.check_mode:
                module = self.create_or_update_module(module)
            twin = self.get_twin()
            if not twin.get('tags'):
                twin['tags'] = dict()
            twin_change = False
            if self.twin_tags and not self.is_equal(self.twin_tags, twin['tags']):
                twin_change = True
            if self.desired and not self.is_equal(self.desired, twin['properties']['desired']):
                self.module.warn('desired')
                twin_change = True
            if twin_change and not self.check_mode:
                twin = self.update_twin(twin)
            changed = changed or twin_change
            module['tags'] = twin.get('tags') or dict()
            module['properties'] = twin['properties']
        elif module:
            if not self.check_mode:
                self.delete_module(module['etag'])
            changed = True
            module = None
        self.results = module or dict()
        self.results['changed'] = changed
        return self.results

    def is_equal(self, updated, original):
        changed = False
        if not isinstance(updated, dict):
            self.fail('The Property or Tag should be a dict')
        for key in updated.keys():
            if re.search(r'[.|$|#|\s]', key):
                self.fail("Property or Tag name has invalid characters: '.', '$', '#' or ' '. Got '{0}'".format(key))
            original_value = original.get(key)
            updated_value = updated[key]
            if isinstance(updated_value, dict):
                if not isinstance(original_value, dict):
                    changed = True
                    original[key] = updated_value
                elif not self.is_equal(updated_value, original_value):
                    changed = True
            elif original_value != updated_value:
                changed = True
                original[key] = updated_value
        return not changed

    def create_or_update_module(self, module):
        try:
            url = '/devices/{0}/modules/{1}'.format(self.device, self.name)
            headers = copy.copy(self.header_parameters)
            if module.get('etag'):
                headers['If-Match'] = '"{0}"'.format(module['etag'])
            request = self._mgmt_client.put(url, self.query_parameters)
            response = self._mgmt_client.send(request=request, headers=headers, content=module)
            if response.status_code not in [200, 201]:
                raise CloudError(response)
            return json.loads(response.text)
        except Exception as exc:
            self.fail('Error when creating or updating IoT Hub device {0}: {1}'.format(self.name, exc.message or str(exc)))

    def delete_module(self, etag):
        try:
            url = '/devices/{0}/modules/{1}'.format(self.device, self.name)
            headers = copy.copy(self.header_parameters)
            headers['If-Match'] = '"{0}"'.format(etag)
            request = self._mgmt_client.delete(url, self.query_parameters)
            response = self._mgmt_client.send(request=request, headers=headers)
            if response.status_code not in [204]:
                raise CloudError(response)
        except Exception as exc:
            self.fail('Error when deleting IoT Hub device {0}: {1}'.format(self.name, exc.message or str(exc)))

    def get_module(self):
        try:
            url = '/devices/{0}/modules/{1}'.format(self.device, self.name)
            return self._https_get(url, self.query_parameters, self.header_parameters)
        except Exception:
            return None

    def get_twin(self):
        try:
            url = '/twins/{0}/modules/{1}'.format(self.device, self.name)
            return self._https_get(url, self.query_parameters, self.header_parameters)
        except Exception as exc:
            self.fail('Error when getting IoT Hub device {0} module twin {1}: {2}'.format(self.device, self.name, exc.message or str(exc)))

    def update_twin(self, twin):
        try:
            url = '/twins/{0}/modules/{1}'.format(self.device, self.name)
            headers = copy.copy(self.header_parameters)
            headers['If-Match'] = twin['etag']
            request = self._mgmt_client.patch(url, self.query_parameters)
            response = self._mgmt_client.send(request=request, headers=headers, content=twin)
            if response.status_code not in [200]:
                raise CloudError(response)
            return json.loads(response.text)
        except Exception as exc:
            self.fail('Error when creating or updating IoT Hub device {0} module twin {1}: {2}'.format(self.device, self.name, exc.message or str(exc)))

    def _https_get(self, url, query_parameters, header_parameters):
        request = self._mgmt_client.get(url, query_parameters)
        response = self._mgmt_client.send(request=request, headers=header_parameters, content=None)
        if response.status_code not in [200]:
            raise CloudError(response)
        return json.loads(response.text)


def main():
    AzureRMIoTDeviceModule()


if __name__ == '__main__':
    main()
