#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: xcc_redfish_command
short_description: Manages Lenovo Out-Of-Band controllers using Redfish APIs
version_added: 2.4.0
description:
  - Builds Redfish URIs locally and sends them to remote OOB controllers to perform an action or get information back or update
    a configuration attribute.
  - Manages virtual media.
  - Supports getting information back using GET method.
  - Supports updating a configuration attribute using PATCH method.
  - Supports performing an action using POST method.
extends_documentation_fragment:
  - community.general.attributes
  - community.general.redfish
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options:
  category:
    required: true
    description:
      - Category to execute on OOB controller.
    type: str
  command:
    required: true
    description:
      - List of commands to execute on OOB controller.
    type: list
    elements: str
  baseuri:
    required: true
    description:
      - Base URI of OOB controller.
    type: str
  username:
    description:
      - Username for authentication with OOB controller.
    type: str
  password:
    description:
      - Password for authentication with OOB controller.
    type: str
  auth_token:
    description:
      - Security token for authentication with OOB controller.
    type: str
  timeout:
    description:
      - Timeout in seconds for URL requests to OOB controller.
    default: 10
    type: int
  resource_id:
    required: false
    description:
      - The ID of the System, Manager or Chassis to modify.
    type: str
  virtual_media:
    required: false
    description:
      - The options for VirtualMedia commands.
    type: dict
    suboptions:
      media_types:
        description:
          - The list of media types appropriate for the image.
        type: list
        elements: str
        default: []
      image_url:
        description:
          - The URL of the image to insert or eject.
        type: str
      inserted:
        description:
          - Indicates if the image is treated as inserted on command completion.
        type: bool
        default: true
      write_protected:
        description:
          - Indicates if the media is treated as write-protected.
        type: bool
        default: true
      username:
        description:
          - The username for accessing the image URL.
        type: str
      password:
        description:
          - The password for accessing the image URL.
        type: str
      transfer_protocol_type:
        description:
          - The network protocol to use with the image.
        type: str
      transfer_method:
        description:
          - The transfer method to use with the image.
        type: str
  resource_uri:
    required: false
    description:
      - The resource URI to get or patch or post.
    type: str
  request_body:
    required: false
    description:
      - The request body to patch or post.
    type: dict
  validate_certs:
    version_added: 10.6.0
  ca_path:
    version_added: 10.6.0
  ciphers:
    version_added: 10.6.0

author: "Yuyan Pan (@panyy3)"
"""

EXAMPLES = r"""
- name: Insert Virtual Media
  community.general.xcc_redfish_command:
    category: Manager
    command: VirtualMediaInsert
    baseuri: "{{ baseuri }}"
    username: "{{ username }}"
    password: "{{ password }}"
    virtual_media:
      image_url: "http://example.com/images/SomeLinux-current.iso"
      media_types:
        - CD
        - DVD
    resource_id: "1"

- name: Eject Virtual Media
  community.general.xcc_redfish_command:
    category: Manager
    command: VirtualMediaEject
    baseuri: "{{ baseuri }}"
    username: "{{ username }}"
    password: "{{ password }}"
    virtual_media:
      image_url: "http://example.com/images/SomeLinux-current.iso"
    resource_id: "1"

- name: Eject all Virtual Media
  community.general.xcc_redfish_command:
    category: Manager
    command: VirtualMediaEject
    baseuri: "{{ baseuri }}"
    username: "{{ username }}"
    password: "{{ password }}"
    resource_id: "1"

- name: Get ComputeSystem Oem property SystemStatus via GetResource command
  community.general.xcc_redfish_command:
    category: Raw
    command: GetResource
    baseuri: "{{ baseuri }}"
    username: "{{ username }}"
    password: "{{ password }}"
    resource_uri: "/redfish/v1/Systems/1"
  register: result
- ansible.builtin.debug:
    msg: "{{ result.redfish_facts.data.Oem.Lenovo.SystemStatus }}"

- name: Get Oem DNS setting via GetResource command
  community.general.xcc_redfish_command:
    category: Raw
    command: GetResource
    baseuri: "{{ baseuri }}"
    username: "{{ username }}"
    password: "{{ password }}"
    resource_uri: "/redfish/v1/Managers/1/NetworkProtocol/Oem/Lenovo/DNS"
  register: result

- name: Print fetched information
  ansible.builtin.debug:
    msg: "{{ result.redfish_facts.data }}"

