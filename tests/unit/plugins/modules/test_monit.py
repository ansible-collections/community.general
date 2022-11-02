# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import mock
import pytest

from ansible_collections.community.general.tests.unit.compat import unittest
from ansible_collections.community.general.plugins.modules import monit
from ansible_collections.community.general.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson


TEST_OUTPUT = """
%s '%s'
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
        self.monit._status_change_retry_count = 1
        mock_sleep = mock.patch('time.sleep')
        mock_sleep.start()
        self.addCleanup(mock_sleep.stop)

    def patch_status(self, side_effect):
        if not isinstance(side_effect, list):
            side_effect = [side_effect]
        return mock.patch.object(self.monit, 'get_status', side_effect=side_effect)

    def test_change_state_success(self):
        with self.patch_status([monit.Status.OK, monit.Status.NOT_MONITORED]):
            with self.assertRaises(AnsibleExitJson):
                self.monit.stop()
        self.module.fail_json.assert_not_called()
        self.module.run_command.assert_called_with(['monit', 'stop', 'processX'], check_rc=True)

    def test_change_state_fail(self):
        with self.patch_status([monit.Status.OK] * 3):
            with self.assertRaises(AnsibleFailJson):
                self.monit.stop()

    def test_reload_fail(self):
        self.module.run_command.return_value = (1, 'stdout', 'stderr')
        with self.assertRaises(AnsibleFailJson):
            self.monit.reload()

    def test_reload(self):
        self.module.run_command.return_value = (0, '', '')
        with self.patch_status(monit.Status.OK):
            with self.assertRaises(AnsibleExitJson):
                self.monit.reload()

    def test_wait_for_status_to_stop_pending(self):
        status = [
            monit.Status.MISSING,
            monit.Status.DOES_NOT_EXIST,
            monit.Status.INITIALIZING,
            monit.Status.OK.pending(),
            monit.Status.OK
        ]
        with self.patch_status(status) as get_status:
            self.monit.wait_for_monit_to_stop_pending()
            self.assertEqual(get_status.call_count, len(status))

    def test_wait_for_status_change(self):
        with self.patch_status([monit.Status.NOT_MONITORED, monit.Status.OK]) as get_status:
            self.monit.wait_for_status_change(monit.Status.NOT_MONITORED)
        self.assertEqual(get_status.call_count, 2)

    def test_wait_for_status_change_fail(self):
        with self.patch_status([monit.Status.OK] * 3):
            with self.assertRaises(AnsibleFailJson):
                self.monit.wait_for_status_change(monit.Status.OK)

    def test_monitor(self):
        with self.patch_status([monit.Status.NOT_MONITORED, monit.Status.OK.pending(), monit.Status.OK]):
            with self.assertRaises(AnsibleExitJson):
                self.monit.monitor()

    def test_monitor_fail(self):
        with self.patch_status([monit.Status.NOT_MONITORED] * 3):
            with self.assertRaises(AnsibleFailJson):
                self.monit.monitor()

    def test_timeout(self):
        self.monit.timeout = 0
        with self.patch_status(monit.Status.NOT_MONITORED.pending()):
            with self.assertRaises(AnsibleFailJson):
                self.monit.wait_for_monit_to_stop_pending()


@pytest.mark.parametrize('status_name', monit.StatusValue.ALL_STATUS)
def test_status_value(status_name):
    value = getattr(monit.StatusValue, status_name.upper())
    status = monit.StatusValue(value)
    assert getattr(status, 'is_%s' % status_name)
    assert not all(getattr(status, 'is_%s' % name) for name in monit.StatusValue.ALL_STATUS if name != status_name)


BASIC_OUTPUT_CASES = [
    (TEST_OUTPUT % ('Process', 'processX', name), getattr(monit.Status, name.upper()))
    for name in monit.StatusValue.ALL_STATUS
]


@pytest.mark.parametrize('output, expected', BASIC_OUTPUT_CASES + [
    ('', monit.Status.MISSING),
    (TEST_OUTPUT % ('Process', 'processY', 'OK'), monit.Status.MISSING),
    (TEST_OUTPUT % ('Process', 'processX', 'Not Monitored - start pending'), monit.Status.OK),
    (TEST_OUTPUT % ('Process', 'processX', 'Monitored - stop pending'), monit.Status.NOT_MONITORED),
    (TEST_OUTPUT % ('Process', 'processX', 'Monitored - restart pending'), monit.Status.OK),
    (TEST_OUTPUT % ('Process', 'processX', 'Not Monitored - monitor pending'), monit.Status.OK),
    (TEST_OUTPUT % ('Process', 'processX', 'Does not exist'), monit.Status.DOES_NOT_EXIST),
    (TEST_OUTPUT % ('Process', 'processX', 'Not monitored'), monit.Status.NOT_MONITORED),
    (TEST_OUTPUT % ('Process', 'processX', 'Running'), monit.Status.OK),
    (TEST_OUTPUT % ('Process', 'processX', 'Execution failed | Does not exist'), monit.Status.EXECUTION_FAILED),
])
def test_parse_status(output, expected):
    status = monit.Monit(None, '', 'processX', 0)._parse_status(output, '')
    assert status == expected


@pytest.mark.parametrize('output, expected', BASIC_OUTPUT_CASES + [
    (TEST_OUTPUT % ('Process', 'processX', 'OK'), monit.Status.OK),
    (TEST_OUTPUT % ('File', 'processX', 'OK'), monit.Status.OK),
    (TEST_OUTPUT % ('Fifo', 'processX', 'OK'), monit.Status.OK),
    (TEST_OUTPUT % ('Filesystem', 'processX', 'OK'), monit.Status.OK),
    (TEST_OUTPUT % ('Directory', 'processX', 'OK'), monit.Status.OK),
    (TEST_OUTPUT % ('Remote host', 'processX', 'OK'), monit.Status.OK),
    (TEST_OUTPUT % ('System', 'processX', 'OK'), monit.Status.OK),
    (TEST_OUTPUT % ('Program', 'processX', 'OK'), monit.Status.OK),
    (TEST_OUTPUT % ('Network', 'processX', 'OK'), monit.Status.OK),
    (TEST_OUTPUT % ('Unsupported', 'processX', 'OK'), monit.Status.MISSING),
])
def test_parse_status_supports_all_services(output, expected):
    status = monit.Monit(None, '', 'processX', 0)._parse_status(output, '')
    assert status == expected


@pytest.mark.parametrize('output, expected', [
    ('This is monit version 5.18.1', '5.18.1'),
    ('This is monit version 12.18', '12.18'),
    ('This is monit version 5.1.12', '5.1.12'),
])
def test_parse_version(output, expected):
    module = mock.MagicMock()
    module.run_command.return_value = (0, output, '')
    raw_version, version_tuple = monit.Monit(module, '', 'processX', 0)._get_monit_version()
    assert raw_version == expected
