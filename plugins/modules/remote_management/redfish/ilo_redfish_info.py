#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2021-2022 Hewlett Packard Enterprise, Inc. All rights reserved.
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: ilo_redfish_info
short_description: Gathers server information through iLO using Redfish APIs
description:
  - Builds Redfish URIs locally and sends them to iLO to
    get information back.
  - For use with HPE iLO operations that require Redfish OEM extensions.
options:
  category:
    required: false
    description:
      - List of categories to execute on iLO.
    choices: ['Sessions']
    type: list
    elements: str
  command:
    required: false
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
      - User for authentication with iLO.
    type: str
  password:
    description:
      - Password for authentication with iLO.
    type: str
  auth_token:
    description:
      - Security token for authentication with iLO.
    type: str
    version_added: 2.3.0
  timeout:
    description:
      - Timeout in seconds for URL requests to iLO.
    default: 10
    type: int

requirements:
    - "python >= 3.8"
    - "ansible >= 3.2"
author:
    - "Bhavya B (@bhavya06)"
'''

EXAMPLES = '''
  - name: Get iLO Sessions
    community.general.ilo_redfish_info:
      category: Sessions
      command: GetiLOSessions
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
'''

CATEGORY_COMMANDS_ALL = {
    "Sessions": ["GetiLOSessions"]
}

CATEGORY_COMMANDS_DEFAULT = {}

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
from ansible_collections.community.general.plugins.module_utils.ilo_redfish_utils import iLORedfishUtils


def main():
    result = {}
    category_list = []
    module = AnsibleModule(
        argument_spec=dict(
            category=dict(type='list', default=['Systems']),
            command=dict(type='list'),
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
        supports_check_mode=False
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
                for entry in range(len(CATEGORY_COMMANDS_ALL[category])):
                    command_list.append(CATEGORY_COMMANDS_ALL[category][entry])
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
                result = rf_utils.get_ilo_sessions()

    if result['ret']:
        del result['ret']
        module.exit_json(redfish_info=result)
    else:
        module.fail_json(msg=to_native(result))


if __name__ == '__main__':
    main()
