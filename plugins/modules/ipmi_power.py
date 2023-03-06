#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: ipmi_power
short_description: Power management for machine
description:
  - Use this module for power management
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  name:
    description:
      - Hostname or ip address of the BMC.
    required: true
    type: str
  port:
    description:
      - Remote RMCP port.
    default: 623
    type: int
  user:
    description:
      - Username to use to connect to the BMC.
    required: true
    type: str
  password:
    description:
      - Password to connect to the BMC.
    required: true
    type: str
  key:
    description:
      - Encryption key to connect to the BMC in hex format.
    required: false
    type: str
    version_added: 4.1.0
  state:
    description:
      - Whether to ensure that the machine in desired state.
      - "The choices for state are:
            - on -- Request system turn on
            - off -- Request system turn off without waiting for OS to shutdown
            - shutdown -- Have system request OS proper shutdown
            - reset -- Request system reset without waiting for OS
            - boot -- If system is off, then 'on', else 'reset'"
      - Either this option or I(machine) is required.
    choices: ['on', 'off', shutdown, reset, boot]
    type: str
  timeout:
    description:
      - Maximum number of seconds before interrupt request.
    default: 300
    type: int
  machine:
    description:
      - Provide a list of the remote target address for the bridge IPMI request,
        and the power status.
      - Either this option or I(state) is required.
    required: false
    type: list
    elements: dict
    version_added: 4.3.0
    suboptions:
      targetAddress:
        description:
          - Remote target address for the bridge IPMI request.
        type: int
        required: true
      state:
        description:
          - Whether to ensure that the machine specified by I(targetAddress) in desired state.
          - If this option is not set, the power state is set by I(state).
          - If both this option and I(state) are set, this option takes precedence over I(state).
        choices: ['on', 'off', shutdown, reset, boot]
        type: str

requirements:
  - "python >= 2.6"
  - pyghmi
author: "Bulat Gaifullin (@bgaifullin) <gaifullinbf@gmail.com>"
'''

RETURN = '''
powerstate:
    description: The current power state of the machine.
    returned: success and I(machine) is not provided
    type: str
    sample: 'on'
status:
    description: The current power state of the machine when the machine option is set.
    returned: success and I(machine) is provided
    type: list
    elements: dict
    version_added: 4.3.0
    contains:
        powerstate:
          description: The current power state of the machine specified by I(targetAddress).
          type: str
        targetAddress:
          description: The remote target address.
          type: int
    sample: [
              {
                "powerstate": "on",
                "targetAddress": 48,
              },
              {
                "powerstate": "on",
                "targetAddress": 50,
              },
    ]
'''

EXAMPLES = '''
- name: Ensure machine is powered on
  community.general.ipmi_power:
    name: test.testdomain.com
    user: admin
    password: password
    state: 'on'

- name: Ensure machines of which remote target address is 48 and 50 are powered off
  community.general.ipmi_power:
    name: test.testdomain.com
    user: admin
    password: password
    state: 'off'
    machine:
      - targetAddress: 48
      - targetAddress: 50

- name: Ensure machine of which remote target address is 48 is powered on, and 50 is powered off
  community.general.ipmi_power:
    name: test.testdomain.com
    user: admin
    password: password
    machine:
      - targetAddress: 48
        state: 'on'
      - targetAddress: 50
        state: 'off'
'''

import traceback
import binascii

PYGHMI_IMP_ERR = None
INVALID_TARGET_ADDRESS = 0x100
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
            state=dict(choices=['on', 'off', 'shutdown', 'reset', 'boot']),
            user=dict(required=True, no_log=True),
            password=dict(required=True, no_log=True),
            key=dict(type='str', no_log=True),
            timeout=dict(default=300, type='int'),
            machine=dict(
                type='list', elements='dict',
                options=dict(
                    targetAddress=dict(required=True, type='int'),
                    state=dict(type='str', choices=['on', 'off', 'shutdown', 'reset', 'boot']),
                ),
            ),
        ),
        supports_check_mode=True,
        required_one_of=(
            ['state', 'machine'],
        ),
    )

    if command is None:
        module.fail_json(msg=missing_required_lib('pyghmi'), exception=PYGHMI_IMP_ERR)

    name = module.params['name']
    port = module.params['port']
    user = module.params['user']
    password = module.params['password']
    state = module.params['state']
    timeout = module.params['timeout']
    machine = module.params['machine']

    try:
        if module.params['key']:
            key = binascii.unhexlify(module.params['key'])
        else:
            key = None
    except Exception:
        module.fail_json(msg="Unable to convert 'key' from hex string.")

    # --- run command ---
    try:
        ipmi_cmd = command.Command(
            bmc=name, userid=user, password=password, port=port, kg=key
        )
        module.debug('ipmi instantiated - name: "%s"' % name)

        changed = False
        if machine is None:
            current = ipmi_cmd.get_power()
            if current['powerstate'] != state:
                response = {'powerstate': state} if module.check_mode \
                    else ipmi_cmd.set_power(state, wait=timeout)
                changed = True
            else:
                response = current

            if 'error' in response:
                module.fail_json(msg=response['error'])

            module.exit_json(changed=changed, **response)
        else:
            response = []
            for entry in machine:
                taddr = entry['targetAddress']
                if taddr >= INVALID_TARGET_ADDRESS:
                    module.fail_json(msg="targetAddress should be set between 0 to 255.")

                try:
                    # bridge_request is supported on pyghmi 1.5.30 and later
                    current = ipmi_cmd.get_power(bridge_request={"addr": taddr})
                except TypeError:
                    module.fail_json(
                        msg="targetAddress isn't supported on the installed pyghmi.")

                if entry['state']:
                    tstate = entry['state']
                elif state:
                    tstate = state
                else:
                    module.fail_json(msg="Either state or suboption of machine state should be set.")

                if current['powerstate'] != tstate:
                    changed = True
                    if not module.check_mode:
                        new = ipmi_cmd.set_power(tstate, wait=timeout, bridge_request={"addr": taddr})
                        if 'error' in new:
                            module.fail_json(msg=new['error'])

                        response.append(
                            {'targetAddress:': taddr, 'powerstate': new['powerstate']})

                if current['powerstate'] == tstate or module.check_mode:
                    response.append({'targetAddress:': taddr, 'powerstate': tstate})

            module.exit_json(changed=changed, status=response)
    except Exception as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
