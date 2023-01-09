#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2017-2018 Dell EMC Inc.
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: ilo_redfish_command
short_description: Manages Out-Of-Band controllers using Redfish APIs
version_added: 6.1.0
description:
  - Builds Redfish URIs locally and sends them to remote OOB controllers to
    perform an action.
options:
  category:
    required: true
    description:
      - Category to execute on OOB controller.
    type: str
  command:
    required: true
    description:
      - List of commands to execute on OOB controller
    type: list
    elements: str
  baseuri:
    required: true
    description:
      - Base URI of OOB controller
    type: str
  username:
    required: false
    description:
      - Username for authenticating to iLO.
    type: str
  password:
    required: false
    description:
      - Password for authenticating to iLO.
    type: str
  auth_token:
    required: false
    description:
      - Security token for authenticating to iLO.
    type: str
  timeout:
    required: false
    description:
      - Timeout in seconds for HTTP requests to iLO.
    default: 60
    type: int
  bios_attributes:
    required: false
    description:
      - BIOS attributes that needs to be verified in the given server
    type: dict
  raid_details:
    required: false
    description:
      - List of RAID details that need to be configured in the given server
    type: list
    elements: dict
    suboptions:
      LogicalDriveName:
        required: false
        description:
          - Logical drive name that needs to be configured in the given server
        type: str
      Raid:
        required: false
        description:
          - Type of RAID
        type: str
      DataDrives:
        required: false
        description:
          - Specifies the data drive details like media type, interface type, disk count and size
        type: dict
      DataDriveCount:
        required: false
        description:
          - Number of physical drives that is required to create specified RAID
        type: int
      DataDriveMediaType:
        required: false
        description:
          - Media type of the disk
        type: str
      DataDriveInterfaceType:
        required: false
        description:
          - Interface type of the disk
        type: str
      DataDriveMinimumSizeGiB:
        required: false
        description:
          - Minimum size required in the physical drive
        type: int
  uefi_boot_order:
    required: false
    description:
      - Input UEFI Boot Order
    type: list
    elements: str
  logical_drives_names:
    required: false
    description:
      - List of names of logical drives to be fetched from the given server
    type: list
    elements: str
  cert_file:
    required: false
    description:
      - absolute path to the server cert file
    type: str
  key_file:
    required: false
    description:
      - absolute path to the server key file
    type: str
author:
  - Gayathiri Devi Ramasamy (@Gayathirideviramasamy)
  - T S Kushal (@TSKushal)
  - Varni H P (@varini-hp)
  - Prativa Nayak (@prativa-n)
'''

EXAMPLES = '''
  - name: Verify bios attributes
    community.general.ilo_redfish_command:
      category: Systems
      command: VerifyBiosAttributes
      baseuri: "***.***.***.***"
      username: "abcxyz"
      password: "*****"
      bios_attributes:
        SubNumaClustering: "Disabled"
        WorkloadProfile: "Virtualization-MaxPerformance"

  - name: Verify logical drives
    community.general.ilo_redfish_command:
      category: Systems
      command: VerifyLogicalDrives
      baseuri: "***.***.***.***"
      username: "abcxyz"
      password: "******"
      raid_details:
        - LogicalDriveName: LD1
          Raid: Raid1
          DataDrives:
              DataDriveCount: 2
              DataDriveMediaType: HDD
              DataDriveInterfaceType: SAS
              DataDriveMinimumSizeGiB: 0

  - name: Verify UEFI boot order
    community.general.ilo_redfish_command:
      category: Systems
      command: VerifyUefiBootOrder
      baseuri: "***.***.***.***"
      username: "abcxyz"
      password: "******"
      uefi_boot_order: ["Generic.USB.1.1"]

  - name: Verify specified logical drives
    community.general.ilo_redfish_command:
      category: Systems
      command: VerifySpecifiedLogicalDrives
      baseuri: "***.***.***.***"
      username: "abcxyz"
      password: "******"
      raid_details:
        - LogicalDriveName: LD1
          Raid: Raid1
          DataDrives:
              DataDriveCount: 2
              DataDriveMediaType: HDD
              DataDriveInterfaceType: SAS
              DataDriveMinimumSizeGiB: 0

  - name: Check server reboot status
    community.general.ilo_redfish_command:
      category: Systems
      command: CheckiLORebootStatus
      baseuri: "***.***.***.***"
      username: "abcxyz"
      password: "******"

  - name: Get specified logical drives details
    community.general.ilo_redfish_command:
      category: Systems
      command: GetSpecifiedLogicalDrives
      baseuri: "***.***.***.***"
      username: "abcxyz"
      password: "******"
      logical_drives_names: ["LD1", "LD2"]

'''

RETURN = '''
ilo_redfish_command:
    description: Returns the status of the operation performed on the iLO.
    type: dict
    contains:
        command:
            description: Returns the output msg and whether the function executed successfully.
            type: dict
            contains:
                ret:
                    description: Return True/False based on whether the operation was performed succesfully.
                    type: bool
                msg:
                    description: Status of the operation performed on the iLO.
                    type: dict
    returned: always
