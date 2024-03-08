# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.community.general.tests.unit.compat import mock
from ansible_collections.community.general.tests.unit.compat import unittest

from ansible_collections.community.general.plugins.modules import usb_facts


class TestUsbFacts(unittest.TestCase):

    def setUp(self):
        self.testing_data = [
            {
                "input": "Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub",
                "bus": "001",
                "device": "001",
                "id": "1d6b:0002",
                "name": "Linux Foundation 2.0 root hub"
            },
            {
                "input": "Bus 003 Device 002: ID 8087:8008 Intel Corp. Integrated Rate Matching Hub",
                "bus": "003",
                "device": "002",
                "id": "8087:8008",
                "name": "Intel Corp. Integrated Rate Matching Hub"
            }
        ]
        self.output_fields = ["bus", "device", "id", "name"]

    @mock.patch('ansible_collections.community.general.plugins.modules.usb_facts.AnsibleModule')
    def test_parsing_single_line(self, mock_module):
        usb_facts.LSUSB_PATH = ""
        mock_module.run_command.return_value = (0, command_output, None)
        for data in self.testing_data:
            command_output = data ["input"]
            command_result = usb_facts.parse_lsusb(mock_module)
            for output_field in self.output_fields:
                self.assertEqual(command_result["ansible_facts"][0][output_field], data[output_field])

    @mock.patch('ansible_collections.community.general.plugins.modules.usb_facts.AnsibleModule')
    def test_parsing_multiple_lines(self, mock_module):
        usb_facts.LSUSB_PATH = ""
        input = ""
        for data in self.testing_data:
            input.append("%s\n" % data["input"])
        mock_module.run_command.return_value = (0, input, None)
        command_result = usb_facts.parse_lsusb(mock_module)
        for index in range(0, len(self.testing_data)):
            for output_field in self.output_fields:
                self.assertEqual(command_result["ansible_facts"][index][output_field], data[index][output_field])