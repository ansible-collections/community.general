# -*- coding: utf-8 -*-
# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import shutil
import uuid
import tarfile
import tempfile
import os

from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import patch
from ansible_collections.community.internal_test_tools.tests.unit.compat import unittest
from ansible.module_utils import basic
import ansible_collections.community.general.plugins.modules.wdc_redfish_command as module
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import set_module_args, exit_json, fail_json

MOCK_SUCCESSFUL_HTTP_EMPTY_RESPONSE = {
    "ret": True,
    "data": {
    }
}

MOCK_GET_ENCLOSURE_RESPONSE_SINGLE_TENANT = {
    "ret": True,
    "data": {
        "SerialNumber": "12345"
    }
}

MOCK_GET_ENCLOSURE_RESPONSE_MULTI_TENANT = {
    "ret": True,
    "data": {
        "SerialNumber": "12345-A"
    }
}

MOCK_URL_ERROR = {
    "ret": False,
    "msg": "This is a mock URL error",
    "status": 500
}

MOCK_SUCCESSFUL_RESPONSE_WITH_UPDATE_SERVICE_RESOURCE = {
    "ret": True,
    "data": {
        "UpdateService": {
            "@odata.id": "/UpdateService"
        },
        "Chassis": {
            "@odata.id": "/Chassis"
        }
    }
}

MOCK_SUCCESSFUL_RESPONSE_CHASSIS = {
    "ret": True,
    "data": {
        "Members": [
            {
                "@odata.id": "/redfish/v1/Chassis/Enclosure"
            }
        ]
    }
}

MOCK_SUCCESSFUL_RESPONSE_CHASSIS_ENCLOSURE = {
    "ret": True,
    "data": {
        "Id": "Enclosure",
        "IndicatorLED": "Off",
        "Actions": {
            "Oem": {
                "WDC": {
                    "#Chassis.Locate": {
                        "target": "/Chassis.Locate"
                    },
                    "#Chassis.PowerMode": {
                        "target": "/redfish/v1/Chassis/Enclosure/Actions/Chassis.PowerMode",
                    }
                }
            }
        },
        "Oem": {
            "WDC": {
                "PowerMode": "Normal"
            }
        }
    }
}

MOCK_SUCCESSFUL_RESPONSE_WITH_SIMPLE_UPDATE_AND_FW_ACTIVATE = {
    "ret": True,
    "data": {
        "Actions": {
            "#UpdateService.SimpleUpdate": {
                "target": "mocked value"
            },
            "Oem": {
                "WDC": {
                    "#UpdateService.FWActivate": {
                        "title": "Activate the downloaded firmware.",
                        "target": "/redfish/v1/UpdateService/Actions/UpdateService.FWActivate"
                    }
                }
            }
        }
    }
}

MOCK_SUCCESSFUL_RESPONSE_WITH_ACTIONS = {
    "ret": True,
    "data": {
        "Actions": {}
    }
}

MOCK_GET_IOM_A_MULTI_TENANT = {
    "ret": True,
    "data": {
        "Id": "IOModuleAFRU"
    }
}

MOCK_GET_IOM_B_MULTI_TENANAT = {
    "ret": True,
    "data": {
        "error": {
            "message": "IOM Module B cannot be read"
        }
    }
}


MOCK_READY_FOR_FW_UPDATE = {
    "ret": True,
    "entries": {
        "Description": "Ready for FW update",
        "StatusCode": 0
    }
}

MOCK_FW_UPDATE_IN_PROGRESS = {
    "ret": True,
    "entries": {
        "Description": "FW update in progress",
        "StatusCode": 1
    }
}

MOCK_WAITING_FOR_ACTIVATION = {
    "ret": True,
    "entries": {
        "Description": "FW update completed. Waiting for activation.",
        "StatusCode": 2
    }
}

MOCK_SIMPLE_UPDATE_STATUS_LIST = [
    MOCK_READY_FOR_FW_UPDATE,
    MOCK_FW_UPDATE_IN_PROGRESS,
    MOCK_WAITING_FOR_ACTIVATION
]


def get_bin_path(self, arg, required=False):
    """Mock AnsibleModule.get_bin_path"""
    return arg


def get_exception_message(ansible_exit_json):
    """From an AnsibleExitJson exception, get the message string."""
    return ansible_exit_json.exception.args[0]["msg"]


