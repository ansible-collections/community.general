# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import pytest
from ansible_collections.community.general.tests.unit.compat.mock import Mock, patch
from ansible_collections.community.general.plugins.modules.monitoring import alerta_customer
from ansible_collections.community.general.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args


class MockedReponse(object):
    def __init__(self, data):
        self.data = data

    def read(self):
        return self.data


def customer_response_page1():
    server_response = json.dumps({"customers": [
        {
            "customer": "admin",
            "href": "http://localhost:8080/api/customer/d89664a7-9c87-4ab9-8be8-830e7e5f0616",
            "id": "d89664a7-9c87-4ab9-8be8-830e7e5f0616",
            "match": "admin@example.com"
        },
        {
            "customer": "Developer",
            "href": "http://localhost:8080/api/customer/188ed093-84cc-4f46-bf80-4c9127180d9c",
            "id": "188ed093-84cc-4f46-bf80-4c9127180d9c",
            "match": "dev@example.com"
        }],
        "more": True,
        "page": 1,
        "pageSize": 50,
        "pages": 1,
        "status": "ok",
        "total": 2})
    return (MockedReponse(server_response), {"status": 200})


def customer_response_page2():
    server_response = json.dumps({"customers": [
        {
            "customer": "admin",
            "href": "http://localhost:8080/api/customer/d89664a7-9c87-4ab9-8be8-830e7e5f0616",
            "id": "d89664a7-9c87-4ab9-8be8-830e7e5f0616",
            "match": "admin@example.com"
        },
        {
            "customer": "Developer",
            "href": "http://localhost:8080/api/customer/188ed093-84cc-4f46-bf80-4c9127180d9c",
            "id": "188ed093-84cc-4f46-bf80-4c9127180d9c",
            "match": "dev@example.com"
        }],
        "more": True,
        "page": 2,
        "pageSize": 50,
        "pages": 2,
        "status": "ok",
        "total": 52})
    return (MockedReponse(server_response), {"status": 200})


