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
    required: false
    type: list
    elements: dict
    suboptions:
      targetAddress:
        description:
          - Remote target address for the bridge IPMI request.
        type: int
      state:
        description:
          - Whether to ensure that the machine specified by targetAddress in desired state.
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
    returned: success
    type: str
    sample: on
status:
    description: The current power state of the machine when the machine option is set.
    returned: success
    type: list
    sample: [
              {
                "powerstate": "on",
                "targetAddress': 48,
              },
              {
                "powerstate": "on",
                "targetAddress": 50,
              },
    ]

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
status:
    description: The current power state of the machine when the machine option is set.
    returned: success
    type: list
    sample: [
              {
                "powerstate": "on",
                "targetAddress': 48,
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
    state: on

- name: Ensure machines of which remote target address is 48 and 50 are powered off
  community.general.ipmi_power:
    name: test.testdomain.com
    user: admin
    password: password
    state: off
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
        state: on
      - targetAddress: 50
        state: off
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
                    targetAddress=dict(type='int'),
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
        if not machine:
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
                    module.fail_json(msg="targetAddress isn't supported on this module")

                if entry['state']:
                    state = entry['state']
                elif not state:
                    module.fail_json(msg="Either state or suboption of machine state should be set.")

                if current['powerstate'] != state:
                    if module.check_mode:
                        pass
                    else:
                        new = ipmi_cmd.set_power(state, wait=timeout, bridge_request={"addr": taddr})
                        if 'error' in new:
                            module.fail_json(msg=response['error'])

                        response.append(
                            {'targetAddress:': taddr, 'powerstate': new['powerstate']})

                        changed = True
                else:
                    response.append({'targetAddress:': taddr, 'powerstate': state})

            module.exit_json(changed=changed, status=response)
    except Exception as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
