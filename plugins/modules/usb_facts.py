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
short_description: Allows listing information about USB devices
version_added: 8.5.0
description:
  - Allows retrieving information about available USB devices through C(lsusb).
author:
  - Max Maxopoly (@maxopoly)
extends_documentation_fragment:
  - community.general.attributes
  - community.general.attributes.facts
  - community.general.attributes.facts_module
requirements:
  - lsusb binary on PATH (usually installed through the package usbutils and preinstalled on many systems)
'''

EXAMPLES = '''
- name: Get information about USB devices
  community.general.usb_facts:

- name: Print information about USB devices
  ansible.builtin.debug:
    msg: "On bus {{ item.bus }} device {{ item.device }} with id {{ item.id }} is {{ item.name }}"
  loop: "{{ ansible_facts.usb_devices }}"
'''

RETURN = r'''
ansible_facts:
  description: Dictionary containing details of connected USB devices.
  returned: always
  type: dict
  contains:
    usb_devices:
      description: A list of USB devices available.
      returned: always
      type: list
      elements: dict
      contains:
        bus:
          description: The bus the usb device is connected to.
          returned: always
          type: str
          sample: "001"
        device:
          description: The device number occupied on the bus.
          returned: always
          type: str
          sample: "002"
        id:
          description: ID of the USB device.
          returned: always
          type: str
          sample: "1d6b:0002"
        name:
          description: Human readable name of the device.
          returned: always
          type: str
          sample: Linux Foundation 2.0 root hub
'''

import re
from ansible.module_utils.basic import AnsibleModule


def parse_lsusb(module, lsusb_path):
    rc, stdout, stderr = module.run_command(lsusb_path, check_rc=True)
    regex = re.compile(r'^Bus (\d{3}) Device (\d{3}): ID ([0-9a-f]{4}:[0-9a-f]{4}) (.*)$')
    usb_devices = []
    for line in stdout.splitlines():
        match = re.match(regex, line)
        if not match:
            module.fail_json(msg="failed to parse unknown lsusb output %s" % (line), stdout=stdout, stderr=stderr)
        current_device = {
            'bus': match.group(1),
            'device': match.group(2),
            'id': match.group(3),
            'name': match.group(4)
        }
        usb_devices.append(current_device)
    return_value = {
        "usb_devices": usb_devices
    }
    module.exit_json(msg="parsed %s USB devices" % (len(usb_devices)), stdout=stdout, stderr=stderr, ansible_facts=return_value)


def main():
    module = AnsibleModule(
        {},
        supports_check_mode=True
    )

    # Set LANG env since we parse stdout
    module.run_command_environ_update = dict(LANGUAGE='C', LC_ALL='C')

    lsusb_path = module.get_bin_path('lsusb', required=True)
    parse_lsusb(module, lsusb_path)


if __name__ == '__main__':
    main()
