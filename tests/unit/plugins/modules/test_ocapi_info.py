# -*- coding: utf-8 -*-
# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import patch
from ansible_collections.community.internal_test_tools.tests.unit.compat import unittest
from ansible.module_utils import basic
import ansible_collections.community.general.plugins.modules.ocapi_info as module
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import set_module_args, exit_json, fail_json

MOCK_BASE_URI = "mockBaseUri"
MOCK_JOB_NAME_IN_PROGRESS = "MockJobInProgress"
MOCK_JOB_NAME_COMPLETE = "MockJobComplete"
MOCK_JOB_NAME_DOES_NOT_EXIST = "MockJobDoesNotExist"

ACTION_WAS_SUCCESSFUL = "Action was successful."

MOCK_SUCCESSFUL_HTTP_RESPONSE = {
    "ret": True,
    "data": {}
}

MOCK_404_RESPONSE = {
    "ret": False,
    "status": 404
}

MOCK_HTTP_RESPONSE_JOB_IN_PROGRESS = {
    "ret": True,
    "data": {
        "Self": "https://openflex-data24-usalp02120qo0012-iomb:443/Storage/Devices/openflex-data24-usalp02120qo0012/Jobs/FirmwareUpdate/",
        "ID": MOCK_JOB_NAME_IN_PROGRESS,
        "PercentComplete": 10,
        "Status": {
            "State": {
                "ID": 16,
                "Name": "In service"
            },
            "Health": [
                {
                    "ID": 5,
                    "Name": "OK"
                }
            ]
        }
    }
}

MOCK_HTTP_RESPONSE_JOB_COMPLETE = {
    "ret": True,
    "data": {
        "Self": "https://openflex-data24-usalp02120qo0012-iomb:443/Storage/Devices/openflex-data24-usalp02120qo0012/Jobs/FirmwareUpdate/",
        "ID": MOCK_JOB_NAME_COMPLETE,
        "PercentComplete": 100,
        "Status": {
            "State": {
                "ID": 65540,
                "Name": "Activate needed"
            },
            "Health": [
                {
                    "ID": 5,
                    "Name": "OK"
                }
            ],
            "Details": [
                "Completed."
            ]
        }
    }
}


def get_bin_path(self, arg, required=False):
    """Mock AnsibleModule.get_bin_path"""
    return arg


def get_exception_message(ansible_exit_json):
    """From an AnsibleExitJson exception, get the message string."""
    return ansible_exit_json.exception.args[0]["msg"]


def mock_get_request(*args, **kwargs):
    """Mock for get_request."""
    url = args[1]
    if url == "https://" + MOCK_BASE_URI:
        return MOCK_SUCCESSFUL_HTTP_RESPONSE
    elif url == "https://" + MOCK_BASE_URI + '/Jobs/' + MOCK_JOB_NAME_IN_PROGRESS:
        return MOCK_HTTP_RESPONSE_JOB_IN_PROGRESS
    elif url == "https://" + MOCK_BASE_URI + '/Jobs/' + MOCK_JOB_NAME_COMPLETE:
        return MOCK_HTTP_RESPONSE_JOB_COMPLETE
    elif url == "https://" + MOCK_BASE_URI + '/Jobs/' + MOCK_JOB_NAME_DOES_NOT_EXIST:
        return MOCK_404_RESPONSE
    else:
        raise RuntimeError("Illegal GET call to: " + args[1])


def mock_put_request(*args, **kwargs):
    """Mock put_request.  PUT should never happen so it will raise an error."""
    raise RuntimeError("Illegal PUT call to: " + args[1])


def mock_delete_request(*args, **kwargs):
    """Mock delete request.  DELETE should never happen so it will raise an error."""
    raise RuntimeError("Illegal DELETE call to: " + args[1])


def mock_post_request(*args, **kwargs):
    """Mock post_request.  POST should never happen so it will raise an error."""
    raise RuntimeError("Illegal POST call to: " + args[1])


