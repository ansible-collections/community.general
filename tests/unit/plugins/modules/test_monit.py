# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import unittest
from unittest import mock

from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
)

from ansible_collections.community.general.plugins.modules import monit

from .uthelper import RunCommandMock, UTHelper

UTHelper.from_module(monit, __name__, mocks=[RunCommandMock])


class MonitTest(unittest.TestCase):
    def setUp(self):
        self.module = mock.MagicMock()
        self.module.exit_json.side_effect = AnsibleExitJson
        self.module.fail_json.side_effect = AnsibleFailJson
        self.module.run_command.return_value = (0, "This is monit version 5.26.0", "")
        self.monit = monit.Monit(self.module, "monit", "processX", 1)
        self.monit._status_change_retry_count = 1
        mock_sleep = mock.patch("time.sleep")
        mock_sleep.start()
        self.addCleanup(mock_sleep.stop)

    def patch_status(self, side_effect):
        if not isinstance(side_effect, list):
            side_effect = [side_effect]
        return mock.patch.object(self.monit, "get_status", side_effect=side_effect)

    def test_change_state_fail(self):
        with self.patch_status([monit.Status("OK")] * 3):
            with self.assertRaises(AnsibleFailJson):
                self.monit.stop()

    def test_wait_for_status_to_stop_pending(self):
        status = [
            monit.Status("MISSING"),
            monit.Status("DOES_NOT_EXIST"),
            monit.Status("INITIALIZING"),
            monit.Status("OK").pending(),
            monit.Status("OK"),
        ]
        with self.patch_status(status) as get_status:
            self.monit.wait_for_monit_to_stop_pending()
            self.assertEqual(get_status.call_count, len(status))

    def test_wait_for_status_change_fail(self):
        with self.patch_status([monit.Status("OK")] * 3):
            with self.assertRaises(AnsibleFailJson):
                self.monit.wait_for_status_change(monit.Status("OK"))

    def test_monitor(self):
        with self.patch_status([monit.Status("NOT_MONITORED"), monit.Status("OK").pending(), monit.Status("OK")]):
            with self.assertRaises(AnsibleExitJson):
                self.monit.monitor()

    def test_monitor_fail(self):
        with self.patch_status([monit.Status("NOT_MONITORED")] * 3):
            with self.assertRaises(AnsibleFailJson):
                self.monit.monitor()
