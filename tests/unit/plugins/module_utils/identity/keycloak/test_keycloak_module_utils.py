# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import unittest

from ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak import is_struct_included


class KeycloakIsStructIncludedTestCase(unittest.TestCase):
    dict1 = dict(
        test1='test1',
        test2=dict(
            test1='test1',
            test2='test2'
        ),
        test3=['test1', dict(test='test1', test2='test2')]
    )
    dict2 = dict(
        test1='test1',
        test2=dict(
            test1='test1',
            test2='test2',
            test3='test3'
        ),
        test3=['test1', dict(test='test1', test2='test2'), 'test3'],
        test4='test4'
    )
    dict3 = dict(
        test1='test1',
        test2=dict(
            test1='test1',
            test2='test23',
            test3='test3'
        ),
        test3=['test1', dict(test='test1', test2='test23'), 'test3'],
        test4='test4'
    )

    dict5 = dict(
        test1='test1',
        test2=dict(
            test1=True,
            test2='test23',
            test3='test3'
        ),
        test3=['test1', dict(test='test1', test2='test23'), 'test3'],
        test4='test4'
    )

    dict6 = dict(
        test1='test1',
        test2=dict(
            test1='true',
            test2='test23',
            test3='test3'
        ),
        test3=['test1', dict(test='test1', test2='test23'), 'test3'],
        test4='test4'
    )
    dict7 = [
        {
            'roles': ['view-clients', 'view-identity-providers', 'view-users', 'query-realms', 'manage-users'],
            'clientid': 'master-realm'
        },
        {
            'roles': ['manage-account', 'view-profile', 'manage-account-links'],
            'clientid': 'account'
        }
    ]
    dict8 = [
        {
            'roles': ['view-clients', 'query-realms', 'view-users'],
            'clientid': 'master-realm'
        },
        {
            'roles': ['manage-account-links', 'view-profile', 'manage-account'],
            'clientid': 'account'
        }
    ]

    def test_trivial(self):
        self.assertTrue(is_struct_included(self.dict1, self.dict1))

    def test_equals_with_dict2_bigger_than_dict1(self):
        self.assertTrue(is_struct_included(self.dict1, self.dict2))

    def test_not_equals_with_dict2_bigger_than_dict1(self):
        self.assertFalse(is_struct_included(self.dict2, self.dict1))

    def test_not_equals_with_dict1_different_than_dict3(self):
        self.assertFalse(is_struct_included(self.dict1, self.dict3))

    def test_equals_with_dict5_contain_bool_and_dict6_contain_true_string(self):
        self.assertFalse(is_struct_included(self.dict5, self.dict6))
        self.assertFalse(is_struct_included(self.dict6, self.dict5))

    def test_not_equals_dict7_dict8_compare_dict7_with_list_bigger_than_dict8_but_reverse_equals(self):
        self.assertFalse(is_struct_included(self.dict7, self.dict8))
        self.assertTrue(is_struct_included(self.dict8, self.dict7))
