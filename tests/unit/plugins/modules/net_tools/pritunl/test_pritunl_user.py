# -*- coding: utf-8 -*-
# (c) 2021 Florian Dambrine <android.florian@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

import sys

from ansible.module_utils.common.dict_transformations import dict_merge
from ansible.module_utils.six import iteritems
from ansible_collections.community.general.plugins.modules.net_tools.pritunl import (
    pritunl_user,
)
from ansible_collections.community.general.tests.unit.compat.mock import patch
from ansible_collections.community.general.tests.unit.plugins.module_utils.net_tools.pritunl.test_api import (
    PritunlDeleteUserMock,
    PritunlListOrganizationMock,
    PritunlListUserMock,
    PritunlPostUserMock,
    PritunlPutUserMock,
)
from ansible_collections.community.general.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    ModuleTestCase,
    set_module_args,
)

__metaclass__ = type


def mock_pritunl_api(func, **kwargs):
    def wrapped(self=None):
        with self.patch_get_pritunl_organizations(
            side_effect=PritunlListOrganizationMock
        ):
            with self.patch_get_pritunl_users(side_effect=PritunlListUserMock):
                with self.patch_add_pritunl_users(side_effect=PritunlPostUserMock):
                    with self.patch_delete_pritunl_users(
                        side_effect=PritunlDeleteUserMock
                    ):
                        func(self, **kwargs)

    return wrapped


class TestPritunlUser(ModuleTestCase):
    def setUp(self):
        super(TestPritunlUser, self).setUp()
        self.module = pritunl_user

        # Add backward compatibility
        if sys.version_info < (3, 2):
            self.assertRegex = self.assertRegexpMatches

    def tearDown(self):
        super(TestPritunlUser, self).tearDown()

    def patch_get_pritunl_users(self, **kwds):
        return patch(
            "ansible_collections.community.general.plugins.module_utils.net_tools.pritunl.api._get_pritunl_users",
            autospec=True,
            **kwds
        )

    def patch_add_pritunl_users(self, **kwds):
        return patch(
            "ansible_collections.community.general.plugins.module_utils.net_tools.pritunl.api._post_pritunl_user",
            autospec=True,
            **kwds
        )

    def patch_update_pritunl_users(self, **kwds):
        return patch(
            "ansible_collections.community.general.plugins.module_utils.net_tools.pritunl.api._put_pritunl_user",
            autospec=True,
            **kwds
        )

    def patch_delete_pritunl_users(self, **kwds):
        return patch(
            "ansible_collections.community.general.plugins.module_utils.net_tools.pritunl.api._delete_pritunl_user",
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
        set_module_args({})
        with self.assertRaises(AnsibleFailJson):
            self.module.main()

    @mock_pritunl_api
    def test_present(self):
        """Test Pritunl user creation and update."""
        user_params = {
            "user_name": "alice",
            "user_email": "alice@company.com",
        }
        set_module_args(
            dict_merge(
                {
                    "pritunl_api_token": "token",
                    "pritunl_api_secret": "secret",
                    "pritunl_url": "https://pritunl.domain.com",
                    "organization": "GumGum",
                },
                user_params,
            )
        )

        with self.patch_update_pritunl_users(
            side_effect=PritunlPostUserMock
        ) as post_mock:
            with self.assertRaises(AnsibleExitJson) as create_result:
                self.module.main()

        create_exc = create_result.exception.args[0]

        self.assertTrue(create_exc["changed"])
        self.assertEqual(create_exc["response"]["name"], user_params["user_name"])
        self.assertEqual(create_exc["response"]["email"], user_params["user_email"])
        self.assertFalse(create_exc["response"]["disabled"])

        # Changing user from alice to bob should update certain fields only

        new_user_params = {
            "user_name": "bob",
            "user_email": "bob@company.com",
            "user_disabled": True,
        }
        set_module_args(
            dict_merge(
                {
                    "pritunl_api_token": "token",
                    "pritunl_api_secret": "secret",
                    "pritunl_url": "https://pritunl.domain.com",
                    "organization": "GumGum",
                },
                new_user_params,
            )
        )

        with self.patch_update_pritunl_users(
            side_effect=PritunlPutUserMock
        ) as put_mock:

            with self.assertRaises(AnsibleExitJson) as update_result:
                self.module.main()

        update_exc = update_result.exception.args[0]

        # Ensure only certain settings changed and the rest remained untouched.
        for k, v in iteritems(update_exc):
            if k in new_user_params:
                assert update_exc[k] == v
            else:
                assert update_exc[k] == create_exc[k]

    @mock_pritunl_api
    def test_absent(self):
        """Test user removal from Pritunl."""
        set_module_args(
            {
                "state": "absent",
                "pritunl_api_token": "token",
                "pritunl_api_secret": "secret",
                "pritunl_url": "https://pritunl.domain.com",
                "organization": "GumGum",
                "user_name": "florian",
            }
        )

        with self.assertRaises(AnsibleExitJson) as result:
            self.module.main()

        exc = result.exception.args[0]

        self.assertTrue(exc["changed"])
        self.assertEqual(exc["response"], {})

    @mock_pritunl_api
    def test_absent_failure(self):
        """Test user removal from a non existing organization."""
        set_module_args(
            {
                "state": "absent",
                "pritunl_api_token": "token",
                "pritunl_api_secret": "secret",
                "pritunl_url": "https://pritunl.domain.com",
                "organization": "Unknown",
                "user_name": "floria@company.com",
            }
        )

        with self.assertRaises(AnsibleFailJson) as result:
            self.module.main()

        exc = result.exception.args[0]

        self.assertRegex(exc["msg"], "Can not remove user")
