#!/usr/bin/python

# Copyright (c) 2018 Dell EMC Inc.
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: idrac_redfish_command
short_description: Manages Out-Of-Band controllers using iDRAC OEM Redfish APIs
description:
  - Builds Redfish URIs locally and sends them to remote OOB controllers to perform an action.
  - For use with Dell iDRAC operations that require Redfish OEM extensions.
extends_documentation_fragment:
  - community.general.attributes
  - community.general.redfish
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
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
  resource_id:
    description:
      - ID of the System, Manager or Chassis to modify.
    type: str
    version_added: '0.2.0'
  validate_certs:
    version_added: 10.6.0
  ca_path:
    version_added: 10.6.0
  ciphers:
    version_added: 10.6.0

author: "Jose Delarosa (@jose-delarosa)"
"""

EXAMPLES = r"""
- name: Create BIOS configuration job (schedule BIOS setting update)
  community.general.idrac_redfish_command:
    category: Systems
    command: CreateBiosConfigJob
    resource_id: System.Embedded.1
    baseuri: "{{ baseuri }}"
    username: "{{ username }}"
    password: "{{ password }}"
"""

RETURN = r"""
msg:
  description: Message with action result or error description.
  returned: always
  type: str
  sample: "Action was successful"
return_values:
  description: Dictionary containing command-specific response data from the action.
  returned: on success
  type: dict
  version_added: 6.6.0
  sample: {"job_id": "/redfish/v1/Managers/iDRAC.Embedded.1/Jobs/JID_471269252011"}
"""

import re
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.redfish_utils import (
    RedfishUtils,
    REDFISH_COMMON_ARGUMENT_SPEC,
)
from ansible.module_utils.common.text.converters import to_native


class IdracRedfishUtils(RedfishUtils):
    def create_bios_config_job(self):
        result = {}
        key = "Bios"
        jobs = "Jobs"

        # Search for 'key' entry and extract URI from it
        response = self.get_request(self.root_uri + self.systems_uris[0])
        if response["ret"] is False:
            return response
        result["ret"] = True
        data = response["data"]

        if key not in data:
            return {"ret": False, "msg": f"Key {key} not found"}

        bios_uri = data[key]["@odata.id"]

        # Extract proper URI
        response = self.get_request(self.root_uri + bios_uri)
        if response["ret"] is False:
            return response
        result["ret"] = True
        data = response["data"]
        set_bios_attr_uri = data["@Redfish.Settings"]["SettingsObject"]["@odata.id"]

        payload = {"TargetSettingsURI": set_bios_attr_uri}
        response = self.post_request(f"{self.root_uri}{self.manager_uri}/{jobs}", payload)
        if response["ret"] is False:
            return response

        response_output = response["resp"].__dict__
        job_id_full = response_output["headers"]["Location"]
        job_id = re.search("JID_.+", job_id_full).group()
        return {"ret": True, "msg": f"Config job {job_id} created", "job_id": job_id_full}


CATEGORY_COMMANDS_ALL = {"Systems": ["CreateBiosConfigJob"], "Accounts": [], "Manager": []}


def main():
    result = {}
    return_values = {}
    argument_spec = dict(
        category=dict(required=True),
        command=dict(required=True, type="list", elements="str"),
        baseuri=dict(required=True),
        username=dict(),
        password=dict(no_log=True),
        auth_token=dict(no_log=True),
        timeout=dict(type="int", default=10),
        resource_id=dict(),
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
        supports_check_mode=False,
    )

    category = module.params["category"]
    command_list = module.params["command"]

    # admin credentials used for authentication
    creds = {"user": module.params["username"], "pswd": module.params["password"], "token": module.params["auth_token"]}

    # timeout
    timeout = module.params["timeout"]

    # System, Manager or Chassis ID to modify
    resource_id = module.params["resource_id"]

    # Build root URI
    root_uri = f"https://{module.params['baseuri']}"
    rf_utils = IdracRedfishUtils(creds, root_uri, timeout, module, resource_id=resource_id, data_modification=True)

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

    if category == "Systems":
        # execute only if we find a System resource
        # NOTE: Currently overriding the usage of 'data_modification' due to
        # how 'resource_id' is processed.  In the case of CreateBiosConfigJob,
        # we interact with BOTH systems and managers, so you currently cannot
        # specify a single 'resource_id' to make both '_find_systems_resource'
        # and '_find_managers_resource' return success.  Since
        # CreateBiosConfigJob doesn't use the matched 'resource_id' for a
        # system regardless of what's specified, disabling the 'resource_id'
        # inspection for the next call allows a specific manager to be
        # specified with 'resource_id'.  If we ever need to expand the input
        # to inspect a specific system and manager in parallel, this will need
        # updates.
        rf_utils.data_modification = False
        result = rf_utils._find_systems_resource()
        rf_utils.data_modification = True
        if result["ret"] is False:
            module.fail_json(msg=to_native(result["msg"]))

        for command in command_list:
            if command == "CreateBiosConfigJob":
                # execute only if we find a Managers resource
                result = rf_utils._find_managers_resource()
                if result["ret"] is False:
                    module.fail_json(msg=to_native(result["msg"]))
                result = rf_utils.create_bios_config_job()
                if "job_id" in result:
                    return_values["job_id"] = result["job_id"]

    # Return data back or fail with proper message
    if result["ret"] is True:
        del result["ret"]
        module.exit_json(changed=True, msg="Action was successful", return_values=return_values)
    else:
        module.fail_json(msg=to_native(result["msg"]))


if __name__ == "__main__":
    main()
