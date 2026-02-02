# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError

from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    ModuleTestCase,
    set_module_args,
)

from ansible_collections.community.general.plugins.modules import icinga2_downtime


class TestIcinga2Downtime(ModuleTestCase):
    def setUp(self):
        super().setUp()
        self.module = icinga2_downtime

    def tearDown(self):
        super().tearDown()

    @patch("ansible_collections.community.general.plugins.modules.icinga2_downtime.Icinga2Client")
    def test_schedule_downtime_successfully(self, client_mock):
        module_args = {
            "url": "http://icinga2.example.com:5665",
            "url_username": "icingaadmin",
            "url_password": "secret",
            "author": "Ansible",
            "comment": "This is a test comment.",
            "state": "present",
            "start_time": 1769954400,
            "end_time": 1769958000,
            "duration": 3600,
            "fixed": True,
            "object_type": "Host",
            "filter": 'host.name=="host.example.com"',
        }
        with set_module_args(module_args):
            info = {
                "content-type": "application/json",
                "server": "Icinga/r2.15.1-1",
                "status": 200,
                "url": "https://icinga2.example.com:5665/v1/actions/schedule-downtime",
            }
            response = {
                "results": [
                    {
                        "code": 200,
                        "legacy_id": 28911,
                        "name": "host.example.com!e19c705a-54c2-49c5-8014-70ff624f9e51",
                        "status": "Successfully scheduled downtime 'host.example.com!e19c705a-54c2-49c5-8014-70ff624f9e51' for object 'host.example.com'.",
                    }
                ]
            }
            response_read_mock = MagicMock(return_value=json.dumps(response))
            response_mock = MagicMock(read=response_read_mock)
            schedule_downtime_mock = MagicMock(return_value=(response_mock, info))
            actions_mock = MagicMock(schedule_downtime=schedule_downtime_mock)
            client_mock.return_value = MagicMock(actions=actions_mock)

            with self.assertRaises(AnsibleExitJson) as result:
                self.module.main()

        self.assertTrue(result.exception.args[0]["changed"])
        self.assertEqual(result.exception.args[0]["results"], response["results"])
        schedule_downtime_mock.assert_called_once_with(
            all_services=None,
            author=module_args["author"],
            child_options=None,
            comment=module_args["comment"],
            duration=module_args["duration"],
            end_time=module_args["end_time"],
            filter=module_args["filter"],
            filter_vars=None,
            fixed=module_args["fixed"],
            object_type=module_args["object_type"],
            start_time=module_args["start_time"],
            trigger_name=None,
        )

    @patch("ansible_collections.community.general.plugins.modules.icinga2_downtime.Icinga2Client")
    def test_schedule_downtime_failed(self, client_mock):
        module_args = {
            "url": "http://icinga2.example.com:5665",
            "url_username": "icingaadmin",
            "url_password": "secret",
            "author": "Ansible",
            "comment": "This is a test comment.",
            "state": "present",
            "start_time": 1769954400,
            "end_time": 1769958000,
            "duration": 3600,
            "fixed": True,
            "object_type": "Host",
            "filter": 'host.name=="unknown.example.com"',
        }
        with set_module_args(module_args):
            info = {
                "body": '{"error":404,"status":"No objects found."}',
                "content-length": "42",
                "content-type": "application/json",
                "msg": "HTTP Error 404: Not Found",
                "server": "Icinga/r2.15.1-1",
                "status": 404,
                "url": "https://icinga2.example.com:5665/v1/actions/remove-downtime",
            }
            response = HTTPError(url=info["url"], code=404, msg=info["msg"], hdrs={}, fp=None)
            schedule_downtime_mock = MagicMock(return_value=(response, info))
            actions_mock = MagicMock(schedule_downtime=schedule_downtime_mock)
            client_mock.return_value = MagicMock(actions=actions_mock)

            with self.assertRaises(AnsibleFailJson) as result:
                self.module.main()

        self.assertFalse(result.exception.args[0]["changed"])
        self.assertTrue(result.exception.args[0]["failed"])
        self.assertEqual(
            result.exception.args[0]["error"],
            {"error": 404, "status": "No objects found."},
        )
        schedule_downtime_mock.assert_called_once_with(
            all_services=None,
            author=module_args["author"],
            child_options=None,
            comment=module_args["comment"],
            duration=module_args["duration"],
            end_time=module_args["end_time"],
            filter=module_args["filter"],
            filter_vars=None,
            fixed=module_args["fixed"],
            object_type=module_args["object_type"],
            start_time=module_args["start_time"],
            trigger_name=None,
        )

    @patch("ansible_collections.community.general.plugins.modules.icinga2_downtime.Icinga2Client")
    def test_remove_existing_downtime(self, client_mock):
        module_args = {
            "url": "http://icinga2.example.com:5665",
            "url_username": "icingaadmin",
            "url_password": "secret",
            "state": "absent",
            "name": "host.example.com!e19c705a-54c2-49c5-8014-70ff624f9e51",
            "object_type": "Downtime",
        }
        with set_module_args(module_args):
            info = {
                "content-type": "application/json",
                "server": "Icinga/r2.15.1-1",
                "status": 200,
                "url": "https://icinga2.example.com:5665/v1/actions/remove-downtime",
            }
            response = {
                "results": [
                    {
                        "code": 200,
                        "status": "Successfully removed downtime 'host.example.com!e19c705a-54c2-49c5-8014-70ff624f9e51' and 0 child downtimes.",
                    }
                ]
            }
            response_read_mock = MagicMock(return_value=json.dumps(response))
            response_mock = MagicMock(read=response_read_mock)
            remove_downtime_mock = MagicMock(return_value=(response_mock, info))
            actions_mock = MagicMock(remove_downtime=remove_downtime_mock)
            client_mock.return_value = MagicMock(actions=actions_mock)

            with self.assertRaises(AnsibleExitJson) as result:
                self.module.main()

        self.assertTrue(result.exception.args[0]["changed"])
        self.assertEqual(result.exception.args[0]["results"], response["results"])
        remove_downtime_mock.assert_called_once_with(
            filter=None,
            filter_vars=None,
            name=module_args["name"],
            object_type=module_args["object_type"],
        )

    @patch("ansible_collections.community.general.plugins.modules.icinga2_downtime.Icinga2Client")
    def test_remove_non_existing_downtime(self, client_mock):
        module_args = {
            "url": "http://icinga2.example.com:5665",
            "url_username": "icingaadmin",
            "url_password": "secret",
            "state": "absent",
            "name": "unknown.example.com!e19c705a-54c2-49c5-8014-70ff624f9e51",
            "object_type": "Downtime",
        }
        with set_module_args(module_args):
            info = {
                "body": '{"error":404,"status":"No objects found."}',
                "content-length": "42",
                "content-type": "application/json",
                "msg": "HTTP Error 404: Not Found",
                "server": "Icinga/r2.15.1-1",
                "status": 404,
                "url": "https://icinga2.example.com:5665/v1/actions/remove-downtime",
            }
            response = HTTPError(url=info["url"], code=404, msg=info["msg"], hdrs={}, fp=None)
            remove_downtime_mock = MagicMock(return_value=(response, info))
            actions_mock = MagicMock(remove_downtime=remove_downtime_mock)
            client_mock.return_value = MagicMock(actions=actions_mock)

            with self.assertRaises(AnsibleExitJson) as result:
                self.module.main()

        self.assertFalse(result.exception.args[0]["changed"])
        self.assertFalse(result.exception.args[0]["failed"])
        remove_downtime_mock.assert_called_once_with(
            filter=None,
            filter_vars=None,
            name=module_args["name"],
            object_type=module_args["object_type"],
        )
