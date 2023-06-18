#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2022 Western Digital Corporation
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: wdc_redfish_command
short_description: Manages WDC UltraStar Data102 Out-Of-Band controllers using Redfish APIs
version_added: 5.4.0
description:
  - Builds Redfish URIs locally and sends them to remote OOB controllers to
    perform an action.
  - Manages OOB controller firmware. For example, Firmware Activate, Update and Activate.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
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
      - Base URI of OOB controller.  Must include this or O(ioms).
    type: str
  ioms:
    description:
      - List of IOM FQDNs for the enclosure.  Must include this or O(baseuri).
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
  resource_id:
    required: false
    description:
      - ID of the component to modify, such as V(Enclosure), V(IOModuleAFRU), V(PowerSupplyBFRU), V(FanExternalFRU3), or V(FanInternalFRU).
    type: str
    version_added: 5.4.0
  update_image_uri:
    required: false
    description:
      - The URI of the image for the update.
    type: str
  update_creds:
    required: false
    description:
      - The credentials for retrieving the update image.
    type: dict
    suboptions:
      username:
        required: false
        description:
          - The username for retrieving the update image.
        type: str
      password:
        required: false
        description:
          - The password for retrieving the update image.
        type: str
notes:
  - In the inventory, you can specify baseuri or ioms.  See the EXAMPLES section.
  - ioms is a list of FQDNs for the enclosure's IOMs.


author: Mike Moerk (@mikemoerk)
'''

EXAMPLES = '''
- name: Firmware Activate (required after SimpleUpdate to apply the new firmware)
  community.general.wdc_redfish_command:
    category: Update
    command: FWActivate
    ioms: "{{ ioms }}"
    username: "{{ username }}"
    password: "{{ password }}"

- name: Firmware Activate with individual IOMs specified
  community.general.wdc_redfish_command:
    category: Update
    command: FWActivate
    ioms:
      - iom1.wdc.com
      - iom2.wdc.com
    username: "{{ username }}"
    password: "{{ password }}"

- name: Firmware Activate with baseuri specified
  community.general.wdc_redfish_command:
    category: Update
    command: FWActivate
    baseuri: "iom1.wdc.com"
    username: "{{ username }}"
    password: "{{ password }}"


- name: Update and Activate (orchestrates firmware update and activation with a single command)
  community.general.wdc_redfish_command:
    category: Update
    command: UpdateAndActivate
    ioms: "{{ ioms }}"
    username: "{{ username }}"
    password: "{{ password }}"
    update_image_uri: "{{ update_image_uri }}"
    update_creds:
      username: operator
      password: supersecretpwd

- name: Turn on enclosure indicator LED
  community.general.wdc_redfish_command:
    category: Chassis
    resource_id: Enclosure
    command: IndicatorLedOn
    username: "{{ username }}"
    password: "{{ password }}"

- name: Turn off IOM A indicator LED
  community.general.wdc_redfish_command:
    category: Chassis
    resource_id: IOModuleAFRU
    command: IndicatorLedOff
    username: "{{ username }}"
    password: "{{ password }}"

- name: Turn on Power Supply B indicator LED
  community.general.wdc_redfish_command:
    category: Chassis
    resource_id: PowerSupplyBFRU
    command: IndicatorLedOn
    username: "{{ username }}"
    password: "{{ password }}"

- name: Turn on External Fan 3 indicator LED
  community.general.wdc_redfish_command:
    category: Chassis
    resource_id: FanExternalFRU3
    command: IndicatorLedOn
    username: "{{ username }}"
    password: "{{ password }}"

- name: Turn on Internal Fan indicator LED
  community.general.wdc_redfish_command:
    category: Chassis
    resource_id: FanInternalFRU
    command: IndicatorLedOn
    username: "{{ username }}"
    password: "{{ password }}"

- name: Set chassis to Low Power Mode
  community.general.wdc_redfish_command:
    category: Chassis
    resource_id: Enclosure
    command: PowerModeLow

- name: Set chassis to Normal Power Mode
  community.general.wdc_redfish_command:
    category: Chassis
    resource_id: Enclosure
    command: PowerModeNormal

'''

RETURN = '''
msg:
    description: Message with action result or error description
    returned: always
    type: str
    sample: "Action was successful"
'''

from ansible_collections.community.general.plugins.module_utils.wdc_redfish_utils import WdcRedfishUtils
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native

CATEGORY_COMMANDS_ALL = {
    "Update": [
        "FWActivate",
        "UpdateAndActivate"
    ],
    "Chassis": [
        "IndicatorLedOn",
        "IndicatorLedOff",
        "PowerModeLow",
        "PowerModeNormal",
    ]
}


def main():
    module = AnsibleModule(
        argument_spec=dict(
            category=dict(required=True),
            command=dict(required=True, type='list', elements='str'),
            ioms=dict(type='list', elements='str'),
            baseuri=dict(),
            username=dict(),
            password=dict(no_log=True),
            auth_token=dict(no_log=True),
            update_creds=dict(
                type='dict',
                options=dict(
                    username=dict(),
                    password=dict(no_log=True)
                )
            ),
            resource_id=dict(),
            update_image_uri=dict(),
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

    # Resource to modify
    resource_id = module.params['resource_id']

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
                               resource_id=resource_id, data_modification=True)

    # Organize by Categories / Commands

    if category == "Update":
        # execute only if we find UpdateService resources
        resource = rf_utils._find_updateservice_resource()
        if resource['ret'] is False:
            module.fail_json(msg=resource['msg'])
        # update options
        update_opts = {
            'update_creds': module.params['update_creds']
        }
        for command in command_list:
            if command == "FWActivate":
                if module.check_mode:
                    result = {
                        'ret': True,
                        'changed': True,
                        'msg': 'FWActivate not performed in check mode.'
                    }
                else:
                    result = rf_utils.firmware_activate(update_opts)
            elif command == "UpdateAndActivate":
                update_opts["update_image_uri"] = module.params['update_image_uri']
                result = rf_utils.update_and_activate(update_opts)

    elif category == "Chassis":
        result = rf_utils._find_chassis_resource()
        if result['ret'] is False:
            module.fail_json(msg=to_native(result['msg']))

        led_commands = ["IndicatorLedOn", "IndicatorLedOff"]

        # Check if more than one led_command is present
        num_led_commands = sum([command in led_commands for command in command_list])
        if num_led_commands > 1:
            result = {'ret': False, 'msg': "Only one IndicatorLed command should be sent at a time."}
        else:
            for command in command_list:
                if command.startswith("IndicatorLed"):
                    result = rf_utils.manage_chassis_indicator_led(command)
                elif command.startswith("PowerMode"):
                    result = rf_utils.manage_chassis_power_mode(command)

    if result['ret'] is False:
        module.fail_json(msg=to_native(result['msg']))
    else:
        del result['ret']
        changed = result.get('changed', True)
        session = result.get('session', dict())
        module.exit_json(changed=changed,
                         session=session,
                         msg='Action was successful' if not module.check_mode else result.get(
                             'msg', "No action performed in check mode."
                         ))


if __name__ == '__main__':
    main()
