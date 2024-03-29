# -*- coding: utf-8 -*-
# Copyright (c) 2022, Jonathan Lung <lungj@heresjono.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.community.general.tests.unit.compat import unittest
from ansible_collections.community.general.tests.unit.compat.mock import patch

from ansible.errors import AnsibleError
from ansible.module_utils import six
from ansible.plugins.loader import lookup_loader
from ansible_collections.community.general.plugins.lookup.bitwarden import Bitwarden

MOCK_COLLECTION_ID = "3b12a9da-7c49-40b8-ad33-aede017a7ead"

MOCK_RECORDS = [
    {
        "collectionIds": [
            MOCK_COLLECTION_ID
        ],
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
        "collectionIds": [
            MOCK_COLLECTION_ID
        ],
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
        "collectionIds": [
            MOCK_COLLECTION_ID
        ],
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

    def _get_matches(self, search_value=None, search_field="name", collection_id=None):
        if not search_value and collection_id:
            return list(filter(lambda record: collection_id in record['collectionIds'], MOCK_RECORDS))

        return list(filter(lambda record: record[search_field] == search_value, MOCK_RECORDS))


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
        with self.assertRaises(AnsibleError) as raised_error:
            self.lookup.run([record_name], field='password')

        self.assertEqual("Bitwarden Vault locked. Run 'bw unlock'.", str(raised_error.exception))

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
    def test_bitwarden_plugin_full_collection(self):
        # Try to retrieve the full records of the given collection.
        self.assertEqual(MOCK_RECORDS, self.lookup.run(None, collection_id=MOCK_COLLECTION_ID)[0])
