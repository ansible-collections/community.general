# -*- coding: utf-8 -*-
# Copyright (c) 2022, Jonathan Lung <lungj@heresjono.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import re
import base64

from ansible_collections.community.general.tests.unit.compat import unittest
from ansible_collections.community.general.tests.unit.compat.mock import patch

from ansible.errors import AnsibleError
from ansible.module_utils import six
from ansible.plugins.loader import lookup_loader
from ansible_collections.community.general.plugins.lookup.bitwarden import Bitwarden
from ansible.parsing.ajson import AnsibleJSONEncoder, AnsibleJSONDecoder

MOCK_RECORDS = [
    {
        "collectionIds": [],
        "deletedDate": None,
        "favorite": False,
        "fields": [
            {
                "linkedId": None,
                "name": "a_new_secret",
                "type": 1,
                "value": "this is a new secret"
            },
            {
                "linkedId": None,
                "name": "not so secret",
                "type": 0,
                "value": "not secret"
            }
        ],
        "folderId": "3b12a9da-7c49-40b8-ad33-aede017a7ead",
        "id": "90992f63-ddb6-4e76-8bfc-aede016ca5eb",
        "login": {
            "password": "passwordA3",
            "passwordRevisionDate": "2022-07-26T23:03:23.399Z",
            "totp": None,
            "username": "userA"
        },
        "name": "a_test",
        "notes": None,
        "object": "item",
        "organizationId": None,
        "passwordHistory": [
            {
                "lastUsedDate": "2022-07-26T23:03:23.405Z",
                "password": "a_new_secret: this is secret"
            },
            {
                "lastUsedDate": "2022-07-26T23:03:23.399Z",
                "password": "passwordA2"
            },
            {
                "lastUsedDate": "2022-07-26T22:59:52.885Z",
                "password": "passwordA"
            }
        ],
        "reprompt": 0,
        "revisionDate": "2022-07-26T23:03:23.743Z",
        "type": 1
    },
    {
        "collectionIds": [],
        "deletedDate": None,
        "favorite": False,
        "folderId": None,
        "id": "5ebd4d31-104c-49fc-a09c-aedf003d28ad",
        "login": {
            "password": "b",
            "passwordRevisionDate": None,
            "totp": None,
            "username": "a"
        },
        "name": "dupe_name",
        "notes": None,
        "object": "item",
        "organizationId": None,
        "reprompt": 0,
        "revisionDate": "2022-07-27T03:42:40.353Z",
        "type": 1
    },
    {
        "collectionIds": [],
        "deletedDate": None,
        "favorite": False,
        "folderId": None,
        "id": "90657653-6695-496d-9431-aedf003d3015",
        "login": {
            "password": "d",
            "passwordRevisionDate": None,
            "totp": None,
            "username": "c"
        },
        "name": "dupe_name",
        "notes": None,
        "object": "item",
        "organizationId": None,
        "reprompt": 0,
        "revisionDate": "2022-07-27T03:42:46.673Z",
        "type": 1
    }
]


class MockBitwarden(Bitwarden):

    unlocked = True

    def _run(self, args, stdin=None, expected_rc=0):
        try:
            collection_id = args[args.index('--collectionid') + 1]
        except ValueError:
            collection_id = None

        if args[0] == 'get':
            if args[1] == 'item':
                for item in MOCK_RECORDS:
                    if collection_id and collection_id not in item.get('collectionIds', []):
                        continue
                    if item.get('id') == args[2]:
                        return AnsibleJSONEncoder().encode(item), ''
            if args[1] == 'template':
                if args[2] == 'item':
                    return AnsibleJSONEncoder().encode({"passwordHistory": [], "revisionDate": None,
                                                        "creationDate": None, "deletedDate": None,
                                                        "organizationId": None, "collectionIds": None,
                                                        "folderId": None, "type": 1, "name": "Item name",
                                                        "notes": "Some notes about this item.", "favorite": False,
                                                        "fields": [], "login": None, "secureNote": None, "card": None,
                                                        "identity": None, "reprompt": 0}
                                                       ), ''
        if args[0] == 'list':
            if args[1] == 'items':
                return AnsibleJSONEncoder().encode(
                    [item for item in MOCK_RECORDS
                     if (collection_id is None or collection_id in item.get('collectionIds', [])) and
                        re.search(args[3], item.get('name'))
                     ]
                ), ''
        if args[0] == 'generate':
            return 'random_password', ''
        if args[0] == 'create':
            if args[1] == 'item':
                new_record = AnsibleJSONDecoder().decode(base64.b64decode(stdin).decode('UTF-8'))
                MOCK_RECORDS.append(new_record)
        if args[0] == 'edit':
            if args[1] == 'item':
                for record in MOCK_RECORDS:
                    if record.get('id') == args[2]:
                        record.update(AnsibleJSONDecoder().decode(base64.b64decode(stdin).decode('UTF-8')))
                        return AnsibleJSONEncoder().encode(record), ''

        return '[]', ''


