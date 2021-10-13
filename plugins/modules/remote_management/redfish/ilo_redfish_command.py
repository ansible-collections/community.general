#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2021-2022 Hewlett Packard Enterprise, Inc. All rights reserved.
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: iLO Redfish Command
short_description: Builds Redfish URIs locally and sends them to remote OOB controllers to perform an action.
                    For use with HPE iLO operations that require Redfish OEM extensions.
description:
    - "Provides an interface to perform an action."
requirements:
    - "python >= 3.8"
    - "ansible >= 3.2"
author:
    - "Bhavya B (@Bhavya06)"
'''

EXAMPLES = '''
  - name: Add iLO User
    community.general.ilo_redfish_command:
      category: Accounts
      command: AddiLOuser
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"

  - name: Delete iLO User
    community.general.ilo_redfish_command:
      category: Accounts
      command: DeliLOuser
'''

ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'community',
                    'metadata_version': '1.1'}

CATEGORY_COMMANDS_ALL = {
    "Authorization": ["Login", "Logout"],
    "Accounts": ["AddiLOuser", "DeliLOuser", "UpdateiLOpassword", "UpdateiLOUserRole"],
    "Serverclone": ["LoadUsers"]
}

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.ilo_redfish_utils import iLORedfishUtils

def main():
    result = {}
    module = AnsibleModule(
        argument_spec=dict(
            category=dict(required=True),
            command=dict(required=True, type='list'),
            baseuri=dict(required=True),
            username=dict(),
            password=dict(),
            loginname=dict(),
            new_username=dict(),
            new_password=dict(no_log=True),
            roleid=dict(),
            auth_token=dict(),
            path=dict(),
            keepexisting=dict(),
            defaultpass=dict(no_log=True),
            timeout=dict(type='int', default=10),
        ),
        supports_check_mode=False
    )

    category = module.params['category']
    command_list = module.params['command']

    loginname = module.params['loginname']

    creds = {}
    session_id = None

    timeout = module.params['timeout']

    if module.params['baseuri'] is None:
        module.fail_json(msg=to_native("Baseuri is empty."))

    root_uri = "https://" + module.params['baseuri']

    creds = {"user": module.params['username'],
             "pswd": module.params['password'],
             "token": module.params['auth_token']}

    rf_utils = iLORedfishUtils(creds, root_uri, timeout, module)

    user = {'username': module.params['new_username'],
            'userpswd': module.params['new_password'],
            'roleid': module.params['roleid']}

    if category not in CATEGORY_COMMANDS_ALL:
        module.fail_json(msg=to_native("Invalid Category '%s'. Valid Categories = %s" % (
            category, CATEGORY_COMMANDS_ALL.keys())))

    for cmd in command_list:
        # Fail if even one command given is invalid
        if cmd not in CATEGORY_COMMANDS_ALL[category]:
            module.fail_json(msg=to_native("Invalid Command '%s'. Valid Commands = %s" % (
                cmd, CATEGORY_COMMANDS_ALL[category])))

    if category == "Accounts":

        result = rf_utils._find_accountservice_resource()
        if result['ret'] is False:
            result['id'] = session_id
            module.fail_json(msg=to_native(result))

        for command in command_list:
            if command == "AddiLOuser":
                result = rf_utils.AddiLOuser(user)
            elif command == "DeliLOuser":
                result = rf_utils.DeliLOuser(loginname)
            elif command == "UpdateiLOpassword":
                user['username'] = loginname
                result = rf_utils.UpdateiLOpass(user)
            elif command == "UpdateiLOUserRole":
                user['username'] = loginname
                result = rf_utils.UpdateiLOUserRole(user)

    elif category == "Serverclone":
        for command in command_list:
            if command == "LoadUsers":
                result = rf_utils._find_accountservice_resource(session_id)
                if result['ret'] is False:
                    module.fail_json(msg=to_native(result['msg']))
                result = rf_utils.loadaccounts(
                    module.params['keepexisting'], module.params['defaultpass'], session_id)

    if result['ret'] is True:
        del result['ret']
        changed = result.get('changed', True)
        module.exit_json(
            changed=changed, msg=command + ' was successful', result=to_native(result), session=session_id, payload=result.get("response"))

    else:
        module.fail_json(msg=to_native(result))


if __name__ == '__main__':
    main()
