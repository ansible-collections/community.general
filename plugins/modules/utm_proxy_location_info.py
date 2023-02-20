#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2018, Johannes Brunswicker <johannes.brunswicker@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: utm_proxy_location_info

author:
    - Johannes Brunswicker (@MatrixCrawler)

short_description: Create, update or destroy reverse_proxy location entry in Sophos UTM

description:
    - Create, update or destroy a reverse_proxy location entry in SOPHOS UTM.
    - This module needs to have the REST Ability of the UTM to be activated.

attributes:
    check_mode:
        version_added: 3.3.0
        # This was backported to 2.5.4 and 1.3.11 as well, since this was a bugfix

options:
    name:
        type: str
        description:
          - The name of the object. Will be used to identify the entry
        required: true

extends_documentation_fragment:
    - community.general.utm
    - community.general.attributes
    - community.general.attributes.info_module
'''

EXAMPLES = """
- name: Remove UTM proxy_location
  community.general.utm_proxy_location_info:
    utm_host: sophos.host.name
    utm_token: abcdefghijklmno1234
    name: TestLocationEntry
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
    key_to_check_for_changes = []
    module = UTMModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
        ),
        supports_check_mode=True,
    )
    try:
        UTM(module, endpoint, key_to_check_for_changes, info_only=True).execute()
    except Exception as e:
        module.fail_json(msg=to_native(e))


if __name__ == '__main__':
    main()
