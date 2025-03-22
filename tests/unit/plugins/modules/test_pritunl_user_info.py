# -*- coding: utf-8 -*-
# Copyright (c) 2021, Florian Dambrine <android.florian@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

import sys

from ansible_collections.community.general.plugins.modules import (
    pritunl_user_info,
)
from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import patch
from ansible_collections.community.general.tests.unit.plugins.module_utils.net_tools.pritunl.test_api import (
    PritunlListOrganizationMock,
    PritunlListUserMock,
)
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    ModuleTestCase,
    set_module_args,
)

__metaclass__ = type


class TestPritunlUserInfo(ModuleTestCase):
    def setUp(self):
        super(TestPritunlUserInfo, self).setUp()
        self.module = pritunl_user_info

        # Add backward compatibility
        if sys.version_info < (3, 2):
            self.assertRegex = self.assertRegexpMatches

    def tearDown(self):
        super(TestPritunlUserInfo, self).tearDown()

    def patch_get_pritunl_users(self, **kwds):
        return patch(
            "ansible_collections.community.general.plugins.module_utils.net_tools.pritunl.api._get_pritunl_users",
            autospec=True,
            **kwds
        )

    def patch_get_pritunl_organizations(self, **kwds):
        return patch(
            "ansible_collections.community.general.plugins.module_utils.net_tools.pritunl.api._get_pritunl_organizations",
            autospec=True,
            **kwds
        )

    def test_without_parameters(self):
        """Test without parameters"""
        with self.patch_get_pritunl_organizations(
            side_effect=PritunlListOrganizationMock
        ) as org_mock:
            with self.patch_get_pritunl_users(
                side_effect=PritunlListUserMock
            ) as user_mock:
                with set_module_args({}):
                    with self.assertRaises(AnsibleFailJson):
                        self.module.main()

                self.assertEqual(org_mock.call_count, 0)
                self.assertEqual(user_mock.call_count, 0)

    def test_missing_organization(self):
        """Failure must occur when the requested organization is not found."""
        with self.patch_get_pritunl_organizations(
            side_effect=PritunlListOrganizationMock
        ) as org_mock:
            with self.patch_get_pritunl_users(
                side_effect=PritunlListUserMock
            ) as user_mock:
                with self.assertRaises(AnsibleFailJson) as result:
                    with set_module_args(
                        {
                            "pritunl_api_token": "token",
                            "pritunl_api_secret": "secret",
                            "pritunl_url": "https://pritunl.domain.com",
                            "organization": "Unknown",
                        }
                    ):
                        self.module.main()

                self.assertEqual(org_mock.call_count, 1)
                self.assertEqual(user_mock.call_count, 0)

                exc = result.exception.args[0]
                self.assertRegex(exc["msg"], "Can not list users from the organization")

    def test_get_all_client_users_from_organization(self):
        """
        The list of all Pritunl client users from the organization must be returned when no user specified.
        """
        expected_user_type = "client"
        with self.patch_get_pritunl_organizations(
            side_effect=PritunlListOrganizationMock
        ) as org_mock:
            with self.patch_get_pritunl_users(
                side_effect=PritunlListUserMock
            ) as user_mock:
                with self.assertRaises(AnsibleExitJson) as result:
                    with set_module_args(
                        {
                            "pritunl_api_token": "token",
                            "pritunl_api_secret": "secret",
                            "pritunl_url": "https://pritunl.domain.com",
                            "organization": "GumGum",
                        }
                    ):
                        self.module.main()

                self.assertEqual(org_mock.call_count, 1)
                self.assertEqual(user_mock.call_count, 1)

                exc = result.exception.args[0]
                # module should not report changes
                self.assertFalse(exc["changed"])
                # user_type when not provided is set client and should only return client user type
                self.assertEqual(len(exc["users"]), 1)
                for user in exc["users"]:
                    self.assertEqual(user["type"], expected_user_type)

    def test_get_specific_server_user_from_organization(self):
        """
        Retrieving a specific user from the organization must return a single record.
        """
        expected_user_type = "server"
        expected_user_name = "ops"
        with self.patch_get_pritunl_organizations(
            side_effect=PritunlListOrganizationMock
        ) as org_mock:
            with self.patch_get_pritunl_users(
                side_effect=PritunlListUserMock
            ) as user_mock:
                with self.assertRaises(AnsibleExitJson) as result:
                    with set_module_args(
                        {
                            "pritunl_api_token": "token",
                            "pritunl_api_secret": "secret",
                            "pritunl_url": "https://pritunl.domain.com",
                            "organization": "GumGum",
                            "user_name": expected_user_name,
                            "user_type": expected_user_type,
                        }
                    ):
                        self.module.main()

                self.assertEqual(org_mock.call_count, 1)
                self.assertEqual(user_mock.call_count, 1)

                exc = result.exception.args[0]
                # module should not report changes
                self.assertFalse(exc["changed"])
                self.assertEqual(len(exc["users"]), 1)
                for user in exc["users"]:
                    self.assertEqual(user["type"], expected_user_type)
                    self.assertEqual(user["name"], expected_user_name)
