#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2021-2022 Hewlett Packard Enterprise, Inc. All rights reserved.
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: iLO Redfish Config
short_description: Sets or updates a configuration attribute. For use with HPE iLO operations that require Redfish OEM extensions.
description:
    - "Provides an interface to manage configuration attributes."
requirements:
    - "python >= 3.8"
    - "ansible >= 3.2"
author:
    - "Bhavya B (@Bhavya06)"
'''

EXAMPLES = '''
  - name: Disable WINS Registration
    community.general.ilo_redfish_config:
      category: Manager
      command: SetWINSReg
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
      attribute_name: "{{ attribute_name }}"

  - name: Set Time Zone
    community.general.ilo_redfish_config:
      category: Manager
      command: SetTimeZone
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
      attribute_name: TimeZone
      attribute_value: "{{ attribute_value }}"
'''

ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'community',
                    'metadata_version': '1.1'}


CATEGORY_COMMANDS_ALL = {
    "Manager": ["SetTimeZone", "SetDNSserver", "SetDomainName", "SetNTPServers", "SetWINSReg", "ConfigureHostName"]
}

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.ilo_redfish_utils import iLORedfishUtils


def main():
    result = {}
    module = AnsibleModule(
        argument_spec=dict(
            category=dict(required=True),
            command=dict(required=True, type='list'),
            baseuri=dict(required=True),
            username=dict(),
            password=dict(no_log=True),
            attribute_name=dict(default='null'),
            attribute_value=dict(default='null'),
            auth_token=dict(),
            timeout=dict(type='int', default=10)
        ),
        supports_check_mode=False
    )

    category = module.params['category']
    command_list = module.params['command']

    # creds = None
    session_id = None
    creds = {"user": module.params['username'],
             "pswd": module.params['password'],
             "token": module.params['auth_token']}
    # creds["Hpe"] = True

    timeout = module.params['timeout']

    if module.params['baseuri'] is None:
        module.fail_json(msg=to_native("Baseuri is empty."))

    root_uri = "https://" + module.params['baseuri']
    # Auto_login = False
    rf_utils = iLORedfishUtils(creds, root_uri, timeout, module)
    mgr_attributes = {'mgr_attr_name': module.params['attribute_name'],
                      'mgr_attr_value': module.params['attribute_value']}

    if category not in CATEGORY_COMMANDS_ALL:
        module.fail_json(msg=to_native("Invalid Category '%s'. Valid Categories = %s" % (
            category, CATEGORY_COMMANDS_ALL.keys())))

    for cmd in command_list:
        if cmd not in CATEGORY_COMMANDS_ALL[category]:
            module.fail_json(msg=to_native("Invalid Command '%s'. Valid Commands = %s" % (
                cmd, CATEGORY_COMMANDS_ALL[category])))

    if category == "Manager":
        result = rf_utils._find_managers_resource()
        if(result['ret'] is False):
            module.fail_json(msg=to_native(result['msg']))

        for command in command_list:
            if command == "SetVLANAttr":
                result = rf_utils.set_VLANId(mgr_attributes)
            elif command == "SetTimeZone":
                result = rf_utils.setTimeZone(mgr_attributes)
            elif command == "SetDNSserver":
                result = rf_utils.set_DNSserver(mgr_attributes)
            elif command == "SetDomainName":
                result = rf_utils.set_DomainName(mgr_attributes)
            elif command == "SetNTPServers":
                result = rf_utils.set_NTPServer(mgr_attributes)
            elif command == "SetWINSReg":
                result = rf_utils.set_WINSRegistration(mgr_attributes)
            elif command == "ConfigureHostName":
                result = rf_utils.set_HostName(mgr_attributes)

    if result['ret'] is True:
        module.exit_json(changed=result['changed'],
                         msg=to_native(result.get('msg')), sessionid=session_id)
    else:
        module.fail_json(msg=to_native(result['msg']))


if __name__ == '__main__':
    main()
