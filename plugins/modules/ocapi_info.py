#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2022 Western Digital Corporation
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: ocapi_info
version_added: 6.3.0
short_description: Manages Out-Of-Band controllers using Open Composable API (OCAPI)
description:
  - Builds OCAPI URIs locally and sends them to remote OOB controllers to get information back.
extends_documentation_fragment:
  - community.general.attributes
  - community.general.attributes.info_module
options:
  category:
    required: true
    description:
      - Category to execute on OOB controller.
    type: str
  command:
    required: true
    description:
      - Command to execute on OOB controller.
    type: str
  baseuri:
    required: true
    description:
      - Base URI of OOB controller.
    type: str
  proxy_slot_number:
    description: For proxied inband requests, the slot number of the IOM. Only applies if O(baseuri) is a proxy server.
    type: int
  username:
    required: true
    description:
      - Username for authenticating to OOB controller.
    type: str
  password:
    required: true
    description:
      - Password for authenticating to OOB controller.
    type: str
  timeout:
    description:
      - Timeout in seconds for URL requests to OOB controller.
    default: 10
    type: int
  job_name:
    description:
      - Name of job for fetching status.
    type: str


author: "Mike Moerk (@mikemoerk)"
"""

EXAMPLES = r"""
- name: Get job status
  community.general.ocapi_info:
    category: Status
    command: JobStatus
    baseuri: "http://iom1.wdc.com"
    jobName: FirmwareUpdate
    username: "{{ username }}"
    password: "{{ password }}"
"""

RETURN = r"""
msg:
  description: Message with action result or error description.
  returned: always
  type: str
  sample: "Action was successful"

percentComplete:
  description: Percent complete of the relevant operation. Applies to O(command=JobStatus).
  returned: when supported
  type: int
  sample: 99

operationStatus:
  description: Status of the relevant operation. Applies to O(command=JobStatus). See OCAPI documentation for details.
  returned: when supported
  type: str
  sample: "Activate needed"

operationStatusId:
  description: Integer value of status (corresponds to operationStatus). Applies to O(command=JobStatus). See OCAPI documentation
    for details.
  returned: when supported
  type: int
  sample: 65540

operationHealth:
  description: Health of the operation. Applies to O(command=JobStatus). See OCAPI documentation for details.
  returned: when supported
  type: str
  sample: "OK"

operationHealthId:
  description: >-
    Integer value for health of the operation (corresponds to RV(operationHealth)). Applies to O(command=JobStatus). See OCAPI
    documentation for details.
  returned: when supported
  type: str
  sample: "OK"

details:
  description: Details of the relevant operation. Applies to O(command=JobStatus).
  returned: when supported
  type: list
  elements: str

status:
  description: Dictionary containing status information. See OCAPI documentation for details.
  returned: when supported
  type: dict
  sample:
    {
      "Details": [
        "None"
      ],
      "Health": [
        {
          "ID": 5,
          "Name": "OK"
        }
      ],
      "State": {
        "ID": 16,
        "Name": "In service"
      }
    }
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.ocapi_utils import OcapiUtils
from ansible.module_utils.common.text.converters import to_native
from ansible.module_utils.six.moves.urllib.parse import urljoin

# More will be added as module features are expanded
CATEGORY_COMMANDS_ALL = {
    "Jobs": ["JobStatus"]
}


def main():
    result = {}
    module = AnsibleModule(
        argument_spec=dict(
            category=dict(required=True),
            command=dict(required=True, type='str'),
            job_name=dict(type='str'),
            baseuri=dict(required=True, type='str'),
            proxy_slot_number=dict(type='int'),
            username=dict(required=True),
            password=dict(required=True, no_log=True),
            timeout=dict(type='int', default=10)
        ),
        supports_check_mode=True
    )

    category = module.params['category']
    command = module.params['command']

    # admin credentials used for authentication
    creds = {
        'user': module.params['username'],
        'pswd': module.params['password']
    }

    # timeout
    timeout = module.params['timeout']

    base_uri = "https://" + module.params["baseuri"]
    proxy_slot_number = module.params.get("proxy_slot_number")
    ocapi_utils = OcapiUtils(creds, base_uri, proxy_slot_number, timeout, module)

    # Check that Category is valid
    if category not in CATEGORY_COMMANDS_ALL:
        module.fail_json(msg=to_native("Invalid Category '%s'. Valid Categories = %s" % (category, list(CATEGORY_COMMANDS_ALL.keys()))))

    # Check that the command is valid
    if command not in CATEGORY_COMMANDS_ALL[category]:
        module.fail_json(msg=to_native("Invalid Command '%s'. Valid Commands = %s" % (command, CATEGORY_COMMANDS_ALL[category])))

    # Organize by Categories / Commands
    if category == "Jobs":
        if command == "JobStatus":
            if module.params.get("job_name") is None:
                module.fail_json(msg=to_native(
                    "job_name required for JobStatus command."))
            job_uri = urljoin(base_uri, 'Jobs/' + module.params["job_name"])
            result = ocapi_utils.get_job_status(job_uri)

    if result['ret'] is False:
        module.fail_json(msg=to_native(result['msg']))
    else:
        del result['ret']
        changed = False
        session = result.get('session', dict())
        kwargs = {
            "changed": changed,
            "session": session,
            "msg": "Action was successful." if not module.check_mode else result.get(
                "msg", "No action performed in check mode."
            )
        }
        result_keys = [result_key for result_key in result if result_key not in kwargs]
        for result_key in result_keys:
            kwargs[result_key] = result[result_key]
        module.exit_json(**kwargs)


if __name__ == '__main__':
    main()
