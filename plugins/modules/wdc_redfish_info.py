#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2022 Western Digital Corporation
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: wdc_redfish_info
short_description: Manages WDC UltraStar Data102 Out-Of-Band controllers using Redfish APIs
version_added: 5.4.0
description:
  - Builds Redfish URIs locally and sends them to remote OOB controllers to
    get information back.
extends_documentation_fragment:
  - community.general.attributes
  - community.general.attributes.info_module
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
    description:
      - Base URI of OOB controller.  Must include this or I(ioms).
    type: str
  ioms:
    description:
      - List of IOM FQDNs for the enclosure.  Must include this or I(baseuri).
    type: list
    elements: str
  username:
    description:
      - User for authentication with OOB controller.
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

notes:
  - In the inventory, you can specify baseuri or ioms.  See the EXAMPLES section.
  - ioms is a list of FQDNs for the enclosure's IOMs.

author: Mike Moerk (@mikemoerk)
'''

EXAMPLES = '''
- name: Get Simple Update Status with individual IOMs specified
  community.general.wdc_redfish_info:
    category: Update
    command: SimpleUpdateStatus
    ioms:
      - iom1.wdc.com
      - iom2.wdc.com
    username: "{{ username }}"
    password: "{{ password }}"
  register: result

- name: Print fetched information
  ansible.builtin.debug:
    msg: "{{ result.redfish_facts.simple_update_status.entries | to_nice_json }}"

- name: Get Simple Update Status with baseuri specified
  community.general.wdc_redfish_info:
    category: Update
    command: SimpleUpdateStatus
    baseuri: "iom1.wdc.com"
    username: "{{ username }}"
    password: "{{ password }}"
  register: result

- name: Print fetched information
  ansible.builtin.debug:
    msg: "{{ result.redfish_facts.simple_update_status.entries | to_nice_json }}"
'''

RETURN = '''
Description:
    description: Firmware update status description.
    returned: always
    type: str
    sample: Ready for FW update
ErrorCode:
    description: Numeric error code for firmware update status.  Non-zero indicates an error condition.
    returned: always
    type: int
    sample: 0
EstimatedRemainingMinutes:
    description: Estimated number of minutes remaining in firmware update operation.
    returned: always
    type: int
    sample: 20
StatusCode:
    description: Firmware update status code.
    returned: always
    type: int
    sample: 2
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native
from ansible_collections.community.general.plugins.module_utils.wdc_redfish_utils import WdcRedfishUtils

CATEGORY_COMMANDS_ALL = {
    "Update": ["SimpleUpdateStatus"]
}


def main():
    result = {}
    module = AnsibleModule(
        argument_spec=dict(
            category=dict(required=True),
            command=dict(required=True, type='list', elements='str'),
            ioms=dict(type='list', elements='str'),
            baseuri=dict(),
            username=dict(),
            password=dict(no_log=True),
            auth_token=dict(no_log=True),
            timeout=dict(type='int', default=10)
        ),
        required_together=[
            ('username', 'password'),
        ],
        required_one_of=[
            ('username', 'auth_token'),
            ('baseuri', 'ioms')
        ],
        mutually_exclusive=[
            ('username', 'auth_token'),
        ],
        supports_check_mode=True
    )

    category = module.params['category']
    command_list = module.params['command']

    # admin credentials used for authentication
    creds = {'user': module.params['username'],
             'pswd': module.params['password'],
             'token': module.params['auth_token']}

    # timeout
    timeout = module.params['timeout']

    # Check that Category is valid
    if category not in CATEGORY_COMMANDS_ALL:
        module.fail_json(msg=to_native("Invalid Category '%s'. Valid Categories = %s" % (category, sorted(CATEGORY_COMMANDS_ALL.keys()))))

    # Check that all commands are valid
    for cmd in command_list:
        # Fail if even one command given is invalid
        if cmd not in CATEGORY_COMMANDS_ALL[category]:
            module.fail_json(msg=to_native("Invalid Command '%s'. Valid Commands = %s" % (cmd, CATEGORY_COMMANDS_ALL[category])))

    # Build root URI(s)
    if module.params.get("baseuri") is not None:
        root_uris = ["https://" + module.params['baseuri']]
    else:
        root_uris = [
            "https://" + iom for iom in module.params['ioms']
        ]
    rf_utils = WdcRedfishUtils(creds, root_uris, timeout, module,
                               resource_id=None,
                               data_modification=False
                               )

    # Organize by Categories / Commands

    if category == "Update":
        # execute only if we find UpdateService resources
        resource = rf_utils._find_updateservice_resource()
        if resource['ret'] is False:
            module.fail_json(msg=resource['msg'])
        for command in command_list:
            if command == "SimpleUpdateStatus":
                simple_update_status_result = rf_utils.get_simple_update_status()
                if simple_update_status_result['ret'] is False:
                    module.fail_json(msg=to_native(result['msg']))
                else:
                    del simple_update_status_result['ret']
                    result["simple_update_status"] = simple_update_status_result
                    module.exit_json(changed=False, redfish_facts=result)


if __name__ == '__main__':
    main()
