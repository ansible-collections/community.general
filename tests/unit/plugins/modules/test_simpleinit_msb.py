# Copyright (c) 2023 Vlad Glagolev <scm@vaygr.net>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import patch
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import AnsibleFailJson, ModuleTestCase, set_module_args

from ansible_collections.community.general.plugins.modules.simpleinit_msb import SimpleinitMSB, build_module


_TELINIT_LIST = """
RUNLEVEL SCRIPT
2        smgl-suspend-single
3        crond
3        fuse
3        network
3        nscd
3        smgl-default-remote-fs
3        smgl-misc
3        sshd
DEV        coldplug
DEV        devices
DEV        udevd
S        hostname.sh
S        hwclock.sh
S        keymap.sh
S        modutils
S        mountall.sh
S        mountroot.sh
S        single
S        smgl-default-crypt-fs
S        smgl-metalog
S        smgl-sysctl
S        sysstat
"""

_TELINIT_LIST_ENABLED = """
smgl-suspend-single
crond
fuse
network
nscd
smgl-default-remote-fs
smgl-misc
sshd
coldplug
devices
udevd
hostname.sh
hwclock.sh
keymap.sh
modutils
mountall.sh
mountroot.sh
single
smgl-default-crypt-fs
smgl-metalog
smgl-sysctl
"""

_TELINIT_LIST_DISABLED = """
sysstat
"""

_TELINIT_ALREADY_ENABLED = """
Service smgl-suspend-single already enabled.
"""

_TELINIT_ALREADY_DISABLED = """
Service smgl-suspend-single already disabled.
"""

_TELINIT_STATUS_RUNNING = """
sshd is running with Process ID(s) 8510 8508 2195
"""

_TELINIT_STATUS_RUNNING_NOT = """
/sbin/metalog is not running
"""


class TestSimpleinitMSB(ModuleTestCase):

    def setUp(self):
        super(TestSimpleinitMSB, self).setUp()

    def tearDown(self):
        super(TestSimpleinitMSB, self).tearDown()

    @patch('os.path.exists', return_value=True)
    @patch('ansible.module_utils.basic.AnsibleModule.get_bin_path', return_value="/sbin/telinit")
    def test_get_service_tools(self, *args, **kwargs):
        with set_module_args({
            'name': 'smgl-suspend-single',
            'state': 'running',
        }):
            simpleinit_msb = SimpleinitMSB(build_module())

            simpleinit_msb.get_service_tools()

            self.assertEqual(simpleinit_msb.telinit_cmd, "/sbin/telinit")

    @patch('ansible_collections.community.general.plugins.modules.simpleinit_msb.SimpleinitMSB.execute_command')
    def test_service_exists(self, execute_command):
        with set_module_args({
            'name': 'smgl-suspend-single',
            'state': 'running',
        }):
            simpleinit_msb = SimpleinitMSB(build_module())

            execute_command.return_value = (0, _TELINIT_LIST, "")

            simpleinit_msb.service_exists()

    @patch('ansible_collections.community.general.plugins.modules.simpleinit_msb.SimpleinitMSB.execute_command')
    def test_service_exists_not(self, execute_command):
        with set_module_args({
            'name': 'ntp',
            'state': 'running',
        }):
            simpleinit_msb = SimpleinitMSB(build_module())

            execute_command.return_value = (0, _TELINIT_LIST, "")

            with self.assertRaises(AnsibleFailJson) as context:
                simpleinit_msb.service_exists()

            self.assertEqual("telinit could not find the requested service: ntp", context.exception.args[0]["msg"])

    @patch('ansible_collections.community.general.plugins.modules.simpleinit_msb.SimpleinitMSB.service_exists')
    @patch('ansible_collections.community.general.plugins.modules.simpleinit_msb.SimpleinitMSB.execute_command')
    def test_check_service_enabled(self, execute_command, service_exists):
        with set_module_args({
            'name': 'nscd',
            'state': 'running',
            'enabled': 'true',
        }):
            simpleinit_msb = SimpleinitMSB(build_module())

            service_exists.return_value = True
            execute_command.return_value = (0, _TELINIT_LIST_ENABLED, "")

            self.assertTrue(simpleinit_msb.service_enabled())

            # Race condition check
            with patch('ansible_collections.community.general.plugins.modules.simpleinit_msb.SimpleinitMSB.service_enabled', return_value=False):
                execute_command.return_value = (0, "", _TELINIT_ALREADY_ENABLED)

                simpleinit_msb.service_enable()

                self.assertFalse(simpleinit_msb.changed)

    @patch('ansible_collections.community.general.plugins.modules.simpleinit_msb.SimpleinitMSB.service_exists')
    @patch('ansible_collections.community.general.plugins.modules.simpleinit_msb.SimpleinitMSB.execute_command')
    def test_check_service_disabled(self, execute_command, service_exists):
        with set_module_args({
            'name': 'sysstat',
            'state': 'stopped',
            'enabled': 'false',
        }):
            simpleinit_msb = SimpleinitMSB(build_module())

            service_exists.return_value = True
            execute_command.return_value = (0, _TELINIT_LIST_DISABLED, "")

            self.assertFalse(simpleinit_msb.service_enabled())

            # Race condition check
            with patch('ansible_collections.community.general.plugins.modules.simpleinit_msb.SimpleinitMSB.service_enabled', return_value=True):
                execute_command.return_value = (0, "", _TELINIT_ALREADY_DISABLED)

                simpleinit_msb.service_enable()

                self.assertFalse(simpleinit_msb.changed)

    @patch('ansible_collections.community.general.plugins.modules.simpleinit_msb.SimpleinitMSB.service_control')
    def test_check_service_running(self, service_control):
        with set_module_args({
            'name': 'sshd',
            'state': 'running',
        }):
            simpleinit_msb = SimpleinitMSB(build_module())

            service_control.return_value = (0, _TELINIT_STATUS_RUNNING, "")

            self.assertFalse(simpleinit_msb.get_service_status())

    @patch('ansible_collections.community.general.plugins.modules.simpleinit_msb.SimpleinitMSB.service_control')
    def test_check_service_running_not(self, service_control):
        with set_module_args({
            'name': 'smgl-metalog',
            'state': 'running',
        }):
            simpleinit_msb = SimpleinitMSB(build_module())

            service_control.return_value = (0, _TELINIT_STATUS_RUNNING_NOT, "")

            self.assertFalse(simpleinit_msb.get_service_status())
