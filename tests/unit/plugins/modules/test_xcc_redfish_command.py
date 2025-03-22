# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import patch
from ansible_collections.community.internal_test_tools.tests.unit.compat import unittest
from ansible.module_utils import basic
import ansible_collections.community.general.plugins.modules.xcc_redfish_command as module
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import set_module_args, exit_json, fail_json


def get_bin_path(self, arg, required=False):
    """Mock AnsibleModule.get_bin_path"""
    return arg


class TestXCCRedfishCommand(unittest.TestCase):

    def setUp(self):
        self.mock_module_helper = patch.multiple(basic.AnsibleModule,
                                                 exit_json=exit_json,
                                                 fail_json=fail_json,
                                                 get_bin_path=get_bin_path)
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)

    def test_module_fail_when_required_args_missing(self):
        with self.assertRaises(AnsibleFailJson):
            with set_module_args({}):
                module.main()

    def test_module_fail_when_unknown_category(self):
        with self.assertRaises(AnsibleFailJson):
            with set_module_args({
                'category': 'unknown',
                'command': 'VirtualMediaEject',
                'baseuri': '10.245.39.251',
                'username': 'USERID',
                'password': 'PASSW0RD=21',
            }):
                module.main()

    def test_module_fail_when_unknown_command(self):
        with self.assertRaises(AnsibleFailJson):
            with set_module_args({
                'category': 'Manager',
                'command': 'unknown',
                'baseuri': '10.245.39.251',
                'username': 'USERID',
                'password': 'PASSW0RD=21',
            }):
                module.main()

    def test_module_command_VirtualMediaInsert_pass(self):
        with set_module_args({
            'category': 'Manager',
            'command': 'VirtualMediaInsert',
            'baseuri': '10.245.39.251',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'timeout': 30,
            'virtual_media': {
                'image_url': "nfs://10.245.52.18:/home/nfs/bootable-sr635-20210111-autorun.iso",
                'media_types': ['CD'],
                'inserted': True,
                'write_protected': True,
                'transfer_protocol_type': 'NFS'
            }
        }):
            with patch.object(module.XCCRedfishUtils, '_find_systems_resource') as mock__find_systems_resource:
                mock__find_systems_resource.return_value = {'ret': True, 'changed': True, 'msg': 'success'}
                with patch.object(module.XCCRedfishUtils, '_find_managers_resource') as mock__find_managers_resource:
                    mock__find_managers_resource.return_value = {'ret': True, 'changed': True, 'msg': 'success'}

                    with patch.object(module.XCCRedfishUtils, 'virtual_media_insert') as mock_virtual_media_insert:
                        mock_virtual_media_insert.return_value = {'ret': True, 'changed': True, 'msg': 'success'}

                        with self.assertRaises(AnsibleExitJson) as result:
                            module.main()

    def test_module_command_VirtualMediaEject_pass(self):
        with set_module_args({
            'category': 'Manager',
            'command': 'VirtualMediaEject',
            'baseuri': '10.245.39.251',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'timeout': 30,
            'virtual_media': {
                'image_url': "nfs://10.245.52.18:/home/nfs/bootable-sr635-20210111-autorun.iso",
            }
        }):
            with patch.object(module.XCCRedfishUtils, '_find_systems_resource') as mock__find_systems_resource:
                mock__find_systems_resource.return_value = {'ret': True, 'changed': True, 'msg': 'success'}
                with patch.object(module.XCCRedfishUtils, '_find_managers_resource') as mock__find_managers_resource:
                    mock__find_managers_resource.return_value = {'ret': True, 'changed': True, 'msg': 'success'}

                    with patch.object(module.XCCRedfishUtils, 'virtual_media_eject') as mock_virtual_media_eject:
                        mock_virtual_media_eject.return_value = {'ret': True, 'changed': True, 'msg': 'success'}

                        with self.assertRaises(AnsibleExitJson) as result:
                            module.main()

    def test_module_command_VirtualMediaEject_fail_when_required_args_missing(self):
        with self.assertRaises(AnsibleFailJson):
            with set_module_args({
                'category': 'Manager',
                'command': 'VirtualMediaEject',
                'baseuri': '10.245.39.251',
                'username': 'USERID',
                'password': 'PASSW0RD=21',
            }):
                module.main()

    def test_module_command_GetResource_fail_when_required_args_missing(self):
        with set_module_args({
            'category': 'Raw',
            'command': 'GetResource',
            'baseuri': '10.245.39.251',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
        }):
            with patch.object(module.XCCRedfishUtils, 'get_request') as mock_get_request:
                mock_get_request.return_value = {'ret': True, 'data': {'teststr': 'xxxx'}}

                with self.assertRaises(AnsibleFailJson) as result:
                    module.main()

    def test_module_command_GetResource_fail_when_get_return_false(self):
        with set_module_args({
            'category': 'Raw',
            'command': 'GetResource',
            'baseuri': '10.245.39.251',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'resource_uri': '/redfish/v1/testuri',
        }):
            with patch.object(module.XCCRedfishUtils, 'get_request') as mock_get_request:
                mock_get_request.return_value = {'ret': False, 'msg': '404 error'}

                with self.assertRaises(AnsibleFailJson) as result:
                    module.main()

    def test_module_command_GetResource_pass(self):
        with set_module_args({
            'category': 'Raw',
            'command': 'GetResource',
            'baseuri': '10.245.39.251',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'resource_uri': '/redfish/v1/testuri',
        }):
            with patch.object(module.XCCRedfishUtils, 'get_request') as mock_get_request:
                mock_get_request.return_value = {'ret': True, 'data': {'teststr': 'xxxx'}}

                with self.assertRaises(AnsibleExitJson) as result:
                    module.main()

    def test_module_command_GetCollectionResource_fail_when_required_args_missing(self):
        with set_module_args({
            'category': 'Raw',
            'command': 'GetCollectionResource',
            'baseuri': '10.245.39.251',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
        }):
            with patch.object(module.XCCRedfishUtils, 'get_request') as mock_get_request:
                mock_get_request.return_value = {'ret': True, 'data': {'teststr': 'xxxx'}}

                with self.assertRaises(AnsibleFailJson) as result:
                    module.main()

    def test_module_command_GetCollectionResource_fail_when_get_return_false(self):
        with set_module_args({
            'category': 'Raw',
            'command': 'GetCollectionResource',
            'baseuri': '10.245.39.251',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'resource_uri': '/redfish/v1/testuri',
        }):
            with patch.object(module.XCCRedfishUtils, 'get_request') as mock_get_request:
                mock_get_request.return_value = {'ret': False, 'msg': '404 error'}

                with self.assertRaises(AnsibleFailJson) as result:
                    module.main()

    def test_module_command_GetCollectionResource_fail_when_get_not_colection(self):
        with set_module_args({
            'category': 'Raw',
            'command': 'GetCollectionResource',
            'baseuri': '10.245.39.251',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'resource_uri': '/redfish/v1/testuri',
        }):
            with patch.object(module.XCCRedfishUtils, 'get_request') as mock_get_request:
                mock_get_request.return_value = {'ret': True, 'data': {'teststr': 'xxxx'}}

                with self.assertRaises(AnsibleFailJson) as result:
                    module.main()

    def test_module_command_GetCollectionResource_pass_when_get_empty_collection(self):
        with set_module_args({
            'category': 'Raw',
            'command': 'GetCollectionResource',
            'baseuri': '10.245.39.251',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'resource_uri': '/redfish/v1/testuri',
        }):
            with patch.object(module.XCCRedfishUtils, 'get_request') as mock_get_request:
                mock_get_request.return_value = {'ret': True, 'data': {'Members': [], 'Members@odata.count': 0}}

                with self.assertRaises(AnsibleExitJson) as result:
                    module.main()

    def test_module_command_GetCollectionResource_pass_when_get_collection(self):
        with set_module_args({
            'category': 'Raw',
            'command': 'GetCollectionResource',
            'baseuri': '10.245.39.251',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'resource_uri': '/redfish/v1/testuri',
        }):
            with patch.object(module.XCCRedfishUtils, 'get_request') as mock_get_request:
                mock_get_request.return_value = {'ret': True, 'data': {'Members': [{'@odata.id': '/redfish/v1/testuri/1'}], 'Members@odata.count': 1}}

                with self.assertRaises(AnsibleExitJson) as result:
                    module.main()

    def test_module_command_PatchResource_fail_when_required_args_missing(self):
        with set_module_args({
            'category': 'Raw',
            'command': 'PatchResource',
            'baseuri': '10.245.39.251',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
        }):
            with patch.object(module.XCCRedfishUtils, 'get_request') as mock_get_request:
                mock_get_request.return_value = {'ret': True, 'data': {'teststr': 'xxxx', '@odata.etag': '27f6eb13fa1c28a2711'}}

                with patch.object(module.XCCRedfishUtils, 'patch_request') as mock_patch_request:
                    mock_patch_request.return_value = {'ret': True, 'data': {'teststr': 'xxxx'}}

                    with self.assertRaises(AnsibleFailJson) as result:
                        module.main()

    def test_module_command_PatchResource_fail_when_required_args_missing_no_requestbody(self):
        with set_module_args({
            'category': 'Raw',
            'command': 'PatchResource',
            'baseuri': '10.245.39.251',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'resource_uri': '/redfish/v1/testuri',
        }):
            with patch.object(module.XCCRedfishUtils, 'get_request') as mock_get_request:
                mock_get_request.return_value = {'ret': True, 'data': {'teststr': 'xxxx', '@odata.etag': '27f6eb13fa1c28a2711'}}

                with patch.object(module.XCCRedfishUtils, 'patch_request') as mock_patch_request:
                    mock_patch_request.return_value = {'ret': True, 'data': {'teststr': 'xxxx'}}

                    with self.assertRaises(AnsibleFailJson) as result:
                        module.main()

    def test_module_command_PatchResource_fail_when_noexisting_property_in_requestbody(self):
        with set_module_args({
            'category': 'Raw',
            'command': 'PatchResource',
            'baseuri': '10.245.39.251',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'resource_uri': '/redfish/v1/testuri',
            'request_body': {'teststr': 'yyyy', 'otherkey': 'unknownkey'}
        }):
            with patch.object(module.XCCRedfishUtils, 'get_request') as mock_get_request:
                mock_get_request.return_value = {'ret': True, 'data': {'teststr': 'xxxx', '@odata.etag': '27f6eb13fa1c28a2711'}}

                with patch.object(module.XCCRedfishUtils, 'patch_request') as mock_patch_request:
                    mock_patch_request.return_value = {'ret': True, 'data': {'teststr': 'xxxx'}}

                    with self.assertRaises(AnsibleFailJson) as result:
                        module.main()

    def test_module_command_PatchResource_fail_when_get_return_false(self):
        with set_module_args({
            'category': 'Raw',
            'command': 'PatchResource',
            'baseuri': '10.245.39.251',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'resource_uri': '/redfish/v1/testuri',
            'request_body': {'teststr': 'yyyy'}
        }):
            with patch.object(module.XCCRedfishUtils, 'get_request') as mock_get_request:
                mock_get_request.return_value = {'ret': True, 'data': {'teststr': 'xxxx', '@odata.etag': '27f6eb13fa1c28a2711'}}

                with patch.object(module.XCCRedfishUtils, 'patch_request') as mock_patch_request:
                    mock_patch_request.return_value = {'ret': False, 'msg': '500 internal error'}

                    with self.assertRaises(AnsibleFailJson) as result:
                        module.main()

    def test_module_command_PatchResource_pass(self):
        with set_module_args({
            'category': 'Raw',
            'command': 'PatchResource',
            'baseuri': '10.245.39.251',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'resource_uri': '/redfish/v1/testuri',
            'request_body': {'teststr': 'yyyy'}
        }):
            with patch.object(module.XCCRedfishUtils, 'get_request') as mock_get_request:
                mock_get_request.return_value = {'ret': True, 'data': {'teststr': 'xxxx', '@odata.etag': '27f6eb13fa1c28a2711'}}

                with patch.object(module.XCCRedfishUtils, 'patch_request') as mock_patch_request:
                    mock_patch_request.return_value = {'ret': True, 'data': {'teststr': 'yyyy', '@odata.etag': '322e0d45d9572723c98'}}

                    with self.assertRaises(AnsibleExitJson) as result:
                        module.main()

    def test_module_command_PostResource_fail_when_required_args_missing(self):
        with set_module_args({
            'category': 'Raw',
            'command': 'PostResource',
            'baseuri': '10.245.39.251',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
        }):
            with patch.object(module.XCCRedfishUtils, 'get_request') as mock_get_request:
                mock_get_request.return_value = {
                    'ret': True,
                    'data': {
                        'Actions': {
                            '#Bios.ChangePassword': {
                                '@Redfish.ActionInfo': "/redfish/v1/Systems/1/Bios/ChangePasswordActionInfo",
                                'target': "/redfish/v1/Systems/1/Bios/Actions/Bios.ChangePassword",
                                'title': "ChangePassword",
                                'PasswordName@Redfish.AllowableValues': [
                                    "UefiAdminPassword",
                                    "UefiPowerOnPassword"
                                ]
                            },
                            '#Bios.ResetBios': {
                                'title': "ResetBios",
                                'target': "/redfish/v1/Systems/1/Bios/Actions/Bios.ResetBios"
                            }
                        },
                    }
                }

                with patch.object(module.XCCRedfishUtils, 'post_request') as mock_post_request:
                    mock_post_request.return_value = {'ret': True}

                    with self.assertRaises(AnsibleFailJson) as result:
                        module.main()

    def test_module_command_PostResource_fail_when_invalid_resourceuri(self):
        with set_module_args({
            'category': 'Raw',
            'command': 'PostResource',
            'baseuri': '10.245.39.251',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'resource_uri': '/redfish/v1/testuri',
        }):
            with patch.object(module.XCCRedfishUtils, 'get_request') as mock_get_request:
                mock_get_request.return_value = {
                    'ret': True,
                    'data': {
                        'Actions': {
                            '#Bios.ChangePassword': {
                                '@Redfish.ActionInfo': "/redfish/v1/Systems/1/Bios/ChangePasswordActionInfo",
                                'target': "/redfish/v1/Systems/1/Bios/Actions/Bios.ChangePassword",
                                'title': "ChangePassword",
                                'PasswordName@Redfish.AllowableValues': [
                                    "UefiAdminPassword",
                                    "UefiPowerOnPassword"
                                ]
                            },
                            '#Bios.ResetBios': {
                                'title': "ResetBios",
                                'target': "/redfish/v1/Systems/1/Bios/Actions/Bios.ResetBios"
                            }
                        },
                    }
                }

                with patch.object(module.XCCRedfishUtils, 'post_request') as mock_post_request:
                    mock_post_request.return_value = {'ret': True}

                    with self.assertRaises(AnsibleFailJson) as result:
                        module.main()

    def test_module_command_PostResource_fail_when_no_requestbody(self):
        with set_module_args({
            'category': 'Raw',
            'command': 'PostResource',
            'baseuri': '10.245.39.251',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'resource_uri': '/redfish/v1/Systems/1/Bios/Actions/Bios.ChangePassword',
        }):
            with patch.object(module.XCCRedfishUtils, 'get_request') as mock_get_request:
                mock_get_request.return_value = {
                    'ret': True,
                    'data': {
                        'Actions': {
                            '#Bios.ChangePassword': {
                                '@Redfish.ActionInfo': "/redfish/v1/Systems/1/Bios/ChangePasswordActionInfo",
                                'target': "/redfish/v1/Systems/1/Bios/Actions/Bios.ChangePassword",
                                'title': "ChangePassword",
                                'PasswordName@Redfish.AllowableValues': [
                                    "UefiAdminPassword",
                                    "UefiPowerOnPassword"
                                ]
                            },
                            '#Bios.ResetBios': {
                                'title': "ResetBios",
                                'target': "/redfish/v1/Systems/1/Bios/Actions/Bios.ResetBios"
                            }
                        },
                    }
                }

                with patch.object(module.XCCRedfishUtils, 'post_request') as mock_post_request:
                    mock_post_request.return_value = {'ret': True}

                    with self.assertRaises(AnsibleFailJson) as result:
                        module.main()

    def test_module_command_PostResource_fail_when_no_requestbody(self):
        with set_module_args({
            'category': 'Raw',
            'command': 'PostResource',
            'baseuri': '10.245.39.251',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'resource_uri': '/redfish/v1/Systems/1/Bios/Actions/Bios.ChangePassword',
        }):
            with patch.object(module.XCCRedfishUtils, 'get_request') as mock_get_request:
                mock_get_request.return_value = {
                    'ret': True,
                    'data': {
                        'Actions': {
                            '#Bios.ChangePassword': {
                                '@Redfish.ActionInfo': "/redfish/v1/Systems/1/Bios/ChangePasswordActionInfo",
                                'target': "/redfish/v1/Systems/1/Bios/Actions/Bios.ChangePassword",
                                'title': "ChangePassword",
                                'PasswordName@Redfish.AllowableValues': [
                                    "UefiAdminPassword",
                                    "UefiPowerOnPassword"
                                ]
                            },
                            '#Bios.ResetBios': {
                                'title': "ResetBios",
                                'target': "/redfish/v1/Systems/1/Bios/Actions/Bios.ResetBios"
                            }
                        },
                    }
                }

                with patch.object(module.XCCRedfishUtils, 'post_request') as mock_post_request:
                    mock_post_request.return_value = {'ret': True}

                    with self.assertRaises(AnsibleFailJson) as result:
                        module.main()

    def test_module_command_PostResource_fail_when_requestbody_mismatch_with_data_from_actioninfo_uri(self):
        with set_module_args({
            'category': 'Raw',
            'command': 'PostResource',
            'baseuri': '10.245.39.251',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'resource_uri': '/redfish/v1/Systems/1/Bios/Actions/Bios.ChangePassword',
            'request_body': {'PasswordName': 'UefiAdminPassword', 'NewPassword': 'PASSW0RD=='}
        }):
            with patch.object(module.XCCRedfishUtils, 'get_request') as mock_get_request:
                mock_get_request.return_value = {
                    'ret': True,
                    'data': {
                        'Parameters': [],
                        'Actions': {
                            '#Bios.ChangePassword': {
                                '@Redfish.ActionInfo': "/redfish/v1/Systems/1/Bios/ChangePasswordActionInfo",
                                'target': "/redfish/v1/Systems/1/Bios/Actions/Bios.ChangePassword",
                                'title': "ChangePassword",
                                'PasswordName@Redfish.AllowableValues': [
                                    "UefiAdminPassword",
                                    "UefiPowerOnPassword"
                                ]
                            },
                            '#Bios.ResetBios': {
                                'title': "ResetBios",
                                'target': "/redfish/v1/Systems/1/Bios/Actions/Bios.ResetBios"
                            }
                        },
                    }
                }

                with patch.object(module.XCCRedfishUtils, 'post_request') as mock_post_request:
                    mock_post_request.return_value = {'ret': True}

                    with self.assertRaises(AnsibleFailJson) as result:
                        module.main()

    def test_module_command_PostResource_fail_when_get_return_false(self):
        with set_module_args({
            'category': 'Raw',
            'command': 'PostResource',
            'baseuri': '10.245.39.251',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'resource_uri': '/redfish/v1/Systems/1/Bios/Actions/Bios.ChangePassword',
            'request_body': {'PasswordName': 'UefiAdminPassword', 'NewPassword': 'PASSW0RD=='}
        }):
            with patch.object(module.XCCRedfishUtils, 'get_request') as mock_get_request:
                mock_get_request.return_value = {'ret': False, 'msg': '404 error'}

                with patch.object(module.XCCRedfishUtils, 'post_request') as mock_post_request:
                    mock_post_request.return_value = {'ret': True}

                    with self.assertRaises(AnsibleFailJson) as result:
                        module.main()

    def test_module_command_PostResource_fail_when_post_return_false(self):
        with set_module_args({
            'category': 'Raw',
            'command': 'PostResource',
            'baseuri': '10.245.39.251',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'resource_uri': '/redfish/v1/Systems/1/Bios/Actions/Bios.ResetBios',
            'request_body': {}
        }):
            with patch.object(module.XCCRedfishUtils, 'get_request') as mock_get_request:
                mock_get_request.return_value = {
                    'ret': True,
                    'data': {
                        'Actions': {
                            '#Bios.ChangePassword': {
                                '@Redfish.ActionInfo': "/redfish/v1/Systems/1/Bios/ChangePasswordActionInfo",
                                'target': "/redfish/v1/Systems/1/Bios/Actions/Bios.ChangePassword",
                                'title': "ChangePassword",
                                'PasswordName@Redfish.AllowableValues': [
                                    "UefiAdminPassword",
                                    "UefiPowerOnPassword"
                                ]
                            },
                            '#Bios.ResetBios': {
                                'title': "ResetBios",
                                'target': "/redfish/v1/Systems/1/Bios/Actions/Bios.ResetBios"
                            }
                        },
                    }
                }

                with patch.object(module.XCCRedfishUtils, 'post_request') as mock_post_request:
                    mock_post_request.return_value = {'ret': False, 'msg': '500 internal error'}

                    with self.assertRaises(AnsibleFailJson) as result:
                        module.main()

    def test_module_command_PostResource_pass(self):
        with set_module_args({
            'category': 'Raw',
            'command': 'PostResource',
            'baseuri': '10.245.39.251',
            'username': 'USERID',
            'password': 'PASSW0RD=21',
            'resource_uri': '/redfish/v1/Systems/1/Bios/Actions/Bios.ResetBios',
            'request_body': {}
        }):
            with patch.object(module.XCCRedfishUtils, 'get_request') as mock_get_request:
                mock_get_request.return_value = {
                    'ret': True,
                    'data': {
                        'Actions': {
                            '#Bios.ChangePassword': {
                                '@Redfish.ActionInfo': "/redfish/v1/Systems/1/Bios/ChangePasswordActionInfo",
                                'target': "/redfish/v1/Systems/1/Bios/Actions/Bios.ChangePassword",
                                'title': "ChangePassword",
                                'PasswordName@Redfish.AllowableValues': [
                                    "UefiAdminPassword",
                                    "UefiPowerOnPassword"
                                ]
                            },
                            '#Bios.ResetBios': {
                                'title': "ResetBios",
                                'target': "/redfish/v1/Systems/1/Bios/Actions/Bios.ResetBios"
                            }
                        },
                    }
                }

                with patch.object(module.XCCRedfishUtils, 'post_request') as mock_post_request:
                    mock_post_request.return_value = {'ret': True, 'msg': 'post success'}

                    with self.assertRaises(AnsibleExitJson) as result:
                        module.main()
