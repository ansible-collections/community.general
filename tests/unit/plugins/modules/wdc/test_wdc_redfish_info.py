# -*- coding: utf-8 -*-
# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.community.general.tests.unit.compat.mock import patch
from ansible_collections.community.general.tests.unit.compat import unittest
from ansible.module_utils import basic
import ansible_collections.community.general.plugins.modules.wdc_redfish_info as module
from ansible_collections.community.general.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson
from ansible_collections.community.general.tests.unit.plugins.modules.utils import set_module_args, exit_json, fail_json

MOCK_SUCCESSFUL_RESPONSE_WITH_ACTIONS = {
    "ret": True,
    "data": {
        "Actions": {}
    }
}

MOCK_SUCCESSFUL_HTTP_EMPTY_RESPONSE = {
    "ret": True,
    "data": {
    }
}

MOCK_SUCCESSFUL_RESPONSE_WITH_UPDATE_SERVICE_RESOURCE = {
    "ret": True,
    "data": {
        "UpdateService": {
            "@odata.id": "/UpdateService"
        }
    }
}

MOCK_SUCCESSFUL_RESPONSE_WITH_SIMPLE_UPDATE_BUT_NO_FW_ACTIVATE = {
    "ret": True,
    "data": {
        "Actions": {
            "#UpdateService.SimpleUpdate": {
                "target": "mocked value"
            },
            "Oem": {
                "WDC": {}  # No #UpdateService.FWActivate
            }
        }
    }
}


def get_bin_path(self, arg, required=False):
    """Mock AnsibleModule.get_bin_path"""
    return arg


def get_redfish_facts(ansible_exit_json):
    """From an AnsibleExitJson exception, get the redfish facts dict."""
    return ansible_exit_json.exception.args[0]["redfish_facts"]


def get_exception_message(ansible_exit_json):
    """From an AnsibleExitJson exception, get the message string."""
    return ansible_exit_json.exception.args[0]["msg"]


class TestWdcRedfishInfo(unittest.TestCase):

    def setUp(self):
        self.mock_module_helper = patch.multiple(basic.AnsibleModule,
                                                 exit_json=exit_json,
                                                 fail_json=fail_json,
                                                 get_bin_path=get_bin_path)
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)

    def test_module_fail_when_required_args_missing(self):
        with self.assertRaises(AnsibleFailJson):
            set_module_args({})
            module.main()

    def test_module_fail_when_unknown_category(self):
        with self.assertRaises(AnsibleFailJson):
            set_module_args({
                'category': 'unknown',
                'command': 'SimpleUpdateStatus',
                'username': 'USERID',
                'password': 'PASSW0RD=21',
                'ioms': [],
            })
            module.main()

    def test_module_fail_when_unknown_command(self):
        with self.assertRaises(AnsibleFailJson):
            set_module_args({
                'category': 'Update',
                'command': 'unknown',
                'username': 'USERID',
                'password': 'PASSW0RD=21',
                'ioms': [],
            })
            module.main()

    def test_module_simple_update_status_pass(self):
        set_module_args({
            'category': 'Update',
            'command': 'SimpleUpdateStatus',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'ioms': ["example1.example.com"],
        })

        def mock_simple_update_status(*args, **kwargs):
            return {
                "ret": True,
                "data": {
                    "Description": "Ready for FW update",
                    "ErrorCode": 0,
                    "EstimatedRemainingMinutes": 0,
                    "StatusCode": 0
                }
            }

        def mocked_string_response(*args, **kwargs):
            return "mockedUrl"

        def empty_return(*args, **kwargs):
            return {"ret": True}

        with patch.multiple(module.WdcRedfishUtils,
                            _simple_update_status_uri=mocked_string_response,
                            _find_updateservice_resource=empty_return,
                            _find_updateservice_additional_uris=empty_return,
                            get_request=mock_simple_update_status):
            with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
                module.main()
            redfish_facts = get_redfish_facts(ansible_exit_json)
            self.assertEqual(mock_simple_update_status()["data"],
                             redfish_facts["simple_update_status"]["entries"])

    def test_module_simple_update_status_updateservice_resource_not_found(self):
        set_module_args({
            'category': 'Update',
            'command': 'SimpleUpdateStatus',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'ioms': ["example1.example.com"],
        })
        with patch.object(module.WdcRedfishUtils, 'get_request') as mock_get_request:
            mock_get_request.return_value = {
                "ret": True,
                "data": {}  # Missing UpdateService property
            }
            with self.assertRaises(AnsibleFailJson) as ansible_exit_json:
                module.main()
            self.assertEqual("UpdateService resource not found",
                             get_exception_message(ansible_exit_json))

    def test_module_simple_update_status_service_does_not_support_simple_update(self):
        set_module_args({
            'category': 'Update',
            'command': 'SimpleUpdateStatus',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'ioms': ["example1.example.com"],
        })

        def mock_get_request_function(uri):
            mock_url_string = "mockURL"
            if mock_url_string in uri:
                return {
                    "ret": True,
                    "data": {
                        "Actions": {  # No #UpdateService.SimpleUpdate
                        }
                    }
                }
            else:
                return {
                    "ret": True,
                    "data": mock_url_string
                }

        with patch.object(module.WdcRedfishUtils, 'get_request') as mock_get_request:
            mock_get_request.side_effect = mock_get_request_function
            with self.assertRaises(AnsibleFailJson) as ansible_exit_json:
                module.main()
            self.assertEqual("UpdateService resource not found",
                             get_exception_message(ansible_exit_json))

    def test_module_simple_update_status_service_does_not_support_fw_activate(self):
        set_module_args({
            'category': 'Update',
            'command': 'SimpleUpdateStatus',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'ioms': ["example1.example.com"],
        })

        def mock_get_request_function(uri):
            if uri.endswith("/redfish/v1") or uri.endswith("/redfish/v1/"):
                return MOCK_SUCCESSFUL_RESPONSE_WITH_UPDATE_SERVICE_RESOURCE
            elif uri.endswith("/mockedUrl"):
                return MOCK_SUCCESSFUL_HTTP_EMPTY_RESPONSE
            elif uri.endswith("/UpdateService"):
                return MOCK_SUCCESSFUL_RESPONSE_WITH_SIMPLE_UPDATE_BUT_NO_FW_ACTIVATE
            else:
                raise RuntimeError("Illegal call to get_request in test: " + uri)

        with patch("ansible_collections.community.general.plugins.module_utils.wdc_redfish_utils.WdcRedfishUtils.get_request") as mock_get_request:
            mock_get_request.side_effect = mock_get_request_function
            with self.assertRaises(AnsibleFailJson) as ansible_exit_json:
                module.main()
            self.assertEqual("Service does not support FWActivate",
                             get_exception_message(ansible_exit_json))
