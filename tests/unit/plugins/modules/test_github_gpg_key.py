# Copyright (c) 2024-2025, Austin Lucas Lake, <git@austinlucaslake.com>
# Based on tests/unit/plugins/modules/test_github_repo.py by Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import datetime
from httmock import with_httmock, urlmatch, response
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.tests.unit.compat import unittest
from ansible_collections.community.general.plugins.modules import github_gpg_key

GITHUB_MINIMUM_PYTHON_VERSION = (2, 7)


@urlmatch(netloc=r'.*')
def debug_mock(url, request):
    print(request.original.__dict__)


@urlmatch(netloc=r'api\.github\.com(:[0-9]+)?$', path=r'/user/gpg_keys', method="get")
def list_gpg_keys_mock(url, request):
    # https://docs.github.com/en/rest/reference/repos#get-a-repository
    headers = {'content-type': 'application/json'}
    content = [{
        "id": 3,
        "name": "Octocat's GPG Key",
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
            "created_at": "2016-03-24T11:31:04-06:00",
            "expires_at": "2016-03-24T11:31:04-07:00",
            "revoked": False
        }],
        "can_sign": True,
        "can_encrypt_comms": False,
        "can_encrypt_storage": False,
        "can_certify": True,
        "created_at": "2016-03-24T11:31:04-06:00",
        "expires_at": "2016-03-24T11:31:04-07:00",
        "revoked": False,
        "raw_key": "string"
    }]

    content = json.dumps(content).encode("utf-8")
    return response(200, content, headers, None, 5, request)


@urlmatch(netloc=r'api\.github\.com(:[0-9]+)?$', path=r'/user/gpg_keys', method="post")
def create_gpg_key_mock(url, request):
    gpg_key = json.loads(request.body)

    now_t = datetime.datetime.now()

    headers = {'content-type': 'application/json'}
    # https://docs.github.com/en/rest/reference/repos#create-a-repository-for-the-authenticated-user
    content = {
        "id": 3,
        "name": gpg_key["name"],
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
    return response(204, None, None, None, 5, request)


@urlmatch(netloc=r'api\.github\.com(:[0-9]+)?$', path=r'/user/gpg_keys/.*', method="delete")
def delete_gpg_key_notfound_mock(url, request):
    # https://docs.github.com/en/rest/users/gpg-keys#delete-a-gpg-key-for-the-authenticated-user
    return response(404, "{\"message\": \"Not Found\"}", "", "Not Found", 5, request)


class TestGithubRepo(unittest.TestCase):
    def setUp(self):
<<<<<<< Updated upstream
        self.module = AnsibleModule(
            argument_spec=dict(
                state=dict(type='str', default='present', choice=['present', 'absent']),
                token=dict(type='str', required=True, no_log=True),
                name=dict(type='str', required=True),
                armored_public_key=dict(type='str', no_log=True),
                force=dict(type='bool', default=True)
            ),
            supports_check_mode=True,
            required_if=[
                ['state', 'present', ['armored_public_key']],
            ]
=======
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
            ),
            check_mode=False
>>>>>>> Stashed changes
        )

    @with_httmock(list_gpg_keys_mock)
    @with_httmock(create_gpg_key_mock)
    def test_create_gpg_key_repo(self):
        result = github_gpg_key.run_module(
            params=dict(
<<<<<<< Updated upstream
                token="github_access_token",
                name="GPG public key",
                armored_public_key="-----BEGIN PGP PUBLIC KEY BLOCK-----\r\n\n\nMy ASCII-armored GPG public key\r\n-----END PGP PUBLIC KEY BLOCK-----",
                state="present",
                force=True
            )
=======
                state="absent",
                token=self.token,
                gpg_key_id=self.gpg_key_id
            ),
            check_mode=False
>>>>>>> Stashed changes
        )
        self.assertEqual(result['changed'], True)
        self.assertEqual(result['key']['name'], 'GPG public key')

    @with_httmock(list_gpg_keys_mock)
    @with_httmock(delete_gpg_key_mock)
    def test_delete_user_repo(self):
        result = github_gpg_key.run_module(
            module=self.module,
            params=dict(
                token="github_access_token",
                name="GPG public key",
                armored_public_key="-----BEGIN PGP PUBLIC KEY BLOCK-----\r\n\n\nMy ASCII-armored GPG public key\r\n-----END PGP PUBLIC KEY BLOCK-----",
                state="absent",
                force=True
            )
        )
        self.assertEqual(result['changed'], True)

    @with_httmock(list_gpg_keys_mock)
    @with_httmock(delete_gpg_key_notfound_mock)
    def test_delete_gpg_key_notfound(self):
        result = github_gpg_key.run_module(
            module=self.module,
            params=dict(
                token="github_access_token",
                name="GPG public key",
                armored_public_key="-----BEGIN PGP PUBLIC KEY BLOCK-----\r\n\n\nMy ASCII-armored GPG public key\r\n-----END PGP PUBLIC KEY BLOCK-----",
                state="absent",
                force=True
            )
        )
        self.assertEqual(result['changed'], False)



if __name__ == "__main__":
    unittest.main()
