# -*- coding: utf-8 -*-
# Copyright (c) 2021, Florian Dambrine <android.florian@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

import json

import pytest
from ansible.module_utils.common.dict_transformations import dict_merge
from ansible.module_utils.six import iteritems
from ansible_collections.community.general.plugins.module_utils.net_tools.pritunl import (
    api,
)
from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import MagicMock

__metaclass__ = type


# Pritunl Mocks

PRITUNL_ORGS = [
    {
        "auth_api": False,
        "name": "Foo",
        "auth_token": None,
        "user_count": 0,
        "auth_secret": None,
        "id": "csftwlu6uhralzi2dpmhekz3",
    },
    {
        "auth_api": False,
        "name": "GumGum",
        "auth_token": None,
        "user_count": 3,
        "auth_secret": None,
        "id": "58070daee63f3b2e6e472c36",
    },
    {
        "auth_api": False,
        "name": "Bar",
        "auth_token": None,
        "user_count": 0,
        "auth_secret": None,
        "id": "v1sncsxxybnsylc8gpqg85pg",
    },
]

NEW_PRITUNL_ORG = {
    "auth_api": False,
    "name": "NewOrg",
    "auth_token": None,
    "user_count": 0,
    "auth_secret": None,
    "id": "604a140ae63f3b36bc34c7bd",
}

PRITUNL_USERS = [
    {
        "auth_type": "google",
        "dns_servers": None,
        "pin": True,
        "dns_suffix": None,
        "servers": [
            {
                "status": False,
                "platform": None,
                "server_id": "580711322bb66c1d59b9568f",
                "virt_address6": "fd00:c0a8: 9700: 0: 192: 168: 101: 27",
                "virt_address": "192.168.101.27",
                "name": "vpn-A",
                "real_address": None,
                "connected_since": None,
                "id": "580711322bb66c1d59b9568f",
                "device_name": None,
            },
            {
                "status": False,
                "platform": None,
                "server_id": "5dad2cc6e63f3b3f4a6dfea5",
                "virt_address6": "fd00:c0a8:f200: 0: 192: 168: 201: 37",
                "virt_address": "192.168.201.37",
                "name": "vpn-B",
                "real_address": None,
                "connected_since": None,
                "id": "5dad2cc6e63f3b3f4a6dfea5",
                "device_name": None,
            },
        ],
        "disabled": False,
        "network_links": [],
        "port_forwarding": [],
        "id": "58070dafe63f3b2e6e472c3b",
        "organization_name": "GumGum",
        "type": "server",
        "email": "bot@company.com",
        "status": True,
        "dns_mapping": None,
        "otp_secret": "123456789ABCDEFG",
        "client_to_client": False,
        "sso": "google",
        "bypass_secondary": False,
        "groups": ["admin", "multiregion"],
        "audit": False,
        "name": "bot",
        "gravatar": True,
        "otp_auth": True,
        "organization": "58070daee63f3b2e6e472c36",
    },
    {
        "auth_type": "google",
        "dns_servers": None,
        "pin": True,
        "dns_suffix": None,
        "servers": [
            {
                "status": False,
                "platform": None,
                "server_id": "580711322bb66c1d59b9568f",
                "virt_address6": "fd00:c0a8: 9700: 0: 192: 168: 101: 27",
                "virt_address": "192.168.101.27",
                "name": "vpn-A",
                "real_address": None,
                "connected_since": None,
                "id": "580711322bb66c1d59b9568f",
                "device_name": None,
            },
            {
                "status": False,
                "platform": None,
                "server_id": "5dad2cc6e63f3b3f4a6dfea5",
                "virt_address6": "fd00:c0a8:f200: 0: 192: 168: 201: 37",
                "virt_address": "192.168.201.37",
                "name": "vpn-B",
                "real_address": None,
                "connected_since": None,
                "id": "5dad2cc6e63f3b3f4a6dfea5",
                "device_name": None,
            },
        ],
        "disabled": False,
        "network_links": [],
        "port_forwarding": [],
        "id": "58070dafe63f3b2e6e472c3b",
        "organization_name": "GumGum",
        "type": "client",
        "email": "florian@company.com",
        "status": True,
        "dns_mapping": None,
        "otp_secret": "123456789ABCDEFG",
        "client_to_client": False,
        "sso": "google",
        "bypass_secondary": False,
        "groups": ["web", "database"],
        "audit": False,
        "name": "florian",
        "gravatar": True,
        "otp_auth": True,
        "organization": "58070daee63f3b2e6e472c36",
    },
    {
        "auth_type": "google",
        "dns_servers": None,
        "pin": True,
        "dns_suffix": None,
        "servers": [
            {
                "status": False,
                "platform": None,
                "server_id": "580711322bb66c1d59b9568f",
                "virt_address6": "fd00:c0a8: 9700: 0: 192: 168: 101: 27",
                "virt_address": "192.168.101.27",
                "name": "vpn-A",
                "real_address": None,
                "connected_since": None,
                "id": "580711322bb66c1d59b9568f",
                "device_name": None,
            },
            {
                "status": False,
                "platform": None,
                "server_id": "5dad2cc6e63f3b3f4a6dfea5",
                "virt_address6": "fd00:c0a8:f200: 0: 192: 168: 201: 37",
                "virt_address": "192.168.201.37",
                "name": "vpn-B",
                "real_address": None,
                "connected_since": None,
                "id": "5dad2cc6e63f3b3f4a6dfea5",
                "device_name": None,
            },
        ],
        "disabled": False,
        "network_links": [],
        "port_forwarding": [],
        "id": "58070dafe63f3b2e6e472c3b",
        "organization_name": "GumGum",
        "type": "server",
        "email": "ops@company.com",
        "status": True,
        "dns_mapping": None,
        "otp_secret": "123456789ABCDEFG",
        "client_to_client": False,
        "sso": "google",
        "bypass_secondary": False,
        "groups": ["web", "database"],
        "audit": False,
        "name": "ops",
        "gravatar": True,
        "otp_auth": True,
        "organization": "58070daee63f3b2e6e472c36",
    },
]

