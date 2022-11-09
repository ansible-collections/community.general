#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2018, Johannes Brunswicker <johannes.brunswicker@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: utm_proxy_location

author:
    - Johannes Brunswicker (@MatrixCrawler)

short_description: Create, update or destroy reverse_proxy location entry in Sophos UTM

description:
    - Create, update or destroy a reverse_proxy location entry in SOPHOS UTM.
    - This module needs to have the REST Ability of the UTM to be activated.


options:
    name:
        type: str
        description:
          - The name of the object. Will be used to identify the entry
        required: true
    access_control:
        description:
          - whether to activate the access control for the location
        type: str
        default: '0'
        choices:
          - '0'
          - '1'
    allowed_networks:
        description:
          - A list of allowed networks
        type: list
        elements: str
        default:
          - REF_NetworkAny
    auth_profile:
        type: str
        description:
          - The reference name of the auth profile
        default: ''
    backend:
        type: list
        elements: str
        description:
          - A list of backends that are connected with this location declaration
        default: []
    be_path:
        type: str
        description:
          - The path of the backend
        default: ''
    comment:
        type: str
        description:
          - The optional comment string
        default: ''
    denied_networks:
        type: list
        elements: str
        description:
          - A list of denied network references
        default: []
    hot_standby:
        description:
          - Activate hot standby mode
        type: bool
        default: false
    path:
        type: str
        description:
          - The path of the location
        default: "/"
    status:
        description:
          - Whether the location is active or not
        type: bool
        default: true
    stickysession_id:
        type: str
        description:
          - The stickysession id
        default: ROUTEID
    stickysession_status:
        description:
          - Enable the stickysession
        type: bool
        default: false
    websocket_passthrough:
        description:
          - Enable the websocket passthrough
        type: bool
        default: false

extends_documentation_fragment:
- community.general.utm

'''

EXAMPLES = """
- name: Create UTM proxy_location
  utm_proxy_backend:
    utm_host: sophos.host.name
    utm_token: abcdefghijklmno1234
    name: TestLocationEntry
    backend: REF_OBJECT_STRING
    state: present

- name: Remove UTM proxy_location
  utm_proxy_backend:
    utm_host: sophos.host.name
    utm_token: abcdefghijklmno1234
    name: TestLocationEntry
    state: absent
"""

RETURN = """
result:
    description: The utm object that was created
    returned: success
    type: complex
    contains:
        _ref:
            description: The reference name of the object
            type: str
        _locked:
            description: Whether or not the object is currently locked
            type: bool
        _type:
            description: The type of the object
            type: str
        name:
            description: The name of the object
            type: str
        access_control:
            description: Whether to use access control state
            type: str
        allowed_networks:
            description: List of allowed network reference names
            type: list
        auth_profile:
            description: The auth profile reference name
            type: str
        backend:
            description: The backend reference name
            type: str
        be_path:
            description: The backend path
            type: str
        comment:
            description: The comment string
            type: str
        denied_networks:
            description: The list of the denied network names
            type: list
        hot_standby:
            description: Use hot standy
            type: bool
        path:
            description: Path name
            type: str
        status:
            description: Whether the object is active or not
            type: bool
        stickysession_id:
            description: The identifier of the stickysession
            type: str
        stickysession_status:
            description: Whether to use stickysession or not
            type: bool
        websocket_passthrough:
            description: Whether websocket passthrough will be used or not
            type: bool
"""

from ansible_collections.community.general.plugins.module_utils.utm_utils import UTM, UTMModule
from ansible.module_utils.common.text.converters import to_native


def main():
    endpoint = "reverse_proxy/location"
    key_to_check_for_changes = ["access_control", "allowed_networks", "auth_profile", "backend", "be_path", "comment",
                                "denied_networks", "hot_standby", "path", "status", "stickysession_id",
                                "stickysession_status", "websocket_passthrough"]
    module = UTMModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            access_control=dict(type='str', required=False, default="0", choices=['0', '1']),
            allowed_networks=dict(type='list', elements='str', required=False, default=['REF_NetworkAny']),
            auth_profile=dict(type='str', required=False, default=""),
            backend=dict(type='list', elements='str', required=False, default=[]),
            be_path=dict(type='str', required=False, default=""),
            comment=dict(type='str', required=False, default=""),
            denied_networks=dict(type='list', elements='str', required=False, default=[]),
            hot_standby=dict(type='bool', required=False, default=False),
            path=dict(type='str', required=False, default="/"),
            status=dict(type='bool', required=False, default=True),
            stickysession_id=dict(type='str', required=False, default='ROUTEID'),
            stickysession_status=dict(type='bool', required=False, default=False),
            websocket_passthrough=dict(type='bool', required=False, default=False),
        )
    )
    try:
        UTM(module, endpoint, key_to_check_for_changes).execute()
    except Exception as e:
        module.fail_json(msg=to_native(e))


if __name__ == '__main__':
    main()
