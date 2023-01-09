#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 Hewlett Packard Enterprise, Inc. All rights reserved.
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: ilo_redfish_info
short_description: Gathers server information through iLO using Redfish APIs
version_added: 4.2.0
description:
  - Builds Redfish URIs locally and sends them to iLO to
    get information back.
  - For use with HPE iLO operations that require Redfish OEM extensions.
extends_documentation_fragment:
  - community.general.attributes
  - community.general.attributes.info_module
options:
  category:
    required: true
    description:
      - List of categories to execute on iLO.
    type: list
    elements: str
  command:
    required: true
    description:
      - List of commands to execute on iLO.
    type: list
    elements: str
  baseuri:
    required: true
    description:
      - Base URI of iLO.
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
    version_added: 2.3.0
  timeout:
    required: false
    description:
      - Timeout in seconds for URL requests to iLO.
      - The default value for this param is C(10) but that is being deprecated
        and it will be replaced with C(60) in community.general 8.0.0.
    type: int
  cert_file:
    required: false
    description:
      - absolute path to the server cert file
    type: str
    version_added: 6.1.0
  key_file:
    required: false
    description:
      - absolute path to the server key file
    type: str
    version_added: 6.1.0
author:
  - Bhavya B (@bhavya06)
  - Gayathiri Devi Ramasamy (@Gayathirideviramasamy)
  - T S Kushal (@TSKushal)
  - Varni H P (@varini-hp)
  - Prativa Nayak (@prativa-n)
'''

EXAMPLES = '''
  - name: Get iLO Sessions
    community.general.ilo_redfish_info:
      category: Sessions
      command: GetiLOSessions
      baseuri: "***.***.***.***"
      username: "abcxyz"
      password: "******"

  - name: Get physical drive details
    community.general.ilo_redfish_info:
      category: Systems
      command: GetPhysicalDrives
      baseuri: "***.***.***.***"
      username: "abcxyz"
      password: "******"

  - name: Get logical drive details
    community.general.ilo_redfish_info:
      category: Systems
      command: GetLogicalDrives
      baseuri: "***.***.***.***"
      username: "abcxyz"
      password: "******"

  - name: Get SNMP alert destinations
    community.general.ilo_redfish_info:
      category: Managers
      command: GetSnmpAlertDestinations
      baseuri: "***.***.***.***"
      username: "abcxyz"
      password: "******"

  - name: Get SNMP V3 Users
    community.general.ilo_redfish_info:
      category: Managers
      command: GetSnmpV3Users
      baseuri: "***.***.***.***"
      username: "abcxyz"
      password: "******"

  - name: Get network boot settings
    community.general.ilo_redfish_info:
      category: Systems
      command: GetBootSettings
      baseuri: "***.***.***.***"
      username: "abcxyz"
      password: "******"

  - name: Get service bios attributes
    community.general.ilo_redfish_info:
      category: Systems
      command: GetServiceBiosAttributes
      baseuri: "***.***.***.***"
      username: "abcxyz"
      password: "******"

  - name: Get logical drive details with array controllers
    community.general.ilo_redfish_info:
      category: Systems
      command: GetLogicalDrivesWithArrayControllers
      baseuri: "***.***.***.***"
      username: "abcxyz"
      password: "******"
'''

RETURN = '''
ilo_redfish_info:
    description: Returns the retrieved information from the iLO.
    type: dict
    contains:
        command:
            description: Returns the output msg and whether the function executed successfully.
            type: dict
            contains:
                ret:
                    description: Return whether the information was retrieved succesfully.
                    type: bool
                msg:
                    description: Information of all retrieved details.
                    type: dict
    returned: always
