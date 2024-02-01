#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2021-2022 Hewlett Packard Enterprise, Inc. All rights reserved.
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: hpc_update_system_firmware
short_description: Updates CrayXD components using Redfish APIs
version_added: 1.1.0
description:
  - using Redfish URI's updates the CrayXD components from the local HPM file
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
      - Category to Update the components of CrayXD.
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
      - To save the output of the update mention the output file name in csv.
    type: str
    default: update_output.csv
  update_target:
    required: true
    description:
      - To build the Redfish URI and to update that component it is required.
    type: str
    choices: [BMC , BIOS , BIOS2 , MainCPLD , HDDBPPIC , PDBPIC , RT_NVME , RT_OTHER , RT_SA , PDB , UBM6 , SCM_CPLD1_MB_CPLD1 , BPB_CPLD]
  update_image_path_xd295V:
    required: false
    description:
      - To get the path of local HPM file the Image path needs to be mentioned
    type: str
    default: NA
  update_image_path_xd225V:
    required: false
    description:
      - To get the path of local HPM file the Image path needs to be mentioned
    type: str
    default: NA
  update_image_path_xd220V:
    required: false
    description:
      - To get the path of local HPM file the Image path needs to be mentioned
    type: str
    default: NA
  update_image_path_xd665:
    required: false
    description:
      - To get the path of local HPM file the Image path needs to be mentioned
    type: str
    default: NA
  update_image_path_xd670:
    required: false
    description:
      - To get the path of local HPM file the Image path needs to be mentioned
    type: str
    default: NA
  update_image_type:
    required: false
    description:
      - Type of the file that is being uploaded for the update
    default: HPM
    type: str

author:
  - Srujana Yasa (@srujana)
'''

EXAMPLES = r'''
    - name: Running Firmware Update for Cray XD Servers
      hpc_update_system_firmware:
        category: Update
        command: SystemFirmwareUpdate
        baseuri: "baseuri"
        username: "bmc_username"
        password: "bmc_password"
        output_file_name: "output_file_name"
        update_target: "target"
        update_image_path_xd295V: "path"
        update_image_path_xd225V: "path"
        update_image_path_xd220V: "path"
        update_image_path_xd665: "path"
        update_image_path_xd670: "path"
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
    "Update": ["SystemFirmwareUpdate"],
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
            update_image_type=dict(type='str', default='HPM'),
            update_target=dict(required=True, type='str', choices=['BMC', 'BIOS', 'BIOS2', 'MainCPLD',
                                                                   'HDDBPPIC', 'PDBPIC', 'RT_NVME',
                                                                   'RT_OTHER', 'RT_SA', 'PDB', 'UBM6',
                                                                   'SCM_CPLD1_MB_CPLD1', 'BPB_CPLD']),
            update_image_path_xd220V=dict(type='str', default='NA'),
            update_image_path_xd225V=dict(type='str', default='NA'),
            update_image_path_xd295V=dict(type='str', default='NA'),
            update_image_path_xd665=dict(type='str', default='NA'),
            update_image_path_xd670=dict(type='str', default='NA'),
            output_file_name=dict(type='str', default='update_output.csv')
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
    update_uri = "/redfish/v1/UpdateService"
    rf_utils = CrayRedfishUtils(creds, root_uri, timeout, module, data_modification=True)

    # Check that Category is valid
    if category not in category_commands:
        module.fail_json(msg=to_native("Invalid Category '%s'. Valid Categories = %s" % (category, list(category_commands.keys()))))

    # Check that all commands are valid
    for cmd in command_list:
        # Fail if even one command given is invalid
        if cmd not in category_commands[category]:
            module.fail_json(msg=to_native("Invalid Command '%s'. Valid Commands = %s" % (cmd, category_commands[category])))

    if category == "Update":
        for command in command_list:
            if command == "SystemFirmwareUpdate":
                result = rf_utils.system_fw_update({'baseuri': module.params['baseuri'],
                                                    'username': module.params['username'],
                                                    'password': module.params['password'],
                                                    'update_image_type': module.params['update_image_type'],
                                                    'update_target': module.params['update_target'],
                                                    'power_state': module.params['power_state'],
                                                    'update_image_path_xd220V': module.params['update_image_path_xd220V'],
                                                    'update_image_path_xd225V': module.params['update_image_path_xd225V'],
                                                    'update_image_path_xd295V': module.params['update_image_path_xd295V'],
                                                    'update_image_path_xd665': module.params['update_image_path_xd665'],
                                                    'update_image_path_xd670': module.params['update_image_path_xd670'],
                                                    'output_file_name': module.params['output_file_name']})
                if result['ret']:
                    msg = result.get('msg', False)
                    module.exit_json(msg=msg)
                else:
                    module.fail_json(msg=to_native(result))


if __name__ == '__main__':
    main()
