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
module: ipmi_boot
short_description: Management of order of boot devices
description:
  - Use this module to manage order of boot devices
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
  bootdev:
    description:
      - Set boot device to use on next reboot
      - "The choices for the device are:
          - network -- Request network boot
          - floppy -- Boot from floppy
          - hd -- Boot from hard drive
          - safe -- Boot from hard drive, requesting 'safe mode'
          - optical -- boot from CD/DVD/BD drive
          - setup -- Boot into setup utility
          - default -- remove any IPMI directed boot device request"
    required: true
    choices:
      - network
      - floppy
      - hd
      - safe
      - optical
      - setup
      - default
    type: str
  state:
    description:
      - Whether to ensure that boot devices is desired.
      - "The choices for the state are:
            - present -- Request system turn on
            - absent -- Request system turn on"
    default: present
    choices: [ present, absent ]
    type: str
  persistent:
    description:
      - If set, ask that system firmware uses this device beyond next boot.
        Be aware many systems do not honor this.
    type: bool
    default: false
  uefiboot:
    description:
      - If set, request UEFI boot explicitly.
        Strictly speaking, the spec suggests that if not set, the system should BIOS boot and offers no "don't care" option.
        In practice, this flag not being set does not preclude UEFI boot on any system I've encountered.
    type: bool
    default: false
requirements:
  - pyghmi
author: "Bulat Gaifullin (@bgaifullin) <gaifullinbf@gmail.com>"
'''

RETURN = '''
bootdev:
    description: The boot device name which will be used beyond next boot.
    returned: success
    type: str
    sample: default
persistent:
    description: If True, system firmware will use this device beyond next boot.
    returned: success
    type: bool
    sample: false
uefimode:
    description: If True, system firmware will use UEFI boot explicitly beyond next boot.
    returned: success
    type: bool
    sample: false
'''

EXAMPLES = '''
- name: Ensure bootdevice is HD
  community.general.ipmi_boot:
    name: test.testdomain.com
    user: admin
    password: password
    bootdev: hd

- name: Ensure bootdevice is not Network
  community.general.ipmi_boot:
    name: test.testdomain.com
    user: admin
    password: password
    key: 1234567890AABBCCDEFF000000EEEE12
    bootdev: network
    state: absent
'''

import traceback
import binascii

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
            user=dict(required=True, no_log=True),
            password=dict(required=True, no_log=True),
            key=dict(type='str', no_log=True),
            state=dict(default='present', choices=['present', 'absent']),
            bootdev=dict(required=True, choices=['network', 'hd', 'floppy', 'safe', 'optical', 'setup', 'default']),
            persistent=dict(default=False, type='bool'),
            uefiboot=dict(default=False, type='bool')
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
    bootdev = module.params['bootdev']
    persistent = module.params['persistent']
    uefiboot = module.params['uefiboot']
    request = dict()

    if state == 'absent' and bootdev == 'default':
        module.fail_json(msg="The bootdev 'default' cannot be used with state 'absent'.")

    try:
        if module.params['key']:
            key = binascii.unhexlify(module.params['key'])
        else:
            key = None
    except Exception as e:
        module.fail_json(msg="Unable to convert 'key' from hex string.")

    # --- run command ---
    try:
        ipmi_cmd = command.Command(
            bmc=name, userid=user, password=password, port=port, kg=key
        )
        module.debug('ipmi instantiated - name: "%s"' % name)
        current = ipmi_cmd.get_bootdev()
        # uefimode may not supported by BMC, so use desired value as default
        current.setdefault('uefimode', uefiboot)
        if state == 'present' and current != dict(bootdev=bootdev, persistent=persistent, uefimode=uefiboot):
            request = dict(bootdev=bootdev, uefiboot=uefiboot, persist=persistent)
        elif state == 'absent' and current['bootdev'] == bootdev:
            request = dict(bootdev='default')
        else:
            module.exit_json(changed=False, **current)

        if module.check_mode:
            response = dict(bootdev=request['bootdev'])
        else:
            response = ipmi_cmd.set_bootdev(**request)

        if 'error' in response:
            module.fail_json(msg=response['error'])

        if 'persist' in request:
            response['persistent'] = request['persist']
        if 'uefiboot' in request:
            response['uefimode'] = request['uefiboot']

        module.exit_json(changed=True, **response)
    except Exception as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
