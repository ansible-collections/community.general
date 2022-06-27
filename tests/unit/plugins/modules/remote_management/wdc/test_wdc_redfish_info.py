# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.community.general.tests.unit.compat.mock import patch
from ansible_collections.community.general.tests.unit.compat import unittest
from ansible.module_utils import basic
import ansible_collections.community.general.plugins.modules.remote_management.redfish.wdc_redfish_info as module
from ansible_collections.community.general.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson
from ansible_collections.community.general.tests.unit.plugins.modules.utils import set_module_args, exit_json, fail_json


def get_bin_path(self, arg, required=False):
    """Mock AnsibleModule.get_bin_path"""
    return arg


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
            with patch.object(module, 'dns_available') as mock_dns_available:
                mock_dns_available.return_value = True
                with self.assertRaises(AnsibleExitJson) as exit_json:
                    module.main()
                    self.assertEqual(mock_simple_update_status,
                                     exit_json["redfish_facts"]["entries"])

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
            with patch.object(module, 'dns_available') as mock_dns_available:
                mock_dns_available.return_value = True
                with self.assertRaises(AnsibleFailJson) as exit_json:
                    module.main()
                    self.assertEqual("UpdateService resource not found",
                                     exit_json["msg"])

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
            with patch.object(module, 'dns_available') as mock_dns_available:
                mock_dns_available.return_value = True
                with self.assertRaises(AnsibleFailJson) as exit_json:
                    module.main()
                    self.assertEqual("UpdateService resource not found",
                                     exit_json["msg"])

    def test_module_simple_update_status_service_does_not_support_fw_activate(self):
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
                        "Actions": {
                            "#UpdateService.SimpleUpdate": "mocked value",
                            "Oem": {
                                "WDC": {}  # No #UpdateService.FWActivate
                            }
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
            with patch.object(module, 'dns_available') as mock_dns_available:
                mock_dns_available.return_value = True
                with self.assertRaises(AnsibleFailJson) as exit_json:
                    module.main()
                    self.assertEqual("Service does not support FWActivate",
                                     exit_json["msg"])
