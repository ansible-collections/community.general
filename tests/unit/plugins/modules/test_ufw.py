# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.community.general.tests.unit.compat import unittest
from ansible_collections.community.general.tests.unit.compat.mock import patch
from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes
import ansible_collections.community.general.plugins.modules.system.ufw as module

import json


# mock ufw messages

ufw_version_35 = """ufw 0.35\nCopyright 2008-2015 Canonical Ltd.\n"""

ufw_verbose_header = """Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), deny (routed)
New profiles: skip

To                         Action      From
--                         ------      ----"""


ufw_status_verbose_with_port_7000 = ufw_verbose_header + """
7000/tcp                   ALLOW IN    Anywhere
7000/tcp (v6)              ALLOW IN    Anywhere (v6)
"""

user_rules_with_port_7000 = """### tuple ### allow tcp 7000 0.0.0.0/0 any 0.0.0.0/0 in
### tuple ### allow tcp 7000 ::/0 any ::/0 in
"""

user_rules_with_ipv6 = """### tuple ### allow udp 5353 0.0.0.0/0 any 224.0.0.251 in
### tuple ### allow udp 5353 ::/0 any ff02::fb in
"""

ufw_status_verbose_with_ipv6 = ufw_verbose_header + """
5353/udp                   ALLOW IN    224.0.0.251
5353/udp                   ALLOW IN    ff02::fb
"""

ufw_status_verbose_nothing = ufw_verbose_header

skippg_adding_existing_rules = "Skipping adding existing rule\nSkipping adding existing rule (v6)\n"

grep_config_cli = "grep -h '^### tuple' /lib/ufw/user.rules /lib/ufw/user6.rules /etc/ufw/user.rules /etc/ufw/user6.rules "
grep_config_cli += "/var/lib/ufw/user.rules /var/lib/ufw/user6.rules"

dry_mode_cmd_with_port_700 = {
    "ufw status verbose": ufw_status_verbose_with_port_7000,
    "ufw --version": ufw_version_35,
    "ufw --dry-run allow from any to any port 7000 proto tcp": skippg_adding_existing_rules,
    "ufw --dry-run insert 1 allow from any to any port 7000 proto tcp": skippg_adding_existing_rules,
    "ufw --dry-run delete allow from any to any port 7000 proto tcp": "",
    "ufw --dry-run delete allow from any to any port 7001 proto tcp": user_rules_with_port_7000,
    "ufw --dry-run route allow in on foo out on bar from 1.1.1.1 port 7000 to 8.8.8.8 port 7001 proto tcp": "",
    "ufw --dry-run allow in on foo from any to any port 7003 proto tcp": "",
    "ufw --dry-run allow in on foo from 1.1.1.1 port 7002 to 8.8.8.8 port 7003 proto tcp": "",
    "ufw --dry-run allow out on foo from any to any port 7004 proto tcp": "",
    "ufw --dry-run allow out on foo from 1.1.1.1 port 7003 to 8.8.8.8 port 7004 proto tcp": "",
    grep_config_cli: user_rules_with_port_7000
}

# setup configuration :
# ufw reset
# ufw enable
# ufw allow proto udp to any port 5353 from 224.0.0.251
# ufw allow proto udp to any port 5353 from ff02::fb
dry_mode_cmd_with_ipv6 = {
    "ufw status verbose": ufw_status_verbose_with_ipv6,
    "ufw --version": ufw_version_35,
    # CONTENT of the command sudo ufw --dry-run delete allow in from ff02::fb port 5353 proto udp | grep -E "^### tupple"
    "ufw --dry-run delete allow from ff02::fb to any port 5353 proto udp": "### tuple ### allow udp any ::/0 5353 ff02::fb in",
    grep_config_cli: user_rules_with_ipv6,
    "ufw --dry-run allow from ff02::fb to any port 5353 proto udp": skippg_adding_existing_rules,
    "ufw --dry-run allow from 224.0.0.252 to any port 5353 proto udp": """### tuple ### allow udp 5353 0.0.0.0/0 any 224.0.0.251 in
### tuple ### allow udp 5353 0.0.0.0/0 any 224.0.0.252 in
""",
    "ufw --dry-run allow from 10.0.0.0/24 to any port 1577 proto udp": "### tuple ### allow udp 1577 0.0.0.0/0 any 10.0.0.0/24 in"
}

