# -*- coding: utf-8 -*-
# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from ansible_collections.community.general.plugins.modules import datadog_downtime
from ansible_collections.community.general.tests.unit.compat.mock import MagicMock, patch
from ansible_collections.community.general.tests.unit.plugins.modules.utils import (
    AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args
)
from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

import json
import sys
import pytest
from pytest import importorskip

MIN_PYTHON_REQUIRED = sys.version_info < (3, 7)
REASON = "datadog-api-client requires Python 3.7+"

if datadog_downtime.HAS_DATADOG:
    datadog_api_client = importorskip("datadog_api_client")
    from datadog_api_client.exceptions import (
        ApiException
    )
    from datadog_api_client.v2.model.downtime_response import DowntimeResponse
    from datadog_api_client.v2.model.downtime_response_data import DowntimeResponseData
    from datadog_api_client.v2.model.downtime_response_attributes import DowntimeResponseAttributes
    from datadog_api_client.v2.model.downtime_create_request import DowntimeCreateRequest
    from datadog_api_client.v2.model.downtime_create_request_data import DowntimeCreateRequestData
    from datadog_api_client.v2.model.downtime_create_request_attributes import DowntimeCreateRequestAttributes
    from datadog_api_client.v2.model.downtime_schedule_recurrence_create_update_request import (
        DowntimeScheduleRecurrenceCreateUpdateRequest
    )


