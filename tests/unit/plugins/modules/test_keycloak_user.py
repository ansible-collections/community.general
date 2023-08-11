# -*- coding: utf-8 -*-

# Copyright (c) 2021, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from contextlib import contextmanager

from ansible_collections.community.general.tests.unit.compat import unittest
from ansible_collections.community.general.tests.unit.compat.mock import patch
from ansible_collections.community.general.tests.unit.plugins.modules.utils import AnsibleExitJson, ModuleTestCase, set_module_args

from ansible_collections.community.general.plugins.modules import keycloak_user

from itertools import count

from ansible.module_utils.six import StringIO


@contextmanager
def patch_keycloak_api(get_user_by_username=None,
                       create_user=None,
                       update_user_groups_membership=None,
                       get_user_groups=None,
                       delete_user=None,
                       update_user=None):
    """Mock context manager for patching the methods in KeycloakAPI that contact the Keycloak server

    Patches the `get_user_by_username` and `create_user` methods

    """

    obj = keycloak_user.KeycloakAPI
    with patch.object(obj, 'get_user_by_username', side_effect=get_user_by_username) as mock_get_user_by_username:
        with patch.object(obj, 'create_user', side_effect=create_user) as mock_create_user:
            with patch.object(obj, 'update_user_groups_membership', side_effect=update_user_groups_membership) as mock_update_user_groups_membership:
                with patch.object(obj, 'get_user_groups', side_effect=get_user_groups) as mock_get_user_groups:
                    with patch.object(obj, 'delete_user', side_effect=delete_user) as mock_delete_user:
                        with patch.object(obj, 'update_user', side_effect=update_user) as mock_update_user:
                            yield mock_get_user_by_username, mock_create_user, mock_update_user_groups_membership, \
                                mock_get_user_groups, mock_delete_user, mock_update_user


def get_response(object_with_future_response, method, get_id_call_count):
    if callable(object_with_future_response):
        return object_with_future_response()
    if isinstance(object_with_future_response, dict):
        return get_response(
            object_with_future_response[method], method, get_id_call_count)
    if isinstance(object_with_future_response, list):
        call_number = next(get_id_call_count)
        return get_response(
            object_with_future_response[call_number], method, get_id_call_count)
    return object_with_future_response


def build_mocked_request(get_id_user_count, response_dict):
    def _mocked_requests(*args, **kwargs):
        url = args[0]
        method = kwargs['method']
        future_response = response_dict.get(url, None)
        return get_response(future_response, method, get_id_user_count)

    return _mocked_requests


def create_wrapper(text_as_string):
    """Allow to mock many times a call to one address.
    Without this function, the StringIO is empty for the second call.
    """

    def _create_wrapper():
        return StringIO(text_as_string)

    return _create_wrapper


def mock_good_connection():
    token_response = {
        'http://keycloak.url/auth/realms/master/protocol/openid-connect/token': create_wrapper(
            '{"access_token": "alongtoken"}'), }
    return patch(
        'ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak.open_url',
        side_effect=build_mocked_request(count(), token_response),
        autospec=True
    )


