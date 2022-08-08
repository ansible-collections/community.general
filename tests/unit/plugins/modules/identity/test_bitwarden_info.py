# -*- coding: utf-8 -*-

# Copyright (c) 2022, Jonathan Lung (@lungj) <lungj@heresjono.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible_collections.community.general.tests.unit.compat import unittest
from ansible_collections.community.general.tests.unit.compat.mock import Mock, patch
from ansible_collections.community.general.tests.unit.plugins.modules.utils import (
    AnsibleExitJson, AnsibleFailJson, set_module_args
)

from ansible_collections.community.general.plugins.module_utils.identity.bitwarden import BitwardenException
from ansible_collections.community.general.plugins.modules.identity import bitwarden_info

from ansible_collections.community.general.tests.unit.plugins.modules.identity.test_bitwarden import (
    ORGANIZATIONS, FOLDERS, ITEMS, MOCK_RESPONSES, MockClient, client, mock
)


@patch('ansible.module_utils.basic.AnsibleModule.get_bin_path', new=Mock(return_value='/usr/bin/bw'))
@patch(
    'ansible.module_utils.basic.AnsibleModule.run_command',
    new=client(MOCK_RESPONSES))
class TestBitwardenQueryOrganization(unittest.TestCase):
    '''Test querying organizations or organization information.'''
    def setUp(self):
        mock()
        self.module = bitwarden_info
        MockClient.command_history = []

    def tearDown(self):
        self.assertFalse(MockClient.number_of_edits())

    def test_query_all(self):
        '''Test getting a list of all organizations.'''
        set_module_args({
            'target': 'organizations',
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(ansible_exit_json.exception.args[0], {
            'changed': False,
            'ansible_module_results': [ORGANIZATIONS['9ca']]
        })

    def test_query_by_name(self):
        '''Test getting an organization by name.'''
        set_module_args({
            'target': 'organization',
            'organization_name': 'Test',
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(ansible_exit_json.exception.args[0], {
            'changed': False,
            'ansible_module_results': ORGANIZATIONS['9ca']
        })

    def test_query_by_id(self):
        '''Test getting an organization by id.'''
        set_module_args({
            'target':
            'organization',
            'organization_id':
            '9caf72f5-55ad-4a15-b923-aee001714d67',
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(ansible_exit_json.exception.args[0], {
            'changed': False,
            'ansible_module_results': ORGANIZATIONS['9ca']
        })

    def test_query_by_name_and_id(self):
        '''Test getting an organization by specifying both name and id.'''
        set_module_args({
            'target':
            'organization',
            'organization_name':
            'Test',
            'organization_id':
            '9caf72f5-55ad-4a15-b923-aee001714d67',
        })
        with self.assertRaises(AnsibleFailJson):
            self.module.main()

    def test_query_by_name_non_existent(self):
        '''Test getting an organization by name where it does not exist.'''
        set_module_args({
            'target': 'organization',
            'organization_name': 'Tes',
        })
        with self.assertRaises(KeyError):
            self.module.main()

    def test_query_by_id_non_existent(self):
        '''Test getting an organization by id where it does not exist.'''
        set_module_args({
            'target':
            'organization',
            'organization_id':
            '9caf72f5-55ad-4a15-b923-aee001714d6',
        })
        with self.assertRaises(KeyError):
            self.module.main()


@patch('ansible.module_utils.basic.AnsibleModule.get_bin_path', new=Mock(return_value='/usr/bin/bw'))
@patch(
    'ansible.module_utils.basic.AnsibleModule.run_command',
    new=client(MOCK_RESPONSES))
class TestBitwardenQueryFolder(unittest.TestCase):
    '''Test querying folders or folder information.'''
    def setUp(self):
        mock()
        self.module = bitwarden_info
        MockClient.command_history = []

    def tearDown(self):
        self.assertFalse(MockClient.number_of_edits())

    def test_query_all(self):
        '''Test getting all folders.'''
        set_module_args({
            'target': 'folders',
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(
            ansible_exit_json.exception.args[0], {
                'changed':
                False,
                'ansible_module_results': [
                    FOLDERS[None], FOLDERS['2c8'], FOLDERS['2d0'],
                    FOLDERS['3b1'], FOLDERS['6b7']
                ]
            })

    def test_query_by_name(self):
        '''Test getting information about a folder with a specific name.'''
        set_module_args({
            'target': 'folder',
            'folder_name': 'my_folder',
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(ansible_exit_json.exception.args[0], {
            'changed': False,
            'ansible_module_results': FOLDERS['2d0']
        })

    def test_query_by_id(self):
        '''Test getting information about a folder with a specific id.'''
        set_module_args({
            'target': 'folder',
            'folder_id': '2d03899d-d56f-43ed-923d-aee100334387',
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(ansible_exit_json.exception.args[0], {
            'changed': False,
            'ansible_module_results': FOLDERS['2d0']
        })

    def test_query_by_name_and_id(self):
        '''Test getting information about a folder by specifying name and id.'''
        set_module_args({
            'target': 'folder',
            'folder_name': 'my_folder',
            'folder_id': '2d03899d-d56f-43ed-923d-aee100334387',
        })
        with self.assertRaises(AnsibleFailJson):
            self.module.main()

    def test_query_by_name_non_existent(self):
        '''Test getting information about a folder with a specific name that does not exist.'''
        set_module_args({
            'target': 'folder',
            'folder_name': 'my_folde',
        })
        with self.assertRaises(KeyError):
            self.module.main()

    def test_query_by_id_non_existent(self):
        '''Test getting information about a folder with a specific id that does not exist.'''
        set_module_args({
            'target': 'folder',
            'folder_id': '2d03899d-d56f-43ed-923d-aee10033438',
        })
        with self.assertRaises(KeyError):
            self.module.main()


@patch('ansible.module_utils.basic.AnsibleModule.get_bin_path', new=Mock(return_value='/usr/bin/bw'))
@patch(
    'ansible.module_utils.basic.AnsibleModule.run_command',
    new=client(MOCK_RESPONSES))
class TestBitwardenQueryItem(unittest.TestCase):
    '''Test querying items or item information.'''
    def setUp(self):
        mock()
        self.module = bitwarden_info
        MockClient.command_history = []

    def tearDown(self):
        self.assertFalse(MockClient.number_of_edits())

    def test_query_all(self):
        '''Test getting a list of all items.'''
        set_module_args({'target': 'items'})
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(
            ansible_exit_json.exception.args[0], {
                'changed':
                False,
                'ansible_module_results': [
                    ITEMS['08c'], ITEMS['3e4'], ITEMS['58b'], ITEMS['5eb'],
                    ITEMS['634'], ITEMS['650'], ITEMS['7b1'], ITEMS['7fa'],
                    ITEMS['8d1'], ITEMS['909'], ITEMS['ac4'], ITEMS['d2f'],
                    ITEMS['d3c'], ITEMS['d69'], ITEMS['dcb'], ITEMS['e51'],
                    ITEMS['ed4'], ITEMS['f12']
                ]
            })

    def test_query_all_in_no_organization(self):
        '''Test getting a list of all items in the personal vault.'''
        set_module_args({
            'target': 'items',
            'organization_name': '',
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(
            ansible_exit_json.exception.args[0], {
                'changed':
                False,
                'ansible_module_results':
                [ITEMS['5eb'], ITEMS['650'], ITEMS['909'], ITEMS['dcb']]
            })

    def test_query_all_in_organization_by_name(self):
        '''Test getting a list of all items in a named organization.'''
        set_module_args({
            'target': 'items',
            'organization_name': 'Test',
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(
            ansible_exit_json.exception.args[0], {
                'changed':
                False,
                'ansible_module_results': [
                    ITEMS['08c'], ITEMS['3e4'], ITEMS['58b'], ITEMS['634'],
                    ITEMS['7b1'], ITEMS['7fa'], ITEMS['8d1'], ITEMS['ac4'],
                    ITEMS['d2f'], ITEMS['d3c'], ITEMS['d69'], ITEMS['e51'],
                    ITEMS['ed4'], ITEMS['f12']
                ]
            })

    def test_query_all_in_organization_by_id(self):
        '''Test getting a list of all items in a organization specified by id.'''
        set_module_args({
            'target':
            'items',
            'organization_id':
            '9caf72f5-55ad-4a15-b923-aee001714d67',
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(
            ansible_exit_json.exception.args[0], {
                'changed':
                False,
                'ansible_module_results': [
                    ITEMS['08c'], ITEMS['3e4'], ITEMS['58b'], ITEMS['634'],
                    ITEMS['7b1'], ITEMS['7fa'], ITEMS['8d1'], ITEMS['ac4'],
                    ITEMS['d2f'], ITEMS['d3c'], ITEMS['d69'], ITEMS['e51'],
                    ITEMS['ed4'], ITEMS['f12']
                ]
            })

    def test_query_all_in_no_folder(self):
        '''Test getting a list of all items not in a folder.'''
        set_module_args({
            'target': 'items',
            'folder_name': '',
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(
            ansible_exit_json.exception.args[0], {
                'changed':
                False,
                'ansible_module_results': [
                    ITEMS['08c'], ITEMS['3e4'], ITEMS['58b'], ITEMS['5eb'],
                    ITEMS['634'], ITEMS['7b1'], ITEMS['7fa'], ITEMS['8d1'],
                    ITEMS['ac4'], ITEMS['d2f'], ITEMS['d3c'], ITEMS['d69'],
                    ITEMS['dcb'], ITEMS['ed4']
                ]
            })

    def test_query_all_in_folder_by_name(self):
        '''Test getting a list of all items in a folder with a specified name.'''
        set_module_args({
            'target': 'items',
            'folder_name': 'Hellog',
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(ansible_exit_json.exception.args[0], {
            'changed': False,
            'ansible_module_results': [ITEMS['e51']]
        })

    def test_query_all_in_folder_by_id(self):
        '''Test getting a list of all items in a folder with a specified id.'''
        set_module_args({
            'target': 'items',
            'folder_id': '2c8a747e-6f0b-4cc8-a98f-aee20038cc9a',
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(ansible_exit_json.exception.args[0], {
            'changed': False,
            'ansible_module_results': [ITEMS['e51']]
        })

    def test_query_all_in_folder_empty_in_org(self):
        '''Test getting a list of all items in a folder that is empty for a specific organization.'''
        set_module_args({
            'target': 'items',
            'folder_id': '3b12a9da-7c49-40b8-ad33-aede017a7ead',
            'organization_name': 'Test',
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(ansible_exit_json.exception.args[0], {
            'changed': False,
            'ansible_module_results': []
        })

    def test_query_all_in_folder_empty_in_personal(self):
        '''Test getting a list of all items in a folder that is empty for the personal vault.'''
        set_module_args({
            'target': 'items',
            'folder_id': '2c8a747e-6f0b-4cc8-a98f-aee20038cc9a',
            'organization_name': '',
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(ansible_exit_json.exception.args[0], {
            'changed': False,
            'ansible_module_results': []
        })

    def test_query_all_in_folder_in_org(self):
        '''Test getting a list of all items in a folder in an organization.'''
        set_module_args({
            'target': 'items',
            'folder_id': '2c8a747e-6f0b-4cc8-a98f-aee20038cc9a',
            'organization_name': 'Test',
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(ansible_exit_json.exception.args[0], {
            'changed': False,
            'ansible_module_results': [ITEMS['e51']]
        })

    def test_query_by_name(self):
        '''Test getting an item by name that is unique across all organizations/folders.'''
        set_module_args({
            'target': 'item',
            'item_name': 'a_test',
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(ansible_exit_json.exception.args[0], {
            'changed': False,
            'ansible_module_results': ITEMS['909']
        })

    def test_query_by_name_partial_match(self):
        '''Test getting an item by name that is unique across all organizations/folders
        but is a partial match to other items.'''
        set_module_args({
            'target': 'item',
            'item_name': 'some item',
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(ansible_exit_json.exception.args[0], {
            'changed': False,
            'ansible_module_results': ITEMS['e51']
        })

    def test_query_by_name_duplicate(self):
        '''Test getting an item by name that is not unique across all organizations/folders.'''
        set_module_args({
            'target': 'item',
            'item_name': 'some item2',
        })
        with self.assertRaises(BitwardenException):
            self.module.main()

    def test_query_by_name_duplicate_folder(self):
        '''Test getting an item by name that appears in a folder that is in two organizations.'''
        set_module_args({
            'target': 'item',
            'folder_name': 'my_folder',
            'item_name': 'my_account',
        })
        with self.assertRaises(BitwardenException):
            self.module.main()

    def test_query_by_name_duplicate_organization(self):
        '''Test getting an item by name that appears in two folders in the same organization.'''
        set_module_args({
            'target': 'item',
            'organization_name': 'Test',
            'item_name': 'my_account',
        })
        with self.assertRaises(BitwardenException):
            self.module.main()

    def test_query_by_name_disambiguated(self):
        '''Test getting an item by name that appears in different folders and organizations
        but specifying both organization and folder to disambiguate.'''
        set_module_args({
            'target': 'item',
            'organization_name': 'Test',
            'folder_name': 'my_folder',
            'item_name': 'my_account',
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(ansible_exit_json.exception.args[0], {
            'changed': False,
            'ansible_module_results': ITEMS['f12']
        })

    def test_query_by_id(self):
        '''Test getting an item by id.'''
        set_module_args({
            'target': 'item',
            'item_id': 'e5148226-34b3-4bad-bc37-aee20038d49c',
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(ansible_exit_json.exception.args[0], {
            'changed': False,
            'ansible_module_results': ITEMS['e51']
        })

    def test_query_by_name_and_id(self):
        '''Test getting an item by specifying both name and id.'''
        set_module_args({
            'target': 'item',
            'item_name': 'some item',
            'item_id': 'e5148226-34b3-4bad-bc37-aee20038d49c',
        })
        with self.assertRaises(AnsibleFailJson):
            self.module.main()

    def test_query_by_name_non_existent(self):
        '''Test getting an item by name that is a substring of an existent item.'''
        set_module_args({
            'target': 'item',
            'folder_name': 'some ite',
        })
        with self.assertRaises(KeyError):
            self.module.main()

    def test_query_by_id_non_existent(self):
        '''Test getting an item by id that is a substring of an existent item's id.'''
        set_module_args({
            'target': 'item',
            'item_id': 'e5148226-34b3-4bad-bc37-aee20038d49',
        })
        with self.assertRaises(KeyError):
            self.module.main()

    def test_query_by_id_in_correct_folder(self):
        '''Test getting an item by id in a specific folder.'''
        set_module_args({
            'target': 'item',
            'folder_name': 'Hellog',
            'item_id': 'e5148226-34b3-4bad-bc37-aee20038d49c',
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(ansible_exit_json.exception.args[0], {
            'changed': False,
            'ansible_module_results': ITEMS['e51']
        })

    def test_query_by_id_in_wrong_folder(self):
        '''Test getting an item by id in a folder where it does not exist.'''
        set_module_args({
            'target': 'item',
            'folder_name': 'my_folder',
            'item_id': 'e5148226-34b3-4bad-bc37-aee20038d49c',
        })
        with self.assertRaises(KeyError):
            self.module.main()


if __name__ == '__main__':
    unittest.main()
