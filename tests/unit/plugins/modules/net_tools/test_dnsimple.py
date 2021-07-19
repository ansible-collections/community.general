# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.community.general.plugins.modules.net_tools import dnsimple as dnsimple_module
from ansible_collections.community.general.tests.unit.plugins.modules.utils import AnsibleFailJson, ModuleTestCase, set_module_args
from unittest import mock
from dnsimple import DNSimpleException


class TestDNSimple(ModuleTestCase):
    """Main class for testing dnsimple module."""

    def setUp(self):
        """Setup."""
        super(TestDNSimple, self).setUp()
        self.module = dnsimple_module

    def tearDown(self):
        """Teardown."""
        super(TestDNSimple, self).tearDown()

    def test_without_required_parameters(self):
        """Failure must occurs when all parameters are missing"""
        with self.assertRaises(AnsibleFailJson):
            set_module_args({})
            self.module.main()

    @mock.patch('dnsimple.service.Identity.whoami')
    def test_account_token(self, mock_whoami):
        mock_whoami.return_value.data.account = 42
        ds = self.module.DNSimpleV2('fake', 'fake', True, self.module)
        self.assertEquals(ds.account, 42)

    @mock.patch('dnsimple.service.Accounts.list_accounts')
    @mock.patch('dnsimple.service.Identity.whoami')
    def test_user_token_multiple_accounts(self, mock_whoami, mock_accounts):
        mock_accounts.return_value.data = [1, 2, 3]
        mock_whoami.return_value.data.account = None
        with self.assertRaises(DNSimpleException):
            self.module.DNSimpleV2('fake', 'fake', True, self.module)

    @mock.patch('dnsimple.service.Accounts.list_accounts')
    @mock.patch('dnsimple.service.Identity.whoami')
    def test_user_token_single_account(self, mock_whoami, mock_accounts):
        mock_accounts.return_value.data = [42]
        mock_whoami.return_value.data.account = None
        ds = self.module.DNSimpleV2('fake', 'fake', True, self.module)
        self.assertEquals(ds.account, 42)