dry_mode_cmd_nothing = {
    "ufw status verbose": ufw_status_verbose_nothing,
    "ufw --version": ufw_version_35,
    grep_config_cli: "",
    "ufw --dry-run allow from any to :: port 23": "### tuple ### allow any 23 :: any ::/0 in"
}


def do_nothing_func_nothing(*args, **kwarg):
    return 0, dry_mode_cmd_nothing[args[0]], ""


def do_nothing_func_ipv6(*args, **kwarg):
    return 0, dry_mode_cmd_with_ipv6[args[0]], ""


def do_nothing_func_port_7000(*args, **kwarg):
    return 0, dry_mode_cmd_with_port_700[args[0]], ""


def set_module_args(args):
    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    """prepare arguments so that they will be picked up during module creation"""
    basic._ANSIBLE_ARGS = to_bytes(args)


class AnsibleExitJson(Exception):
    """Exception class to be raised by module.exit_json and caught by the test case"""
    pass


class AnsibleFailJson(Exception):
    """Exception class to be raised by module.fail_json and caught by the test case"""
    pass


def exit_json(*args, **kwargs):
    """function to patch over exit_json; package return data into an exception"""
    if 'changed' not in kwargs:
        kwargs['changed'] = False
    raise AnsibleExitJson(kwargs)


def fail_json(*args, **kwargs):
    """function to patch over fail_json; package return data into an exception"""
    kwargs['failed'] = True
    raise AnsibleFailJson(kwargs)


def get_bin_path(self, arg, required=False):
    """Mock AnsibleModule.get_bin_path"""
    return arg