class TestKeycloakUser(ModuleTestCase):
    def setUp(self):
        super(TestKeycloakUser, self).setUp()
        self.module = keycloak_user

    def test_add_new_user(self):
        """Add a new user"""

        module_args = {
            'auth_keycloak_url': 'https: // auth.example.com / auth',
            'token': '{{ access_token }}',
            'state': 'present',
            'realm': 'master',
            'username': 'test',
            'groups': []
        }
        return_value_get_user_by_username = [None]
        return_value_update_user_groups_membership = [False]
        return_get_user_groups = [[]]
        return_create_user = [{'id': '123eqwdawer24qwdqw4'}]
        return_delete_user = None
        return_update_user = None
        changed = True

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_user_by_username=return_value_get_user_by_username,
                                    create_user=return_create_user,
                                    update_user_groups_membership=return_value_update_user_groups_membership,
                                    get_user_groups=return_get_user_groups,
                                    update_user=return_update_user,
                                    delete_user=return_delete_user) \
                    as (mock_get_user_by_username,
                        mock_create_user,
                        mock_update_user_groups_membership,
                        mock_get_user_groups,
                        mock_delete_user,
                        mock_update_user):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        self.assertEqual(mock_get_user_by_username.call_count, 1)
        self.assertEqual(mock_create_user.call_count, 1)
        self.assertEqual(mock_update_user_groups_membership.call_count, 1)
        self.assertEqual(mock_get_user_groups.call_count, 1)
        self.assertEqual(mock_update_user.call_count, 0)
        self.assertEqual(mock_delete_user.call_count, 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_add_exiting_user_no_change(self):
        """Add a new user"""

        module_args = {
            'auth_keycloak_url': 'https: // auth.example.com / auth',
            'token': '{{ access_token }}',
            'state': 'present',
            'realm': 'master',
            'username': 'test',
            'groups': []
        }
        return_value_get_user_by_username = [
            {
                'id': '123eqwdawer24qwdqw4',
                'username': 'test',
                'groups': [],
                'enabled': True,
                'emailVerified': False,
                'disableableCredentialTypes': [],
                'requiredActions': [],
                'credentials': [],
                'federatedIdentities': [],
                'clientConsents': []
            }
        ]
        return_value_update_user_groups_membership = [False]
        return_get_user_groups = [[]]
        return_create_user = None
        return_delete_user = None
        return_update_user = None
        changed = False

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_user_by_username=return_value_get_user_by_username,
                                    create_user=return_create_user,
                                    update_user_groups_membership=return_value_update_user_groups_membership,
                                    get_user_groups=return_get_user_groups,
                                    update_user=return_update_user,
                                    delete_user=return_delete_user) \
                    as (mock_get_user_by_username,
                        mock_create_user,
                        mock_update_user_groups_membership,
                        mock_get_user_groups,
                        mock_delete_user,
                        mock_update_user):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        self.assertEqual(mock_get_user_by_username.call_count, 1)
        self.assertEqual(mock_create_user.call_count, 0)
        self.assertEqual(mock_update_user_groups_membership.call_count, 1)
        self.assertEqual(mock_get_user_groups.call_count, 1)
        self.assertEqual(mock_update_user.call_count, 0)
        self.assertEqual(mock_delete_user.call_count, 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_update_user_with_group_changes(self):
        """Update groups for a user"""

        module_args = {
            'auth_keycloak_url': 'https: // auth.example.com / auth',
            'token': '{{ access_token }}',
            'state': 'present',
            'realm': 'master',
            'username': 'test',
            'first_name': 'test',
            'last_name': 'user',
            'groups': [{
                'name': 'group1',
                'state': 'present'
            }]
        }
        return_value_get_user_by_username = [
            {
                'id': '123eqwdawer24qwdqw4',
                'username': 'test',
                'groups': [],
                'enabled': True,
                'emailVerified': False,
                'disableableCredentialTypes': [],
                'requiredActions': [],
                'credentials': [],
                'federatedIdentities': [],
                'clientConsents': []
            }
        ]
        return_value_update_user_groups_membership = [True]
        return_get_user_groups = [['group1']]
        return_create_user = None
        return_delete_user = None
        return_update_user = [
            {
                'id': '123eqwdawer24qwdqw4',
                'username': 'test',
                'first_name': 'test',
                'last_name': 'user',
                'enabled': True,
                'emailVerified': False,
                'disableableCredentialTypes': [],
                'requiredActions': [],
                'credentials': [],
                'federatedIdentities': [],
                'clientConsents': []
            }
        ]
        changed = True

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_user_by_username=return_value_get_user_by_username,
                                    create_user=return_create_user,
                                    update_user_groups_membership=return_value_update_user_groups_membership,
                                    get_user_groups=return_get_user_groups,
                                    update_user=return_update_user,
                                    delete_user=return_delete_user) \
                    as (mock_get_user_by_username,
                        mock_create_user,
                        mock_update_user_groups_membership,
                        mock_get_user_groups,
                        mock_delete_user,
                        mock_update_user):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        self.assertEqual(mock_get_user_by_username.call_count, 1)
        self.assertEqual(mock_create_user.call_count, 0)
        self.assertEqual(mock_update_user_groups_membership.call_count, 1)
        self.assertEqual(mock_get_user_groups.call_count, 1)
        self.assertEqual(mock_update_user.call_count, 1)
        self.assertEqual(mock_delete_user.call_count, 0)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)

    def test_delete_user(self):
        """Delete a user"""

        module_args = {
            'auth_keycloak_url': 'https: // auth.example.com / auth',
            'token': '{{ access_token }}',
            'state': 'absent',
            'realm': 'master',
            'username': 'test',
            'groups': []
        }
        return_value_get_user_by_username = [
            {
                'id': '123eqwdawer24qwdqw4',
                'username': 'test',
                'groups': [],
                'enabled': True,
                'emailVerified': False,
                'disableableCredentialTypes': [],
                'requiredActions': [],
                'credentials': [],
                'federatedIdentities': [],
                'clientConsents': []
            }
        ]
        return_value_update_user_groups_membership = None
        return_get_user_groups = None
        return_create_user = None
        return_delete_user = None
        return_update_user = None
        changed = True

        set_module_args(module_args)

        # Run the module

        with mock_good_connection():
            with patch_keycloak_api(get_user_by_username=return_value_get_user_by_username,
                                    create_user=return_create_user,
                                    update_user_groups_membership=return_value_update_user_groups_membership,
                                    get_user_groups=return_get_user_groups,
                                    update_user=return_update_user,
                                    delete_user=return_delete_user) \
                    as (mock_get_user_by_username,
                        mock_create_user,
                        mock_update_user_groups_membership,
                        mock_get_user_groups,
                        mock_delete_user,
                        mock_update_user):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        self.assertEqual(mock_get_user_by_username.call_count, 1)
        self.assertEqual(mock_create_user.call_count, 0)
        self.assertEqual(mock_update_user_groups_membership.call_count, 0)
        self.assertEqual(mock_get_user_groups.call_count, 0)
        self.assertEqual(mock_update_user.call_count, 0)
        self.assertEqual(mock_delete_user.call_count, 1)

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]['changed'], changed)


if __name__ == '__main__':
    unittest.main()
