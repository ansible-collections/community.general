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
short_description: Manage GitHub access keys
description:
  - Creates, removes, or updates GitHub GPG keys.
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
      - GitHub OAuth or personal access token (classic) with the read:gpg_key, write:gpg_key, and admin:gpg_key scopes needed to manage GPG keys.
    required: true
    type: str
  name:
    description:
      - GPG key name
    required: true
    type: str
  armored_pubkey:
    description:
      - ASCII-armored GPG public key value. Required when O(state=present).
    type: str
  state:
    description:
      - Whether to remove a key, ensure that it exists, or update its value.
    choices: ['present', 'absent']
    default: 'present'
    type: str
  force:
    description:
      - The default is V(true), which will replace the existing remote key
        if it is different than O(pubkey). If V(false), the key will only be
        set if no key with the given O(name) exists.
    type: bool
    default: true

author: Austin Lucas Lake (@austinlucaslake)
'''

RETURN = '''
deleted_keys:
    description: An array of key objects that were deleted. Only present on state=absent
    type: list
    returned: When state=absent
    sample: [{
        "id": 1,
        "name": "EXAMPLE_NAME",
        "primary_key_id": 0,
        "key_id": "EXAMPLE_KEY_ID",
        "public_key": "EXAMPLE_PUBLIC_KEY",
        "emails": [{ "email": "example@email.com", "verified": True }],
        "subkeys": [],
        "can_sign": True,
        "can_encrypt_comms": False,
        "can_encrypt_storage": False,
        "can_certify": True,
        "created_at": "%Y-%m-%dT%H:%M:%SZ",
        "expires_at": "%Y-%m-%dT%H:%M:%SZ",
        "revoked": False,
        "raw_key": "ASCII-armored GPG public key"
    }]
matching_keys:
    description: An array of keys matching the specified name. Only present on state=present
    type: list
    returned: When state=present
    sample: [{
        "id": 1,
        "name": "EXAMPLE_NAME",
        "primary_key_id": 0,
        "key_id": "EXAMPLE_KEY_ID",
        "public_key": "EXAMPLE_PUBLIC_KEY",
        "emails": [{ "email": "example@email.com", "verified": True }],
        "subkeys": [],
        "can_sign": True,
        "can_encrypt_comms": False,
        "can_encrypt_storage": False,
        "can_certify": True,
        "created_at": "%Y-%m-%dT%H:%M:%SZ",
        "expires_at": "%Y-%m-%dT%H:%M:%SZ",
        "revoked": False,
        "raw_key": "ASCII-armored GPG public key"
    }]
key:
    description: Metadata about the key just created. Only present on state=present
    type: dict
    returned: success
    sample: {
        "id": 1,
        "name": "EXAMPLE_NAME",
        "primary_key_id": 0,
        "key_id": "EXAMPLE_KEY_ID",
        "public_key": "EXAMPLE_PUBLIC_KEY",
        "emails": [{ "email": "example@email.com", "verified": True }],
        "subkeys": [],
        "can_sign": True,
        "can_encrypt_comms": False,
        "can_encrypt_storage": False,
        "can_certify": True,
        "created_at": "%Y-%m-%dT%H:%M:%SZ",
        "expires_at": "%Y-%m-%dT%H:%M:%SZ",
        "revoked": False,
        "raw_key": "ASCII-armored GPG public key"
    }
'''

EXAMPLES = '''
- name: Read ASCII-armored GPG public key to authorize
  ansible.builtin.command:
    cmd: gpg --armor --export EXAMPLE_KEY_ID
  register: gpg_public_key

- name: Authorize key with GitHub
  community.general.github_gpg_key:
    name: Access Key for Some Machine
    token: '{{ github_access_token }}'
    armored_pubkey: '{{ gpg_public_key.stdout }}'