NEW_PRITUNL_USER = {
    "auth_type": "local",
    "disabled": False,
    "dns_servers": None,
    "otp_secret": "6M4UWP2BCJBSYZAT",
    "name": "alice",
    "pin": False,
    "dns_suffix": None,
    "client_to_client": False,
    "email": "alice@company.com",
    "organization_name": "GumGum",
    "bypass_secondary": False,
    "groups": ["a", "b"],
    "organization": "58070daee63f3b2e6e472c36",
    "port_forwarding": [],
    "type": "client",
    "id": "590add71e63f3b72d8bb951a",
}

NEW_PRITUNL_USER_UPDATED = dict_merge(
    NEW_PRITUNL_USER,
    {
        "disabled": True,
        "name": "bob",
        "email": "bob@company.com",
        "groups": ["c", "d"],
    },
)


class PritunlEmptyOrganizationMock(MagicMock):
    """Pritunl API Mock for organization GET API calls."""

    def getcode(self):
        return 200

    def read(self):
        return json.dumps([])


class PritunlListOrganizationMock(MagicMock):
    """Pritunl API Mock for organization GET API calls."""

    def getcode(self):
        return 200

    def read(self):
        return json.dumps(PRITUNL_ORGS)


class PritunlListUserMock(MagicMock):
    """Pritunl API Mock for user GET API calls."""

    def getcode(self):
        return 200

    def read(self):
        return json.dumps(PRITUNL_USERS)


class PritunlErrorMock(MagicMock):
    """Pritunl API Mock for API call failures."""

    def getcode(self):
        return 500

    def read(self):
        return "{}"


class PritunlPostOrganizationMock(MagicMock):
    def getcode(self):
        return 200

    def read(self):
        return json.dumps(NEW_PRITUNL_ORG)


class PritunlListOrganizationAfterPostMock(MagicMock):
    def getcode(self):
        return 200

    def read(self):
        return json.dumps(PRITUNL_ORGS + [NEW_PRITUNL_ORG])


class PritunlPostUserMock(MagicMock):
    """Pritunl API Mock for POST API calls."""

    def getcode(self):
        return 200

    def read(self):
        return json.dumps([NEW_PRITUNL_USER])