class TestAlertaCustomerModule(ModuleTestCase):

    def setUp(self):
        super(TestAlertaCustomerModule, self).setUp()
        self.module = alerta_customer

    def tearDown(self):
        super(TestAlertaCustomerModule, self).tearDown()

    @pytest.fixture
    def fetch_url_mock(self, mocker):
        return mocker.patch()

    def test_without_parameters(self):
        """Failure if no parameters set"""
        with self.assertRaises(AnsibleFailJson):
            set_module_args({})
            self.module.main()

    def test_without_content(self):
        """Failure if customer and match are missing"""
        set_module_args({
            'alerta_url': "http://localhost:8080",
            'api_username': "admin@example.com",
            'api_password': "password"
        })
        with self.assertRaises(AnsibleFailJson):
            self.module.main()

    def test_successful_existing_customer_creation(self):
        """Test the customer creation (already exists)."""
        set_module_args({
            'alerta_url': "http://localhost:8080",
            'api_username': "admin@example.com",
            'api_password': "password",
            'customer': 'Developer',
            'match': 'dev@example.com'
        })

        with patch.object(alerta_customer, "fetch_url") as fetch_url_mock:
            fetch_url_mock.return_value = customer_response_page1()
            with self.assertRaises(AnsibleExitJson):
                self.module.main()
            self.assertTrue(fetch_url_mock.call_count, 1)

    def test_successful_customer_creation(self):
        """Test the customer creation."""
        set_module_args({
            'alerta_url': "http://localhost:8080",
            'api_username': "admin@example.com",
            'api_password': "password",
            'customer': 'Developer',
            'match': 'dev2@example.com'
        })

        with patch.object(alerta_customer, "fetch_url") as fetch_url_mock:
            fetch_url_mock.return_value = customer_response_page1()
            with self.assertRaises(AnsibleExitJson):
                self.module.main()

            self.assertTrue(fetch_url_mock.call_count, 1)
            call_data = json.loads(fetch_url_mock.call_args[1]['data'])
            assert call_data['match'] == "dev2@example.com"
            assert call_data['customer'] == "Developer"

    def test_successful_customer_creation_key(self):
        """Test the customer creation using api_key."""
        set_module_args({
            'alerta_url': "http://localhost:8080",
            'api_key': "demo-key",
            'customer': 'Developer',
            'match': 'dev2@example.com'
        })

        with patch.object(alerta_customer, "fetch_url") as fetch_url_mock:
            fetch_url_mock.return_value = customer_response_page1()
            with self.assertRaises(AnsibleExitJson):
                self.module.main()

            self.assertTrue(fetch_url_mock.call_count, 1)
            call_data = json.loads(fetch_url_mock.call_args[1]['data'])
            assert call_data['match'] == "dev2@example.com"
            assert call_data['customer'] == "Developer"

    def test_failed_not_found(self):
        """Test failure with wrong URL."""

        set_module_args({
            'alerta_url': "http://localhost:8080/s",
            'api_username': "admin@example.com",
            'api_password': "password",
            'customer': 'Developer',
            'match': 'dev@example.com'
        })

        with patch.object(alerta_customer, "fetch_url") as fetch_url_mock:
            fetch_url_mock.return_value = (None, {"status": 404, 'msg': 'Not found for request GET on http://localhost:8080/a/api/customers'})
            with self.assertRaises(AnsibleFailJson):
                self.module.main()

    def test_failed_forbidden(self):
        """Test failure with wrong user."""

        set_module_args({
            'alerta_url': "http://localhost:8080",
            'api_username': "dev@example.com",
            'api_password': "password",
            'customer': 'Developer',
            'match': 'dev@example.com'
        })

        with patch.object(alerta_customer, "fetch_url") as fetch_url_mock:
            fetch_url_mock.return_value = (None, {"status": 403, 'msg': 'Permission Denied for GET on http://localhost:8080/api/customers'})
            with self.assertRaises(AnsibleFailJson):
                self.module.main()

    def test_failed_unauthorized(self):
        """Test failure with wrong username or password."""

        set_module_args({
            'alerta_url': "http://localhost:8080",
            'api_username': "admin@example.com",
            'api_password': "password_wrong",
            'customer': 'Developer',
            'match': 'dev@example.com'
        })

        with patch.object(alerta_customer, "fetch_url") as fetch_url_mock:
            fetch_url_mock.return_value = (None, {"status": 401, 'msg': 'Unauthorized to request GET on http://localhost:8080/api/customers'})
            with self.assertRaises(AnsibleFailJson):
                self.module.main()

    def test_successful_customer_deletion(self):
        """Test the customer deletion."""

        set_module_args({
            'alerta_url': "http://localhost:8080",
            'api_username': "admin@example.com",
            'api_password': "password",
            'customer': 'Developer',
            'match': 'dev@example.com',
            'state': 'absent'
        })

        with patch.object(alerta_customer, "fetch_url") as fetch_url_mock:
            fetch_url_mock.return_value = customer_response_page1()
            with self.assertRaises(AnsibleExitJson):
                self.module.main()

    def test_successful_customer_deletion_page2(self):
        """Test the customer deletion on the second page."""

        set_module_args({
            'alerta_url': "http://localhost:8080",
            'api_username': "admin@example.com",
            'api_password': "password",
            'customer': 'Developer',
            'match': 'dev@example.com',
            'state': 'absent'
        })

        with patch.object(alerta_customer, "fetch_url") as fetch_url_mock:
            fetch_url_mock.return_value = customer_response_page2()
            with self.assertRaises(AnsibleExitJson):
                self.module.main()

    def test_successful_nonexisting_customer_deletion(self):
        """Test the customer deletion (non existing)."""

        set_module_args({
            'alerta_url': "http://localhost:8080",
            'api_username': "admin@example.com",
            'api_password': "password",
            'customer': 'Billing',
            'match': 'dev@example.com',
            'state': 'absent'
        })

        with patch.object(alerta_customer, "fetch_url") as fetch_url_mock:
            fetch_url_mock.return_value = customer_response_page1()
            with self.assertRaises(AnsibleExitJson):
                self.module.main()