'''

import datetime
import json
import re

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url

from ansible_collections.community.general.plugins.module_utils.datetime import (
    now,
)


API_BASE = 'https://api.github.com'


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
            'Authorization': 'token %s' % self.token,
            'Content-Type': 'application/json',
            'Accept': 'application/vnd.github+json',
        }
        response, info = fetch_url(
            self.module, url, method=method, data=data, headers=headers)
        if not (200 <= info['status'] < 400):
            self.module.fail_json(
                msg=(" failed to send request %s to %s: %s"
                     % (method, url, info['msg'])))
        return GitHubResponse(response, info)


def get_all_keys(session):
    url = API_BASE + '/user/gpg_keys'
    result = []
    while url:
        r = session.request('GET', url)
        result.extend(r.json())
        url = r.links().get('next')
    return result


def create_key(session, name, armored_pubkey, check_mode):
    if check_mode:
        now_t = datetime.datetime.now()
        return {
            "id": 1,
            "name": name,
            "primary_key_id": 0,
            "key_id": "EXAMPLE_KEY_ID",
            "public_key": "EXAMPLE_PUBLIC_KEY",
            "emails": [
                {
                  "email": "example@email.com",
                  "verified": True
                }
            ],
            "subkeys": [],
            "can_sign": True,
            "can_encrypt_comms": False,
            "can_encrypt_storage": False,
            "can_certify": True,
            "created_at": datetime.strftime(now_t, '%Y-%m-%dT%H:%M:%SZ'),
            "expires_at": datetime.strftime(now_t, '%Y-%m-%dT%H:%M:%SZ'),
            "revoked": False,
            "raw_key": armored_pubkey
          }

    else:
        return session.request(
            'POST',
            API_BASE + '/user/gpg_keys',
            data=json.dumps({'name': name, 'raw_key': armored_pubkey})).json()


def delete_keys(session, to_delete, check_mode):
    if check_mode:
        return

    for key in to_delete:
        session.request('DELETE', API_BASE + '/user/gpg_keys/%s' % key["id"])


def ensure_key_absent(session, name, check_mode):
    to_delete = [key for key in get_all_keys(session) if key['name'] == name]
    delete_keys(session, to_delete, check_mode=check_mode)

    return {'changed': bool(to_delete),
            'deleted_keys': to_delete}


def ensure_key_present(module, session, name, armored_pubkey, force, check_mode):
    all_keys = get_all_keys(session)
    matching_keys = [k for k in all_keys if k['name'] == name]
    deleted_keys = []

    new_signature = armored_pubkey
    for key in all_keys:
        existing_signature = key['raw_key']
        if new_signature == existing_signature and key['name'] != name:
            module.fail_json(msg=(
                "another key with the same content is already registered "
                "under the name |{0}|").format(key['name']))

    if matching_keys and force and matching_keys[0]['raw_key'] != new_signature:
        delete_keys(session, matching_keys, check_mode=check_mode)
        (deleted_keys, matching_keys) = (matching_keys, [])

    if not matching_keys:
        key = create_key(session, name, armored_pubkey, check_mode=check_mode)
    else:
        key = matching_keys[0]

    return {
        'changed': bool(deleted_keys or not matching_keys),
        'deleted_keys': deleted_keys,
        'matching_keys': matching_keys,
        'key': key
    }


def main():
    argument_spec = {
        'token': {'required': True, 'no_log': True},
        'name': {'required': True},
        'armored_pubkey': {},
        'state': {'choices': ['present', 'absent'], 'default': 'present'},
        'force': {'default': True, 'type': 'bool'},
    }
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    token = module.params['token']
    name = module.params['name']
    state = module.params['state']
    force = module.params['force']
    armored_pubkey = module.params.get('armored_pubkey')

    if armored_pubkey:
        armored_pubkey_parts = armored_pubkey.split('\r\n')
        armored_pubkey_start = '-----BEGIN PGP PUBLIC KEY BLOCK-----'
        armored_pubkey_end = '-----END PGP PUBLIC KEY BLOCK-----'
        if armored_pubkey_parts[0] != armored_pubkey_start or \
            armored_pubkey_parts[-1] != armored_pubkey_end:
            module.fail_json(msg='"armored_pubkey" parameter has an invalid format')
    elif state == 'present':
        module.fail_json(msg='"armored_pubkey" is required when state=present')

    session = GitHubSession(module, token)
    if state == 'present':
        result = ensure_key_present(module, session, name, armored_pubkey, force=force, check_mode=module.check_mode)
    elif state == 'absent':
        result = ensure_key_absent(session, name, check_mode=module.check_mode)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