class TestOcapiInfo(unittest.TestCase):
    def setUp(self):
        self.mock_module_helper = patch.multiple(basic.AnsibleModule,
                                                 exit_json=exit_json,
                                                 fail_json=fail_json,
                                                 get_bin_path=get_bin_path)
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)

    def test_module_fail_when_required_args_missing(self):
        with self.assertRaises(AnsibleFailJson) as ansible_fail_json:
            with set_module_args({}):
                module.main()
        self.assertIn("missing required arguments:", get_exception_message(ansible_fail_json))

    def test_module_fail_when_unknown_category(self):
        with self.assertRaises(AnsibleFailJson) as ansible_fail_json:
            with set_module_args({
                'category': 'unknown',
                'command': 'JobStatus',
                'username': 'USERID',
                'password': 'PASSW0RD=21',
                'baseuri': MOCK_BASE_URI
            }):
                module.main()
        self.assertIn("Invalid Category 'unknown", get_exception_message(ansible_fail_json))

    def test_module_fail_when_unknown_command(self):
        with self.assertRaises(AnsibleFailJson) as ansible_fail_json:
            with set_module_args({
                'category': 'Jobs',
                'command': 'unknown',
                'username': 'USERID',
                'password': 'PASSW0RD=21',
                'baseuri': MOCK_BASE_URI
            }):
                module.main()
        self.assertIn("Invalid Command 'unknown", get_exception_message(ansible_fail_json))

    def test_job_status_in_progress(self):
        with patch.multiple("ansible_collections.community.general.plugins.module_utils.ocapi_utils.OcapiUtils",
                            get_request=mock_get_request,
                            put_request=mock_put_request,
                            delete_request=mock_delete_request,
                            post_request=mock_post_request):
            with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
                with set_module_args({
                    'category': 'Jobs',
                    'command': 'JobStatus',
                    'job_name': MOCK_JOB_NAME_IN_PROGRESS,
                    'baseuri': MOCK_BASE_URI,
                    'username': 'USERID',
                    'password': 'PASSWORD=21'
                }):
                    module.main()
            self.assertEqual(ACTION_WAS_SUCCESSFUL, get_exception_message(ansible_exit_json))
            response_data = ansible_exit_json.exception.args[0]
            self.assertEqual(MOCK_HTTP_RESPONSE_JOB_IN_PROGRESS["data"]["PercentComplete"], response_data["percentComplete"])
            self.assertEqual(MOCK_HTTP_RESPONSE_JOB_IN_PROGRESS["data"]["Status"]["State"]["ID"], response_data["operationStatusId"])
            self.assertEqual(MOCK_HTTP_RESPONSE_JOB_IN_PROGRESS["data"]["Status"]["State"]["Name"], response_data["operationStatus"])
            self.assertEqual(MOCK_HTTP_RESPONSE_JOB_IN_PROGRESS["data"]["Status"]["Health"][0]["Name"], response_data["operationHealth"])
            self.assertEqual(MOCK_HTTP_RESPONSE_JOB_IN_PROGRESS["data"]["Status"]["Health"][0]["ID"], response_data["operationHealthId"])
            self.assertTrue(response_data["jobExists"])
            self.assertFalse(response_data["changed"])
            self.assertEqual(ACTION_WAS_SUCCESSFUL, response_data["msg"])
            self.assertIsNone(response_data["details"])

    def test_job_status_complete(self):
        with patch.multiple("ansible_collections.community.general.plugins.module_utils.ocapi_utils.OcapiUtils",
                            get_request=mock_get_request,
                            put_request=mock_put_request,
                            delete_request=mock_delete_request,
                            post_request=mock_post_request):
            with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
                with set_module_args({
                    'category': 'Jobs',
                    'command': 'JobStatus',
                    'job_name': MOCK_JOB_NAME_COMPLETE,
                    'baseuri': MOCK_BASE_URI,
                    'username': 'USERID',
                    'password': 'PASSWORD=21'
                }):
                    module.main()
            self.assertEqual(ACTION_WAS_SUCCESSFUL, get_exception_message(ansible_exit_json))
            response_data = ansible_exit_json.exception.args[0]
            self.assertEqual(MOCK_HTTP_RESPONSE_JOB_COMPLETE["data"]["PercentComplete"], response_data["percentComplete"])
            self.assertEqual(MOCK_HTTP_RESPONSE_JOB_COMPLETE["data"]["Status"]["State"]["ID"], response_data["operationStatusId"])
            self.assertEqual(MOCK_HTTP_RESPONSE_JOB_COMPLETE["data"]["Status"]["State"]["Name"], response_data["operationStatus"])
            self.assertEqual(MOCK_HTTP_RESPONSE_JOB_COMPLETE["data"]["Status"]["Health"][0]["Name"], response_data["operationHealth"])
            self.assertEqual(MOCK_HTTP_RESPONSE_JOB_COMPLETE["data"]["Status"]["Health"][0]["ID"], response_data["operationHealthId"])
            self.assertTrue(response_data["jobExists"])
            self.assertFalse(response_data["changed"])
            self.assertEqual(ACTION_WAS_SUCCESSFUL, response_data["msg"])
            self.assertEqual(["Completed."], response_data["details"])

    def test_job_status_not_found(self):
        with patch.multiple("ansible_collections.community.general.plugins.module_utils.ocapi_utils.OcapiUtils",
                            get_request=mock_get_request,
                            put_request=mock_put_request,
                            delete_request=mock_delete_request,
                            post_request=mock_post_request):
            with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
                with set_module_args({
                    'category': 'Jobs',
                    'command': 'JobStatus',
                    'job_name': MOCK_JOB_NAME_DOES_NOT_EXIST,
                    'baseuri': MOCK_BASE_URI,
                    'username': 'USERID',
                    'password': 'PASSWORD=21'
                }):
                    module.main()
            self.assertEqual(ACTION_WAS_SUCCESSFUL, get_exception_message(ansible_exit_json))
            response_data = ansible_exit_json.exception.args[0]
            self.assertFalse(response_data["jobExists"])
            self.assertEqual(0, response_data["percentComplete"])
            self.assertEqual(1, response_data["operationStatusId"])
            self.assertEqual("Not Available", response_data["operationStatus"])
            self.assertIsNone(response_data["operationHealth"])
            self.assertIsNone(response_data["operationHealthId"])
            self.assertFalse(response_data["changed"])
            self.assertEqual(ACTION_WAS_SUCCESSFUL, response_data["msg"])
            self.assertEqual("Job does not exist.", response_data["details"])