'''

CATEGORY_COMMANDS_ALL = {"Sessions": ["GetiLOSessions"],
                         "Systems": ["GetServiceBiosAttributes", "GetBootSettings", "GetPhysicalDrives",
                                     "GetLogicalDrives", "GetLogicalDrivesWithArrayControllers",
                                     "GetServerPostState", "GetUSBInfo", "GetPCIDevices", "GetPCISlots", "GetNetworkAdapters"],
                         "Managers": ["GetSNMPv3Users", "GetSNMPAlertDestinations", "GetiLOBackupFiles"]}

CATEGORY_COMMANDS_DEFAULT = {"Sessions": "GetiLOSessions"}

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


def main():
    result = {}
    category_list = []
    module = AnsibleModule(
        argument_spec=dict(
            category=dict(required=True, type='list', elements='str'),
            command=dict(required=True, type='list', elements='str'),
            baseuri=dict(required=True),
            username=dict(),
            password=dict(no_log=True),
            auth_token=dict(no_log=True),
            timeout=dict(type='int'),
            cert_file=dict(type='str'),
            key_file=dict(type='str')
        ),
        required_together=[
            ('username', 'password'),
            ('cert_file', 'key_file')
        ],
        required_one_of=[
            ('username', 'auth_token', 'cert_file'),
        ],
        mutually_exclusive=[
            ('username', 'auth_token', 'cert_file'),
        ],
        supports_check_mode=True
    )

    if not HAS_iLO_REDFISH:
        module.fail_json(msg="missing required fucntions in ilo_redfish_utils.py")

    creds = {"user": module.params['username'],
             "pswd": module.params['password'],
             "token": module.params['auth_token']}

    timeout = module.params['timeout']
    if module.params['timeout'] is None:
        timeout = 10
        module.deprecate(
            'The default value {0} for parameter param1 is being deprecated and it will be replaced by {1}'.format(
                10, 60
            ),
            version='8.0.0',
            collection_name='community.general'
        )

    root_uri = "https://" + module.params['baseuri']

    if module.params["cert_file"]:
        creds["token"] = ilo_certificate_login(root_uri, module, module.params["cert_file"], module.params["key_file"])

    rf_utils = iLORedfishUtils(creds, root_uri, timeout, module)

    # Build Category list
    if module.params['category'] == "all":
        for entry in CATEGORY_COMMANDS_ALL:
            category_list.append(entry)
    else:
        # one or more categories specified
        category_list = module.params['category']

    for category in category_list:
        command_list = []
        # Build Command list for each Category
        if category in CATEGORY_COMMANDS_ALL:
            if not module.params['command']:
                # True if we don't specify a command --> use default
                command_list.append(CATEGORY_COMMANDS_DEFAULT[category])
            elif "all" in module.params['command']:
                for entry in CATEGORY_COMMANDS_ALL[category]:
                    command_list.append(entry)
            # one or more commands
            else:
                command_list = module.params['command']
                # Verify that all commands are valid
                for cmd in command_list:
                    # Fail if even one command given is invalid
                    if cmd not in CATEGORY_COMMANDS_ALL[category]:
                        module.fail_json(msg="Invalid Command: %s" % cmd)
        else:
            # Fail if even one category given is invalid
            module.fail_json(msg="Invalid Category: %s" % category)

        # Organize by Categories / Commands
        if category == "Sessions":
            for command in command_list:
                if command == "GetiLOSessions":
                    result[command] = rf_utils.get_ilo_sessions()
        elif category == "Systems":
            for command in command_list:
                if command == "GetServiceBiosAttributes":
                    result[command] = rf_utils.get_service_bios_attributes()
                elif command == "GetBootSettings":
                    result[command] = rf_utils.get_network_boot_settings()
                elif command == "GetPhysicalDrives":
                    result[command] = rf_utils.get_smartstorage_physical_drives()
                elif command == "GetLogicalDrives":
                    result[command] = rf_utils.get_smartstorage_logical_drives()
                elif command == "GetLogicalDrivesWithArrayControllers":
                    result[command] = rf_utils.get_smartstorage_logical_drives(True)
                elif command == "GetServerPostState":
                    result[command] = rf_utils.get_server_poststate()
        elif category == "Managers":
            for command in command_list:
                if command == "GetSNMPv3Users":
                    result[command] = rf_utils.get_snmpv3_users()
                elif command == "GetSNMPAlertDestinations":
                    result[command] = rf_utils.get_snmp_alert_destinations()

    if not result[command]['ret']:
        module.fail_json(msg=to_native(result))

    module.exit_json(ilo_redfish_info=result)


if __name__ == '__main__':
    main()