class TestDatadogDowntime(ModuleTestCase):

    def setUp(self):
        super(TestDatadogDowntime, self).setUp()
        self.module = datadog_downtime
        self.base_args = {
            'api_key': 'fake_api_key',
            'app_key': 'fake_app_key',
        }

    def set_module_args(self, args):
        """Prepare arguments so that they will be picked up during module creation"""
        full_args = self.base_args.copy()
        full_args.update(args)
        args_json = json.dumps({'ANSIBLE_MODULE_ARGS': full_args})
        basic._ANSIBLE_ARGS = to_bytes(args_json)

    def tearDown(self):
        super(TestDatadogDowntime, self).tearDown()

    @pytest.mark.skipif(MIN_PYTHON_REQUIRED, reason=REASON)
    def test_without_required_parameters(self):
        """Failure must occurs when all parameters are missing"""
        with self.assertRaises(AnsibleFailJson):
            set_module_args({})
            self.module.main()

    @pytest.mark.skipif(MIN_PYTHON_REQUIRED, reason=REASON)
    @patch("ansible_collections.community.general.plugins.modules.datadog_downtime.DowntimesApi")
    def test_create_downtime_when_no_id(self, downtimes_api_mock):
        set_module_args({
            "monitor_tags": ["foo:bar"],
            "scope": "*",
            "monitor_id": 12345,
            "downtime_message": "Message",
            "mute_first_recovery_notification": False,
            "start": 1111,
            "end": 2222,
            "timezone": "UTC",
            "rrule": "rrule",
            "duration": "3600",
            "api_key": "an_api_key",
            "app_key": "an_app_key",
        })

        recurrence = DowntimeScheduleRecurrenceCreateUpdateRequest(
            type="rrule",
            rrule="rrule",
            duration="3600",
        )

        body = DowntimeCreateRequest(
            data=DowntimeCreateRequestData(
                attributes=DowntimeCreateRequestAttributes(
                    message="Message",
                    monitor_identifier={"monitor_id": 12345},
                    monitor_tags=["foo:bar"],
                    scope="*",
                    mute_first_recovery_notification=False,
                    schedule={
                        "start": 1111,
                        "end": 2222,
                        "timezone": "UTC",
                        "recurrences": [recurrence]
                    }
                ),
                type="downtime"
            )
        )

        create_downtime_mock = MagicMock(
            return_value=self.__downtime_with_id(12345))
        downtimes_api_mock.return_value = MagicMock(
            create_downtime=create_downtime_mock)
        with self.assertRaises(AnsibleExitJson) as result:
            self.module.main()
        self.assertTrue(result.exception.args[0]['changed'])
        self.assertEqual(result.exception.args[0]['downtime']['id'], "12345")
        create_downtime_mock.assert_called_once_with(body=body)

    @pytest.mark.skipif(MIN_PYTHON_REQUIRED, reason=REASON)
    @patch("ansible_collections.community.general.plugins.modules.datadog_downtime.DowntimesApi")
    def test_create_downtime_when_id_and_disabled(self, downtimes_api_mock):
        set_module_args({
            "id": 1212,
            "monitor_tags": ["foo:bar"],
            "scope": "*",
            "monitor_id": 12345,
            "downtime_message": "Message",
            "mute_first_recovery_notification": False,
            "start": 1111,
            "end": 2222,
            "timezone": "UTC",
            "rrule": "rrule",
            "duration": "3600",
            "api_key": "an_api_key",
            "app_key": "an_app_key",
        })

        disabled_downtime = MagicMock()
        disabled_downtime.data.attributes.status = 'disabled'

        api_instance = MagicMock()
        api_instance.get_downtime.return_value = disabled_downtime

        recurrence = DowntimeScheduleRecurrenceCreateUpdateRequest(
            type="rrule",
            rrule="rrule",
            duration="3600",
        )

        body = DowntimeCreateRequest(
            data=DowntimeCreateRequestData(
                attributes=DowntimeCreateRequestAttributes(
                    message="Message",
                    monitor_identifier={"monitor_id": 12345},
                    monitor_tags=["foo:bar"],
                    scope="*",
                    mute_first_recovery_notification=False,
                    schedule={
                        "start": 1111,
                        "end": 2222,
                        "timezone": "UTC",
                        "recurrences": [recurrence]
                    }
                ),
                type="downtime"
            )
        )

        create_response = self.__downtime_with_id(12345)
        api_instance.create_downtime.return_value = create_response

        downtimes_api_mock.return_value = api_instance

        with self.assertRaises(AnsibleExitJson) as result:
            self.module.main()

        self.assertTrue(result.exception.args[0]['changed'])
        self.assertEqual(result.exception.args[0]['downtime']['id'], "12345")

        api_instance.get_downtime.assert_called_once_with(downtime_id="1212")

        api_instance.create_downtime.assert_called_once_with(body=body)

    @pytest.mark.skipif(MIN_PYTHON_REQUIRED, reason=REASON)
    @patch("ansible_collections.community.general.plugins.modules.datadog_downtime.DowntimesApi")
    def test_update_downtime_when_not_disabled(self, downtimes_api_mock):
        set_module_args({
            "monitor_tags": ["foo:bar"],
            "scope": "*",
            "monitor_id": 12345,
            "downtime_message": "Updated Message",
            "mute_first_recovery_notification": True,
            "start": 1111,
            "end": 2222,
            "timezone": "UTC",
            "rrule": "rrule",
            "duration": "3600",
            "id": 12345,
            "api_key": "an_api_key",
            "app_key": "an_app_key",
        })

        existing_downtime = DowntimeResponse(
            data=DowntimeResponseData(
                id="12345",
                type="downtime",
                attributes=DowntimeResponseAttributes(
                    message="Message",
                    monitor_identifier={"monitor_id": 12345},
                    monitor_tags=["foo:bar"],
                    scope="*",
                    mute_first_recovery_notification=False,
                    schedule={
                        "start": 1111,
                        "end": 2222,
                        "timezone": "UTC",
                        "recurrences": [{
                            "type": "rrule",
                            "rrule": "rrule",
                            "duration": "3600"
                        }]
                    },
                    status="active"
                )
            )
        )

        updated_downtime = DowntimeResponse(
            data=DowntimeResponseData(
                id="12345",
                type="downtime",
                attributes=DowntimeResponseAttributes(
                    message="Updated Message",
                    monitor_identifier={"monitor_id": 12345},
                    monitor_tags=["foo:bar"],
                    scope="*",
                    mute_first_recovery_notification=True,
                    schedule={
                        "start": 1111,
                        "end": 2222,
                        "timezone": "UTC",
                        "recurrences": [{
                            "type": "rrule",
                            "rrule": "rrule",
                            "duration": "3600"
                        }]
                    },
                    status="active"
                )
            )
        )

        api_instance = MagicMock()
        api_instance.get_downtime.return_value = existing_downtime
        api_instance.update_downtime.return_value = updated_downtime

        downtimes_api_mock.return_value = api_instance

        with self.assertRaises(AnsibleExitJson) as result:
            self.module.main()

        self.assertTrue(result.exception.args[0]['changed'])
        self.assertEqual(
            result.exception.args[0]['downtime']['data']['id'], '12345')

    @pytest.mark.skipif(MIN_PYTHON_REQUIRED, reason=REASON)
    @patch("ansible_collections.community.general.plugins.modules.datadog_downtime.DowntimesApi")
    def test_update_downtime_no_change(self, downtimes_api_mock):
        set_module_args({
            "monitor_tags": ["foo:bar"],
            "scope": "*",
            "monitor_id": 12345,
            "downtime_message": "Message",
            "mute_first_recovery_notification": False,
            "start": 1111,
            "end": 2222,
            "timezone": "UTC",
            "rrule": "rrule",
            "duration": "3600",
            "id": "12345",
            "api_key": "an_api_key",
            "app_key": "an_app_key",
        })

        existing_downtime = DowntimeResponse(
            data=DowntimeResponseData(
                id="12345",
                type="downtime",
                attributes=DowntimeResponseAttributes(
                    message="Message",
                    monitor_identifier={"monitor_id": 12345},
                    monitor_tags=["foo:bar"],
                    scope="*",
                    mute_first_recovery_notification=False,
                    schedule={
                        "start": 1111,
                        "end": 2222,
                        "timezone": "UTC",
                        "recurrences": [{
                            "type": "rrule",
                            "rrule": "rrule",
                            "duration": "3600"
                        }]
                    },
                    status="active"
                )
            )
        )

        api_instance = MagicMock()
        api_instance.get_downtime.return_value = existing_downtime
        downtimes_api_mock.return_value = api_instance

        with self.assertRaises(AnsibleExitJson) as result:
            self.module.main()

        self.assertFalse(result.exception.args[0]['changed'])
        self.assertEqual(
            result.exception.args[0]['downtime']['data']['id'], "12345")
        api_instance.update_downtime.assert_not_called()

    @pytest.mark.skipif(MIN_PYTHON_REQUIRED, reason=REASON)
    @patch("ansible_collections.community.general.plugins.modules.datadog_downtime.DowntimesApi")
    def test_delete_downtime(self, downtimes_api_mock):
        module_args = {
            "id": 1212,
            "state": "absent",
            "api_key": "an_api_key",
            "app_key": "an_app_key",
        }
        self.set_module_args(module_args)

        api_instance = MagicMock()
        api_instance.get_downtime.return_value = self.__downtime_with_id(
            "1212")
        api_instance.cancel_downtime = MagicMock()
        downtimes_api_mock.return_value = api_instance

        with self.assertRaises(AnsibleExitJson):
            self.module.main()

        api_instance.get_downtime.assert_called_once_with(downtime_id="1212")

    @pytest.mark.skipif(MIN_PYTHON_REQUIRED, reason=REASON)
    @patch("ansible_collections.community.general.plugins.modules.datadog_downtime.DowntimesApi")
    def test_get_downtime_api_exception(self, downtimes_api_mock):
        module = MagicMock()
        module.params = {"id": 12345}
        module.fail_json.side_effect = AnsibleFailJson

        api_instance = MagicMock()
        api_instance.get_downtime.side_effect = ApiException()
        downtimes_api_mock.return_value = api_instance

        with self.assertRaises(AnsibleFailJson):
            self.module._get_downtime(module, api_instance)

    @pytest.mark.skipif(MIN_PYTHON_REQUIRED, reason=REASON)
    def test_build_downtime_without_optional_params(self):
        module = MagicMock()
        module.params = {
            "api_key": "an_api_key",
            "app_key": "an_app_key",
            "scope": "*"
        }
        downtime = self.module.build_downtime(module)
        self.assertIsNone(downtime.data.attributes.monitor_tags)
        self.assertIsNone(downtime.data.attributes.schedule.recurrences)

    @pytest.mark.skipif(MIN_PYTHON_REQUIRED, reason=REASON)
    @patch("ansible_collections.community.general.plugins.modules.datadog_downtime.DowntimesApi")
    def test_update_downtime_api_exception(self, downtimes_api_mock):
        module = MagicMock()
        module.params = {"id": 12345}
        module.fail_json.side_effect = AnsibleFailJson

        api_instance = MagicMock()
        api_instance.update_downtime.side_effect = ApiException()
        downtimes_api_mock.return_value = api_instance

        current_downtime = self.__downtime_with_id(12345)

        with self.assertRaises(AnsibleFailJson):
            self.module._update_downtime(
                module, current_downtime, api_instance)

    @pytest.mark.skipif(MIN_PYTHON_REQUIRED, reason=REASON)
    @patch("ansible_collections.community.general.plugins.modules.datadog_downtime.DowntimesApi")
    def test_cancel_downtime_api_exception(self, downtimes_api_mock):
        module = MagicMock()
        module.params = {
            "id": 12345,
            "state": "absent",
            "api_key": "an_api_key",
            "app_key": "an_app_key",
        }
        module.fail_json.side_effect = AnsibleFailJson

        api_instance = MagicMock()
        api_instance.cancel_downtime.side_effect = ApiException()
        downtimes_api_mock.return_value = api_instance

        with self.assertRaises(AnsibleFailJson):
            self.module.cancel_downtime(module, api_instance)

    @pytest.mark.skipif(MIN_PYTHON_REQUIRED, reason=REASON)
    @patch("ansible_collections.community.general.plugins.modules.datadog_downtime.DowntimesApi")
    def test_api_validation_failure(self, downtimes_api_mock):
        set_module_args({
            "api_key": "invalid_key",
            "app_key": "invalid_app_key"
        })

        api_instance = MagicMock()
        api_instance.list_downtimes.side_effect = ApiException(status=403)
        downtimes_api_mock.return_value = api_instance

        with self.assertRaises(AnsibleFailJson) as result:
            self.module.main()
        self.assertIn("Failed to connect Datadog server",
                      str(result.exception))

    @pytest.mark.skipif(MIN_PYTHON_REQUIRED, reason=REASON)
    @patch("ansible_collections.community.general.plugins.modules.datadog_downtime.DowntimesApi")
    def test_post_downtime_forbidden(self, downtimes_api_mock):
        self.set_module_args({
            'monitor_tags': ["test:tag"],
            'scope': "*",
            'monitor_identifier': {"monitor_id": 12345},
            'duration': 3600,
            'state': 'present'
        })

        api_instance = MagicMock()
        api_instance.create_downtime.side_effect = ApiException(
            status=403,
            reason="Access forbidden"
        )
        downtimes_api_mock.return_value = api_instance

        with self.assertRaises(AnsibleFailJson) as context:
            self.module.main()

        self.assertIn("Failed to create downtime", str(context.exception))

    @pytest.mark.skipif(MIN_PYTHON_REQUIRED, reason=REASON)
    @patch("ansible_collections.community.general.plugins.modules.datadog_downtime.DowntimesApi")
    def test_cancel_nonexistent_downtime(self, downtimes_api_mock):
        module_args = {
            'id': 12345,
            'state': 'absent',
            'api_key': 'abc123',
            'app_key': 'def456'
        }
        self.set_module_args(module_args)

        api_instance = MagicMock()
        mock_404 = ApiException(status=404, reason="Downtime not found")
        api_instance.get_downtime.side_effect = mock_404
        downtimes_api_mock.return_value = api_instance

        with self.assertRaises(AnsibleExitJson):
            self.module.main()

        self.assertEqual(api_instance.get_downtime.call_count, 1,
                         "get_downtime should be called once")

    @pytest.mark.skipif(MIN_PYTHON_REQUIRED, reason=REASON)
    @patch("ansible_collections.community.general.plugins.modules.datadog_downtime.DowntimesApi")
    def test_get_downtime_not_found(self, downtimes_api_mock):
        module_args = {
            'id': 12345,
            'state': 'present'
        }
        self.set_module_args(module_args)

        api_instance = MagicMock()
        api_instance.get_downtime.side_effect = ApiException(
            status=404,
            reason="Downtime not found"
        )
        api_instance.create_downtime.return_value = MagicMock(
            data=MagicMock(id=12345, to_dict=lambda: {'id': 12345})
        )
        downtimes_api_mock.return_value = api_instance

        with self.assertRaises(AnsibleExitJson) as result:
            self.module.main()

        self.assertTrue(result.exception.args[0]['changed'])
        self.assertEqual(result.exception.args[0]['downtime']['id'], 12345)

    @pytest.mark.skipif(MIN_PYTHON_REQUIRED, reason=REASON)
    def test_equal_dicts_edge_cases(self):
        dict1 = {"a": 1}
        list1 = [1, 2, 3]
        self.assertFalse(self.module._equal_dicts(dict1, list1))

        list2 = [{"a": 1}, {"b": 2}]
        list3 = [{"a": 1}]
        self.assertFalse(self.module._equal_dicts(list2, list3))

        dict2 = {"a": 1, "b": 2}
        dict3 = {"a": 1, "c": 2}
        self.assertFalse(self.module._equal_dicts(dict2, dict3))

        dict4 = {"a": 1, "status": "active", "creator_id": 123}
        dict5 = {"a": 1, "status": "disabled", "creator_id": 456}
        self.assertTrue(self.module._equal_dicts(
            dict4, dict5, ignore_keys={"status", "creator_id"}))

    @pytest.mark.skipif(MIN_PYTHON_REQUIRED, reason=REASON)
    def __downtime_with_id(self, id, changed=False, status="active"):
        return DowntimeResponse(
            data=DowntimeResponseData(
                id=str(id),
                type="downtime",
                attributes=DowntimeResponseAttributes(
                    changed=changed,
                    status=status
                )
            )
        )