'''

HAS_iLO_REDFISH = True

import traceback
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
try:
    from ansible_collections.community.general.plugins.module_utils.ilo_redfish_utils import (
        iLORedfishUtils, ilo_certificate_login
    )
except ImportError as e:
    iLO_REDFISH_IMP_ERR = traceback.format_exc()
    HAS_iLO_REDFISH = False

# More will be added as module features are expanded
CATEGORY_COMMANDS_ALL = {
    "Systems": ["VerifyBiosAttributes", "VerifyLogicalDrives", "VerifyUefiBootOrder",
                "VerifySpecifiedLogicalDrives", "CheckiLORebootStatus", "GetSpecifiedLogicalDrives"]
}


def main():
    result = {}
    module = AnsibleModule(
        argument_spec=dict(
            category=dict(required=True),
            command=dict(required=True, type='list', elements='str'),
            baseuri=dict(required=True),
            timeout=dict(type="int", default=60),
            username=dict(),
            password=dict(no_log=True),
            auth_token=dict(no_log=True),
            bios_attributes=dict(type="dict"),
            raid_details=dict(type="list", elements='dict'),
            uefi_boot_order=dict(type='list', elements='str'),
            logical_drives_names=dict(type='list', elements='str'),
            cert_file=dict(type="str"),
            key_file=dict(type="str")
        ),
        required_together=[
            ("username", "password"),
            ("cert_file", "key_file")
        ],
        required_one_of=[
            ("username", "auth_token", "cert_file"),
        ],
        mutually_exclusive=[
            ("username", "auth_token", "cert_file"),
        ],
        supports_check_mode=False
    )

    if not HAS_iLO_REDFISH:
        module.fail_json(msg="missing required fucntions in ilo_redfish_utils.py")

    category = module.params['category']
    command_list = module.params['command']

    # admin credentials used for authentication
    creds = {'user': module.params['username'],
             'pswd': module.params['password'],
             'token': module.params['auth_token']}

    timeout = module.params['timeout']

    # Build root URI
    root_uri = "https://" + module.params['baseuri']

    if module.params["cert_file"]:
        creds["token"] = ilo_certificate_login(root_uri, module, module.params["cert_file"], module.params["key_file"])

    rf_utils = iLORedfishUtils(creds, root_uri, timeout, module)

    # Check that Category is valid
    if category not in CATEGORY_COMMANDS_ALL:
        module.fail_json(msg=to_native(
            "Invalid Category '%s'. Valid Categories = %s" % (category, list(CATEGORY_COMMANDS_ALL.keys()))))

    # Check that all commands are valid
    for cmd in command_list:
        # Fail if even one command given is invalid
        if cmd not in CATEGORY_COMMANDS_ALL[category]:
            module.fail_json(
                msg=to_native("Invalid Command '%s'. Valid Commands = %s" % (cmd, CATEGORY_COMMANDS_ALL[category])))

    if category == "Systems":
        # execute only if we find a System resource

        result = {}

        for command in command_list:
            result[command] = {}

            res = rf_utils._find_systems_resource()
            if res['ret'] is False:
                result[command] = res
                module.fail_json(msg=to_native(result))

            if command == "VerifyBiosAttributes":
                if not module.params.get("bios_attributes") and module.params.get("bios_attributes") != {}:
                    result[command]['ret'] = False
                    result[command]['msg'] = "bios_attributes params is required"
                    module.fail_json(result)
                result[command] = rf_utils.verify_bios_attributes(module.params["bios_attributes"])
            elif command == "VerifyLogicalDrives":
                if not module.params.get("raid_details") and module.params.get("raid_details") != []:
                    result[command]['ret'] = False
                    result[command]['msg'] = "raid_details params is required"
                    module.fail_json(result)
                result[command] = rf_utils.verify_logical_drives(module.params["raid_details"], True)
            elif command == "VerifySpecifiedLogicalDrives":
                if not module.params.get("raid_details") and module.params.get("raid_details") != []:
                    result[command]['ret'] = False
                    result[command]['msg'] = "raid_details params is required"
                    module.fail_json(result)
                result[command] = rf_utils.verify_logical_drives(module.params["raid_details"], False)
            elif command == "VerifyUefiBootOrder":
                if not module.params["uefi_boot_order"]:
                    result[command]['ret'] = False
                    result[command]['msg'] = "uefi_boot_order params is required"
                    module.fail_json(result)
                result[command] = rf_utils.verify_uefi_boot_order(module.params["uefi_boot_order"])
            elif command == "CheckiLORebootStatus":
                result[command] = rf_utils.check_reboot_status()
            elif command == "GetSpecifiedLogicalDrives":
                if not module.params["logical_drives_names"]:
                    result[command]['ret'] = False
                    result[command]['msg'] = "logical_drives_names params is required"
                    module.fail_json(result)
                result[command] = rf_utils.get_specified_logical_drives(module.params["logical_drives_names"])

    # Return data back or fail with proper message
    if not result[command]['ret']:
        module.fail_json(msg=result)

    changed = result[command].get('changed', False)
    module.exit_json(ilo_redfish_command=result, changed=changed)


if __name__ == '__main__':
    main()