class PritunlPutUserMock(MagicMock):
    """Pritunl API Mock for PUT API calls."""

    def getcode(self):
        return 200

    def read(self):
        return json.dumps(NEW_PRITUNL_USER_UPDATED)


class PritunlDeleteOrganizationMock(MagicMock):
    """Pritunl API Mock for DELETE API calls."""

    def getcode(self):
        return 200

    def read(self):
        return "{}"


class PritunlDeleteUserMock(MagicMock):
    """Pritunl API Mock for DELETE API calls."""

    def getcode(self):
        return 200

    def read(self):
        return "{}"


# Ansible Module Mock and Pytest mock fixtures


class ModuleFailException(Exception):
    def __init__(self, msg, **kwargs):
        super(ModuleFailException, self).__init__(msg)
        self.fail_msg = msg
        self.fail_kwargs = kwargs


@pytest.fixture
def pritunl_settings():
    return {
        "api_token": "token",
        "api_secret": "secret",
        "base_url": "https://pritunl.domain.com",
        "validate_certs": True,
    }


@pytest.fixture
def pritunl_organization_data():
    return {
        "name": NEW_PRITUNL_ORG["name"],
    }


@pytest.fixture
def pritunl_user_data():
    return {
        "name": NEW_PRITUNL_USER["name"],
        "email": NEW_PRITUNL_USER["email"],
        "groups": NEW_PRITUNL_USER["groups"],
        "disabled": NEW_PRITUNL_USER["disabled"],
        "type": NEW_PRITUNL_USER["type"],
    }


@pytest.fixture
def get_pritunl_organization_mock():
    return PritunlListOrganizationMock()


@pytest.fixture
def get_pritunl_user_mock():
    return PritunlListUserMock()


@pytest.fixture
def get_pritunl_error_mock():
    return PritunlErrorMock()


@pytest.fixture
def post_pritunl_organization_mock():
    return PritunlPostOrganizationMock()


@pytest.fixture
def post_pritunl_user_mock():
    return PritunlPostUserMock()


@pytest.fixture
def put_pritunl_user_mock():
    return PritunlPutUserMock()


@pytest.fixture
def delete_pritunl_organization_mock():
    return PritunlDeleteOrganizationMock()


@pytest.fixture
def delete_pritunl_user_mock():
    return PritunlDeleteUserMock()


