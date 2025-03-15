#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2024-2025, Austin Lucas Lake <git@austinlucaslake.com>
# Based on community.general.github_key module by Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
module: github_gpg_key
author: Austin Lucas Lake (@austinlucaslake)
short_description: Manage GitHub GPG keys
version_added: 10.5.0
description:
  - Creates or removes GitHub GPG keys for an authenticated user.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  token:
    description:
      - GitHub OAuth or personal access token (classic) with the C(read:gpg_key), C(write:gpg_key), and C(admin:gpg_key) scopes needed to manage GPG keys.
    required: true
    type: str
  name:
    description:
      - GPG key name
    type: str
  armored_public_key:
    description:
      - ASCII-armored GPG public key value. Required when O(state=present).
    type: str
  gpg_key_id:
    description:
      - GPG key id. Required when O(state=absent).
    type: int
  state:
    description:
      - Whether to remove a key, ensure that it exists, or update its value.
    choices: [ 'present', 'absent' ]
    default: 'present'
    type: str
'''

RETURN = '''
deleted_key:
    description: A GPG key that was deleted from GitHub. Only present on O(state=absent).
    type: list
    elements: dict
    returned: changed or success 
    sample: {
        'id': 3,
        'name': "Octocat's GPG Key",
        'primary_key_id': 2,
        'key_id': '3262EFF25BA0D270',
        'public_key': 'xsBNBFayYZ...',
        'emails': [{
            'email': 'octocat@users.noreply.github.com',
            'verified': true
        }],
        'subkeys': [{
            'id': 4,
            'primary_key_id': 3,
            'key_id': '4A595D4C72EE49C7',
            'public_key': 'zsBNBFayYZ...',
            'emails': [],
            'can_sign': false,
            'can_encrypt_comms': true,
            'can_encrypt_storage': true,
            'can_certify': false,
            'created_at': '2016-03-24T11:31:04-06:00',
            'expires_at': '2016-03-24T11:31:04-07:00',
            'revoked': false
        }],
        'can_sign': true,
        'can_encrypt_comms': false,
        'can_encrypt_storage': false,
        'can_certify': true,
        'created_at': '2016-03-24T11:31:04-06:00',
        'expires_at': '2016-03-24T11:31:04-07:00',
        'revoked': false,
        'raw_key': 'string'
    }
matching_key:
    description: A matching GPG key found on GitHub. Only present when O(state=present) and no new key is created.
    type: dict
    returned: not changed
    sample: {
        'id': 3,
        'name': "Octocat's GPG Key",
        'primary_key_id': 2,
        'key_id': '3262EFF25BA0D270',
        'public_key': 'xsBNBFayYZ...',
        'emails': [{
            'email': 'octocat@users.noreply.github.com',
            'verified': true
        }],
        'subkeys': [{
            'id': 4,
            'primary_key_id': 3,
            'key_id': '4A595D4C72EE49C7',
            'public_key': 'zsBNBFayYZ...',
            'emails': [],
            'can_sign': false,
            'can_encrypt_comms': true,
            'can_encrypt_storage': true,
            'can_certify': false,
            'created_at': '2016-03-24T11:31:04-06:00',
            'expires_at': '2016-03-24T11:31:04-07:00',
            'revoked': false
        }],
        'can_sign': true,
        'can_encrypt_comms': false,
        'can_encrypt_storage': false,
        'can_certify': true,
        'created_at': '2016-03-24T11:31:04-06:00',
        'expires_at': '2016-03-24T11:31:04-07:00',
        'revoked': false,
        'raw_key': 'string'
    }
new_key:
    description: A new GPG key that was added to GitHub. Only present on O(state=present).
    type: dict
    returned: changed or success
    sample: {
        'id': 3,
        'name': "Octocat's GPG Key",
        'primary_key_id': 2,
        'key_id': '3262EFF25BA0D270',
        'public_key': 'xsBNBFayYZ...',
        'emails': [{
            'email': 'octocat@users.noreply.github.com',
            'verified': true
        }],
        'subkeys': [{
            'id': 4,
            'primary_key_id': 3,
            'key_id': '4A595D4C72EE49C7',
            'public_key': 'zsBNBFayYZ...',
            'emails': [],
            'can_sign': false,
            'can_encrypt_comms': true,
            'can_encrypt_storage': true,
            'can_certify': False,
            'created_at': '2016-03-24T11:31:04-06:00',
            'expires_at': '2016-03-24T11:31:04-07:00',
            'revoked': false
        }],
        'can_sign': true,
        'can_encrypt_comms': false,
        'can_encrypt_storage': false,
        'can_certify': true,
        'created_at': '2016-03-24T11:31:04-06:00',
        'expires_at': '2016-03-24T11:31:04-07:00',
        'revoked': false,
        'raw_key': 'string'
    }
