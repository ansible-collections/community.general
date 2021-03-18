#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2018 Dell EMC Inc.
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: idrac_redfish_command
short_description: Manages Out-Of-Band controllers using iDRAC OEM Redfish APIs
description:
  - Builds Redfish URIs locally and sends them to remote OOB controllers to
    perform an action.
  - For use with Dell iDRAC operations that require Redfish OEM extensions
options:
  category:
    required: true
    description:
      - Category to execute on OOB controller
    type: str
  command:
    required: true
    description:
      - List of commands to execute on OOB controller
    type: list
    elements: str
  baseuri:
    required: true
    description:
      - Base URI of OOB controller
    type: str
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
    version_added: 2.3.0
  timeout:
    description:
      - Timeout in seconds for URL requests to OOB controller
    default: 10
    type: int
  resource_id:
    required: false
    description:
      - The ID of the System, Manager or Chassis to modify
    type: str
    version_added: '0.2.0'

author: "Jose Delarosa (@jose-delarosa)"
'''

EXAMPLES = '''
  - name: Create BIOS configuration job (schedule BIOS setting update)
    community.general.idrac_redfish_command:
      category: Systems
      command: CreateBiosConfigJob
      resource_id: System.Embedded.1
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
'''

RETURN = '''
msg:
    description: Message with action result or error description
    returned: always
    type: str
    sample: "Action was successful"
'''

import re
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.redfish_utils import RedfishUtils
from ansible.module_utils._text import to_native


class IdracRedfishUtils(RedfishUtils):

    def create_bios_config_job(self):
        result = {}
        key = "Bios"
        jobs = "Jobs"

        # Search for 'key' entry and extract URI from it
        response = self.get_request(self.root_uri + self.systems_uris[0])
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']

        if key not in data:
            return {'ret': False, 'msg': "Key %s not found" % key}

        bios_uri = data[key]["@odata.id"]

        # Extract proper URI
        response = self.get_request(self.root_uri + bios_uri)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']
        set_bios_attr_uri = data["@Redfish.Settings"]["SettingsObject"][
            "@odata.id"]

        payload = {"TargetSettingsURI": set_bios_attr_uri}
        response = self.post_request(
            self.root_uri + self.manager_uri + "/" + jobs, payload)
        if response['ret'] is False:
            return response

        response_output = response['resp'].__dict__
        job_id = response_output["headers"]["Location"]
        job_id = re.search("JID_.+", job_id).group()
        # Currently not passing job_id back to user but patch is coming
        return {'ret': True, 'msg': "Config job %s created" % job_id}


CATEGORY_COMMANDS_ALL = {
    "Systems": ["CreateBiosConfigJob"],
    "Accounts": [],
    "Manager": []
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

    # Organize by Categories / Commands

    if category == "Systems":
        # execute only if we find a System resource
        result = rf_utils._find_systems_resource()
        if result['ret'] is False:
            module.fail_json(msg=to_native(result['msg']))

        for command in command_list:
            if command == "CreateBiosConfigJob":
                # execute only if we find a Managers resource
                result = rf_utils._find_managers_resource()
                if result['ret'] is False:
                    module.fail_json(msg=to_native(result['msg']))
                result = rf_utils.create_bios_config_job()

    # Return data back or fail with proper message
    if result['ret'] is True:
        del result['ret']
        module.exit_json(changed=True, msg='Action was successful')
    else:
        module.fail_json(msg=to_native(result['msg']))


if __name__ == '__main__':
    main()
