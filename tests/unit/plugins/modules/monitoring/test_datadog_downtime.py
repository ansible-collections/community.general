# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from ansible_collections.community.general.plugins.modules.monitoring.datadog import datadog_downtime
from ansible_collections.community.general.tests.unit.compat.mock import MagicMock, patch
from ansible_collections.community.general.tests.unit.plugins.modules.utils import (
    AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args
)

from pytest import importorskip

# Skip this test if python 2 so datadog_api_client cannot be installed
datadog_api_client = importorskip("datadog_api_client")
Downtime = datadog_api_client.v1.model.downtime.Downtime
DowntimeRecurrence = datadog_api_client.v1.model.downtime_recurrence.DowntimeRecurrence


class TestDatadogDowntime(ModuleTestCase):

    def setUp(self):
        super(TestDatadogDowntime, self).setUp()
        self.module = datadog_downtime

    def tearDown(self):
        super(TestDatadogDowntime, self).tearDown()

    def test_without_required_parameters(self):
        """Failure must occurs when all parameters are missing"""
        with self.assertRaises(AnsibleFailJson):
            set_module_args({})
            self.module.main()

    @patch("ansible_collections.community.general.plugins.modules.monitoring.datadog.datadog_downtime.DowntimesApi")
    def test_create_downtime_when_no_id(self, downtimes_api_mock):
        set_module_args({
            "monitor_tags": ["foo:bar"],
            "scope": ["*"],
            "monitor_id": 12345,
            "downtime_message": "Message",
            "start": 1111,
            "end": 2222,
            "timezone": "UTC",
            "rrule": "rrule",
            "api_key": "an_api_key",
            "app_key": "an_app_key",
        })

        downtime = Downtime()
        downtime.monitor_tags = ["foo:bar"]
        downtime.scope = ["*"]
        downtime.monitor_id = 12345
        downtime.message = "Message"
        downtime.start = 1111
        downtime.end = 2222
        downtime.timezone = "UTC"
        downtime.recurrence = DowntimeRecurrence(
            rrule="rrule"
        )

        create_downtime_mock = MagicMock(return_value=Downtime(id=12345))
        downtimes_api_mock.return_value = MagicMock(create_downtime=create_downtime_mock)
        with self.assertRaises(AnsibleExitJson) as result:
            self.module.main()
        self.assertTrue(result.exception.args[0]['changed'])
        self.assertEqual(result.exception.args[0]['downtime']['id'], 12345)
        create_downtime_mock.assert_called_once_with(downtime)

    @patch("ansible_collections.community.general.plugins.modules.monitoring.datadog.datadog_downtime.DowntimesApi")
    def test_create_downtime_when_id_and_disabled(self, downtimes_api_mock):
        set_module_args({
            "id": 1212,
            "monitor_tags": ["foo:bar"],
            "scope": ["*"],
            "monitor_id": 12345,
            "downtime_message": "Message",
            "start": 1111,
            "end": 2222,
            "timezone": "UTC",
            "rrule": "rrule",
            "api_key": "an_api_key",
            "app_key": "an_app_key",
        })

        downtime = Downtime()
        downtime.monitor_tags = ["foo:bar"]
        downtime.scope = ["*"]
        downtime.monitor_id = 12345
        downtime.message = "Message"
        downtime.start = 1111
        downtime.end = 2222
        downtime.timezone = "UTC"
        downtime.recurrence = DowntimeRecurrence(
            rrule="rrule"
        )

        create_downtime_mock = MagicMock(return_value=Downtime(id=12345))
        get_downtime_mock = MagicMock(return_value=Downtime(id=1212, disabled=True))
        downtimes_api_mock.return_value = MagicMock(
            create_downtime=create_downtime_mock, get_downtime=get_downtime_mock
        )
        with self.assertRaises(AnsibleExitJson) as result:
            self.module.main()
        self.assertTrue(result.exception.args[0]['changed'])
        self.assertEqual(result.exception.args[0]['downtime']['id'], 12345)
        create_downtime_mock.assert_called_once_with(downtime)
        get_downtime_mock.assert_called_once_with(1212)

    @patch("ansible_collections.community.general.plugins.modules.monitoring.datadog.datadog_downtime.DowntimesApi")
    def test_update_downtime_when_not_disabled(self, downtimes_api_mock):
        set_module_args({
            "id": 1212,
            "monitor_tags": ["foo:bar"],
            "scope": ["*"],
            "monitor_id": 12345,
            "downtime_message": "Message",
            "start": 1111,
            "end": 2222,
            "timezone": "UTC",
            "rrule": "rrule",
            "api_key": "an_api_key",
            "app_key": "an_app_key",
        })

        downtime = Downtime()
        downtime.monitor_tags = ["foo:bar"]
        downtime.scope = ["*"]
        downtime.monitor_id = 12345
        downtime.message = "Message"
        downtime.start = 1111
        downtime.end = 2222
        downtime.timezone = "UTC"
        downtime.recurrence = DowntimeRecurrence(
            rrule="rrule"
        )

        update_downtime_mock = MagicMock(return_value=Downtime(id=1212))
        get_downtime_mock = MagicMock(return_value=Downtime(id=1212, disabled=False))
        downtimes_api_mock.return_value = MagicMock(
            update_downtime=update_downtime_mock, get_downtime=get_downtime_mock
        )
        with self.assertRaises(AnsibleExitJson) as result:
            self.module.main()
        self.assertTrue(result.exception.args[0]['changed'])
        self.assertEqual(result.exception.args[0]['downtime']['id'], 1212)
        update_downtime_mock.assert_called_once_with(1212, downtime)
        get_downtime_mock.assert_called_once_with(1212)

    @patch("ansible_collections.community.general.plugins.modules.monitoring.datadog.datadog_downtime.DowntimesApi")
    def test_update_downtime_no_change(self, downtimes_api_mock):
        set_module_args({
            "id": 1212,
            "monitor_tags": ["foo:bar"],
            "scope": ["*"],
            "monitor_id": 12345,
            "downtime_message": "Message",
            "start": 1111,
            "end": 2222,
            "timezone": "UTC",
            "rrule": "rrule",
            "api_key": "an_api_key",
            "app_key": "an_app_key",
        })

        downtime = Downtime()
        downtime.monitor_tags = ["foo:bar"]
        downtime.scope = ["*"]
        downtime.monitor_id = 12345
        downtime.message = "Message"
        downtime.start = 1111
        downtime.end = 2222
        downtime.timezone = "UTC"
        downtime.recurrence = DowntimeRecurrence(
            rrule="rrule"
        )

        downtime_get = Downtime()
        downtime_get.id = 1212
        downtime_get.disabled = False
        downtime_get.monitor_tags = ["foo:bar"]
        downtime_get.scope = ["*"]
        downtime_get.monitor_id = 12345
        downtime_get.message = "Message"
        downtime_get.start = 1111
        downtime_get.end = 2222
        downtime_get.timezone = "UTC"
        downtime_get.recurrence = DowntimeRecurrence(
            rrule="rrule"
        )

        update_downtime_mock = MagicMock(return_value=downtime_get)
        get_downtime_mock = MagicMock(return_value=downtime_get)
        downtimes_api_mock.return_value = MagicMock(
            update_downtime=update_downtime_mock, get_downtime=get_downtime_mock
        )
        with self.assertRaises(AnsibleExitJson) as result:
            self.module.main()
        self.assertFalse(result.exception.args[0]['changed'])
        self.assertEqual(result.exception.args[0]['downtime']['id'], 1212)
        update_downtime_mock.assert_called_once_with(1212, downtime)
        get_downtime_mock.assert_called_once_with(1212)

    @patch("ansible_collections.community.general.plugins.modules.monitoring.datadog.datadog_downtime.DowntimesApi")
    def test_delete_downtime(self, downtimes_api_mock):
        set_module_args({
            "id": 1212,
            "state": "absent",
            "api_key": "an_api_key",
            "app_key": "an_app_key",
        })

        cancel_downtime_mock = MagicMock()
        get_downtime_mock = MagicMock(return_value=Downtime(id=1212))
        downtimes_api_mock.return_value = MagicMock(
            get_downtime=get_downtime_mock,
            cancel_downtime=cancel_downtime_mock
        )
        with self.assertRaises(AnsibleExitJson) as result:
            self.module.main()
        self.assertTrue(result.exception.args[0]['changed'])
        cancel_downtime_mock.assert_called_once_with(1212)
