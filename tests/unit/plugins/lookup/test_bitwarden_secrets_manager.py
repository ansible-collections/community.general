# -*- coding: utf-8 -*-
# Copyright (c) 2023, jantari (https://github.com/jantari)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import json
from ansible_collections.community.internal_test_tools.tests.unit.compat import unittest
from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import patch

from ansible.errors import AnsibleLookupError
from ansible.plugins.loader import lookup_loader
from ansible_collections.community.general.plugins.lookup.bitwarden_secrets_manager import BitwardenSecretsManager


MOCK_SECRETS = [
    {
        "object": "secret",
        "id": "ababc4a8-c242-4e54-bceb-77d17cdf2e07",
        "organizationId": "3c33066c-a0bf-4e70-9a3c-24cda6aaddd5",
        "projectId": "81869439-bfe5-442f-8b4e-b172e68b0ab2",
        "key": "TEST_SECRET",
        "value": "1234supersecret5678",
        "note": "A test secret to use when developing the ansible bitwarden_secrets_manager lookup plugin",
        "creationDate": "2023-04-23T13:13:37.7507017Z",
        "revisionDate": "2023-04-23T13:13:37.7507017Z"
    },
    {
        "object": "secret",
        "id": "d4b7c8fa-fc95-40d7-a13c-6e186ee69d53",
        "organizationId": "3c33066c-a0bf-4e70-9a3c-24cda6aaddd5",
        "projectId": "81869439-bfe5-442f-8b4e-b172e68b0ab2",
        "key": "TEST_SECRET_2",
        "value": "abcd_such_secret_very_important_efgh",
        "note": "notes go here",
        "creationDate": "2023-04-23T13:26:44.0392906Z",
        "revisionDate": "2023-04-23T13:26:44.0392906Z"
    }
]


class MockBitwardenSecretsManager(BitwardenSecretsManager):

    def _run(self, args, stdin=None):
        # mock the --version call
        if args[0] == "--version":
            return "bws 1.0.0", "", 0

        # secret_id is the last argument passed to the bws CLI
        secret_id = args[-1]
        rc = 1
        out = ""
        err = ""
        found_secrets = list(filter(lambda record: record["id"] == secret_id, MOCK_SECRETS))

        if len(found_secrets) == 0:
            err = "simulated bws CLI error: 404 no secret with such id"
        elif len(found_secrets) == 1:
            rc = 0
            # The real bws CLI will only ever return one secret / json object for the "get secret <secret-id>" command
            out = json.dumps(found_secrets[0])
        else:
            # This should never happen unless there's an error in the test MOCK_SECRETS.
            # The real Bitwarden Secrets Manager assigns each secret a unique ID.
            raise ValueError("More than 1 secret found with id: '{0}'. Impossible!".format(secret_id))

        return out, err, rc


class TestLookupModule(unittest.TestCase):

    def setUp(self):
        self.lookup = lookup_loader.get('community.general.bitwarden_secrets_manager')

    @patch('ansible_collections.community.general.plugins.lookup.bitwarden_secrets_manager._bitwarden_secrets_manager', new=MockBitwardenSecretsManager())
    def test_bitwarden_secrets_manager(self):
        # Getting a secret by its id should return the full secret info
        self.assertEqual([MOCK_SECRETS[0]], self.lookup.run(['ababc4a8-c242-4e54-bceb-77d17cdf2e07'], bws_access_token='123'))

    @patch('ansible_collections.community.general.plugins.lookup.bitwarden_secrets_manager._bitwarden_secrets_manager', new=MockBitwardenSecretsManager())
    def test_bitwarden_secrets_manager_no_match(self):
        # Getting a nonexistent secret id throws exception
        with self.assertRaises(AnsibleLookupError):
            self.lookup.run(['nonexistant_id'], bws_access_token='123')
