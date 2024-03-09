#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2024, Max Maxopoly <max@dermax.org>
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: usb_facts
short_description: Allows listing information about usb devices
description:
  - Allows retrieving information about available usb devices through lsusb
author: "Max Maxopoly (max@dermax.org)"
extends_documentation_fragment:
  - community.general.attributes
requirements:
  - lsusb binary on PATH (usually installed through the package usbutils and preinstalled on many systems)
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
'''

EXAMPLES = '''
- name: Get information about USB devices
  community.general.usb_facts:
  register: usb_facts
'''

RETURN = r'''
ansible_facts:
  description: Dictionary containing details of connected usb devices
  returned: always
  type: complex
  contains:
    devices:
      description: A list of usb devices available
      returned: always
      type: list
      contains:
        bus:
          description: The bus the usb device is connected to.
          returned: always
          type: str
          sample: "001"
        device:
          description: The device number occupied on the bus
          returned: always
          type: str
          sample: "002"
        id:
          description: Id of the usb device
          returned: always
          type: str
          sample: "1d6b:0002"
        name:
          description: Human readable name of the device
          returned: always
          type: str
          sample: Linux Foundation 2.0 root hub
'''

import re
# Import module snippets.
from ansible.module_utils.basic import AnsibleModule


def parse_lsusb(module, lsusb_path):
    rc, stdout, stderr = module.run_command(lsusb_path, check_rc=True)
    regex = re.compile(r'^Bus (\d{3}) Device (\d{3}): ID ([0-9a-f]{4}:[0-9a-f]{4}) (.*)$')
    devices = []
    for line in stdout.splitlines(keepends=False):
        match = re.match(regex, line)
        if not match:
            module.fail_json(msg="failed to parse unknown lsusb output %s" % (line), stdout=stdout, stderr=stderr)
        current_device = {
            'bus': match.group(1),
            'device': match.group(2),
            'id': match.group(3),
            'name': match.group(4)
        }
        devices.append(current_device)
    return_value = {
        "devices": devices
    }
    module.exit_json(msg="parsed %s usb devices" % (len(devices)), stdout=stdout, stderr=stderr, ansible_facts=return_value)


def main():
    module = AnsibleModule(
        {},
        supports_check_mode=True
    )

    # Set LANG env since we parse stdout
    module.run_command_environ_update = dict(LANG='C', LC_ALL='C', LC_MESSAGES='C', LC_CTYPE='C')

    lsusb_path = module.get_bin_path('lsusb', required=True)
    parse_lsusb(module, lsusb_path)


if __name__ == '__main__':
    main()
