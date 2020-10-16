# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import mock
import pytest

from ansible_collections.community.general.tests.unit.compat import unittest
from ansible_collections.community.general.plugins.modules.monitoring import monit
from ansible_collections.community.general.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson


TEST_OUTPUT = """
Process '%s'
  status                       %s
  monitoring status            Not monitored
  monitoring mode              active
"""


class MonitTest(unittest.TestCase):
    def setUp(self):
        self.module = mock.MagicMock()
        self.module.exit_json.side_effect = AnsibleExitJson
        self.module.fail_json.side_effect = AnsibleFailJson
        self.monit = monit.Monit(self.module, 'monit', 'processX', 1)

    def patch_status(self, side_effect):
        if not isinstance(side_effect, list):
            side_effect = [side_effect]
        return mock.patch.object(self.monit, 'get_status', side_effect=side_effect)

    def test_min_version(self):
        with mock.patch.object(self.monit, 'monit_version', return_value=(5, 20)):
            with self.assertRaises(AnsibleFailJson):
                self.monit.check_version()

    def test_change_state_success(self):
        with self.patch_status(monit.Status.NOT_MONITORED):
            with self.assertRaises(AnsibleExitJson):
                self.monit.stop()
        self.module.fail_json.assert_not_called()
        self.module.run_command.assert_called_with('monit stop processX', check_rc=True)

    def test_change_state_fail(self):
        with self.patch_status(monit.Status.OK):
            with self.assertRaises(AnsibleFailJson):
                self.monit.stop()

    def test_reload_fail(self):
        self.module.run_command.return_value = (1, 'stdout', 'stderr')
        with self.assertRaises(AnsibleFailJson):
            self.monit.reload()

    def test_reload(self):
        self.module.run_command.return_value = (0, '', '')
        with self.patch_status(monit.Status.OK) as get_status:
            with self.assertRaises(AnsibleExitJson):
                self.monit.reload()

    def test_wait_for_status(self):
        self.monit._sleep_time = 0
        status = [
            monit.Status.MISSING,
            monit.Status.DOES_NOT_EXIST,
            monit.Status.INITIALIZING,
            monit.Status.OK.pending(),
            monit.Status.OK
        ]
        with self.patch_status(status) as get_status:
            self.monit.wait_for_monit_to_stop_pending('ok')
            self.assertEqual(get_status.call_count, len(status))

    def test_monitor(self):
        with self.patch_status(monit.Status.OK.pending()):
            with self.assertRaises(AnsibleExitJson):
                self.monit.monitor()

    def test_monitor_fail(self):
        with self.patch_status(monit.Status.NOT_MONITORED):
            with self.assertRaises(AnsibleFailJson):
                self.monit.monitor()

    def test_timeout(self):
        self.monit.timeout = 0
        with self.patch_status(monit.Status.NOT_MONITORED.pending()):
            with self.assertRaises(AnsibleFailJson):
                self.monit.wait_for_monit_to_stop_pending('stopped')


@pytest.mark.parametrize('status_name', [name for name in monit.StatusValue.ALL_STATUS])
def test_status_value(status_name):
    value = getattr(monit.StatusValue, status_name.upper())
    status = monit.StatusValue(value)
    assert getattr(status, 'is_%s' % status_name)
    assert not all(getattr(status, 'is_%s' % name) for name in monit.StatusValue.ALL_STATUS if name != status_name)


BASIC_OUTPUT_CASES = [
    (TEST_OUTPUT % ('processX', name), getattr(monit.Status, name.upper()))
    for name in monit.StatusValue.ALL_STATUS
]


@pytest.mark.parametrize('output, expected', BASIC_OUTPUT_CASES + [
    ('', monit.Status.MISSING),
    (TEST_OUTPUT % ('processY', 'OK'), monit.Status.MISSING),
    (TEST_OUTPUT % ('processX', 'Not Monitored - start pending'), monit.Status.OK),
    (TEST_OUTPUT % ('processX', 'Monitored - stop pending'), monit.Status.NOT_MONITORED),
    (TEST_OUTPUT % ('processX', 'Monitored - restart pending'), monit.Status.OK),
    (TEST_OUTPUT % ('processX', 'Not Monitored - monitor pending'), monit.Status.OK),
    (TEST_OUTPUT % ('processX', 'Does not exist'), monit.Status.DOES_NOT_EXIST),
    (TEST_OUTPUT % ('processX', 'Not monitored'), monit.Status.NOT_MONITORED),
])
def test_parse_status(output, expected):
    status = monit.Monit(None, '', 'processX', 0)._parse_status(output)
    assert status == expected
