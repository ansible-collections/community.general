# -*- coding: utf-8 -*-
# Copyright (c) 2021, Florian Dambrine <android.florian@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

import sys

from ansible_collections.community.general.plugins.modules import (
    pritunl_org_info,
)
from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import patch
from ansible_collections.community.general.tests.unit.plugins.module_utils.net_tools.pritunl.test_api import (
    PritunlListOrganizationMock,
    PritunlEmptyOrganizationMock,
)
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    ModuleTestCase,
    set_module_args,
)

__metaclass__ = type


class TestPritunlOrgInfo(ModuleTestCase):
    def setUp(self):
        super(TestPritunlOrgInfo, self).setUp()
        self.module = pritunl_org_info

        # Add backward compatibility
        if sys.version_info < (3, 2):
            self.assertRegex = self.assertRegexpMatches

    def tearDown(self):
        super(TestPritunlOrgInfo, self).tearDown()

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
            with set_module_args({}):
                with self.assertRaises(AnsibleFailJson):
                    self.module.main()

            self.assertEqual(org_mock.call_count, 0)

    def test_list_empty_organizations(self):
        """Listing all organizations even when no org exists should be valid."""
        with self.patch_get_pritunl_organizations(
            side_effect=PritunlEmptyOrganizationMock
        ) as org_mock:
            with self.assertRaises(AnsibleExitJson) as result:
                with set_module_args(
                    {
                        "pritunl_api_token": "token",
                        "pritunl_api_secret": "secret",
                        "pritunl_url": "https://pritunl.domain.com",
                    }
                ):
                    self.module.main()

                self.assertEqual(org_mock.call_count, 1)

                exc = result.exception.args[0]
                self.assertEqual(len(exc["organizations"]), 0)

    def test_list_specific_organization(self):
        """Listing a specific organization should be valid."""
        with self.patch_get_pritunl_organizations(
            side_effect=PritunlListOrganizationMock
        ) as org_mock:
            with self.assertRaises(AnsibleExitJson) as result:
                with set_module_args(
                    {
                        "pritunl_api_token": "token",
                        "pritunl_api_secret": "secret",
                        "pritunl_url": "https://pritunl.domain.com",
                        "org": "GumGum",
                    }
                ):
                    self.module.main()

                self.assertEqual(org_mock.call_count, 1)

                exc = result.exception.args[0]
                self.assertEqual(len(exc["organizations"]), 1)

    def test_list_unknown_organization(self):
        """Listing an unknown organization should result in a failure."""
        with self.patch_get_pritunl_organizations(
            side_effect=PritunlListOrganizationMock
        ) as org_mock:
            with self.assertRaises(AnsibleFailJson) as result:
                with set_module_args(
                    {
                        "pritunl_api_token": "token",
                        "pritunl_api_secret": "secret",
                        "pritunl_url": "https://pritunl.domain.com",
                        "org": "Unknown",
                    }
                ):
                    self.module.main()

                self.assertEqual(org_mock.call_count, 1)

                exc = result.exception.args[0]
                self.assertRegex(exc["msg"], "does not exist")

    def test_list_all_organizations(self):
        """Listing all organizations should be valid."""
        with self.patch_get_pritunl_organizations(
            side_effect=PritunlListOrganizationMock
        ) as org_mock:
            with self.assertRaises(AnsibleExitJson) as result:
                with set_module_args(
                    {
                        "pritunl_api_token": "token",
                        "pritunl_api_secret": "secret",
                        "pritunl_url": "https://pritunl.domain.com",
                    }
                ):
                    self.module.main()

                self.assertEqual(org_mock.call_count, 1)

                exc = result.exception.args[0]
                self.assertEqual(len(exc["organizations"]), 3)
