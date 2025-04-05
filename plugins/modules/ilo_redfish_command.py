#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 Hewlett Packard Enterprise, Inc. All rights reserved.
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: ilo_redfish_command
short_description: Manages Out-Of-Band controllers using Redfish APIs
version_added: 6.6.0
description:
  - Builds Redfish URIs locally and sends them to remote OOB controllers to perform an action.
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
extends_documentation_fragment:
  - community.general.attributes
  - community.general.redfish
options:
  category:
    required: true
    description:
      - Category to execute on OOB controller.
    type: str
    choices: ['Systems']
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
  validate_certs:
    version_added: 10.6.0
  ca_path:
    version_added: 10.6.0
  ciphers:
    version_added: 10.6.0
author:
  - Varni H P (@varini-hp)
"""

EXAMPLES = r"""
- name: Wait for iLO Reboot Completion
  community.general.ilo_redfish_command:
    category: Systems
    command: WaitforiLORebootCompletion
    baseuri: "{{ baseuri }}"
    username: "{{ username }}"
    password: "{{ password }}"
"""

RETURN = r"""
ilo_redfish_command:
  description: Returns the status of the operation performed on the iLO.
  type: dict
  contains:
    WaitforiLORebootCompletion:
      description: Returns the output msg and whether the function executed successfully.
      type: dict
      contains:
        ret:
          description: Return V(true)/V(false) based on whether the operation was performed successfully.
          type: bool
        msg:
          description: Status of the operation performed on the iLO.
          type: str
  returned: always
"""

# More will be added as module features are expanded
CATEGORY_COMMANDS_ALL = {
    "Systems": ["WaitforiLORebootCompletion"]
}

from ansible_collections.community.general.plugins.module_utils.ilo_redfish_utils import iLORedfishUtils
from ansible_collections.community.general.plugins.module_utils.redfish_utils import REDFISH_COMMON_ARGUMENT_SPEC
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native


def main():
    result = {}
    argument_spec = dict(
        category=dict(required=True, choices=list(CATEGORY_COMMANDS_ALL.keys())),
        command=dict(required=True, type='list', elements='str'),
        baseuri=dict(required=True),
        timeout=dict(type="int", default=60),
        username=dict(),
        password=dict(no_log=True),
        auth_token=dict(no_log=True)
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

    timeout = module.params['timeout']

    # Build root URI
    root_uri = "https://" + module.params['baseuri']
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

        result = rf_utils._find_systems_resource()
        if result['ret'] is False:
            module.fail_json(msg=to_native(result['msg']))

        for command in command_list:
            if command == "WaitforiLORebootCompletion":
                result[command] = rf_utils.wait_for_ilo_reboot_completion()

    # Return data back or fail with proper message
    if not result[command]['ret']:
        module.fail_json(msg=result)

    changed = result[command].get('changed', False)
    module.exit_json(ilo_redfish_command=result, changed=changed)


if __name__ == '__main__':
    main()
