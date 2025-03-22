# -*- coding: utf-8 -*-
# Copyright (c) 2021 Florian Dambrine <android.florian@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

import sys

from ansible.module_utils.common.dict_transformations import dict_merge
from ansible.module_utils.six import iteritems
from ansible_collections.community.general.plugins.modules import (
    pritunl_org,
)
from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import patch
from ansible_collections.community.general.tests.unit.plugins.module_utils.net_tools.pritunl.test_api import (
    PritunlDeleteOrganizationMock,
    PritunlListOrganizationMock,
    PritunlListOrganizationAfterPostMock,
    PritunlPostOrganizationMock,
)
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    ModuleTestCase,
    set_module_args,
)

__metaclass__ = type


class TestPritunlOrg(ModuleTestCase):
    def setUp(self):
        super(TestPritunlOrg, self).setUp()
        self.module = pritunl_org

        # Add backward compatibility
        if sys.version_info < (3, 2):
            self.assertRegex = self.assertRegexpMatches

    def tearDown(self):
        super(TestPritunlOrg, self).tearDown()

    def patch_add_pritunl_organization(self, **kwds):
        return patch(
            "ansible_collections.community.general.plugins.module_utils.net_tools.pritunl.api._post_pritunl_organization",
            autospec=True,
            **kwds
        )

    def patch_delete_pritunl_organization(self, **kwds):
        return patch(
            "ansible_collections.community.general.plugins.module_utils.net_tools.pritunl.api._delete_pritunl_organization",
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
        with set_module_args({}):
            with self.assertRaises(AnsibleFailJson):
                self.module.main()

    def test_present(self):
        """Test Pritunl organization creation."""
        org_params = {"name": "NewOrg"}
        with set_module_args(
            dict_merge(
                {
                    "pritunl_api_token": "token",
                    "pritunl_api_secret": "secret",
                    "pritunl_url": "https://pritunl.domain.com",
                },
                org_params,
            )
        ):
            # Test creation
            with self.patch_get_pritunl_organizations(
                side_effect=PritunlListOrganizationMock
            ) as mock_get:
                with self.patch_add_pritunl_organization(
                    side_effect=PritunlPostOrganizationMock
                ) as mock_add:
                    with self.assertRaises(AnsibleExitJson) as create_result:
                        self.module.main()

            create_exc = create_result.exception.args[0]

            self.assertTrue(create_exc["changed"])
            self.assertEqual(create_exc["response"]["name"], org_params["name"])
            self.assertEqual(create_exc["response"]["user_count"], 0)

            # Test module idempotency
            with self.patch_get_pritunl_organizations(
                side_effect=PritunlListOrganizationAfterPostMock
            ) as mock_get:
                with self.patch_add_pritunl_organization(
                    side_effect=PritunlPostOrganizationMock
                ) as mock_add:
                    with self.assertRaises(AnsibleExitJson) as idempotent_result:
                        self.module.main()

        idempotent_exc = idempotent_result.exception.args[0]

        # Ensure both calls resulted in the same returned value
        # except for changed which should be false the second time
        for k, v in iteritems(idempotent_exc):
            if k == "changed":
                self.assertFalse(idempotent_exc[k])
            else:
                self.assertEqual(create_exc[k], idempotent_exc[k])

    def test_absent(self):
        """Test organization removal from Pritunl."""
        org_params = {"name": "NewOrg"}
        with set_module_args(
            dict_merge(
                {
                    "state": "absent",
                    "pritunl_api_token": "token",
                    "pritunl_api_secret": "secret",
                    "pritunl_url": "https://pritunl.domain.com",
                },
                org_params,
            )
        ):
            # Test deletion
            with self.patch_get_pritunl_organizations(
                side_effect=PritunlListOrganizationAfterPostMock
            ) as mock_get:
                with self.patch_delete_pritunl_organization(
                    side_effect=PritunlDeleteOrganizationMock
                ) as mock_delete:
                    with self.assertRaises(AnsibleExitJson) as delete_result:
                        self.module.main()

            delete_exc = delete_result.exception.args[0]

            self.assertTrue(delete_exc["changed"])
            self.assertEqual(delete_exc["response"], {})

            # Test module idempotency
            with self.patch_get_pritunl_organizations(
                side_effect=PritunlListOrganizationMock
            ) as mock_get:
                with self.patch_delete_pritunl_organization(
                    side_effect=PritunlDeleteOrganizationMock
                ) as mock_add:
                    with self.assertRaises(AnsibleExitJson) as idempotent_result:
                        self.module.main()

        idempotent_exc = idempotent_result.exception.args[0]

        # Ensure both calls resulted in the same returned value
        # except for changed which should be false the second time
        self.assertFalse(idempotent_exc["changed"])
        self.assertEqual(idempotent_exc["response"], delete_exc["response"])

    def test_absent_with_existing_users(self):
        """Test organization removal with attached users should fail except if force is true."""
        module_args = {
            "state": "absent",
            "pritunl_api_token": "token",
            "pritunl_api_secret": "secret",
            "pritunl_url": "https://pritunl.domain.com",
            "name": "GumGum",
        }
        with set_module_args(module_args):
            # Test deletion
            with self.patch_get_pritunl_organizations(
                side_effect=PritunlListOrganizationMock
            ) as mock_get:
                with self.patch_delete_pritunl_organization(
                    side_effect=PritunlDeleteOrganizationMock
                ) as mock_delete:
                    with self.assertRaises(AnsibleFailJson) as failure_result:
                        self.module.main()

            failure_exc = failure_result.exception.args[0]

            self.assertRegex(failure_exc["msg"], "Can not remove organization")

            # Switch force=True which should run successfully
            with set_module_args(dict_merge(module_args, {"force": True})):
                with self.patch_get_pritunl_organizations(
                    side_effect=PritunlListOrganizationMock
                ) as mock_get:
                    with self.patch_delete_pritunl_organization(
                        side_effect=PritunlDeleteOrganizationMock
                    ) as mock_delete:
                        with self.assertRaises(AnsibleExitJson) as delete_result:
                            self.module.main()

        delete_exc = delete_result.exception.args[0]

        self.assertTrue(delete_exc["changed"])