class TestUFW(unittest.TestCase):

    def setUp(self):
        self.mock_module_helper = patch.multiple(basic.AnsibleModule,
                                                 exit_json=exit_json,
                                                 fail_json=fail_json,
                                                 get_bin_path=get_bin_path)
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)

    def test_filter_line_that_contains_ipv4(self):
        reg = module.compile_ipv4_regexp()

        self.assertTrue(reg.search("### tuple ### allow udp 5353 ::/0 any ff02::fb in") is None)
        self.assertTrue(reg.search("### tuple ### allow udp 5353 0.0.0.0/0 any 224.0.0.251 in") is not None)

        self.assertTrue(reg.match("ff02::fb") is None)
        self.assertTrue(reg.match("224.0.0.251") is not None)
        self.assertTrue(reg.match("10.0.0.0/8") is not None)
        self.assertTrue(reg.match("somethingElse") is None)
        self.assertTrue(reg.match("::") is None)
        self.assertTrue(reg.match("any") is None)

    def test_filter_line_that_contains_ipv6(self):
        reg = module.compile_ipv6_regexp()
        self.assertTrue(reg.search("### tuple ### allow udp 5353 ::/0 any ff02::fb in") is not None)
        self.assertTrue(reg.search("### tuple ### allow udp 5353 0.0.0.0/0 any 224.0.0.251 in") is None)
        self.assertTrue(reg.search("### tuple ### allow any 23 :: any ::/0 in") is not None)
        self.assertTrue(reg.match("ff02::fb") is not None)
        self.assertTrue(reg.match("224.0.0.251") is None)
        self.assertTrue(reg.match("::") is not None)

    def test_check_mode_add_rules(self):
        set_module_args({
            'rule': 'allow',
            'proto': 'tcp',
            'port': '7000',
            '_ansible_check_mode': True
        })
        result = self.__getResult(do_nothing_func_port_7000)
        self.assertFalse(result.exception.args[0]['changed'])

    def test_check_mode_add_insert_rules(self):
        set_module_args({
            'insert': '1',
            'rule': 'allow',
            'proto': 'tcp',
            'port': '7000',
            '_ansible_check_mode': True
        })
        result = self.__getResult(do_nothing_func_port_7000)
        self.assertFalse(result.exception.args[0]['changed'])

    def test_check_mode_add_detailed_route(self):
        set_module_args({
            'rule': 'allow',
            'route': 'yes',
            'interface_in': 'foo',
            'interface_out': 'bar',
            'proto': 'tcp',
            'from_ip': '1.1.1.1',
            'to_ip': '8.8.8.8',
            'from_port': '7000',
            'to_port': '7001',
            '_ansible_check_mode': True
        })

        result = self.__getResult(do_nothing_func_port_7000)
        self.assertTrue(result.exception.args[0]['changed'])

    def test_check_mode_add_ambiguous_route(self):
        set_module_args({
            'rule': 'allow',
            'route': 'yes',
            'interface_in': 'foo',
            'interface_out': 'bar',
            'direction': 'in',
            'interface': 'baz',
            '_ansible_check_mode': True
        })

        with self.assertRaises(AnsibleFailJson) as result:
            self.__getResult(do_nothing_func_port_7000)

        exc = result.exception.args[0]
        self.assertTrue(exc['failed'])
        self.assertIn('mutually exclusive', exc['msg'])

    def test_check_mode_add_interface_in(self):
        set_module_args({
            'rule': 'allow',
            'proto': 'tcp',
            'port': '7003',
            'interface_in': 'foo',
            '_ansible_check_mode': True
        })
        result = self.__getResult(do_nothing_func_port_7000)
        self.assertTrue(result.exception.args[0]['changed'])

    def test_check_mode_add_interface_out(self):
        set_module_args({
            'rule': 'allow',
            'proto': 'tcp',
            'port': '7004',
            'interface_out': 'foo',
            '_ansible_check_mode': True
        })
        result = self.__getResult(do_nothing_func_port_7000)
        self.assertTrue(result.exception.args[0]['changed'])

    def test_check_mode_add_non_route_interface_both(self):
        set_module_args({
            'rule': 'allow',
            'proto': 'tcp',
            'port': '7004',
            'interface_in': 'foo',
            'interface_out': 'bar',
            '_ansible_check_mode': True
        })

        with self.assertRaises(AnsibleFailJson) as result:
            self.__getResult(do_nothing_func_port_7000)

        exc = result.exception.args[0]
        self.assertTrue(exc['failed'])
        self.assertIn('combine', exc['msg'])

    def test_check_mode_add_direction_in(self):
        set_module_args({
            'rule': 'allow',
            'proto': 'tcp',
            'port': '7003',
            'direction': 'in',
            'interface': 'foo',
            '_ansible_check_mode': True
        })
        result = self.__getResult(do_nothing_func_port_7000)
        self.assertTrue(result.exception.args[0]['changed'])

    def test_check_mode_add_direction_in_with_ip(self):
        set_module_args({
            'rule': 'allow',
            'proto': 'tcp',
            'from_ip': '1.1.1.1',
            'from_port': '7002',
            'to_ip': '8.8.8.8',
            'to_port': '7003',
            'direction': 'in',
            'interface': 'foo',
            '_ansible_check_mode': True
        })
        result = self.__getResult(do_nothing_func_port_7000)
        self.assertTrue(result.exception.args[0]['changed'])

    def test_check_mode_add_direction_out(self):
        set_module_args({
            'rule': 'allow',
            'proto': 'tcp',
            'port': '7004',
            'direction': 'out',
            'interface': 'foo',
            '_ansible_check_mode': True
        })
        result = self.__getResult(do_nothing_func_port_7000)
        self.assertTrue(result.exception.args[0]['changed'])

    def test_check_mode_add_direction_out_with_ip(self):
        set_module_args({
            'rule': 'allow',
            'proto': 'tcp',
            'from_ip': '1.1.1.1',
            'from_port': '7003',
            'to_ip': '8.8.8.8',
            'to_port': '7004',
            'direction': 'out',
            'interface': 'foo',
            '_ansible_check_mode': True
        })
        result = self.__getResult(do_nothing_func_port_7000)
        self.assertTrue(result.exception.args[0]['changed'])

    def test_check_mode_delete_existing_rules(self):

        set_module_args({
            'rule': 'allow',
            'proto': 'tcp',
            'port': '7000',
            'delete': 'yes',
            '_ansible_check_mode': True,
        })

        self.assertTrue(self.__getResult(do_nothing_func_port_7000).exception.args[0]['changed'])

    def test_check_mode_delete_existing_insert_rules(self):

        set_module_args({
            'insert': '1',
            'rule': 'allow',
            'proto': 'tcp',
            'port': '7000',
            'delete': 'yes',
            '_ansible_check_mode': True,
        })

        self.assertTrue(self.__getResult(do_nothing_func_port_7000).exception.args[0]['changed'])

    def test_check_mode_delete_not_existing_rules(self):

        set_module_args({
            'rule': 'allow',
            'proto': 'tcp',
            'port': '7001',
            'delete': 'yes',
            '_ansible_check_mode': True,
        })

        self.assertFalse(self.__getResult(do_nothing_func_port_7000).exception.args[0]['changed'])

    def test_check_mode_delete_not_existing_insert_rules(self):

        set_module_args({
            'insert': '1',
            'rule': 'allow',
            'proto': 'tcp',
            'port': '7001',
            'delete': 'yes',
            '_ansible_check_mode': True,
        })

        self.assertFalse(self.__getResult(do_nothing_func_port_7000).exception.args[0]['changed'])

    def test_enable_mode(self):
        set_module_args({
            'state': 'enabled',
            '_ansible_check_mode': True
        })

        self.assertFalse(self.__getResult(do_nothing_func_port_7000).exception.args[0]['changed'])

    def test_disable_mode(self):
        set_module_args({
            'state': 'disabled',
            '_ansible_check_mode': True
        })

        self.assertTrue(self.__getResult(do_nothing_func_port_7000).exception.args[0]['changed'])

    def test_logging_off(self):
        set_module_args({
            'logging': 'off',
            '_ansible_check_mode': True
        })

        self.assertTrue(self.__getResult(do_nothing_func_port_7000).exception.args[0]['changed'])

    def test_logging_on(self):
        set_module_args({
            'logging': 'on',
            '_ansible_check_mode': True
        })

        self.assertFalse(self.__getResult(do_nothing_func_port_7000).exception.args[0]['changed'])

    def test_default_changed(self):
        set_module_args({
            'default': 'allow',
            "direction": "incoming",
            '_ansible_check_mode': True
        })
        self.assertTrue(self.__getResult(do_nothing_func_port_7000).exception.args[0]['changed'])

    def test_default_not_changed(self):
        set_module_args({
            'default': 'deny',
            "direction": "incoming",
            '_ansible_check_mode': True
        })
        self.assertFalse(self.__getResult(do_nothing_func_port_7000).exception.args[0]['changed'])

    def test_ipv6_remove(self):
        set_module_args({
            'rule': 'allow',
            'proto': 'udp',
            'port': '5353',
            'from': 'ff02::fb',
            'delete': 'yes',
            '_ansible_check_mode': True,
        })
        self.assertTrue(self.__getResult(do_nothing_func_ipv6).exception.args[0]['changed'])

    def test_ipv6_add_existing(self):
        set_module_args({
            'rule': 'allow',
            'proto': 'udp',
            'port': '5353',
            'from': 'ff02::fb',
            '_ansible_check_mode': True,
        })
        self.assertFalse(self.__getResult(do_nothing_func_ipv6).exception.args[0]['changed'])

    def test_add_not_existing_ipv4_submask(self):
        set_module_args({
            'rule': 'allow',
            'proto': 'udp',
            'port': '1577',
            'from': '10.0.0.0/24',
            '_ansible_check_mode': True,
        })
        self.assertTrue(self.__getResult(do_nothing_func_ipv6).exception.args[0]['changed'])

    def test_ipv4_add_with_existing_ipv6(self):
        set_module_args({
            'rule': 'allow',
            'proto': 'udp',
            'port': '5353',
            'from': '224.0.0.252',
            '_ansible_check_mode': True,
        })
        self.assertTrue(self.__getResult(do_nothing_func_ipv6).exception.args[0]['changed'])

    def test_ipv6_add_from_nothing(self):
        set_module_args({
            'rule': 'allow',
            'port': '23',
            'to': '::',
            '_ansible_check_mode': True,
        })
        result = self.__getResult(do_nothing_func_nothing).exception.args[0]
        print(result)
        self.assertTrue(result['changed'])

    def __getResult(self, cmd_fun):
        with patch.object(basic.AnsibleModule, 'run_command') as mock_run_command:
            mock_run_command.side_effect = cmd_fun
            with self.assertRaises(AnsibleExitJson) as result:
                module.main()
        return result
