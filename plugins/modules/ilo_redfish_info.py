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
    description:
      - Username for authenticating to iLO.
    type: str
  password:
    description:
      - Password for authenticating to iLO.
    type: str
  auth_token:
    description:
      - Security token for authenticating to iLO.
    type: str
  timeout:
    description:
      - Timeout in seconds for HTTP requests to iLO.
    default: 10
    type: int
author:
    - "Bhavya B (@bhavya06)"
    - "Gayathiri Devi Ramasamy (@Gayathirideviramasamy)"
'''

EXAMPLES = '''
  - name: Get iLO Sessions
    community.general.ilo_redfish_info:
      category: Sessions
      command: GetiLOSessions
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
    register: result_sessions

  - name: Get SNMP alert destinations
    community.general.ilo_redfish_info:
      category: Manager
      command: GetSnmpAlertDestinations
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"

  - name: Get SNMP V3 Users
    community.general.ilo_redfish_info:
      category: Manager
      command: GetSnmpV3Users
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
'''

RETURN = '''
ilo_redfish_info:
    description: Returns the retrieved information from the iLO.
    type: dict
    contains:
        GetiLOSessions:
            description: Returns the iLO session msg and whether the function executed successfully.
            type: dict
            contains:
                ret:
                    description: Check variable to see if the information was successfully retrieved.
                    type: bool
                msg:
                    description: Information of all active iLO sessions.
                    type: list
                    elements: dict
                    contains:
                        Description:
                            description: Provides a description of the resource.
                            type: str
                        Id:
                            description: The sessionId.
                            type: str
                        Name:
                            description: The name of the resource.
                            type: str
                        UserName:
                            description: Name to use to log in to the management processor.
                            type: str
        GetSNMPv3Users:
            description: Returns the output msg and whether the function executed successfully.
            type: dict
            contains:
                ret:
                    description: Return whether the information was retrieved succesfully.
                    type: bool
                entries:
                    description: List of retieved SNMPv3 Users.
                    type: list
                    elements: dict
        GetSNMPAlertDestinations:
            description: Returns the output msg and whether the function executed successfully.
            type: dict
            contains:
                ret:
                    description: Return whether the information was retrieved succesfully.
                    type: bool
                entries:
                    description: List of retieved SNMP Alert Destinations.
                    type: list
                    elements: dict
    returned: always
'''

CATEGORY_COMMANDS_ALL = {
    "Sessions": ["GetiLOSessions"],
    "Manager": ["GetSNMPv3Users", "GetSNMPAlertDestinations"]
}

CATEGORY_COMMANDS_DEFAULT = {
    "Sessions": "GetiLOSessions",
    "Manager": "GetSNMPv3Users"
}

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.ilo_redfish_utils import iLORedfishUtils


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
            timeout=dict(type='int', default=10)
        ),
        required_together=[
            ('username', 'password'),
        ],
        required_one_of=[
            ('username', 'auth_token'),
        ],
        mutually_exclusive=[
            ('username', 'auth_token'),
        ],
        supports_check_mode=True
    )

    creds = {"user": module.params['username'],
             "pswd": module.params['password'],
             "token": module.params['auth_token']}

    timeout = module.params['timeout']

    root_uri = "https://" + module.params['baseuri']
    rf_utils = iLORedfishUtils(creds, root_uri, timeout, module)

    # Build Category list
    if "all" in module.params['category']:
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

        elif category == "Manager":
            resource = rf_utils._find_managers_resource()
            if resource['ret'] is False:
                module.fail_json(msg=resource['msg'])

            for command in command_list:
                if command == "GetSNMPv3Users":
                    result[command] = rf_utils.get_snmpv3_users()
                elif command == "GetSNMPAlertDestinations":
                    result[command] = rf_utils.get_snmp_alert_destinations()

    module.exit_json(ilo_redfish_info=result)


if __name__ == '__main__':
    main()
