#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2019 Dell EMC Inc.
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: idrac_redfish_config
short_description: Manages servers through iDRAC using Dell Redfish APIs
description:
  - For use with Dell iDRAC operations that require Redfish OEM extensions
  - Builds Redfish URIs locally and sends them to remote iDRAC controllers to
    set or update a configuration attribute.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options:
  category:
    required: true
    type: str
    description:
      - Category to execute on iDRAC.
  command:
    required: true
    description:
      - List of commands to execute on iDRAC.
      - V(SetManagerAttributes), V(SetLifecycleControllerAttributes) and
        V(SetSystemAttributes) are mutually exclusive commands when O(category)
        is V(Manager).
    type: list
    elements: str
  baseuri:
    required: true
    description:
      - Base URI of iDRAC.
    type: str
  username:
    description:
      - Username for authenticating to iDRAC.
    type: str
  password:
    description:
      - Password for authenticating to iDRAC.
    type: str
  auth_token:
    description:
      - Security token for authenticating to iDRAC.
    type: str
    version_added: 2.3.0
  manager_attributes:
    required: false
    description:
      - Dictionary of iDRAC attribute name and value pairs to update.
    default: {}
    type: 'dict'
    version_added: '0.2.0'
  timeout:
    description:
      - Timeout in seconds for HTTP requests to iDRAC.
    default: 10
    type: int
  resource_id:
    required: false
    description:
      - ID of the System, Manager or Chassis to modify.
    type: str
    version_added: '0.2.0'

author: "Jose Delarosa (@jose-delarosa)"
'''

EXAMPLES = '''
  - name: Enable NTP and set NTP server and Time zone attributes in iDRAC
    community.general.idrac_redfish_config:
      category: Manager
      command: SetManagerAttributes
      resource_id: iDRAC.Embedded.1
      manager_attributes:
        NTPConfigGroup.1.NTPEnable: "Enabled"
        NTPConfigGroup.1.NTP1: "{{ ntpserver1 }}"
        Time.1.Timezone: "{{ timezone }}"
      baseuri: "{{ baseuri }}"
      username: "{{ username}}"
      password: "{{ password }}"

  - name: Enable Syslog and set Syslog servers in iDRAC
    community.general.idrac_redfish_config:
      category: Manager
      command: SetManagerAttributes
      resource_id: iDRAC.Embedded.1
      manager_attributes:
        SysLog.1.SysLogEnable: "Enabled"
        SysLog.1.Server1: "{{ syslog_server1 }}"
        SysLog.1.Server2: "{{ syslog_server2 }}"
      baseuri: "{{ baseuri }}"
      username: "{{ username}}"
      password: "{{ password }}"

  - name: Configure SNMP community string, port, protocol and trap format
    community.general.idrac_redfish_config:
      category: Manager
      command: SetManagerAttributes
      resource_id: iDRAC.Embedded.1
      manager_attributes:
        SNMP.1.AgentEnable: "Enabled"
        SNMP.1.AgentCommunity: "public_community_string"
        SNMP.1.TrapFormat: "SNMPv1"
        SNMP.1.SNMPProtocol: "All"
        SNMP.1.DiscoveryPort: 161
        SNMP.1.AlertPort: 162
      baseuri: "{{ baseuri }}"
      username: "{{ username}}"
      password: "{{ password }}"

  - name: Enable CSIOR
    community.general.idrac_redfish_config:
      category: Manager
      command: SetLifecycleControllerAttributes
      resource_id: iDRAC.Embedded.1
      manager_attributes:
        LCAttributes.1.CollectSystemInventoryOnRestart: "Enabled"
      baseuri: "{{ baseuri }}"
      username: "{{ username}}"
      password: "{{ password }}"

  - name: Set Power Supply Redundancy Policy to A/B Grid Redundant
    community.general.idrac_redfish_config:
      category: Manager
      command: SetSystemAttributes
      resource_id: iDRAC.Embedded.1
      manager_attributes:
        ServerPwr.1.PSRedPolicy: "A/B Grid Redundant"
      baseuri: "{{ baseuri }}"
      username: "{{ username}}"
      password: "{{ password }}"
'''

RETURN = '''
msg:
    description: Message with action result or error description
    returned: always
    type: str
    sample: "Action was successful"
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.validation import (
    check_mutually_exclusive,
    check_required_arguments
)
from ansible_collections.community.general.plugins.module_utils.redfish_utils import RedfishUtils
from ansible.module_utils.common.text.converters import to_native