class LoggedOutMockBitwarden(MockBitwarden):

    unlocked = False


class TestLookupModule(unittest.TestCase):

    def setUp(self):
        self.lookup = lookup_loader.get('community.general.bitwarden')

    @patch('ansible_collections.community.general.plugins.lookup.bitwarden._bitwarden', new=MockBitwarden())
    def test_bitwarden_plugin_no_match(self):
        # Entry 0, "a_test" of the test input should have no duplicates.
        self.assertEqual([], self.lookup.run(['not_here'], field='password')[0])

    @patch('ansible_collections.community.general.plugins.lookup.bitwarden._bitwarden', new=MockBitwarden())
    def test_bitwarden_plugin_fields(self):
        # Entry 0, "a_test" of the test input should have no duplicates.
        record = MOCK_RECORDS[0]
        record_name = record['name']
        for k, v in six.iteritems(record['login']):
            self.assertEqual([v],
                             self.lookup.run([record_name], field=k)[0])

    @patch('ansible_collections.community.general.plugins.lookup.bitwarden._bitwarden', new=MockBitwarden())
    def test_bitwarden_plugin_duplicates(self):
        # There are two records with name dupe_name; we need to be order-insensitive with
        # checking what was retrieved.
        self.assertEqual(set(['b', 'd']),
                         set(self.lookup.run(['dupe_name'], field='password')[0]))

    @patch('ansible_collections.community.general.plugins.lookup.bitwarden._bitwarden', new=MockBitwarden())
    def test_bitwarden_plugin_full_item(self):
        # Try to retrieve the full record of the first entry where the name is "a_name".
        self.assertEqual([MOCK_RECORDS[0]],
                         self.lookup.run(['a_test'])[0])

    @patch('ansible_collections.community.general.plugins.lookup.bitwarden._bitwarden', LoggedOutMockBitwarden())
    def test_bitwarden_plugin_unlocked(self):
        record = MOCK_RECORDS[0]
        record_name = record['name']
        with self.assertRaises(AnsibleError):
            self.lookup.run([record_name], field='password')

    def test_bitwarden_plugin_without_session_option(self):
        mock_bitwarden = MockBitwarden()
        with patch("ansible_collections.community.general.plugins.lookup.bitwarden._bitwarden", mock_bitwarden):
            record = MOCK_RECORDS[0]
            record_name = record['name']
            session = 'session'

            self.lookup.run([record_name], field=None)
            self.assertIsNone(mock_bitwarden.session)

    def test_bitwarden_plugin_session_option(self):
        mock_bitwarden = MockBitwarden()
        with patch("ansible_collections.community.general.plugins.lookup.bitwarden._bitwarden", mock_bitwarden):
            record = MOCK_RECORDS[0]
            record_name = record['name']
            session = 'session'

            self.lookup.run([record_name], field=None, bw_session=session)
            self.assertEqual(mock_bitwarden.session, session)

    @patch('ansible_collections.community.general.plugins.lookup.bitwarden._bitwarden', new=MockBitwarden())
    def test_bitwarden_plugin_create_record_with_generate(self):
        mock_records_length_before = len(MOCK_RECORDS)

        self.lookup.run(['b_test'], field='password', generate_if_missing='')
        self.assertEqual(len(MOCK_RECORDS), mock_records_length_before + 1)
        self.assertEqual(MOCK_RECORDS[-1].get('login', {}).get('password'), 'random_password')

    @patch('ansible_collections.community.general.plugins.lookup.bitwarden._bitwarden', new=MockBitwarden())
    def test_bitwarden_plugin_create_record_with_set(self):
        mock_records_length_before = len(MOCK_RECORDS)

        self.lookup.run(['b_test'], field='username', set='admin')
        self.assertEqual(len(MOCK_RECORDS), mock_records_length_before + 1)
        self.assertEqual(MOCK_RECORDS[-1].get('login', {}).get('username'), 'admin')

    @patch('ansible_collections.community.general.plugins.lookup.bitwarden._bitwarden', new=MockBitwarden())
    def test_bitwarden_plugin_update_record_with_new_customfield_generate(self):
        self.lookup.run(['a_test'], field='custom_field', generate_if_missing='--length 32')
        self.assertEqual(MOCK_RECORDS[0].get('fields', [{}])[-1].get('name'), 'custom_field')
        self.assertEqual(MOCK_RECORDS[0].get('fields', [{}])[-1].get('value'), 'random_password')

    @patch('ansible_collections.community.general.plugins.lookup.bitwarden._bitwarden', new=MockBitwarden())
    def test_bitwarden_plugin_update_record_with_new_customfield_set(self):
        self.lookup.run(['a_test'], field='custom_field', set='custom_value')
        custom_fields = dict([(field.get('name'), field.get('value')) for field in MOCK_RECORDS[0].get('fields', [])])
        self.assertIn('custom_field', custom_fields.keys())
        self.assertEqual(custom_fields['custom_field'], 'custom_value')

        self.lookup.run(['a_test'], field='another_custom_field', set='custom_value')
        custom_fields = dict([(field.get('name'), field.get('value')) for field in MOCK_RECORDS[0].get('fields', [])])
        self.assertIn('another_custom_field', custom_fields.keys())
        self.assertEqual(custom_fields['another_custom_field'], 'custom_value')

    @patch('ansible_collections.community.general.plugins.lookup.bitwarden._bitwarden', new=MockBitwarden())
    def test_bitwarden_plugin_update_record_with_existing_field_generate(self):
        mock_records_value_before = MOCK_RECORDS[0].get('login', {}).get('password')

        self.lookup.run(['a_test'], field='password', generate_if_missing='--length 32')
        self.assertEqual(MOCK_RECORDS[0].get('login', {}).get('password'), mock_records_value_before)

    @patch('ansible_collections.community.general.plugins.lookup.bitwarden._bitwarden', new=MockBitwarden())
    def test_bitwarden_plugin_generate_does_not_overwrite_existing_values(self):
        self.lookup.run(['a_test'], field='custom_field', set='fixed_value')
        self.assertEqual(MOCK_RECORDS[0].get('fields', [{}])[-1].get('name'), 'custom_field')
        self.assertEqual(MOCK_RECORDS[0].get('fields', [{}])[-1].get('value'), 'fixed_value')
        self.lookup.run(['a_test'], field='custom_field', generate_if_missing='--length 32')
        self.assertNotEqual(MOCK_RECORDS[0].get('fields', [{}])[-1].get('value'), 'random_value')

    @patch('ansible_collections.community.general.plugins.lookup.bitwarden._bitwarden', new=MockBitwarden())
    def test_bitwarden_plugin_set_does_overwrite_existing_values(self):
        self.lookup.run(['a_test'], field='custom_field', set='fixed_value')
        self.assertEqual(MOCK_RECORDS[0].get('fields', [{}])[-1].get('name'), 'custom_field')
        self.assertEqual(MOCK_RECORDS[0].get('fields', [{}])[-1].get('value'), 'fixed_value')
        self.lookup.run(['a_test'], field='custom_field', set='different_value')
        self.assertEqual(MOCK_RECORDS[0].get('fields', [{}])[-1].get('value'), 'different_value')