- name: Get Lenovo FoD key collection resource via GetCollectionResource command
  community.general.xcc_redfish_command:
    category: Raw
    command: GetCollectionResource
    baseuri: "{{ baseuri }}"
    username: "{{ username }}"
    password: "{{ password }}"
    resource_uri: "/redfish/v1/Managers/1/Oem/Lenovo/FoD/Keys"
  register: result

- name: Print fetched information
  ansible.builtin.debug:
    msg: "{{ result.redfish_facts.data_list }}"

- name: Update ComputeSystem property AssetTag via PatchResource command
  community.general.xcc_redfish_command:
    category: Raw
    command: PatchResource
    baseuri: "{{ baseuri }}"
    username: "{{ username }}"
    password: "{{ password }}"
    resource_uri: "/redfish/v1/Systems/1"
    request_body:
      AssetTag: "new_asset_tag"

- name: Perform BootToBIOSSetup action via PostResource command
  community.general.xcc_redfish_command:
    category: Raw
    command: PostResource
    baseuri: "{{ baseuri }}"
    username: "{{ username }}"
    password: "{{ password }}"
    resource_uri: "/redfish/v1/Systems/1/Actions/Oem/LenovoComputerSystem.BootToBIOSSetup"
    request_body: {}

- name: Perform SecureBoot.ResetKeys action via PostResource command
  community.general.xcc_redfish_command:
    category: Raw
    command: PostResource
    baseuri: "{{ baseuri }}"
    username: "{{ username }}"
    password: "{{ password }}"
    resource_uri: "/redfish/v1/Systems/1/SecureBoot/Actions/SecureBoot.ResetKeys"
    request_body:
      ResetKeysType: DeleteAllKeys

- name: Create session
  community.general.redfish_command:
    category: Sessions
    command: CreateSession
    baseuri: "{{ baseuri }}"
    username: "{{ username }}"
    password: "{{ password }}"
  register: result

- name: Update Manager DateTimeLocalOffset property using security token for auth
  community.general.xcc_redfish_command:
    category: Raw
    command: PatchResource
    baseuri: "{{ baseuri }}"
    auth_token: "{{ result.session.token }}"
    resource_uri: "/redfish/v1/Managers/1"
    request_body:
      DateTimeLocalOffset: "+08:00"

- name: Delete session using security token created by CreateSesssion above
  community.general.redfish_command:
    category: Sessions
    command: DeleteSession
    baseuri: "{{ baseuri }}"
    auth_token: "{{ result.session.token }}"
    session_uri: "{{ result.session.uri }}"
"""

RETURN = r"""
msg:
  description: A message related to the performed action(s).
  returned: when failure or action/update success
  type: str
  sample: "Action was successful"
redfish_facts:
  description: Resource content.
  returned: when command == GetResource or command == GetCollectionResource
  type: dict
  sample:
    {
      "redfish_facts": {
        "data": {
          "@odata.etag": "\"3179bf00d69f25a8b3c\"",
          "@odata.id": "/redfish/v1/Managers/1/NetworkProtocol/Oem/Lenovo/DNS",
          "@odata.type": "#LenovoDNS.v1_0_0.LenovoDNS",
          "DDNS": [
            {
              "DDNSEnable": true,
              "DomainName": "",
              "DomainNameSource": "DHCP"
            }
          ],
          "DNSEnable": true,
          "Description": "This resource is used to represent a DNS resource for a Redfish implementation.",
          "IPv4Address1": "10.103.62.178",
          "IPv4Address2": "0.0.0.0",
          "IPv4Address3": "0.0.0.0",
          "IPv6Address1": "::",
          "IPv6Address2": "::",
          "IPv6Address3": "::",
          "Id": "LenovoDNS",
          "PreferredAddresstype": "IPv4"
        },
        "ret": true
      }
    }
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native
from ansible_collections.community.general.plugins.module_utils.redfish_utils import RedfishUtils, REDFISH_COMMON_ARGUMENT_SPEC