class IdracRedfishUtils(RedfishUtils):

    def set_manager_attributes(self, command):

        result = {}
        required_arg_spec = {'manager_attributes': {'required': True}}

        try:
            check_required_arguments(required_arg_spec, self.module.params)

        except TypeError as e:
            msg = to_native(e)
            self.module.fail_json(msg=msg)

        key = "Attributes"
        command_manager_attributes_uri_map = {
            "SetManagerAttributes": self.manager_uri,
            "SetLifecycleControllerAttributes": "/redfish/v1/Managers/LifecycleController.Embedded.1",
            "SetSystemAttributes": "/redfish/v1/Managers/System.Embedded.1"
        }
        manager_uri = command_manager_attributes_uri_map.get(command, self.manager_uri)

        attributes = self.module.params['manager_attributes']

        attrs_to_patch = {}
        attrs_skipped = {}
        attrs_bad = {}  # Store attrs which were not found in the system

        # Search for key entry and extract URI from it
        response = self.get_request(self.root_uri + manager_uri + "/" + key)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']

        if key not in data:
            return {'ret': False,
                    'msg': "%s: Key %s not found" % (command, key),
                    'warning': ""}

        for attr_name, attr_value in attributes.items():
            # Check if attribute exists
            if attr_name not in data[u'Attributes']:
                # Skip and proceed to next attribute if this isn't valid
                attrs_bad.update({attr_name: attr_value})
                continue

            # Find out if value is already set to what we want. If yes, exclude
            # those attributes
            if data[u'Attributes'][attr_name] == attr_value:
                attrs_skipped.update({attr_name: attr_value})
            else:
                attrs_to_patch.update({attr_name: attr_value})

        warning = ""
        if attrs_bad:
            warning = "Incorrect attributes %s" % (attrs_bad)

        if not attrs_to_patch:
            return {'ret': True, 'changed': False,
                    'msg': "No changes made. Manager attributes already set.",
                    'warning': warning}

        payload = {"Attributes": attrs_to_patch}
        response = self.patch_request(self.root_uri + manager_uri + "/" + key, payload)
        if response['ret'] is False:
            return response

        return {'ret': True, 'changed': True,
                'msg': "%s: Modified Manager attributes %s" % (command, attrs_to_patch),
                'warning': warning}


CATEGORY_COMMANDS_ALL = {
    "Manager": ["SetManagerAttributes", "SetLifecycleControllerAttributes",
                "SetSystemAttributes"]
}


# list of mutually exclusive commands for a category
CATEGORY_COMMANDS_MUTUALLY_EXCLUSIVE = {
    "Manager": [["SetManagerAttributes", "SetLifecycleControllerAttributes",
                 "SetSystemAttributes"]]
}


def main():
    result = {}
    module = AnsibleModule(
        argument_spec=dict(
            category=dict(required=True),
            command=dict(required=True, type='list', elements='str'),
            baseuri=dict(required=True),
            username=dict(),
            password=dict(no_log=True),
            auth_token=dict(no_log=True),
            manager_attributes=dict(type='dict', default={}),
            timeout=dict(type='int', default=10),
            resource_id=dict()
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

    category = module.params['category']
    command_list = module.params['command']

    # admin credentials used for authentication
    creds = {'user': module.params['username'],
             'pswd': module.params['password'],
             'token': module.params['auth_token']}

    # timeout
    timeout = module.params['timeout']

    # System, Manager or Chassis ID to modify
    resource_id = module.params['resource_id']

    # Build root URI
    root_uri = "https://" + module.params['baseuri']
    rf_utils = IdracRedfishUtils(creds, root_uri, timeout, module,
                                 resource_id=resource_id, data_modification=True)

    # Check that Category is valid
    if category not in CATEGORY_COMMANDS_ALL:
        module.fail_json(msg=to_native("Invalid Category '%s'. Valid Categories = %s" % (category, list(CATEGORY_COMMANDS_ALL.keys()))))

    # Check that all commands are valid
    for cmd in command_list:
        # Fail if even one command given is invalid
        if cmd not in CATEGORY_COMMANDS_ALL[category]:
            module.fail_json(msg=to_native("Invalid Command '%s'. Valid Commands = %s" % (cmd, CATEGORY_COMMANDS_ALL[category])))

    # check for mutually exclusive commands
    try:
        # check_mutually_exclusive accepts a single list or list of lists that
        # are groups of terms that should be mutually exclusive with one another
        # and checks that against a dictionary
        check_mutually_exclusive(CATEGORY_COMMANDS_MUTUALLY_EXCLUSIVE[category],
                                 dict.fromkeys(command_list, True))

    except TypeError as e:
        module.fail_json(msg=to_native(e))

    # Organize by Categories / Commands

    if category == "Manager":
        # execute only if we find a Manager resource
        result = rf_utils._find_managers_resource()
        if result['ret'] is False:
            module.fail_json(msg=to_native(result['msg']))

        for command in command_list:
            if command in ["SetManagerAttributes", "SetLifecycleControllerAttributes", "SetSystemAttributes"]:
                result = rf_utils.set_manager_attributes(command)

    # Return data back or fail with proper message
    if result['ret'] is True:
        if result.get('warning'):
            module.warn(to_native(result['warning']))

        module.exit_json(changed=result['changed'], msg=to_native(result['msg']))
    else:
        module.fail_json(msg=to_native(result['msg']))


if __name__ == '__main__':
    main()
