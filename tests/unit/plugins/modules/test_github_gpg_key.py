# Copyright (c) 2024-2025, Austin Lucas Lake <git@austinlucaslake.com>
# Based on tests/unit/plugins/modules/test_github_repo.py by Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import datetime
from httmock import with_httmock, urlmatch, response
from ansible_collections.community.general.tests.unit.compat import unittest
from ansible_collections.community.general.plugins.modules import github_gpg_key

GITHUB_MINIMUM_PYTHON_VERSION = (2, 7)


@urlmatch(netloc=r'.*')
def debug_mock(url, request):
    print(request.original.__dict__)


@urlmatch(netloc=r'api\.github\.com(:[0-9]+)?$', path=r'/user/gpg_keys', method="post")
def create_gpg_key_mock(url, request):
    gpg_key = json.loads(request.body)

    now_t = datetime.datetime.now()

    headers = {'content-type': 'application/json'}
    # https://docs.github.com/en/rest/reference/repos#create-a-repository-for-the-authenticated-user
    content = {
        "id": 3,
        "name": gpg_key.get("name"),
        "primary_key_id": 2,
        "key_id": "3262EFF25BA0D270",
        "public_key": "xsBNBFayYZ...",
        "emails": [{
            "email": "octocat@users.noreply.github.com",
            "verified": True
        }],
        "subkeys": [{
            "id": 4,
            "primary_key_id": 3,
            "key_id": "4A595D4C72EE49C7",
            "public_key": "zsBNBFayYZ...",
            "emails": [],
            "can_sign": False,
            "can_encrypt_comms": True,
            "can_encrypt_storage": True,
            "can_certify": False,
            "created_at": now_t.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "expires_at": None,
            "revoked": False
        }],
        "can_sign": True,
        "can_encrypt_comms": False,
        "can_encrypt_storage": False,
        "can_certify": True,
        "created_at": now_t.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "expires_at": None,
        "revoked": False,
        "raw_key": gpg_key.get("armored_public_key")
    }
    content = json.dumps(content).encode("utf-8")
    return response(201, content, headers, None, 5, request)


@urlmatch(netloc=r'api\.github\.com(:[0-9]+)?$', path=r'/user/gpg_keys/.*', method="delete")
def delete_gpg_key_mock(url, request):
    # https://docs.github.com/en/rest/users/gpg-keys#delete-a-gpg-key-for-the-authenticated-user
    return response(200, None, None, None, 5, request)


class TestGithubGPGKey(unittest.TestCase):
    def setUp(self):
        self.token = "github_access_token"
        self.name = "GPG public key"
        self.armored_public_key = "-----BEGIN PGP PUBLIC KEY BLOCK-----\r\n\n\nMy ASCII-armored GPG public key\r\n-----END PGP PUBLIC KEY BLOCK-----"
        self.gpg_key_id = 123456789

    @with_httmock(create_gpg_key_mock)
    def test_create_gpg_key(self):
        result = github_gpg_key.run_module(
            params=dict(
                state="present",
                token=self.token,
                name=self.name,
                armored_public_key=self.armored_public_key
            )
        )
        self.assertEqual(result['changed'], True)
        self.assertEqual(result['key']['name'], self.name)
        self.assertEqual(result['key']['raw_key'], self.armored_public_key)

    @with_httmock(delete_gpg_key_mock)
    def test_delete_gpg_key(self):
        result = github_gpg_key.run_module(
            module=self.module,
            params=dict(
                state="absent",
                token=self.token,
                gpg_key_id=self.gpg_key_id
            )
        )
        self.assertEqual(result['changed'], True)
        self.assertEqual(result['key']['gpg_key_id'], self.gpg_key_id)

if __name__ == "__main__":
    unittest.main()
