#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2021-2022 Hewlett Packard Enterprise, Inc. All rights reserved.
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: hpc_get_system_fw_inv
short_description: Inventory Information of CrayXD components using Redfish APIs
version_added: 1.1.0
description:
  - using Redfish URI's Fetch the CrayXD components Inventory Information
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
extends_documentation_fragment:
  - community.general.attributes
options:
  category:
    required: true
    description:
      - Category to Get Inventory of the CrayXD components.
    type: str
  command:
    required: true
    description:
      - List of commands to execute on the CrayXD.
    type: list
    elements: str
  baseuri:
    required: true
    description:
      - Base URI of OOB controller.
    type: str
  username:
    required: true
    description:
      - Username for authenticating to CrayXD.
    type: str
  password:
    required: true
    description:
      - Password for authenticating to CrayXD.
    type: str
  auth_token:
    required: false
    description:
      - Security token for authenticating to CrayXD.
    type: str
  timeout:
    required: false
    description:
      - Timeout in seconds for HTTP requests to CrayXD.
    default: 300
    type: int
  output_file_name:
    required: false
    description:
      - To save the output of the Inventory, mention the output file name in csv.
    default: get_output.csv
    type: str


author:
  - Srujana Yasa (@srujana)
'''

EXAMPLES = r'''
  - name: Fetching System Firmware Inventory Details
    hpc_get_system_fw_inv:
      category: GetInventory
      command: GetSystemFWInventory
      baseuri: "baseuri"
      username: "bmc_username"
      password: "bmc_password"
      output_file_name: "output_file.csv"
'''

RETURN = r'''
csv:
  description: Output of this Task is saved to a csv file.
  returned: Returned an output file containing the details of update.
  type: str
  sample: Output_file.csv
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.hpc_system_firmware_utils import CrayRedfishUtils
from ansible.module_utils.common.text.converters import to_native


category_commands = {
    "GetInventory": ["GetSystemFWInventory"],
}


def main():
    result = {}
    return_values = {}
    module = AnsibleModule(
        argument_spec=dict(
            category=dict(required=True),
            command=dict(required=True, type='list', elements='str'),
            baseuri=dict(required=True),
            username=dict(required=True),
            password=dict(no_log=True, required=True),
            auth_token=dict(no_log=True),
            timeout=dict(type='int', default=300),
            output_file_name=dict(type='str', default='get_output.csv'),
        ),
        supports_check_mode=False
    )

    category = module.params['category']
    command_list = module.params['command']

    # admin credentials used for authentication
    creds = {'user': module.params['username'],
             'pswd': module.params['password'],
             'token': module.params['auth_token']}

    timeout = module.params['timeout']
    # Build root URI
    root_uri = "https://" + module.params['baseuri']
    # update_uri = "/redfish/v1/UpdateService"
    rf_utils = CrayRedfishUtils(creds, root_uri, timeout, module, data_modification=True)

    # Check that Category is valid
    if category not in category_commands:
        module.fail_json(msg=to_native("Invalid Category '%s'. Valid Categories = %s" % (category, list(category_commands.keys()))))

    # Check that all commands are valid
    for cmd in command_list:
        # Fail if even one command given is invalid
        if cmd not in category_commands[category]:
            module.fail_json(msg=to_native("Invalid Command '%s'. Valid Commands = %s" % (cmd, category_commands[category])))

    if category == "GetInventory":
        for command in command_list:
            if command == "GetSystemFWInventory":
                result = rf_utils.get_sys_fw_inventory({'baseuri': module.params['baseuri'],
                                                        'username': module.params['username'],
                                                        'password': module.params['password'],
                                                        'output_file_name': module.params['output_file_name']})
                if result['ret']:
                    msg = result.get('msg', False)
                    module.exit_json(msg=msg)
                else:
                    module.fail_json(msg=to_native(result))


if __name__ == '__main__':
    main()
