# -*- coding: utf-8 -*-

# Copyright (c) 2021, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import nomad
from ansible_collections.community.general.plugins.modules import nomad_token
from ansible_collections.community.general.tests.unit.compat.mock import patch
from ansible_collections.community.general.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, \
    ModuleTestCase, \
    set_module_args


def mock_acl_get_tokens(empty_list=False):
    response_object = []

    if not empty_list:
        response_object = [
            {
                'AccessorID': 'bac2b162-2a63-efa2-4e68-55d79dcb7721',
                'Name': 'Bootstrap Token', 'Type': 'management',
                'Policies': None, 'Roles': None, 'Global': True,
                'Hash': 'BUJ3BerTfrqFVm1P+vZr1gz9ubOkd+JAvYjNAJyaU9Y=',
                'CreateTime': '2023-11-12T18:44:39.740562185Z',
                'ExpirationTime': None,
                'CreateIndex': 9,
                'ModifyIndex': 9
            },
            {
                'AccessorID': '0d01c55f-8d63-f832-04ff-1866d4eb594e',
                'Name': 'devs',
                'Type': 'client', 'Policies': ['readonly'],
                'Roles': None,
                'Global': True,
                'Hash': 'eSn8H8RVqh8As8WQNnC2vlBRqXy6DECogc5umzX0P30=',
                'CreateTime': '2023-11-12T18:48:34.248857001Z',
                'ExpirationTime': None,
                'CreateIndex': 14,
                'ModifyIndex': 836
            }
        ]

    return response_object


def mock_acl_generate_bootstrap():
    response_object = {
        'AccessorID': '0d01c55f-8d63-f832-04ff-1866d4eb594e',
        'Name': 'Bootstrap Token',
        'Type': 'management',
        'Policies': None,
        'Roles': None,
        'Global': True,
        'Hash': 'BUJ3BerTfrqFVm1P+vZr1gz9ubOkd+JAvYjNAJyaU9Y=',
        'CreateTime': '2023-11-12T18:48:34.248857001Z',
        'ExpirationTime': None,
        'ExpirationTTL': '',
        'CreateIndex': 14,
        'ModifyIndex': 836,
        'SecretID': 'd539a03d-337a-8504-6d12-000f861337bc'
    }
    return response_object


def mock_acl_create_update_token():
    response_object = {
        'AccessorID': '0d01c55f-8d63-f832-04ff-1866d4eb594e',
        'Name': 'dev',
        'Type': 'client',
        'Policies': ['readonly'],
        'Roles': None,
        'Global': True,
        'Hash': 'eSn8H8RVqh8As8WQNnC2vlBRqXy6DECogc5umzX0P30=',
        'CreateTime': '2023-11-12T18:48:34.248857001Z',
        'ExpirationTime': None,
        'ExpirationTTL': '',
        'CreateIndex': 14,
        'ModifyIndex': 836,
        'SecretID': 'd539a03d-337a-8504-6d12-000f861337bc'
    }

    return response_object


def mock_acl_delete_token():
    return {}


class TestNomadTokenModule(ModuleTestCase):

    def setUp(self):
        super(TestNomadTokenModule, self).setUp()
        self.module = nomad_token

    def tearDown(self):
        super(TestNomadTokenModule, self).tearDown()

    def test_should_fail_without_parameters(self):
        with self.assertRaises(AnsibleFailJson):
            set_module_args({})
            self.module.main()

    def test_should_create_token_type_client(self):
        module_args = {
            'host': 'localhost',
            'name': 'Dev token',
            'token_type': 'client',
            'state': 'present'
        }

        set_module_args(module_args)
        with patch.object(nomad.api.acl.Acl, 'get_tokens', return_value=mock_acl_get_tokens()) as mock_get_tokens:
            with patch.object(nomad.api.acl.Acl, 'create_token', return_value=mock_acl_create_update_token()) as \
                    mock_create_update_token:
                with self.assertRaises(AnsibleExitJson):
                    self.module.main()

                self.assertIs(mock_get_tokens.call_count, 1)
                self.assertIs(mock_create_update_token.call_count, 1)

    def test_should_create_token_type_bootstrap(self):
        module_args = {
            'host': 'localhost',
            'token_type': 'bootstrap',
            'state': 'present'
        }

        set_module_args(module_args)

        with patch.object(nomad.api.acl.Acl, 'get_tokens') as mock_get_tokens:
            with patch.object(nomad.api.Acl, 'generate_bootstrap') as mock_generate_bootstrap:
                mock_get_tokens.return_value = mock_acl_get_tokens(empty_list=True)
                mock_generate_bootstrap.return_value = mock_acl_generate_bootstrap()

                with self.assertRaises(AnsibleExitJson):
                    self.module.main()

                self.assertIs(mock_get_tokens.call_count, 1)
                self.assertIs(mock_generate_bootstrap.call_count, 1)

    def test_should_fail_delete_without_name_parameter(self):
        module_args = {
            'host': 'localhost',
            'state': 'absent'
        }

        set_module_args(module_args)
        with patch.object(nomad.api.acl.Acl, 'get_tokens') as mock_get_tokens:
            with patch.object(nomad.api.acl.Acl, 'delete_token') as mock_delete_token:
                mock_get_tokens.return_value = mock_acl_get_tokens()
                mock_delete_token.return_value = mock_acl_delete_token()

                with self.assertRaises(AnsibleFailJson):
                    self.module.main()

    def test_should_fail_delete_bootstrap_token(self):
        module_args = {
            'host': 'localhost',
            'token_type': 'boostrap',
            'state': 'absent'
        }

        set_module_args(module_args)

        with self.assertRaises(AnsibleFailJson):
            self.module.main()

    def test_should_fail_delete_boostrap_token_by_name(self):
        module_args = {
            'host': 'localhost',
            'name': 'Bootstrap Token',
            'state': 'absent'
        }

        set_module_args(module_args)

        with self.assertRaises(AnsibleFailJson):
            self.module.main()

    def test_should_delete_client_token(self):
        module_args = {
            'host': 'localhost',
            'name': 'devs',
            'state': 'absent'
        }

        set_module_args(module_args)

        with patch.object(nomad.api.acl.Acl, 'get_tokens') as mock_get_tokens:
            with patch.object(nomad.api.acl.Acl, 'delete_token') as mock_delete_token:
                mock_get_tokens.return_value = mock_acl_get_tokens()
                mock_delete_token.return_value = mock_acl_delete_token()

                with self.assertRaises(AnsibleExitJson):
                    self.module.main()

                self.assertIs(mock_delete_token.call_count, 1)

    def test_should_update_client_token(self):
        module_args = {
            'host': 'localhost',
            'name': 'devs',
            'token_type': 'client',
            'state': 'present'
        }

        set_module_args(module_args)

        with patch.object(nomad.api.acl.Acl, 'get_tokens') as mock_get_tokens:
            with patch.object(nomad.api.acl.Acl, 'update_token') as mock_create_update_token:
                mock_get_tokens.return_value = mock_acl_get_tokens()
                mock_create_update_token.return_value = mock_acl_create_update_token()

                with self.assertRaises(AnsibleExitJson):
                    self.module.main()
                self.assertIs(mock_get_tokens.call_count, 1)
                self.assertIs(mock_create_update_token.call_count, 1)