'''

EXAMPLES = '''
- name: Add GitHub GPG key
  community.general.github_gpg_key:
    state: present
    token: '{{ token }}'
    name: My GPG Key
    armored_public_key: '{{ armored_public_key }}'

- name: Delete GitHub GPG key
  community.general.github_gpg_key:
    state: absent
    token: '{{ token }}'
    gpg_key_id: '{{ gpg_key_id }}'
'''

import json
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import open_url


GITHUB_GPG_REST_API_URL = 'https://api.github.com/user/gpg_keys'


def ensure_gpg_key_absent(headers, gpg_key_id, check_mode):
    changed = False
    deleted_key = {}

    method = 'GET' if check_mode else 'DELETE'
    response = open_url(
        url=GITHUB_GPG_REST_API_URL+'/'+gpg_key_id,
        method=method,
        headers=headers
    )
    if response.status == 200:
        changed = True
        deleted_key = json.loads(response.read())

    return {
        'changed': changed,
        'deleted_key': deleted_key
    }


def ensure_gpg_key_present(headers, name, armored_public_key, check_mode):
    changed = False
    matching_key = {}
    new_key = {}

    armored_public_key_parts = armored_public_key.splitlines()
    if (armored_public_key_parts[0] != '-----BEGIN PGP PUBLIC KEY BLOCK-----') \
        or (armored_public_key_parts[-1] != '-----END PGP PUBLIC KEY BLOCK-----'):
        raise Exception('GPG key must have ASCII armor')

    response = open_url(
        url=GITHUB_GPG_REST_API_URL,
        method='GET',
        headers=headers
    )
    if response.status != 200:
        raise Exception(
            "Failed to check for matching GPG key: {} {}"
            .format(response.status, response.reason)
        )

    keys = json.loads(response.read())
    for key in keys:
        if key['raw_key'] == armored_public_key:
            matching_key = key
            break

    if not matching_key:
        response = open_url(
            url=GITHUB_GPG_REST_API_URL,
            method='POST',
            data={'name': name, 'armored_public_key': armored_public_key},
            headers=headers
        )
        if response.status != 201:
            raise Exception(
                "Failed to create GPG key: {} {}"
                .format(response.status, response.reason)
            )

        changed = True
        new_key = json.loads(response.json())
        if check_mode and new_key:
            response = open_url(
                url=GITHUB_GPG_REST_API_URL+'/'+new_key['key_id'],
                method='DELETE',
                headers=headers
            )
            if response.status != 200:
                raise Exception(
                    "Failed to undo changes (check_mode=true): {} {}"
                    .format(response.status, response.reason)
                )

    return {
        'changed': changed,
        'matching_key': matching_key,
        'new_key': new_key 
    }

def run_module(params, check_mode):
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': 'Bearer {}'.format(params['token']),
        'X-GitHub-Api-Version': '2022-11-28',
    }
    if params['state'] == 'present':
        result = ensure_gpg_key_present(
            headers,
            params['name'],
            params['armored_public_key'],
            check_mode
        )
    else:
        result = ensure_gpg_key_absent(
            headers,
            params['gpg_key_id'],
            check_mode
        )
    return result


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str', default='present', choices=['present', 'absent']),
            token=dict(type='str', required=True, no_log=True),
            name=dict(type='str', no_log=True),
            armored_public_key=dict(type='str', no_log=True),
            gpg_key_id=dict(type='int', no_log=True)
        ),
        supports_check_mode=True,
        required_if=[
            ['state', 'present', ['armored_public_key']],
            ['state', 'absent', ['gpg_key_id']],
        ]
    )

    try:
        result = run_module(
            module=module,
            params=module.params,
            check_mode=module.check_mode
        )
        module.exit_json(**result)
    except Exception as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
