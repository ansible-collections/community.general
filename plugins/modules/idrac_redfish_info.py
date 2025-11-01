#!/usr/bin/python

# Copyright (c) 2019 Dell EMC Inc.
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: idrac_redfish_info
short_description: Gather PowerEdge server information through iDRAC using Redfish APIs
description:
  - Builds Redfish URIs locally and sends them to remote iDRAC controllers to get information back.
  - For use with Dell EMC iDRAC operations that require Redfish OEM extensions.
extends_documentation_fragment:
  - community.general.attributes
  - community.general.attributes.info_module
  - community.general.redfish
attributes:
  check_mode:
    version_added: 3.3.0
    # This was backported to 2.5.4 and 1.3.11 as well, since this was a bugfix
options:
  category:
    required: true
    description:
      - Category to execute on iDRAC.
    type: str
  command:
    required: true
    description:
      - List of commands to execute on iDRAC.
      - V(GetManagerAttributes) returns the list of dicts containing iDRAC, LifecycleController and System attributes.
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
  timeout:
    description:
      - Timeout in seconds for HTTP requests to iDRAC.
    default: 10
    type: int
  validate_certs:
    version_added: 10.6.0
  ca_path:
    version_added: 10.6.0
  ciphers:
    version_added: 10.6.0

author: "Jose Delarosa (@jose-delarosa)"
"""

EXAMPLES = r"""
- name: Get Manager attributes with a default of 20 seconds
  community.general.idrac_redfish_info:
    category: Manager
    command: GetManagerAttributes
    baseuri: "{{ baseuri }}"
    username: "{{ username }}"
    password: "{{ password }}"
    timeout: 20
  register: result

# Examples to display the value of all or a single iDRAC attribute
- name: Store iDRAC attributes as a fact variable
  ansible.builtin.set_fact:
    idrac_attributes: "{{ result.redfish_facts.entries | selectattr('Id', 'defined') | selectattr('Id', 'equalto', 'iDRACAttributes')
      | list | first }}"

- name: Display all iDRAC attributes
  ansible.builtin.debug:
    var: idrac_attributes

- name: Display the value of 'Syslog.1.SysLogEnable' iDRAC attribute
  ansible.builtin.debug:
    var: idrac_attributes['Syslog.1.SysLogEnable']

# Examples to display the value of all or a single LifecycleController attribute
- name: Store LifecycleController attributes as a fact variable
  ansible.builtin.set_fact:
    lc_attributes: "{{ result.redfish_facts.entries | selectattr('Id', 'defined') | selectattr('Id', 'equalto', 'LCAttributes')
      | list | first }}"

- name: Display LifecycleController attributes
  ansible.builtin.debug:
    var: lc_attributes

- name: Display the value of 'CollectSystemInventoryOnRestart' attribute
  ansible.builtin.debug:
    var: lc_attributes['LCAttributes.1.CollectSystemInventoryOnRestart']

# Examples to display the value of all or a single System attribute
- name: Store System attributes as a fact variable
  ansible.builtin.set_fact:
    system_attributes: "{{ result.redfish_facts.entries | selectattr('Id', 'defined') | selectattr('Id', 'equalto', 'SystemAttributes')
      | list | first }}"

- name: Display System attributes
  ansible.builtin.debug:
    var: system_attributes

- name: Display the value of 'PSRedPolicy'
  ansible.builtin.debug:
    var: system_attributes['ServerPwr.1.PSRedPolicy']
"""

RETURN = r"""
msg:
  description: Different results depending on task.
  returned: always
  type: dict
  sample: List of Manager attributes
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.redfish_utils import (
    RedfishUtils,
    REDFISH_COMMON_ARGUMENT_SPEC,
)
from ansible.module_utils.common.text.converters import to_native


class IdracRedfishUtils(RedfishUtils):
    def get_manager_attributes(self):
        result = {}
        manager_attributes = []
        properties = ["Attributes", "Id"]

        response = self.get_request(self.root_uri + self.manager_uri)

        if response["ret"] is False:
            return response
        data = response["data"]

        # Manager attributes are supported as part of iDRAC OEM extension
        # Attributes are supported only on iDRAC9
        try:
            for members in data["Links"]["Oem"]["Dell"]["DellAttributes"]:
                attributes_uri = members["@odata.id"]

                response = self.get_request(self.root_uri + attributes_uri)
                if response["ret"] is False:
                    return response
                data = response["data"]

                attributes = {}
                for prop in properties:
                    if prop in data:
                        attributes[prop] = data.get(prop)

                if attributes:
                    manager_attributes.append(attributes)

            result["ret"] = True

        except (AttributeError, KeyError) as e:
            result["ret"] = False
            result["msg"] = f"Failed to find attribute/key: {e}"

        result["entries"] = manager_attributes
        return result


CATEGORY_COMMANDS_ALL = {"Manager": ["GetManagerAttributes"]}


def main():
    result = {}
    argument_spec = dict(
        category=dict(required=True),
        command=dict(required=True, type="list", elements="str"),
        baseuri=dict(required=True),
        username=dict(),
        password=dict(no_log=True),
        auth_token=dict(no_log=True),
        timeout=dict(type="int", default=10),
    )
    argument_spec.update(REDFISH_COMMON_ARGUMENT_SPEC)
    module = AnsibleModule(
        argument_spec,
        required_together=[
            ("username", "password"),
        ],
        required_one_of=[
            ("username", "auth_token"),
        ],
        mutually_exclusive=[
            ("username", "auth_token"),
        ],
        supports_check_mode=True,
    )

    category = module.params["category"]
    command_list = module.params["command"]

    # admin credentials used for authentication
    creds = {"user": module.params["username"], "pswd": module.params["password"], "token": module.params["auth_token"]}

    # timeout
    timeout = module.params["timeout"]

    # Build root URI
    root_uri = f"https://{module.params['baseuri']}"
    rf_utils = IdracRedfishUtils(creds, root_uri, timeout, module)

    # Check that Category is valid
    if category not in CATEGORY_COMMANDS_ALL:
        module.fail_json(
            msg=to_native(f"Invalid Category '{category}'. Valid Categories = {list(CATEGORY_COMMANDS_ALL.keys())}")
        )

    # Check that all commands are valid
    for cmd in command_list:
        # Fail if even one command given is invalid
        if cmd not in CATEGORY_COMMANDS_ALL[category]:
            module.fail_json(
                msg=to_native(f"Invalid Command '{cmd}'. Valid Commands = {CATEGORY_COMMANDS_ALL[category]}")
            )

    # Organize by Categories / Commands

    if category == "Manager":
        # execute only if we find a Manager resource
        result = rf_utils._find_managers_resource()
        if result["ret"] is False:
            module.fail_json(msg=to_native(result["msg"]))

        for command in command_list:
            if command == "GetManagerAttributes":
                result = rf_utils.get_manager_attributes()

    # Return data back or fail with proper message
    if result["ret"] is True:
        del result["ret"]
        module.exit_json(redfish_facts=result)
    else:
        module.fail_json(msg=to_native(result["msg"]))


if __name__ == "__main__":
    main()
