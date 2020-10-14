# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest import mock
from unittest.mock import MagicMock

from ansible_collections.community.general.tests.unit.compat import unittest
from ansible_collections.community.general.plugins.modules.monitoring import monit


class AnsibleExitJson(Exception):
    """Exception class to be raised by module.exit_json and caught by the test case"""
    pass


class AnsibleFailJson(Exception):
    """Exception class to be raised by module.fail_json and caught by the test case"""
    pass


class MonitTest(unittest.TestCase):
    def setUp(self):
        self.module = MagicMock()
        self.module.exit_json.side_effect = AnsibleExitJson(Exception)
        self.monit = monit.Monit(self.module, 'monit', 'processX', 1)
        self.version_patch = mock.patch.object(self.monit, "is_version_higher_than_5_18", return_value=True)
        self.version_patch.start()

    def tearDown(self):
        self.version_patch.stop()

    def patch_status(self, side_effect):
        return mock.patch.object(self.monit, 'get_status', side_effect=side_effect)

    def test_change_state_success(self):
        with self.patch_status(['not monitored']), self.assertRaises(AnsibleExitJson):
            self.monit.stop()
        self.module.fail_json.assert_not_called()
        self.module.run_command.assert_called_with('monit stop processX', check_rc=True)

    def test_change_state_fail(self):
        with self.patch_status(['monitored']):
            self.monit.stop()
        self.module.fail_json.assert_called()

    def test_reload_fail(self):
        self.module.run_command.return_value = (1, 'stdout', 'stderr')
        self.module.fail_json.side_effect = AnsibleFailJson(Exception)
        with self.assertRaises(AnsibleFailJson):
            self.monit.reload()

    def test_reload(self):
        self.module.run_command.return_value = (0, '', '')
        self.monit._sleep_time = 0
        with self.patch_status(['', 'pending', 'running']), self.assertRaises(AnsibleExitJson):
            self.monit.reload()

    def test_monitor(self):
        with self.patch_status(['not monitored - start pending']), self.assertRaises(AnsibleExitJson):
            self.monit.monitor()

    def test_monitor_fail(self):
        with self.patch_status(['not monitored']):
            self.monit.monitor()
        self.module.fail_json.assert_called()

    def test_timeout(self):
        self.monit.timeout = 0
        self.module.fail_json.side_effect = AnsibleFailJson(Exception)
        with self.patch_status(['stop pending']), self.assertRaises(AnsibleFailJson):
            self.monit.wait_for_monit_to_stop_pending('stopped')