def is_changed(ansible_exit_json):
    """From an AnsibleExitJson exception, return the value of the changed flag"""
    return ansible_exit_json.exception.args[0]["changed"]


def mock_simple_update(*args, **kwargs):
    return {
        "ret": True
    }


def mocked_url_response(*args, **kwargs):
    """Mock to just return a generic string."""
    return "/mockedUrl"


def mock_update_url(*args, **kwargs):
    """Mock of the update url"""
    return "/UpdateService"


def mock_fw_activate_url(*args, **kwargs):
    """Mock of the FW Activate URL"""
    return "/UpdateService.FWActivate"


def empty_return(*args, **kwargs):
    """Mock to just return an empty successful return."""
    return {"ret": True}


def mock_get_simple_update_status_ready_for_fw_update(*args, **kwargs):
    """Mock to return simple update status Ready for FW update"""
    return MOCK_READY_FOR_FW_UPDATE


def mock_get_request_enclosure_single_tenant(*args, **kwargs):
    """Mock for get_request for single-tenant enclosure."""
    if args[1].endswith("/redfish/v1") or args[1].endswith("/redfish/v1/"):
        return MOCK_SUCCESSFUL_RESPONSE_WITH_UPDATE_SERVICE_RESOURCE
    elif args[1].endswith("/mockedUrl"):
        return MOCK_SUCCESSFUL_HTTP_EMPTY_RESPONSE
    elif args[1].endswith("Chassis/Enclosure"):
        return MOCK_GET_ENCLOSURE_RESPONSE_SINGLE_TENANT
    elif args[1].endswith("/UpdateService"):
        return MOCK_SUCCESSFUL_RESPONSE_WITH_SIMPLE_UPDATE_AND_FW_ACTIVATE
    else:
        raise RuntimeError("Illegal call to get_request in test: " + args[1])


def mock_get_request_enclosure_multi_tenant(*args, **kwargs):
    """Mock for get_request with multi-tenant enclosure."""
    if args[1].endswith("/redfish/v1") or args[1].endswith("/redfish/v1/"):
        return MOCK_SUCCESSFUL_RESPONSE_WITH_UPDATE_SERVICE_RESOURCE
    elif args[1].endswith("/mockedUrl"):
        return MOCK_SUCCESSFUL_HTTP_EMPTY_RESPONSE
    elif args[1].endswith("Chassis/Enclosure"):
        return MOCK_GET_ENCLOSURE_RESPONSE_MULTI_TENANT
    elif args[1].endswith("/UpdateService"):
        return MOCK_SUCCESSFUL_RESPONSE_WITH_SIMPLE_UPDATE_AND_FW_ACTIVATE
    elif args[1].endswith("/IOModuleAFRU"):
        return MOCK_GET_IOM_A_MULTI_TENANT
    elif args[1].endswith("/IOModuleBFRU"):
        return MOCK_GET_IOM_B_MULTI_TENANAT
    else:
        raise RuntimeError("Illegal call to get_request in test: " + args[1])


def mock_get_request(*args, **kwargs):
    """Mock for get_request for simple resource tests."""
    if args[1].endswith("/redfish/v1") or args[1].endswith("/redfish/v1/"):
        return MOCK_SUCCESSFUL_RESPONSE_WITH_UPDATE_SERVICE_RESOURCE
    elif args[1].endswith("/Chassis"):
        return MOCK_SUCCESSFUL_RESPONSE_CHASSIS
    elif args[1].endswith("Chassis/Enclosure"):
        return MOCK_SUCCESSFUL_RESPONSE_CHASSIS_ENCLOSURE
    else:
        raise RuntimeError("Illegal call to get_request in test: " + args[1])


def mock_post_request(*args, **kwargs):
    """Mock post_request with successful response."""
    valid_endpoints = [
        "/UpdateService.FWActivate",
        "/Chassis.Locate",
        "/Chassis.PowerMode",
    ]
    for endpoint in valid_endpoints:
        if args[1].endswith(endpoint):
            return {
                "ret": True,
                "data": ACTION_WAS_SUCCESSFUL_MESSAGE
            }
    raise RuntimeError("Illegal POST call to: " + args[1])


