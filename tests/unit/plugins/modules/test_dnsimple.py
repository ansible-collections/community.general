# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from ansible_collections.community.general.plugins.modules import dnsimple as dnsimple_module
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleFailJson,
    ModuleTestCase,
    set_module_args,
)
from unittest.mock import patch
import pytest

dnsimple = pytest.importorskip("dnsimple")

from dnsimple import DNSimpleException


class TestDNSimple(ModuleTestCase):
    """Main class for testing dnsimple module."""

    def setUp(self):
        """Setup."""
        super().setUp()
        self.module = dnsimple_module

    def tearDown(self):
        """Teardown."""
        super().tearDown()

    def test_without_required_parameters(self):
        """Failure must occurs when all parameters are missing"""
        with self.assertRaises(AnsibleFailJson):
            with set_module_args({}):
                self.module.main()

    @patch("dnsimple.service.Identity.whoami")
    def test_account_token(self, mock_whoami):
        mock_whoami.return_value.data.account = 42
        ds = self.module.DNSimpleV2("fake", "fake", True, self.module)
        self.assertEqual(ds.account, 42)

    @patch("dnsimple.service.Accounts.list_accounts")
    @patch("dnsimple.service.Identity.whoami")
    def test_user_token_multiple_accounts(self, mock_whoami, mock_accounts):
        mock_accounts.return_value.data = [1, 2, 3]
        mock_whoami.return_value.data.account = None
        with self.assertRaises(DNSimpleException):
            self.module.DNSimpleV2("fake", "fake", True, self.module)

    @patch("dnsimple.service.Accounts.list_accounts")
    @patch("dnsimple.service.Identity.whoami")
    def test_user_token_single_account(self, mock_whoami, mock_accounts):
        mock_accounts.return_value.data = [42]
        mock_whoami.return_value.data.account = None
        ds = self.module.DNSimpleV2("fake", "fake", True, self.module)
        self.assertEqual(ds.account, 42)
