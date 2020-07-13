#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: ipmi_power
short_description: Power management for machine
description:
  - Use this module for power management
options:
  name:
    description:
      - Hostname or ip address of the BMC.
    required: true
  port:
    description:
      - Remote RMCP port.
    default: 623
  user:
    description:
      - Username to use to connect to the BMC.
    required: true
  password:
    description:
      - Password to connect to the BMC.
    required: true
  state:
    description:
      - Whether to ensure that the machine in desired state.
    required: true
    choices:
        - on -- Request system turn on
        - off -- Request system turn off without waiting for OS to shutdown
        - shutdown -- Have system request OS proper shutdown
        - reset -- Request system reset without waiting for OS
        - boot -- If system is off, then 'on', else 'reset'
  timeout:
    description:
      - Maximum number of seconds before interrupt request.
    default: 300
requirements:
  - "python >= 2.6"
  - pyghmi
author: "Bulat Gaifullin (@bgaifullin) <gaifullinbf@gmail.com>"
'''

RETURN = '''
powerstate:
    description: The current power state of the machine.
    returned: success
    type: str
    sample: on
'''

EXAMPLES = '''
- name: Ensure machine is powered on
  community.general.ipmi_power:
    name: test.testdomain.com
    user: admin
    password: password
    state: on
'''

import traceback

PYGHMI_IMP_ERR = None
try:
    from pyghmi.ipmi import command
except ImportError:
    PYGHMI_IMP_ERR = traceback.format_exc()
    command = None

from ansible.module_utils.basic import AnsibleModule, missing_required_lib


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            port=dict(default=623, type='int'),
            state=dict(required=True, choices=['on', 'off', 'shutdown', 'reset', 'boot']),
            user=dict(required=True, no_log=True),
            password=dict(required=True, no_log=True),
            timeout=dict(default=300, type='int'),
        ),
        supports_check_mode=True,
    )

    if command is None:
        module.fail_json(msg=missing_required_lib('pyghmi'), exception=PYGHMI_IMP_ERR)

    name = module.params['name']
    port = module.params['port']
    user = module.params['user']
    password = module.params['password']
    state = module.params['state']
    timeout = module.params['timeout']

    # --- run command ---
    try:
        ipmi_cmd = command.Command(
            bmc=name, userid=user, password=password, port=port
        )
        module.debug('ipmi instantiated - name: "%s"' % name)

        current = ipmi_cmd.get_power()
        if current['powerstate'] != state:
            response = {'powerstate': state} if module.check_mode else ipmi_cmd.set_power(state, wait=timeout)
            changed = True
        else:
            response = current
            changed = False

        if 'error' in response:
            module.fail_json(msg=response['error'])

        module.exit_json(changed=changed, **response)
    except Exception as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