def mock_get_firmware_inventory_version_1_2_3(*args, **kwargs):
    return {
        "ret": True,
        "entries": [
            {
                "Id": "IOModuleA_OOBM",
                "Version": "1.2.3"
            },
            {
                "Id": "IOModuleB_OOBM",
                "Version": "1.2.3"
            }
        ]
    }


ERROR_MESSAGE_UNABLE_TO_EXTRACT_BUNDLE_VERSION = "Unable to extract bundle version or multi-tenant status or generation from update image file"
ACTION_WAS_SUCCESSFUL_MESSAGE = "Action was successful"


class TestWdcRedfishCommand(unittest.TestCase):

    def setUp(self):
        self.mock_module_helper = patch.multiple(basic.AnsibleModule,
                                                 exit_json=exit_json,
                                                 fail_json=fail_json,
                                                 get_bin_path=get_bin_path)
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_module_fail_when_required_args_missing(self):
        with self.assertRaises(AnsibleFailJson):
            with set_module_args({}):
                module.main()

    def test_module_fail_when_unknown_category(self):
        with self.assertRaises(AnsibleFailJson):
            with set_module_args({
                'category': 'unknown',
                'command': 'FWActivate',
                'username': 'USERID',
                'password': 'PASSW0RD=21',
                'ioms': [],
            }):
                module.main()

    def test_module_fail_when_unknown_command(self):
        with self.assertRaises(AnsibleFailJson):
            with set_module_args({
                'category': 'Update',
                'command': 'unknown',
                'username': 'USERID',
                'password': 'PASSW0RD=21',
                'ioms': [],
            }):
                module.main()

    def test_module_chassis_power_mode_low(self):
        """Test setting chassis power mode to low (happy path)."""
        module_args = {
            'category': 'Chassis',
            'command': 'PowerModeLow',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'resource_id': 'Enclosure',
            'baseuri': 'example.com'
        }
        with set_module_args(module_args):
            with patch.multiple("ansible_collections.community.general.plugins.module_utils.wdc_redfish_utils.WdcRedfishUtils",
                                get_request=mock_get_request,
                                post_request=mock_post_request):
                with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
                    module.main()
                self.assertEqual(ACTION_WAS_SUCCESSFUL_MESSAGE,
                                 get_exception_message(ansible_exit_json))
                self.assertTrue(is_changed(ansible_exit_json))

    def test_module_chassis_power_mode_normal_when_already_normal(self):
        """Test setting chassis power mode to normal when it already is.  Verify we get changed=False."""
        module_args = {
            'category': 'Chassis',
            'command': 'PowerModeNormal',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'resource_id': 'Enclosure',
            'baseuri': 'example.com'
        }
        with set_module_args(module_args):
            with patch.multiple("ansible_collections.community.general.plugins.module_utils.wdc_redfish_utils.WdcRedfishUtils",
                                get_request=mock_get_request):
                with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
                    module.main()
                self.assertEqual(ACTION_WAS_SUCCESSFUL_MESSAGE,
                                 get_exception_message(ansible_exit_json))
                self.assertFalse(is_changed(ansible_exit_json))

    def test_module_chassis_power_mode_invalid_command(self):
        """Test that we get an error when issuing an invalid PowerMode command."""
        module_args = {
            'category': 'Chassis',
            'command': 'PowerModeExtraHigh',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'resource_id': 'Enclosure',
            'baseuri': 'example.com'
        }
        with set_module_args(module_args):
            with patch.multiple("ansible_collections.community.general.plugins.module_utils.wdc_redfish_utils.WdcRedfishUtils",
                                get_request=mock_get_request):
                with self.assertRaises(AnsibleFailJson) as ansible_fail_json:
                    module.main()
                expected_error_message = "Invalid Command 'PowerModeExtraHigh'"
                self.assertIn(expected_error_message,
                              get_exception_message(ansible_fail_json))

    def test_module_enclosure_led_indicator_on(self):
        """Test turning on a valid LED indicator (in this case we use the Enclosure resource)."""
        module_args = {
            'category': 'Chassis',
            'command': 'IndicatorLedOn',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            "resource_id": "Enclosure",
            "baseuri": "example.com"
        }
        with set_module_args(module_args):
            with patch.multiple("ansible_collections.community.general.plugins.module_utils.wdc_redfish_utils.WdcRedfishUtils",
                                get_request=mock_get_request,
                                post_request=mock_post_request):
                with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
                    module.main()
                self.assertEqual(ACTION_WAS_SUCCESSFUL_MESSAGE,
                                 get_exception_message(ansible_exit_json))
                self.assertTrue(is_changed(ansible_exit_json))

    def test_module_invalid_resource_led_indicator_on(self):
        """Test turning LED on for an invalid resource id."""
        module_args = {
            'category': 'Chassis',
            'command': 'IndicatorLedOn',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            "resource_id": "Disk99",
            "baseuri": "example.com"
        }
        with set_module_args(module_args):
            with patch.multiple("ansible_collections.community.general.plugins.module_utils.wdc_redfish_utils.WdcRedfishUtils",
                                get_request=mock_get_request,
                                post_request=mock_post_request):
                with self.assertRaises(AnsibleFailJson) as ansible_fail_json:
                    module.main()
                expected_error_message = "Chassis resource Disk99 not found"
                self.assertEqual(expected_error_message,
                                 get_exception_message(ansible_fail_json))

    def test_module_enclosure_led_off_already_off(self):
        """Test turning LED indicator off when it's already off.  Confirm changed is False and no POST occurs."""
        module_args = {
            'category': 'Chassis',
            'command': 'IndicatorLedOff',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            "resource_id": "Enclosure",
            "baseuri": "example.com"
        }
        with set_module_args(module_args):
            with patch.multiple("ansible_collections.community.general.plugins.module_utils.wdc_redfish_utils.WdcRedfishUtils",
                                get_request=mock_get_request):
                with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
                    module.main()
                self.assertEqual(ACTION_WAS_SUCCESSFUL_MESSAGE,
                                 get_exception_message(ansible_exit_json))
                self.assertFalse(is_changed(ansible_exit_json))

    def test_module_fw_activate_first_iom_unavailable(self):
        """Test that if the first IOM is not available, the 2nd one is used."""
        ioms = [
            "bad.example.com",
            "good.example.com"
        ]
        module_args = {
            'category': 'Update',
            'command': 'FWActivate',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'ioms': ioms
        }
        with set_module_args(module_args):

            def mock_get_request(*args, **kwargs):
                """Mock for get_request that will fail on the 'bad' IOM."""
                if "bad.example.com" in args[1]:
                    return MOCK_URL_ERROR
                else:
                    return mock_get_request_enclosure_single_tenant(*args, **kwargs)

            with patch.multiple(module.WdcRedfishUtils,
                                _firmware_activate_uri=mock_fw_activate_url,
                                _update_uri=mock_update_url,
                                _find_updateservice_resource=empty_return,
                                _find_updateservice_additional_uris=empty_return,
                                get_request=mock_get_request,
                                post_request=mock_post_request):
                with self.assertRaises(AnsibleExitJson) as cm:
                    module.main()
                self.assertEqual(ACTION_WAS_SUCCESSFUL_MESSAGE,
                                 get_exception_message(cm))

    def test_module_fw_activate_pass(self):
        """Test the FW Activate command in a passing scenario."""
        # Run the same test twice -- once specifying ioms, and once specifying baseuri.
        # Both should work the same way.
        uri_specifiers = [
            {
                "ioms": ["example1.example.com"]
            },
            {
                "baseuri": "example1.example.com"
            }
        ]
        for uri_specifier in uri_specifiers:
            module_args = {
                'category': 'Update',
                'command': 'FWActivate',
                'username': 'USERID',
                'password': 'PASSW0RD=21',
            }
            module_args.update(uri_specifier)
            with set_module_args(module_args):
                with patch.multiple("ansible_collections.community.general.plugins.module_utils.wdc_redfish_utils.WdcRedfishUtils",
                                    _firmware_activate_uri=mock_fw_activate_url,
                                    _update_uri=mock_update_url,
                                    _find_updateservice_resource=empty_return,
                                    _find_updateservice_additional_uris=empty_return,
                                    get_request=mock_get_request_enclosure_single_tenant,
                                    post_request=mock_post_request):
                    with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
                        module.main()
                    self.assertEqual(ACTION_WAS_SUCCESSFUL_MESSAGE,
                                     get_exception_message(ansible_exit_json))
                    self.assertTrue(is_changed(ansible_exit_json))

    def test_module_fw_activate_service_does_not_support_fw_activate(self):
        """Test FW Activate when it is not supported."""
        expected_error_message = "Service does not support FWActivate"
        with set_module_args({
            'category': 'Update',
            'command': 'FWActivate',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'ioms': ["example1.example.com"]
        }):

            def mock_update_uri_response(*args, **kwargs):
                return {
                    "ret": True,
                    "data": {}  # No Actions
                }

            with patch.multiple(module.WdcRedfishUtils,
                                _firmware_activate_uri=mocked_url_response,
                                _update_uri=mock_update_url,
                                _find_updateservice_resource=empty_return,
                                _find_updateservice_additional_uris=empty_return,
                                get_request=mock_update_uri_response):
                with self.assertRaises(AnsibleFailJson) as cm:
                    module.main()
                self.assertEqual(expected_error_message,
                                 get_exception_message(cm))

    def test_module_update_and_activate_image_uri_not_http(self):
        """Test Update and Activate when URI is not http(s)"""
        expected_error_message = "Bundle URI must be HTTP or HTTPS"
        with set_module_args({
            'category': 'Update',
            'command': 'UpdateAndActivate',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'ioms': ["example1.example.com"],
            'update_image_uri': "ftp://example.com/image"
        }):
            with patch.multiple(module.WdcRedfishUtils,
                                _firmware_activate_uri=mocked_url_response,
                                _update_uri=mock_update_url,
                                _find_updateservice_resource=empty_return,
                                _find_updateservice_additional_uris=empty_return):
                with self.assertRaises(AnsibleFailJson) as cm:
                    module.main()
                self.assertEqual(expected_error_message,
                                 get_exception_message(cm))

    def test_module_update_and_activate_target_not_ready_for_fw_update(self):
        """Test Update and Activate when target is not in the correct state."""
        mock_status_code = 999
        mock_status_description = "mock status description"
        expected_error_message = "Target is not ready for FW update.  Current status: {0} ({1})".format(
            mock_status_code,
            mock_status_description
        )
        with set_module_args({
            'category': 'Update',
            'command': 'UpdateAndActivate',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'ioms': ["example1.example.com"],
            'update_image_uri': "http://example.com/image"
        }):
            with patch.object(module.WdcRedfishUtils, "get_simple_update_status") as mock_get_simple_update_status:
                mock_get_simple_update_status.return_value = {
                    "ret": True,
                    "entries": {
                        "StatusCode": mock_status_code,
                        "Description": mock_status_description
                    }
                }

                with patch.multiple(module.WdcRedfishUtils,
                                    _firmware_activate_uri=mocked_url_response,
                                    _update_uri=mock_update_url,
                                    _find_updateservice_resource=empty_return,
                                    _find_updateservice_additional_uris=empty_return):
                    with self.assertRaises(AnsibleFailJson) as cm:
                        module.main()
                    self.assertEqual(expected_error_message,
                                     get_exception_message(cm))

    def test_module_update_and_activate_bundle_not_a_tarfile(self):
        """Test Update and Activate when bundle is not a tarfile"""
        mock_filename = os.path.abspath(__file__)
        expected_error_message = ERROR_MESSAGE_UNABLE_TO_EXTRACT_BUNDLE_VERSION
        with set_module_args({
            'category': 'Update',
            'command': 'UpdateAndActivate',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'ioms': ["example1.example.com"],
            'update_image_uri': "http://example.com/image",
            "update_creds": {
                "username": "image_user",
                "password": "image_password"
            }
        }):
            with patch('ansible_collections.community.general.plugins.module_utils.wdc_redfish_utils.fetch_file') as mock_fetch_file:
                mock_fetch_file.return_value = mock_filename
                with patch.multiple(module.WdcRedfishUtils,
                                    get_simple_update_status=mock_get_simple_update_status_ready_for_fw_update,
                                    _firmware_activate_uri=mocked_url_response,
                                    _update_uri=mock_update_url,
                                    _find_updateservice_resource=empty_return,
                                    _find_updateservice_additional_uris=empty_return):
                    with self.assertRaises(AnsibleFailJson) as cm:
                        module.main()
                    self.assertEqual(expected_error_message,
                                     get_exception_message(cm))

    def test_module_update_and_activate_bundle_contains_no_firmware_version(self):
        """Test Update and Activate when bundle contains no firmware version"""
        expected_error_message = ERROR_MESSAGE_UNABLE_TO_EXTRACT_BUNDLE_VERSION
        with set_module_args({
            'category': 'Update',
            'command': 'UpdateAndActivate',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'ioms': ["example1.example.com"],
            'update_image_uri': "http://example.com/image",
            "update_creds": {
                "username": "image_user",
                "password": "image_password"
            }
        }):

            tar_name = "empty_tarfile{0}.tar".format(uuid.uuid4())
            empty_tarfile = tarfile.open(os.path.join(self.tempdir, tar_name), "w")
            empty_tarfile.close()
            with patch('ansible_collections.community.general.plugins.module_utils.wdc_redfish_utils.fetch_file') as mock_fetch_file:
                mock_fetch_file.return_value = os.path.join(self.tempdir, tar_name)
                with patch.multiple(module.WdcRedfishUtils,
                                    get_simple_update_status=mock_get_simple_update_status_ready_for_fw_update,
                                    _firmware_activate_uri=mocked_url_response,
                                    _update_uri=mock_update_url,
                                    _find_updateservice_resource=empty_return,
                                    _find_updateservice_additional_uris=empty_return):
                    with self.assertRaises(AnsibleFailJson) as cm:
                        module.main()
                    self.assertEqual(expected_error_message,
                                     get_exception_message(cm))

    def test_module_update_and_activate_version_already_installed(self):
        """Test Update and Activate when the bundle version is already installed"""
        mock_firmware_version = "1.2.3"
        expected_error_message = ACTION_WAS_SUCCESSFUL_MESSAGE
        with set_module_args({
            'category': 'Update',
            'command': 'UpdateAndActivate',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'ioms': ["example1.example.com"],
            'update_image_uri': "http://example.com/image",
            "update_creds": {
                "username": "image_user",
                "password": "image_password"
            }
        }):

            tar_name = self.generate_temp_bundlefile(mock_firmware_version=mock_firmware_version,
                                                     is_multi_tenant=False)
            with patch('ansible_collections.community.general.plugins.module_utils.wdc_redfish_utils.fetch_file') as mock_fetch_file:
                mock_fetch_file.return_value = os.path.join(self.tempdir, tar_name)
                with patch.multiple(module.WdcRedfishUtils,
                                    get_firmware_inventory=mock_get_firmware_inventory_version_1_2_3,
                                    get_simple_update_status=mock_get_simple_update_status_ready_for_fw_update,
                                    _firmware_activate_uri=mocked_url_response,
                                    _update_uri=mock_update_url,
                                    _find_updateservice_resource=empty_return,
                                    _find_updateservice_additional_uris=empty_return,
                                    get_request=mock_get_request_enclosure_single_tenant):
                    with self.assertRaises(AnsibleExitJson) as result:
                        module.main()
                    self.assertEqual(expected_error_message,
                                     get_exception_message(result))
                    self.assertFalse(is_changed(result))

    def test_module_update_and_activate_version_already_installed_multi_tenant(self):
        """Test Update and Activate on multi-tenant when version is already installed"""
        mock_firmware_version = "1.2.3"
        expected_error_message = ACTION_WAS_SUCCESSFUL_MESSAGE
        with set_module_args({
            'category': 'Update',
            'command': 'UpdateAndActivate',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'ioms': ["example1.example.com"],
            'update_image_uri': "http://example.com/image",
            "update_creds": {
                "username": "image_user",
                "password": "image_password"
            }
        }):

            tar_name = self.generate_temp_bundlefile(mock_firmware_version=mock_firmware_version,
                                                     is_multi_tenant=True)
            with patch('ansible_collections.community.general.plugins.module_utils.wdc_redfish_utils.fetch_file') as mock_fetch_file:
                mock_fetch_file.return_value = os.path.join(self.tempdir, tar_name)
                with patch.multiple(module.WdcRedfishUtils,
                                    get_firmware_inventory=mock_get_firmware_inventory_version_1_2_3,
                                    get_simple_update_status=mock_get_simple_update_status_ready_for_fw_update,
                                    _firmware_activate_uri=mocked_url_response,
                                    _update_uri=mock_update_url,
                                    _find_updateservice_resource=empty_return,
                                    _find_updateservice_additional_uris=empty_return,
                                    get_request=mock_get_request_enclosure_multi_tenant):
                    with self.assertRaises(AnsibleExitJson) as result:
                        module.main()
                    self.assertEqual(expected_error_message,
                                     get_exception_message(result))
                    self.assertFalse(is_changed(result))

    def test_module_update_and_activate_pass(self):
        """Test Update and Activate (happy path)"""
        mock_firmware_version = "1.2.2"
        with set_module_args({
            'category': 'Update',
            'command': 'UpdateAndActivate',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'ioms': ["example1.example.com"],
            'update_image_uri': "http://example.com/image",
            "update_creds": {
                "username": "image_user",
                "password": "image_password"
            }
        }):

            tar_name = self.generate_temp_bundlefile(mock_firmware_version=mock_firmware_version,
                                                     is_multi_tenant=False)

            with patch('ansible_collections.community.general.plugins.module_utils.wdc_redfish_utils.fetch_file') as mock_fetch_file:
                mock_fetch_file.return_value = os.path.join(self.tempdir, tar_name)
                with patch.multiple("ansible_collections.community.general.plugins.module_utils.wdc_redfish_utils.WdcRedfishUtils",
                                    get_firmware_inventory=mock_get_firmware_inventory_version_1_2_3,
                                    simple_update=mock_simple_update,
                                    _simple_update_status_uri=mocked_url_response,
                                    # _find_updateservice_resource=empty_return,
                                    # _find_updateservice_additional_uris=empty_return,
                                    get_request=mock_get_request_enclosure_single_tenant,
                                    post_request=mock_post_request):

                    with patch("ansible_collections.community.general.plugins.module_utils.wdc_redfish_utils.WdcRedfishUtils.get_simple_update_status"
                               ) as mock_get_simple_update_status:
                        mock_get_simple_update_status.side_effect = MOCK_SIMPLE_UPDATE_STATUS_LIST
                        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
                            module.main()
                        self.assertTrue(is_changed(ansible_exit_json))
                        self.assertEqual(ACTION_WAS_SUCCESSFUL_MESSAGE, get_exception_message(ansible_exit_json))

    def test_module_update_and_activate_pass_multi_tenant(self):
        """Test Update and Activate with multi-tenant (happy path)"""
        mock_firmware_version = "1.2.2"
        with set_module_args({
            'category': 'Update',
            'command': 'UpdateAndActivate',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'ioms': ["example1.example.com"],
            'update_image_uri': "http://example.com/image",
            "update_creds": {
                "username": "image_user",
                "password": "image_password"
            }
        }):

            tar_name = self.generate_temp_bundlefile(mock_firmware_version=mock_firmware_version,
                                                     is_multi_tenant=True)

            with patch('ansible_collections.community.general.plugins.module_utils.wdc_redfish_utils.fetch_file') as mock_fetch_file:
                mock_fetch_file.return_value = os.path.join(self.tempdir, tar_name)
                with patch.multiple(module.WdcRedfishUtils,
                                    get_firmware_inventory=mock_get_firmware_inventory_version_1_2_3,
                                    simple_update=mock_simple_update,
                                    _simple_update_status_uri=mocked_url_response,
                                    # _find_updateservice_resource=empty_return,
                                    # _find_updateservice_additional_uris=empty_return,
                                    get_request=mock_get_request_enclosure_multi_tenant,
                                    post_request=mock_post_request):
                    with patch("ansible_collections.community.general.plugins.module_utils.wdc_redfish_utils.WdcRedfishUtils.get_simple_update_status"
                               ) as mock_get_simple_update_status:
                        mock_get_simple_update_status.side_effect = MOCK_SIMPLE_UPDATE_STATUS_LIST
                        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
                            module.main()
                        self.assertTrue(is_changed(ansible_exit_json))
                        self.assertEqual(ACTION_WAS_SUCCESSFUL_MESSAGE, get_exception_message(ansible_exit_json))

    def test_module_fw_update_multi_tenant_firmware_single_tenant_enclosure(self):
        """Test Update and Activate using multi-tenant bundle on single-tenant enclosure"""
        mock_firmware_version = "1.1.1"
        expected_error_message = "Enclosure multi-tenant is False but bundle multi-tenant is True"
        with set_module_args({
            'category': 'Update',
            'command': 'UpdateAndActivate',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'ioms': ["example1.example.com"],
            'update_image_uri': "http://example.com/image",
            "update_creds": {
                "username": "image_user",
                "password": "image_password"
            }
        }):

            tar_name = self.generate_temp_bundlefile(mock_firmware_version=mock_firmware_version,
                                                     is_multi_tenant=True)
            with patch('ansible_collections.community.general.plugins.module_utils.wdc_redfish_utils.fetch_file') as mock_fetch_file:
                mock_fetch_file.return_value = os.path.join(self.tempdir, tar_name)
                with patch.multiple(module.WdcRedfishUtils,
                                    get_firmware_inventory=mock_get_firmware_inventory_version_1_2_3(),
                                    get_simple_update_status=mock_get_simple_update_status_ready_for_fw_update,
                                    _firmware_activate_uri=mocked_url_response,
                                    _update_uri=mock_update_url,
                                    _find_updateservice_resource=empty_return,
                                    _find_updateservice_additional_uris=empty_return,
                                    get_request=mock_get_request_enclosure_single_tenant):
                    with self.assertRaises(AnsibleFailJson) as result:
                        module.main()
                    self.assertEqual(expected_error_message,
                                     get_exception_message(result))

    def test_module_fw_update_single_tentant_firmware_multi_tenant_enclosure(self):
        """Test Update and Activate using singe-tenant bundle on multi-tenant enclosure"""
        mock_firmware_version = "1.1.1"
        expected_error_message = "Enclosure multi-tenant is True but bundle multi-tenant is False"
        with set_module_args({
            'category': 'Update',
            'command': 'UpdateAndActivate',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'ioms': ["example1.example.com"],
            'update_image_uri': "http://example.com/image",
            "update_creds": {
                "username": "image_user",
                "password": "image_password"
            }
        }):

            tar_name = self.generate_temp_bundlefile(mock_firmware_version=mock_firmware_version,
                                                     is_multi_tenant=False)
            with patch('ansible_collections.community.general.plugins.module_utils.wdc_redfish_utils.fetch_file') as mock_fetch_file:
                mock_fetch_file.return_value = os.path.join(self.tempdir, tar_name)
                with patch.multiple(module.WdcRedfishUtils,
                                    get_firmware_inventory=mock_get_firmware_inventory_version_1_2_3(),
                                    get_simple_update_status=mock_get_simple_update_status_ready_for_fw_update,
                                    _firmware_activate_uri=mocked_url_response,
                                    _update_uri=mock_update_url,
                                    _find_updateservice_resource=empty_return,
                                    _find_updateservice_additional_uris=empty_return,
                                    get_request=mock_get_request_enclosure_multi_tenant):
                    with self.assertRaises(AnsibleFailJson) as result:
                        module.main()
                    self.assertEqual(expected_error_message,
                                     get_exception_message(result))

    def generate_temp_bundlefile(self,
                                 mock_firmware_version,
                                 is_multi_tenant):
        """Generate a temporary fake bundle file.

        :param str mock_firmware_version: The simulated firmware version for the bundle.
        :param bool is_multi_tenant: Is the simulated bundle multi-tenant?

        This can be used for a mock FW update.
        """
        tar_name = "tarfile{0}.tar".format(uuid.uuid4())

        bundle_tarfile = tarfile.open(os.path.join(self.tempdir, tar_name), "w")
        package_filename = "oobm-{0}.pkg".format(mock_firmware_version)
        package_filename_path = os.path.join(self.tempdir, package_filename)
        with open(package_filename_path, "w"):
            pass
        bundle_tarfile.add(os.path.join(self.tempdir, package_filename), arcname=package_filename)
        bin_filename = "firmware.bin"
        bin_filename_path = os.path.join(self.tempdir, bin_filename)
        with open(bin_filename_path, "wb") as bin_file:
            byte_to_write = b'\x80' if is_multi_tenant else b'\xFF'
            bin_file.write(byte_to_write * 12)
        for filename in [package_filename, bin_filename]:
            bundle_tarfile.add(os.path.join(self.tempdir, filename), arcname=filename)
        bundle_tarfile.close()
        return tar_name
