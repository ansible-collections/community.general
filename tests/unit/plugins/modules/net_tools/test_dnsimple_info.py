# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.community.general.plugins.modules.net_tools import dnsimple_info
from ansible_collections.community.general.tests.unit.plugins.modules.utils import AnsibleFailJson, ModuleTestCase, set_module_args, AnsibleExitJson
from httmock import response
from httmock import with_httmock
from httmock import urlmatch
import pytest


dnsimple = pytest.importorskip('dnsimple_info')


@urlmatch(netloc='(.)*dnsimple.com(.)*',
          path='/v2/[0-9]*/zones/')
def zones_resp(url, request):
    """return domains"""
    headers = {'content-type': 'application/json'}
    data_content = {"data":
                    [{"account_id": "1234", }, ],
                    "pagination": {"total_pages": 1}}
    content = data_content
    return response(200, content, headers, None, 5, request)


@urlmatch(netloc='(.)*dnsimple.com(.)*',
          path='/v2/[0-9]*/zones/(.)*/records(.*)')
def records_resp(url, request):
    """return record(s)"""
    headers = {'content-type': 'application/json'}
    data_content = {"data":
                    [{"content": "example",
                      "name": "example.com"}],
                    "pagination": {"total_pages": 1}}
    content = data_content
    return response(200, content, headers, None, 5, request)


class TestDNSimple_Info(ModuleTestCase):
    """Main class for testing dnsimple module."""

    def setUp(self):

        """Setup."""
        super(TestDNSimple_Info, self).setUp()
        self.module = dnsimple_info

    def tearDown(self):
        """Teardown."""
        super(TestDNSimple_Info, self).tearDown()

    def test_with_no_parameters(self):
        """Failure must occurs when all parameters are missing"""
        with self.assertRaises(AnsibleFailJson):
            set_module_args({})
            self.module.main()

    @with_httmock(zones_resp)
    def test_only_key_and_account(self):
        """key and account will pass, returns domains"""
        account_id = "1234"
        with self.assertRaises(AnsibleExitJson) as exc_info:
            set_module_args({
                "api_key": "abcd1324",
                "account_id": account_id
            })
            self.module.main()
        result = exc_info.exception.args[0]
        # nothing should change
        self.assertFalse(result['changed'])
        # we should return at least one item with the matching account ID
        assert result['dnsimple_domain_info'][0]["account_id"] == account_id

    @with_httmock(records_resp)
    def test_only_name_without_record(self):
        """name and no record should not fail, returns the record"""
        name = "example.com"
        with self.assertRaises(AnsibleExitJson) as exc_info:
            set_module_args({
                "api_key": "abcd1324",
                "name": "example.com",
                "account_id": "1234"
            })
            self.module.main()
        result = exc_info.exception.args[0]
        # nothing should change
        self.assertFalse(result['changed'])
        # we should return at least one item with mathing domain
        assert result['dnsimple_records_info'][0]['name'] == name

    @with_httmock(records_resp)
    def test_name_and_record(self):
        """name and record should not fail, returns the record"""
        record = "example"
        with self.assertRaises(AnsibleExitJson) as exc_info:
            set_module_args({
                "api_key": "abcd1324",
                "account_id": "1234",
                "name": "example.com",
                "record": "example"
            })
            self.module.main()
        result = exc_info.exception.args[0]
        # nothing should change
        self.assertFalse(result['changed'])
        # we should return at least one item and content should match
        assert result['dnsimple_record_info'][0]['content'] == record
