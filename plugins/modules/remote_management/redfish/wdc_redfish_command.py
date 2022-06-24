#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2022 Western Digital Corporation
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: wdc_redfish_command
short_description: Manages WDC UltraStar Data102 Out-Of-Band controllers using Redfish APIs
version_added: 5.3.0
description:
  - Builds Redfish URIs locally and sends them to remote OOB controllers to
    perform an action.
  - Manages OOB controller firmware. For example, Firmware Activate, Update and Activate.
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
    description:
      - Base URI of OOB controller.  Must include this or I(ioms).
    type: str
  ioms:
    description:
      - List of IOM FQDNs for the enclosure.  Must include this or baseuri
    type: list
    elements: str
  username:
    description:
      - User for authentication with OOB controller
    type: str
  password:
    description:
      - Password for authentication with OOB controller
    type: str
  auth_token:
    description:
      - Security token for authentication with OOB controller
    type: str
  timeout:
    description:
      - Timeout in seconds for URL requests to OOB controller
    default: 10
    type: int
  update_image_uri:
    required: false
    description:
      - The URI of the image for the update
    type: str
  update_creds:
    required: false
    description:
      - The credentials for retrieving the update image
    type: dict
    suboptions:
      username:
        required: false
        description:
          - The username for retrieving the update image
        type: str
      password:
        required: false
        description:
          - The password for retrieving the update image
        type: str
requirements:
  - dnspython (2.1.0 for Python 3, 1.16.0 for Python 2)
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
'''

RETURN = '''
msg:
    description: Message with action result or error description
    returned: always
    type: str
    sample: "Action was successful"
'''

from ansible_collections.community.general.plugins.module_utils.wdc_redfish_utils import WdcRedfishUtils
try:
    from dns import resolver
    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_native

CATEGORY_COMMANDS_ALL = {
    "Update": [
        "FWActivate",
        "UpdateAndActivate"
    ]
}


def dns_available():
    return DNS_AVAILABLE


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

    if not dns_available():
        module.fail_json(msg=missing_required_lib('dnspython'))

    category = module.params['category']
    command_list = module.params['command']

    # admin credentials used for authentication
    creds = {'user': module.params['username'],
             'pswd': module.params['password'],
             'token': module.params['auth_token']}

    # timeout
    timeout = module.params['timeout']

    # Build root URI(s)
    if module.params.get("baseuri") is not None:
        root_uris = ["https://" + module.params['baseuri']]
    else:
        root_uris = [
            "https://" + iom for iom in module.params['ioms']
        ]
    rf_utils = WdcRedfishUtils(creds, root_uris, timeout, module,
                               resource_id=None, data_modification=True)

    # Check that Category is valid
    if category not in CATEGORY_COMMANDS_ALL:
        module.fail_json(msg=to_native("Invalid Category '%s'. Valid Categories = %s" % (category, sorted(CATEGORY_COMMANDS_ALL.keys()))))

    # Check that all commands are valid
    for cmd in command_list:
        # Fail if even one command given is invalid
        if cmd not in CATEGORY_COMMANDS_ALL[category]:
            module.fail_json(msg=to_native("Invalid Command '%s'. Valid Commands = %s" % (cmd, CATEGORY_COMMANDS_ALL[category])))

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

        if result['ret'] is False:
            module.fail_json(msg=to_native(result['msg']))
        if result['ret'] is True:
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
