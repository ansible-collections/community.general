# Copyright (c) 2017, Roman Belyakovsky <ihryamzik () gmail.com>
#
# This file is part of Ansible
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.community.internal_test_tools.tests.unit.compat import unittest
from ansible_collections.community.general.plugins.modules import interfaces_file
from shutil import copyfile, move
import difflib
import inspect
import io
import json
import os
import re
import shutil
import tempfile


class AnsibleFailJson(Exception):
    pass


class ModuleMocked:
    def atomic_move(self, src, dst):
        move(src, dst)

    def backup_local(self, path):
        backupp = os.path.join("/tmp", os.path.basename(path) + ".bak")
        copyfile(path, backupp)
        return backupp

    def fail_json(self, msg):
        raise AnsibleFailJson(msg)


module = ModuleMocked()
fixture_path = os.path.join(os.path.dirname(__file__), 'interfaces_file_fixtures', 'input')
golden_output_path = os.path.join(os.path.dirname(__file__), 'interfaces_file_fixtures', 'golden_output')


class TestInterfacesFileModule(unittest.TestCase):
    unittest.TestCase.maxDiff = None

    def getTestFiles(self, include_filter=None, exclude_filter=None):
        flist = next(os.walk(fixture_path))[2]
        flist = [file for file in flist if not file.endswith('.license')]
        if include_filter:
            flist = filter(lambda x: re.match(include_filter, x), flist)
        if exclude_filter:
            flist = filter(lambda x: not re.match(exclude_filter, x), flist)
        return flist

    def compareFileToBackup(self, path, backup):
        with open(path) as f1:
            with open(backup) as f2:
                diffs = difflib.context_diff(f1.readlines(),
                                             f2.readlines(),
                                             fromfile=os.path.basename(path),
                                             tofile=os.path.basename(backup))
        # Restore backup
        move(backup, path)
        deltas = list(diffs)
        self.assertTrue(len(deltas) == 0)

    def compareInterfacesLinesToFile(self, interfaces_lines, path, testname=None):
        if not testname:
            testname = "%s.%s" % (path, inspect.stack()[1][3])
        self.compareStringWithFile("".join([d['line'] for d in interfaces_lines if 'line' in d]), testname)

    def compareInterfacesToFile(self, ifaces, path, testname=None):
        if not testname:
            testname = "%s.%s.json" % (path, inspect.stack()[1][3])

        testfilepath = os.path.join(golden_output_path, testname)
        string = json.dumps(ifaces, sort_keys=True, indent=4, separators=(',', ': '))
        if string and not string.endswith('\n'):
            string += '\n'
        goldenstring = string
        goldenData = ifaces
        if not os.path.isfile(testfilepath):
            with io.open(testfilepath, 'wb') as f:
                f.write(string.encode())
        else:
            with open(testfilepath, 'r') as goldenfile:
                goldenData = json.load(goldenfile)
        self.assertEqual(goldenData, ifaces)

    def compareStringWithFile(self, string, path):
        testfilepath = os.path.join(golden_output_path, path)
        if string and not string.endswith('\n'):
            string += '\n'
        goldenstring = string
        if not os.path.isfile(testfilepath):
            f = io.open(testfilepath, 'wb')
            f.write(string.encode())
            f.close()
        else:
            with open(testfilepath, 'r') as goldenfile:
                goldenstring = goldenfile.read()
                goldenfile.close()
        self.assertEqual(goldenstring, string)

    def test_no_changes(self):
        for testfile in self.getTestFiles():
            path = os.path.join(fixture_path, testfile)
            lines, ifaces = interfaces_file.read_interfaces_file(module, path)
            self.compareInterfacesLinesToFile(lines, testfile)
            self.compareInterfacesToFile(ifaces, testfile)

    def test_add_up_option_to_aggi(self):
        testcases = {
            "add_aggi_up": [
                {
                    'iface': 'aggi',
                    'option': 'up',
                    'value': 'route add -net 224.0.0.0 netmask 240.0.0.0 dev aggi',
                    'state': 'present',
                }
            ],
            "add_and_delete_aggi_up": [
                {
                    'iface': 'aggi',
                    'option': 'up',
                    'value': 'route add -net 224.0.0.0 netmask 240.0.0.0 dev aggi',
                    'state': 'present',
                },
                {
                    'iface': 'aggi',
                    'option': 'up',
                    'value': None,
                    'state': 'absent',
                },
            ],
            "add_aggi_up_twice": [
                {
                    'iface': 'aggi',
                    'option': 'up',
                    'value': 'route add -net 224.0.0.0 netmask 240.0.0.0 dev aggi',
                    'state': 'present',
                },
                {
                    'iface': 'aggi',
                    'option': 'up',
                    'value': 'route add -net 224.0.0.0 netmask 240.0.0.0 dev aggi',
                    'state': 'present',
                },
            ],
            "aggi_remove_dup": [
                {
                    'iface': 'aggi',
                    'option': 'up',
                    'value': None,
                    'state': 'absent',
                },
                {
                    'iface': 'aggi',
                    'option': 'up',
                    'value': 'route add -net 224.0.0.0 netmask 240.0.0.0 dev aggi',
                    'state': 'present',
                },
            ],
            "set_aggi_slaves": [
                {
                    'iface': 'aggi',
                    'option': 'slaves',
                    'value': 'int1  int3',
                    'state': 'present',
                },
            ],
            "set_aggi_and_eth0_mtu": [
                {
                    'iface': 'aggi',
                    'option': 'mtu',
                    'value': '1350',
                    'state': 'present',
                },
                {
                    'iface': 'eth0',
                    'option': 'mtu',
                    'value': '1350',
                    'state': 'present',
                },
            ],
        }
        for testname, options_list in testcases.items():
            for testfile in self.getTestFiles():
                path = os.path.join(fixture_path, testfile)
                lines, ifaces = interfaces_file.read_interfaces_file(module, path)
                fail_json_iterations = []
                for i, options in enumerate(options_list):
                    try:
                        dummy, lines = interfaces_file.set_interface_option(module, lines, options['iface'], options['option'],
                                                                            options['value'], options['state'])
                    except AnsibleFailJson as e:
                        fail_json_iterations.append("[%d] fail_json message: %s\noptions:\n%s" %
                                                    (i, str(e), json.dumps(options, sort_keys=True, indent=4, separators=(',', ': '))))
                self.compareStringWithFile("\n=====\n".join(fail_json_iterations), "%s_%s.exceptions.txt" % (testfile, testname))

                self.compareInterfacesLinesToFile(lines, testfile, "%s_%s" % (testfile, testname))
                self.compareInterfacesToFile(ifaces, testfile, "%s_%s.json" % (testfile, testname))

    def test_revert(self):
        testcases = {
            "revert": [
                {
                    'iface': 'eth0',
                    'option': 'mtu',
                    'value': '1350',
                }
            ],
        }
        for testname, options_list in testcases.items():
            for testfile in self.getTestFiles():
                with tempfile.NamedTemporaryFile() as temp_file:
                    src_path = os.path.join(fixture_path, testfile)
                    path = temp_file.name
                    shutil.copy(src_path, path)
                    lines, ifaces = interfaces_file.read_interfaces_file(module, path)
                    backupp = module.backup_local(path)
                    options = options_list[0]
                    for state in ['present', 'absent']:
                        fail_json_iterations = []
                        options['state'] = state
                        try:
                            dummy, lines = interfaces_file.set_interface_option(module, lines,
                                                                                options['iface'], options['option'], options['value'], options['state'])
                        except AnsibleFailJson as e:
                            fail_json_iterations.append("fail_json message: %s\noptions:\n%s" %
                                                        (str(e), json.dumps(options, sort_keys=True, indent=4, separators=(',', ': '))))
                        interfaces_file.write_changes(module, [d['line'] for d in lines if 'line' in d], path)

                    self.compareStringWithFile("\n=====\n".join(fail_json_iterations), "%s_%s.exceptions.txt" % (testfile, testname))

                    self.compareInterfacesLinesToFile(lines, testfile, "%s_%s" % (testfile, testname))
                    self.compareInterfacesToFile(ifaces, testfile, "%s_%s.json" % (testfile, testname))
                    if testfile not in ["no_leading_spaces"]:
                        # skip if eth0 has MTU value
                        self.compareFileToBackup(path, backupp)

    def test_change_method(self):
        testcases = {
            "change_method": [
                {
                    'iface': 'eth1',
                    'option': 'method',
                    'value': 'dhcp',
                    'state': 'present',
                }
            ],
        }
        for testname, options_list in testcases.items():
            for testfile in self.getTestFiles():
                with tempfile.NamedTemporaryFile() as temp_file:
                    src_path = os.path.join(fixture_path, testfile)
                    path = temp_file.name
                    shutil.copy(src_path, path)
                    lines, ifaces = interfaces_file.read_interfaces_file(module, path)
                    backupp = module.backup_local(path)
                    options = options_list[0]
                    fail_json_iterations = []
                    try:
                        changed, lines = interfaces_file.set_interface_option(module, lines, options['iface'], options['option'],
                                                                              options['value'], options['state'])
                        # When a changed is made try running it again for proper idempotency
                        if changed:
                            changed_again, lines = interfaces_file.set_interface_option(module, lines, options['iface'],
                                                                                        options['option'], options['value'], options['state'])
                            self.assertFalse(changed_again,
                                             msg='Second request for change should return false for {0} running on {1}'.format(testname,
                                                                                                                               testfile))
                    except AnsibleFailJson as e:
                        fail_json_iterations.append("fail_json message: %s\noptions:\n%s" %
                                                    (str(e), json.dumps(options, sort_keys=True, indent=4, separators=(',', ': '))))
                    interfaces_file.write_changes(module, [d['line'] for d in lines if 'line' in d], path)

                    self.compareStringWithFile("\n=====\n".join(fail_json_iterations), "%s_%s.exceptions.txt" % (testfile, testname))

                    self.compareInterfacesLinesToFile(lines, testfile, "%s_%s" % (testfile, testname))
                    self.compareInterfacesToFile(ifaces, testfile, "%s_%s.json" % (testfile, testname))
                    # Restore backup
                    move(backupp, path)

    def test_getValueFromLine(self):
        testcases = [
            {
                "line": "  address   1.2.3.5",
                "value": "1.2.3.5",
            }
        ]
        for testcase in testcases:
            value = interfaces_file.getValueFromLine(testcase["line"])
            self.assertEqual(testcase["value"], value)

    def test_get_interface_options(self):
        testcases = {
            "basic": {
                "iface_lines": [
                    {
                        "address_family": "inet",
                        "iface": "eno1",
                        "line": "iface eno1 inet static",
                        "line_type": "iface",
                        "params": {
                            "address": "",
                            "address_family": "inet",
                            "down": [],
                            "gateway": "",
                            "method": "static",
                            "netmask": "",
                            "post-up": [],
                            "pre-up": [],
                            "up": []
                        }
                    },
                    {
                        "address_family": "inet",
                        "iface": "eno1",
                        "line": "  address   1.2.3.5",
                        "line_type": "option",
                        "option": "address",
                        "value": "1.2.3.5"
                    },
                    {
                        "address_family": "inet",
                        "iface": "eno1",
                        "line": "  netmask   255.255.255.0",
                        "line_type": "option",
                        "option": "netmask",
                        "value": "255.255.255.0"
                    },
                    {
                        "address_family": "inet",
                        "iface": "eno1",
                        "line": "  gateway   1.2.3.1",
                        "line_type": "option",
                        "option": "gateway",
                        "value": "1.2.3.1"
                    }
                ],
                "iface_options": [
                    {
                        "address_family": "inet",
                        "iface": "eno1",
                        "line": "  address   1.2.3.5",
                        "line_type": "option",
                        "option": "address",
                        "value": "1.2.3.5"
                    },
                    {
                        "address_family": "inet",
                        "iface": "eno1",
                        "line": "  netmask   255.255.255.0",
                        "line_type": "option",
                        "option": "netmask",
                        "value": "255.255.255.0"
                    },
                    {
                        "address_family": "inet",
                        "iface": "eno1",
                        "line": "  gateway   1.2.3.1",
                        "line_type": "option",
                        "option": "gateway",
                        "value": "1.2.3.1"
                    }
                ]
            },
        }

        for testname in testcases.keys():
            iface_options = interfaces_file.get_interface_options(testcases[testname]["iface_lines"])
            self.assertEqual(testcases[testname]["iface_options"], iface_options)

    def test_get_interface_options(self):
        testcases = {
            "select address": {
                "iface_options": [
                    {
                        "address_family": "inet",
                        "iface": "eno1",
                        "line": "  address   1.2.3.5",
                        "line_type": "option",
                        "option": "address",
                        "value": "1.2.3.5"
                    },
                    {
                        "address_family": "inet",
                        "iface": "eno1",
                        "line": "  netmask   255.255.255.0",
                        "line_type": "option",
                        "option": "netmask",
                        "value": "255.255.255.0"
                    },
                    {
                        "address_family": "inet",
                        "iface": "eno1",
                        "line": "  gateway   1.2.3.1",
                        "line_type": "option",
                        "option": "gateway",
                        "value": "1.2.3.1"
                    }
                ],
                "target_options": [
                    {
                        "address_family": "inet",
                        "iface": "eno1",
                        "line": "  address   1.2.3.5",
                        "line_type": "option",
                        "option": "address",
                        "value": "1.2.3.5"
                    }
                ],
                "option": "address"
            },
        }

        for testname in testcases.keys():
            target_options = interfaces_file.get_target_options(testcases[testname]["iface_options"], testcases[testname]["option"])
            self.assertEqual(testcases[testname]["target_options"], target_options)

    def test_update_existing_option_line(self):
        testcases = {
            "update address": {
                "target_option": {
                    "address_family": "inet",
                    "iface": "eno1",
                    "line": "  address   1.2.3.5",
                    "line_type": "option",
                    "option": "address",
                    "value": "1.2.3.5"
                },
                "value": "1.2.3.4",
                "result": "  address   1.2.3.4",
            },
        }

        for testname in testcases.keys():
            updated = interfaces_file.update_existing_option_line(testcases[testname]["target_option"], testcases[testname]["value"])
            self.assertEqual(testcases[testname]["result"], updated)

    def test_predefined(self):
        testcases = {
            "idempotency": {
                "source_lines": [
                    "iface eno1 inet static",
                    "  address   1.2.3.5",
                    "  netmask   255.255.255.0",
                    "  gateway   1.2.3.1",
                ],
                "input": {
                    "iface": "eno1",
                    "option": "address",
                    "value": "1.2.3.5",
                    'state': 'present',
                },
                "result_lines": [
                    "iface eno1 inet static",
                    "  address   1.2.3.5",
                    "  netmask   255.255.255.0",
                    "  gateway   1.2.3.1",
                ],
                "changed": False,
            },
        }

        for testname in testcases.keys():
            lines, ifaces = interfaces_file.read_interfaces_lines(module, testcases[testname]["source_lines"])
            changed, lines = interfaces_file.set_interface_option(module, lines, testcases[testname]["input"]['iface'], testcases[testname]["input"]['option'],
                                                                  testcases[testname]["input"]['value'], testcases[testname]["input"]['state'])
            self.assertEqual(testcases[testname]["result_lines"], [d['line'] for d in lines if 'line' in d])
            assert testcases[testname]['changed'] == changed

    def test_inet_inet6(self):
        testcases = {
            "change_ipv4": [
                {
                    'iface': 'eth0',
                    'address_family': 'inet',
                    'option': 'address',
                    'value': '192.168.0.42',
                    'state': 'present',
                }
            ],
            "change_ipv6": [
                {
                    'iface': 'eth0',
                    'address_family': 'inet6',
                    'option': 'address',
                    'value': 'fc00::42',
                    'state': 'present',
                }
            ],
            "change_ipv4_pre_up": [
                {
                    'iface': 'eth0',
                    'address_family': 'inet',
                    'option': 'pre-up',
                    'value': 'XXXX_ipv4',
                    'state': 'present',
                }
            ],
            "change_ipv6_pre_up": [
                {
                    'iface': 'eth0',
                    'address_family': 'inet6',
                    'option': 'pre-up',
                    'value': 'XXXX_ipv6',
                    'state': 'present',
                }
            ],
            "change_ipv4_post_up": [
                {
                    'iface': 'eth0',
                    'address_family': 'inet',
                    'option': 'post-up',
                    'value': 'XXXX_ipv4',
                    'state': 'present',
                }
            ],
            "change_ipv6_post_up": [
                {
                    'iface': 'eth0',
                    'address_family': 'inet6',
                    'option': 'post-up',
                    'value': 'XXXX_ipv6',
                    'state': 'present',
                }
            ],
        }
        for testname, options_list in testcases.items():
            for testfile in self.getTestFiles():
                with tempfile.NamedTemporaryFile() as temp_file:
                    src_path = os.path.join(fixture_path, testfile)
                    path = temp_file.name
                    shutil.copy(src_path, path)
                    lines, ifaces = interfaces_file.read_interfaces_file(module, path)
                    backupp = module.backup_local(path)
                    options = options_list[0]
                    fail_json_iterations = []
                    try:
                        dummy, lines = interfaces_file.set_interface_option(module, lines, options['iface'], options['option'],
                                                                            options['value'], options['state'], options['address_family'])
                    except AnsibleFailJson as e:
                        fail_json_iterations.append("fail_json message: %s\noptions:\n%s" %
                                                    (str(e), json.dumps(options, sort_keys=True, indent=4, separators=(',', ': '))))
                    interfaces_file.write_changes(module, [d['line'] for d in lines if 'line' in d], path)

                    self.compareStringWithFile("\n=====\n".join(fail_json_iterations), "%s_%s.exceptions.txt" % (testfile, testname))

                    self.compareInterfacesLinesToFile(lines, testfile, "%s_%s" % (testfile, testname))
                    self.compareInterfacesToFile(ifaces, testfile, "%s_%s.json" % (testfile, testname))
                    # Restore backup
                    move(backupp, path)