class XCCRedfishUtils(RedfishUtils):
    @staticmethod
    def _find_empty_virt_media_slot(resources, media_types,
                                    media_match_strict=True):
        for uri, data in resources.items():
            # check MediaTypes
            if 'MediaTypes' in data and media_types:
                if not set(media_types).intersection(set(data['MediaTypes'])):
                    continue
            else:
                if media_match_strict:
                    continue
            if 'RDOC' in uri:
                continue
            if 'Remote' in uri:
                continue
            # if ejected, 'Inserted' should be False and 'ImageName' cleared
            if (not data.get('Inserted', False) and
                    not data.get('ImageName')):
                return uri, data
        return None, None

    def virtual_media_eject_one(self, image_url):
        # read the VirtualMedia resources from systems
        response = self.get_request(self.root_uri + self.systems_uri)
        if response['ret'] is False:
            return response
        data = response['data']
        if 'VirtualMedia' not in data:
            # read the VirtualMedia resources from manager
            response = self.get_request(self.root_uri + self.manager_uri)
            if response['ret'] is False:
                return response
            data = response['data']
            if 'VirtualMedia' not in data:
                return {'ret': False, 'msg': "VirtualMedia resource not found"}
        virt_media_uri = data["VirtualMedia"]["@odata.id"]
        response = self.get_request(self.root_uri + virt_media_uri)
        if response['ret'] is False:
            return response
        data = response['data']
        virt_media_list = []
        for member in data[u'Members']:
            virt_media_list.append(member[u'@odata.id'])
        resources, headers = self._read_virt_media_resources(virt_media_list)

        # find the VirtualMedia resource to eject
        uri, data, eject = self._find_virt_media_to_eject(resources, image_url)
        if uri and eject:
            if ('Actions' not in data or
                    '#VirtualMedia.EjectMedia' not in data['Actions']):
                # try to eject via PATCH if no EjectMedia action found
                h = headers[uri]
                if 'allow' in h:
                    methods = [m.strip() for m in h.get('allow').split(',')]
                    if 'PATCH' not in methods:
                        # if Allow header present and PATCH missing, return error
                        return {'ret': False,
                                'msg': "%s action not found and PATCH not allowed"
                                       % '#VirtualMedia.EjectMedia'}
                return self.virtual_media_eject_via_patch(uri)
            else:
                # POST to the EjectMedia Action
                action = data['Actions']['#VirtualMedia.EjectMedia']
                if 'target' not in action:
                    return {'ret': False,
                            'msg': "target URI property missing from Action "
                                   "#VirtualMedia.EjectMedia"}
                action_uri = action['target']
                # empty payload for Eject action
                payload = {}
                # POST to action
                response = self.post_request(self.root_uri + action_uri,
                                             payload)
                if response['ret'] is False:
                    return response
                return {'ret': True, 'changed': True,
                        'msg': "VirtualMedia ejected"}
        elif uri and not eject:
            # already ejected: return success but changed=False
            return {'ret': True, 'changed': False,
                    'msg': "VirtualMedia image '%s' already ejected" %
                           image_url}
        else:
            # return failure (no resources matching image_url found)
            return {'ret': False, 'changed': False,
                    'msg': "No VirtualMedia resource found with image '%s' "
                           "inserted" % image_url}

    def virtual_media_eject(self, options):
        if options:
            image_url = options.get('image_url')
            if image_url:  # eject specified one media
                return self.virtual_media_eject_one(image_url)

        # eject all inserted media when no image_url specified
        # read the VirtualMedia resources from systems
        response = self.get_request(self.root_uri + self.systems_uri)
        if response['ret'] is False:
            return response
        data = response['data']
        if 'VirtualMedia' not in data:
            # read the VirtualMedia resources from manager
            response = self.get_request(self.root_uri + self.manager_uri)
            if response['ret'] is False:
                return response
            data = response['data']
            if 'VirtualMedia' not in data:
                return {'ret': False, 'msg': "VirtualMedia resource not found"}
        # read all the VirtualMedia resources
        virt_media_uri = data["VirtualMedia"]["@odata.id"]
        response = self.get_request(self.root_uri + virt_media_uri)
        if response['ret'] is False:
            return response
        data = response['data']
        virt_media_list = []
        for member in data[u'Members']:
            virt_media_list.append(member[u'@odata.id'])
        resources, headers = self._read_virt_media_resources(virt_media_list)

        # eject all inserted media one by one
        ejected_media_list = []
        for uri, data in resources.items():
            if data.get('Image') and data.get('Inserted', True):
                returndict = self.virtual_media_eject_one(data.get('Image'))
                if not returndict['ret']:
                    return returndict
                ejected_media_list.append(data.get('Image'))

        if len(ejected_media_list) == 0:
            # no media inserted: return success but changed=False
            return {'ret': True, 'changed': False,
                    'msg': "No VirtualMedia image inserted"}
        else:
            return {'ret': True, 'changed': True,
                    'msg': "VirtualMedia %s ejected" % str(ejected_media_list)}

    def virtual_media_insert(self, options):
        param_map = {
            'Inserted': 'inserted',
            'WriteProtected': 'write_protected',
            'UserName': 'username',
            'Password': 'password',
            'TransferProtocolType': 'transfer_protocol_type',
            'TransferMethod': 'transfer_method'
        }
        image_url = options.get('image_url')
        if not image_url:
            return {'ret': False,
                    'msg': "image_url option required for VirtualMediaInsert"}
        media_types = options.get('media_types')

        # read the VirtualMedia resources from systems
        response = self.get_request(self.root_uri + self.systems_uri)
        if response['ret'] is False:
            return response
        data = response['data']
        if 'VirtualMedia' not in data:
            # read the VirtualMedia resources from manager
            response = self.get_request(self.root_uri + self.manager_uri)
            if response['ret'] is False:
                return response
            data = response['data']
            if 'VirtualMedia' not in data:
                return {'ret': False, 'msg': "VirtualMedia resource not found"}
        virt_media_uri = data["VirtualMedia"]["@odata.id"]
        response = self.get_request(self.root_uri + virt_media_uri)
        if response['ret'] is False:
            return response
        data = response['data']
        virt_media_list = []
        for member in data[u'Members']:
            virt_media_list.append(member[u'@odata.id'])
        resources, headers = self._read_virt_media_resources(virt_media_list)

        # see if image already inserted; if so, nothing to do
        if self._virt_media_image_inserted(resources, image_url):
            return {'ret': True, 'changed': False,
                    'msg': "VirtualMedia '%s' already inserted" % image_url}

        # find an empty slot to insert the media
        # try first with strict media_type matching
        uri, data = self._find_empty_virt_media_slot(
            resources, media_types, media_match_strict=True)
        if not uri:
            # if not found, try without strict media_type matching
            uri, data = self._find_empty_virt_media_slot(
                resources, media_types, media_match_strict=False)
        if not uri:
            return {'ret': False,
                    'msg': "Unable to find an available VirtualMedia resource "
                           "%s" % ('supporting ' + str(media_types)
                                   if media_types else '')}

        # confirm InsertMedia action found
        if ('Actions' not in data or
                '#VirtualMedia.InsertMedia' not in data['Actions']):
            # try to insert via PATCH if no InsertMedia action found
            h = headers[uri]
            if 'allow' in h:
                methods = [m.strip() for m in h.get('allow').split(',')]
                if 'PATCH' not in methods:
                    # if Allow header present and PATCH missing, return error
                    return {'ret': False,
                            'msg': "%s action not found and PATCH not allowed"
                            % '#VirtualMedia.InsertMedia'}
            return self.virtual_media_insert_via_patch(options, param_map,
                                                       uri, data)

        # get the action property
        action = data['Actions']['#VirtualMedia.InsertMedia']
        if 'target' not in action:
            return {'ret': False,
                    'msg': "target URI missing from Action "
                           "#VirtualMedia.InsertMedia"}
        action_uri = action['target']
        # get ActionInfo or AllowableValues
        ai = self._get_all_action_info_values(action)
        # construct payload
        payload = self._insert_virt_media_payload(options, param_map, data, ai)
        # POST to action
        response = self.post_request(self.root_uri + action_uri, payload)
        if response['ret'] is False:
            return response
        return {'ret': True, 'changed': True, 'msg': "VirtualMedia inserted"}

    def raw_get_resource(self, resource_uri):
        if resource_uri is None:
            return {'ret': False, 'msg': "resource_uri is missing"}
        response = self.get_request(self.root_uri + resource_uri)
        if response['ret'] is False:
            return response
        data = response['data']
        return {'ret': True, 'data': data}

    def raw_get_collection_resource(self, resource_uri):
        if resource_uri is None:
            return {'ret': False, 'msg': "resource_uri is missing"}
        response = self.get_request(self.root_uri + resource_uri)
        if response['ret'] is False:
            return response
        if 'Members' not in response['data']:
            return {'ret': False, 'msg': "Specified resource_uri doesn't have Members property"}
        member_list = [i['@odata.id'] for i in response['data'].get('Members', [])]

        # get member resource one by one
        data_list = []
        for member_uri in member_list:
            uri = self.root_uri + member_uri
            response = self.get_request(uri)
            if response['ret'] is False:
                return response
            data = response['data']
            data_list.append(data)

        return {'ret': True, 'data_list': data_list}

    def raw_patch_resource(self, resource_uri, request_body):
        if resource_uri is None:
            return {'ret': False, 'msg': "resource_uri is missing"}
        if request_body is None:
            return {'ret': False, 'msg': "request_body is missing"}
        # check whether resource_uri existing or not
        response = self.get_request(self.root_uri + resource_uri)
        if response['ret'] is False:
            return response
        original_etag = response['data']['@odata.etag']

        # check validity of keys in request_body
        data = response['data']
        for key in request_body.keys():
            if key not in data:
                return {'ret': False, 'msg': "Key %s not found. Supported key list: %s" % (key, str(data.keys()))}

        # perform patch
        response = self.patch_request(self.root_uri + resource_uri, request_body)
        if response['ret'] is False:
            return response

        # check whether changed or not
        current_etag = ''
        if 'data' in response and '@odata.etag' in response['data']:
            current_etag = response['data']['@odata.etag']
        if current_etag != original_etag:
            return {'ret': True, 'changed': True}
        else:
            return {'ret': True, 'changed': False}

    def raw_post_resource(self, resource_uri, request_body):
        if resource_uri is None:
            return {'ret': False, 'msg': "resource_uri is missing"}
        resource_uri_has_actions = True
        if '/Actions/' not in resource_uri:
            resource_uri_has_actions = False
        if request_body is None:
            return {'ret': False, 'msg': "request_body is missing"}
        # get action base uri data for further checking
        action_base_uri = resource_uri.split('/Actions/')[0]
        response = self.get_request(self.root_uri + action_base_uri)
        if response['ret'] is False:
            return response
        if 'Actions' not in response['data']:
            if resource_uri_has_actions:
                return {'ret': False, 'msg': "Actions property not found in %s" % action_base_uri}
            else:
                response['data']['Actions'] = {}

        # check resouce_uri with target uri found in action base uri data
        action_found = False
        action_info_uri = None
        action_target_uri_list = []
        for key in response['data']['Actions'].keys():
            if action_found:
                break
            if not key.startswith('#'):
                continue
            if 'target' in response['data']['Actions'][key]:
                if resource_uri == response['data']['Actions'][key]['target']:
                    action_found = True
                    if '@Redfish.ActionInfo' in response['data']['Actions'][key]:
                        action_info_uri = response['data']['Actions'][key]['@Redfish.ActionInfo']
                else:
                    action_target_uri_list.append(response['data']['Actions'][key]['target'])
        if not action_found and 'Oem' in response['data']['Actions']:
            for key in response['data']['Actions']['Oem'].keys():
                if action_found:
                    break
                if not key.startswith('#'):
                    continue
                if 'target' in response['data']['Actions']['Oem'][key]:
                    if resource_uri == response['data']['Actions']['Oem'][key]['target']:
                        action_found = True
                        if '@Redfish.ActionInfo' in response['data']['Actions']['Oem'][key]:
                            action_info_uri = response['data']['Actions']['Oem'][key]['@Redfish.ActionInfo']
                    else:
                        action_target_uri_list.append(response['data']['Actions']['Oem'][key]['target'])

        if not action_found and resource_uri_has_actions:
            return {'ret': False,
                    'msg': 'Specified resource_uri is not a supported action target uri, please specify a supported target uri instead. Supported uri: %s'
                    % (str(action_target_uri_list))}

        # check request_body with parameter name defined by @Redfish.ActionInfo
        if action_info_uri is not None:
            response = self.get_request(self.root_uri + action_info_uri)
            if response['ret'] is False:
                return response
            for key in request_body.keys():
                key_found = False
                for para in response['data']['Parameters']:
                    if key == para['Name']:
                        key_found = True
                        break
                if not key_found:
                    return {'ret': False,
                            'msg': 'Invalid property %s found in request_body. Please refer to @Redfish.ActionInfo Parameters: %s'
                            % (key, str(response['data']['Parameters']))}

        # perform post
        response = self.post_request(self.root_uri + resource_uri, request_body)
        if response['ret'] is False:
            return response
        return {'ret': True, 'changed': True}


