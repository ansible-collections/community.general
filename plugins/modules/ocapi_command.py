#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2022 Western Digital Corporation
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: ocapi_command
version_added: 6.3.0
short_description: Manages Out-Of-Band controllers using Open Composable API (OCAPI)
description:
  - Builds OCAPI URIs locally and sends them to remote OOB controllers to
    perform an action.
  - Manages OOB controller such as Indicator LED, Reboot, Power Mode, Firmware Update.
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
      - Command to execute on OOB controller.
    type: str
  baseuri:
    required: true
    description:
      - Base URI of OOB controller.
    type: str
  proxy_slot_number:
    description: For proxied inband requests, the slot number of the IOM.  Only applies if I(baseuri) is a proxy server.
    type: int
  update_image_path:
    required: false
    description:
      - For C(FWUpload), the path on the local filesystem of the firmware update image.
    type: str
  job_name:
    required: false
    description:
      - For C(DeleteJob) command, the name of the job to delete.
    type: str
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

author: "Mike Moerk (@mikemoerk)"
'''

EXAMPLES = '''
  - name: Set the power state to low
    community.general.ocapi_command:
      category: Chassis
      command: PowerModeLow
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"

  - name: Set the power state to normal
    community.general.ocapi_command:
      category: Chassis
      command: PowerModeNormal
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
  - name: Set chassis indicator LED to on
    community.general.ocapi_command:
      category: Chassis
      command: IndicatorLedOn
      baseuri: "{{ baseuri }}"
      proxy_slot_number: 2
      username: "{{ username }}"
      password: "{{ password }}"
  - name: Set chassis indicator LED to off
    community.general.ocapi_command:
      category: Chassis
      command: IndicatorLedOff
      baseuri: "{{ baseuri }}"
      proxy_slot_number: 2
      username: "{{ username }}"
      password: "{{ password }}"
  - name: Reset Enclosure
    community.general.ocapi_command:
      category: Systems
      command: PowerGracefulRestart
      baseuri: "{{ baseuri }}"
      proxy_slot_number: 2
      username: "{{ username }}"
      password: "{{ password }}"
  - name: Firmware Upload
    community.general.ocapi_command:
      category: Update
      command: FWUpload
      baseuri: "iom1.wdc.com"
      proxy_slot_number: 2
      username: "{{ username }}"
      password: "{{ password }}"
      update_image_path: "/path/to/firmware.tar.gz"
  - name: Firmware Update
    community.general.ocapi_command:
      category: Update
      command: FWUpdate
      baseuri: "iom1.wdc.com"
      proxy_slot_number: 2
      username: "{{ username }}"
      password: "{{ password }}"
  - name: Firmware Activate
    community.general.ocapi_command:
      category: Update
      command: FWActivate
      baseuri: "iom1.wdc.com"
      proxy_slot_number: 2
      username: "{{ username }}"
      password: "{{ password }}"
  - name: Delete Job
    community.general.ocapi_command:
      category: Jobs
      command: DeleteJob
      job_name: FirmwareUpdate
      baseuri: "{{ baseuri }}"
      proxy_slot_number: 2
      username: "{{ username }}"
      password: "{{ password }}"
'''

RETURN = '''
msg:
    description: Message with action result or error description.
    returned: always
    type: str
    sample: "Action was successful"

jobUri:
    description: URI to use to monitor status of the operation.  Returned for async commands such as Firmware Update, Firmware Activate.
    returned: when supported
    type: str
    sample: "https://ioma.wdc.com/Storage/Devices/openflex-data24-usalp03020qb0003/Jobs/FirmwareUpdate/"

operationStatusId:
    description: OCAPI State ID (see OCAPI documentation for possible values).
    returned: when supported
    type: int
    sample: 2

'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.ocapi_utils import OcapiUtils
from ansible.module_utils.common.text.converters import to_native
from ansible.module_utils.six.moves.urllib.parse import urljoin

# More will be added as module features are expanded
CATEGORY_COMMANDS_ALL = {
    "Chassis": ["IndicatorLedOn", "IndicatorLedOff", "PowerModeLow", "PowerModeNormal"],
    "Systems": ["PowerGracefulRestart"],
    "Update": ["FWUpload", "FWUpdate", "FWActivate"],
    "Jobs": ["DeleteJob"]
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
            update_image_path=dict(type='str'),
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
    if category == "Chassis":
        if command.startswith("IndicatorLed"):
            result = ocapi_utils.manage_chassis_indicator_led(command)
        elif command.startswith("PowerMode"):
            result = ocapi_utils.manage_system_power(command)
    elif category == "Systems":
        if command.startswith("Power"):
            result = ocapi_utils.manage_system_power(command)
    elif category == "Update":
        if command == "FWUpload":
            update_image_path = module.params.get("update_image_path")
            if update_image_path is None:
                module.fail_json(msg=to_native("Missing update_image_path."))
            result = ocapi_utils.upload_firmware_image(update_image_path)
        elif command == "FWUpdate":
            result = ocapi_utils.update_firmware_image()
        elif command == "FWActivate":
            result = ocapi_utils.activate_firmware_image()
    elif category == "Jobs":
        if command == "DeleteJob":
            job_name = module.params.get("job_name")
            if job_name is None:
                module.fail_json("Missing job_name")
            job_uri = urljoin(base_uri, "Jobs/" + job_name)
            result = ocapi_utils.delete_job(job_uri)

    if result['ret'] is False:
        module.fail_json(msg=to_native(result['msg']))
    else:
        del result['ret']
        changed = result.get('changed', True)
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