class TestPritunlApi:
    """
    Test class to validate CRUD operations on Pritunl.
    """

    # Test for GET / list operation on Pritunl API
    @pytest.mark.parametrize(
        "org_id,org_user_count",
        [
            ("58070daee63f3b2e6e472c36", 3),
            ("v1sncsxxybnsylc8gpqg85pg", 0),
        ],
    )
    def test_list_all_pritunl_organization(
        self,
        pritunl_settings,
        get_pritunl_organization_mock,
        org_id,
        org_user_count,
    ):
        api._get_pritunl_organizations = get_pritunl_organization_mock()

        response = api.list_pritunl_organizations(**pritunl_settings)

        assert len(response) == 3

        for org in response:
            if org["id"] == org_id:
                org["user_count"] == org_user_count

    @pytest.mark.parametrize(
        "org_filters,org_expected",
        [
            ({"id": "58070daee63f3b2e6e472c36"}, "GumGum"),
            ({"name": "GumGum"}, "GumGum"),
        ],
    )
    def test_list_filtered_pritunl_organization(
        self,
        pritunl_settings,
        get_pritunl_organization_mock,
        org_filters,
        org_expected,
    ):
        api._get_pritunl_organizations = get_pritunl_organization_mock()

        response = api.list_pritunl_organizations(
            **dict_merge(pritunl_settings, {"filters": org_filters})
        )

        assert len(response) == 1
        assert response[0]["name"] == org_expected

    @pytest.mark.parametrize(
        "org_id,org_user_count",
        [("58070daee63f3b2e6e472c36", 3)],
    )
    def test_list_all_pritunl_user(
        self, pritunl_settings, get_pritunl_user_mock, org_id, org_user_count
    ):
        api._get_pritunl_users = get_pritunl_user_mock()

        response = api.list_pritunl_users(
            **dict_merge(pritunl_settings, {"organization_id": org_id})
        )

        assert len(response) == org_user_count

    @pytest.mark.parametrize(
        "org_id,user_filters,user_expected",
        [
            ("58070daee63f3b2e6e472c36", {"email": "bot@company.com"}, "bot"),
            ("58070daee63f3b2e6e472c36", {"name": "florian"}, "florian"),
        ],
    )
    def test_list_filtered_pritunl_user(
        self,
        pritunl_settings,
        get_pritunl_user_mock,
        org_id,
        user_filters,
        user_expected,
    ):
        api._get_pritunl_users = get_pritunl_user_mock()

        response = api.list_pritunl_users(
            **dict_merge(
                pritunl_settings, {"organization_id": org_id, "filters": user_filters}
            )
        )

        assert len(response) > 0

        for user in response:
            assert user["organization"] == org_id
            assert user["name"] == user_expected

    # Test for POST operation on Pritunl API
    def test_add_pritunl_organization(
        self,
        pritunl_settings,
        pritunl_organization_data,
        post_pritunl_organization_mock,
    ):
        api._post_pritunl_organization = post_pritunl_organization_mock()

        create_response = api.post_pritunl_organization(
            **dict_merge(
                pritunl_settings,
                {"organization_name": pritunl_organization_data["name"]},
            )
        )

        # Ensure provided settings match with the ones returned by Pritunl
        for k, v in iteritems(pritunl_organization_data):
            assert create_response[k] == v

    @pytest.mark.parametrize("org_id", [("58070daee63f3b2e6e472c36")])
    def test_add_and_update_pritunl_user(
        self,
        pritunl_settings,
        pritunl_user_data,
        post_pritunl_user_mock,
        put_pritunl_user_mock,
        org_id,
    ):
        api._post_pritunl_user = post_pritunl_user_mock()
        api._put_pritunl_user = put_pritunl_user_mock()

        create_response = api.post_pritunl_user(
            **dict_merge(
                pritunl_settings,
                {
                    "organization_id": org_id,
                    "user_data": pritunl_user_data,
                },
            )
        )

        # Ensure provided settings match with the ones returned by Pritunl
        for k, v in iteritems(pritunl_user_data):
            assert create_response[k] == v

        # Update the newly created user to ensure only certain settings are changed

        user_updates = {
            "name": "bob",
            "email": "bob@company.com",
            "disabled": True,
        }

        update_response = api.post_pritunl_user(
            **dict_merge(
                pritunl_settings,
                {
                    "organization_id": org_id,
                    "user_id": create_response["id"],
                    "user_data": dict_merge(pritunl_user_data, user_updates),
                },
            )
        )

        # Ensure only certain settings changed and the rest remained untouched.
        for k, v in iteritems(update_response):
            if k in update_response:
                assert update_response[k] == v
            else:
                assert update_response[k] == create_response[k]

    # Test for DELETE operation on Pritunl API

    @pytest.mark.parametrize("org_id", [("58070daee63f3b2e6e472c36")])
    def test_delete_pritunl_organization(
        self, pritunl_settings, org_id, delete_pritunl_organization_mock
    ):
        api._delete_pritunl_organization = delete_pritunl_organization_mock()

        response = api.delete_pritunl_organization(
            **dict_merge(
                pritunl_settings,
                {
                    "organization_id": org_id,
                },
            )
        )

        assert response == {}

    @pytest.mark.parametrize(
        "org_id,user_id", [("58070daee63f3b2e6e472c36", "590add71e63f3b72d8bb951a")]
    )
    def test_delete_pritunl_user(
        self, pritunl_settings, org_id, user_id, delete_pritunl_user_mock
    ):
        api._delete_pritunl_user = delete_pritunl_user_mock()

        response = api.delete_pritunl_user(
            **dict_merge(
                pritunl_settings,
                {
                    "organization_id": org_id,
                    "user_id": user_id,
                },
            )
        )

        assert response == {}

    # Test API call errors
    def test_pritunl_error(self, pritunl_settings, get_pritunl_error_mock):
        api.pritunl_auth_request = get_pritunl_error_mock()

        with pytest.raises(api.PritunlException):
            response = api.list_pritunl_organizations(**pritunl_settings)
