#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2024, Austin Lucas Lake <53884490+austinlucaslake@users.noreply.github.com>
# Based on community.general.github_key module by Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
module: github_gpg_key
author: Austin Lucas Lake (@austinlucaslake)
short_description: Manage GitHub GPG keys
version_added: 9.0.0
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
    required: true
    type: str
  armored_public_key:
    description:
      - ASCII-armored GPG public key value. Required when O(state=present).
    type: str
  state:
    description:
      - Whether to remove a key, ensure that it exists, or update its value.
    choices: [ 'present', 'absent' ]
    default: 'present'
    type: str
  force:
    description:
      - The default is V(true), which will replace the existing remote key
        if it is different than O(pubkey). If V(false), the key will only be
        set if no key with the given O(name) exists.
    type: bool
    default: true
'''

RETURN = '''
deleted_keys:
    description: An array of key objects that were deleted. Only present on state=absent
    type: list
    elements: dict
    returned: When O(state=absent)
    sample: [{
        'id': 3,
        'name': 'Octocat's GPG Key',
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
    }]
matching_keys:
    description: An array of keys matching the specified name. Only present on state=present
    type: list
    elements: dict
    returned: When O(state=present)
    sample: [{
        'id': 3,
        'name': 'Octocat's GPG Key',
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
    }]
key:
    description: Metadata about the key just created. Only present on state=present
    type: dict
    returned: When O(state=present)
    sample: {
        'id': 3,
        'name': 'Octocat's GPG Key',
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
- name: Authorize key with GitHub
  community.general.github_gpg_key:
    name: My GPG Key
    token: '{{ token }}'
    armored_public_key: '{{ armored_public_key }}'
'''

import json
import re

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url

from ansible_collections.community.general.plugins.module_utils.datetime import now


API_BASE = 'https://api.github.com/user/gpg_keys'


class GitHubResponse(object):
    def __init__(self, response, info):
        self.content = response.read()
        self.info = info

    def json(self):
        return json.loads(self.content)

    def links(self):
        links = {}
        if 'link' in self.info:
            link_header = self.info['link']
            matches = re.findall('<([^>]+)>; rel="([^"]+)"', link_header)
            for url, rel in matches:
                links[rel] = url
        return links


class GitHubSession(object):
    def __init__(self, module, token):
        self.module = module
        self.token = token

    def request(self, method, url, data=None):
        headers = {
            'Authorization': 'token {}'.format(self.token),
            'Content-Type': 'application/json',
            'Accept': 'application/vnd.github.v3+json'
        }
        response, info = fetch_url(
            self.module, url, method=method, data=data, headers=headers)
        if not (200 <= info['status'] < 400):
            self.module.fail_json('failed to send request {0} to {1}: {2}'.format(method, url, info['msg']))
        return GitHubResponse(response, info)


def get_all_keys(session):
    url = API_BASE
    result = []
    while url:
        r = session.request('GET', url)
        result.extend(r.json())
        url = r.links().get('next')
    return result


def create_key(session, name, armored_public_key, check_mode):
    if check_mode:
        now_t = now()
        return {
            'id': 3,
            'name': name,
            'primary_key_id': 2,
            'key_id': '3262EFF25BA0D270',
            'public_key': 'xsBNBFayYZ...',
            'emails': [{
                'email': 'octocat@users.noreply.github.com',
                'verified': True
            }],
            'subkeys': [{
                'id': 4,
                'primary_key_id': 3,
                'key_id': '4A595D4C72EE49C7',
                'public_key': 'zsBNBFayYZ...',
                'emails': [],
                'can_sign': False,
                'can_encrypt_comms': True,
                'can_encrypt_storage': True,
                'can_certify': False,
                'created_at': now_t.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'expires_at': None,
                'revoked': False
            }],
            'can_sign': True,
            'can_encrypt_comms': False,
            'can_encrypt_storage': False,
            'can_certify': True,
            'created_at': now_t.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'expires_at': None,
            'revoked': False,
            'raw_key': armored_public_key
        }
    else:
        return session.request(
            'POST',
            API_BASE,
            data=json.dumps({'name': name, 'raw_key': armored_public_key})).json()


def delete_keys(session, to_delete, check_mode):
    if check_mode:
        return

    for key in to_delete:
        session.request('DELETE', API_BASE + '/' + key['id'])


def ensure_key_absent(session, name, check_mode):
    to_delete = [key for key in get_all_keys(session) if key['name'] == name]
    delete_keys(session, to_delete, check_mode=check_mode)

    return {'changed': bool(to_delete),
            'deleted_keys': to_delete}


def ensure_key_present(module, session, name, armored_public_key, force, check_mode):
    all_keys = get_all_keys(session)
    matching_keys = [k for k in all_keys if k['name'] == name]
    deleted_keys = []

    new_signature = armored_public_key
    for key in all_keys:
        existing_signature = key['raw_key']
        if new_signature == existing_signature and key['name'] != name:
            module.fail_json('Another key with the same content is already registered under the name |{0}|'.format(key['title']))

    if matching_keys and force and matching_keys[0]['raw_key'] != new_signature:
        delete_keys(session, matching_keys, check_mode=check_mode)
        deleted_keys, matching_keys = matching_keys, []

    if not matching_keys:
        key = create_key(session, name, armored_public_key, check_mode=check_mode)
    else:
        key = matching_keys[0]

    return {
        'changed': bool(deleted_keys or not matching_keys),
        'deleted_keys': deleted_keys,
        'matching_keys': matching_keys,
        'key': key
    }


def validate_key(module, armored_public_key):
    armored_public_key_parts = armored_public_key.splitlines()
    if armored_public_key_parts[0] != '-----BEGIN PGP PUBLIC KEY BLOCK-----' or armored_public_key_parts[-1] != '-----END PGP PUBLIC KEY BLOCK-----':
        module.fail_json(msg='"armored_public_key" parameter has an invalid format')


def run_module(module, params, check_mode):
    session = GitHubSession(module, params['token'])
    if params['state'] == 'present':
        validate_key(module, params['armored_public_key'])
        result = ensure_key_present(module, session, params['name'], params['armored_public_key'], params['force'], check_mode)
    else:
        result = ensure_key_absent(session, params['name'], check_mode)
    return result


def main():
    module = AnsibleModule(
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
    )

    try:
        result = run_module(
            module=module,
            params=module.params,
            check_mode=module.check_mode
        )
        module.exit_json(**result)
    except Exception as e:
        module.fail_json(str(e))


if __name__ == '__main__':
    main()