# More will be added as module features are expanded
CATEGORY_COMMANDS_ALL = {
    "Manager": ["VirtualMediaInsert",
                "VirtualMediaEject"],
    "Raw": ["GetResource",
            "GetCollectionResource",
            "PatchResource",
            "PostResource"]
}


def main():
    result = {}
    argument_spec = dict(
        category=dict(required=True),
        command=dict(required=True, type='list', elements='str'),
        baseuri=dict(required=True),
        username=dict(),
        password=dict(no_log=True),
        auth_token=dict(no_log=True),
        timeout=dict(type='int', default=10),
        resource_id=dict(),
        virtual_media=dict(
            type='dict',
            options=dict(
                media_types=dict(type='list', elements='str', default=[]),
                image_url=dict(),
                inserted=dict(type='bool', default=True),
                write_protected=dict(type='bool', default=True),
                username=dict(),
                password=dict(no_log=True),
                transfer_protocol_type=dict(),
                transfer_method=dict(),
            )
        ),
        resource_uri=dict(),
        request_body=dict(
            type='dict',
        ),
    )
    argument_spec.update(REDFISH_COMMON_ARGUMENT_SPEC)
    module = AnsibleModule(
        argument_spec,
        required_together=[
            ('username', 'password'),
        ],
        required_one_of=[
            ('username', 'auth_token'),
        ],
        mutually_exclusive=[
            ('username', 'auth_token'),
        ],
        supports_check_mode=False
    )

    category = module.params['category']
    command_list = module.params['command']

    # admin credentials used for authentication
    creds = {'user': module.params['username'],
             'pswd': module.params['password'],
             'token': module.params['auth_token']}

    # timeout
    timeout = module.params['timeout']

    # System, Manager or Chassis ID to modify
    resource_id = module.params['resource_id']

    # VirtualMedia options
    virtual_media = module.params['virtual_media']

    # resource_uri
    resource_uri = module.params['resource_uri']

    # request_body
    request_body = module.params['request_body']

    # Build root URI
    root_uri = "https://" + module.params['baseuri']
    rf_utils = XCCRedfishUtils(creds, root_uri, timeout, module, resource_id=resource_id, data_modification=True)

    # Check that Category is valid
    if category not in CATEGORY_COMMANDS_ALL:
        module.fail_json(msg=to_native("Invalid Category '%s'. Valid Categories = %s" % (category, CATEGORY_COMMANDS_ALL.keys())))

    # Check that all commands are valid
    for cmd in command_list:
        # Fail if even one command given is invalid
        if cmd not in CATEGORY_COMMANDS_ALL[category]:
            module.fail_json(msg=to_native("Invalid Command '%s'. Valid Commands = %s" % (cmd, CATEGORY_COMMANDS_ALL[category])))

    # Organize by Categories / Commands
    if category == "Manager":
        # For virtual media resource locates on Systems service
        result = rf_utils._find_systems_resource()
        if result['ret'] is False:
            module.fail_json(msg=to_native(result['msg']))
        # For virtual media resource locates on Managers service
        result = rf_utils._find_managers_resource()
        if result['ret'] is False:
            module.fail_json(msg=to_native(result['msg']))

        for command in command_list:
            if command == 'VirtualMediaInsert':
                result = rf_utils.virtual_media_insert(virtual_media)
            elif command == 'VirtualMediaEject':
                result = rf_utils.virtual_media_eject(virtual_media)
    elif category == "Raw":
        for command in command_list:
            if command == 'GetResource':
                result = rf_utils.raw_get_resource(resource_uri)
            elif command == 'GetCollectionResource':
                result = rf_utils.raw_get_collection_resource(resource_uri)
            elif command == 'PatchResource':
                result = rf_utils.raw_patch_resource(resource_uri, request_body)
            elif command == 'PostResource':
                result = rf_utils.raw_post_resource(resource_uri, request_body)

    # Return data back or fail with proper message
    if result['ret'] is True:
        if command == 'GetResource' or command == 'GetCollectionResource':
            module.exit_json(redfish_facts=result)
        else:
            changed = result.get('changed', True)
            msg = result.get('msg', 'Action was successful')
            module.exit_json(changed=changed, msg=msg)
    else:
        module.fail_json(msg=to_native(result['msg']))


if __name__ == '__main__':
    main()
