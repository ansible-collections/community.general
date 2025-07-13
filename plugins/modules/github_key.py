#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r"""
module: github_key
short_description: Manage GitHub access keys
description:
  - Creates, removes, or updates GitHub access keys.
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
      - GitHub Access Token with permission to list and create public keys.
    required: true
    type: str
  name:
    description:
      - SSH key name.
    required: true
    type: str
  pubkey:
    description:
      - SSH public key value. Required when O(state=present).
    type: str
  state:
    description:
      - Whether to remove a key, ensure that it exists, or update its value.
    choices: ['present', 'absent']
    default: 'present'
    type: str
  force:
    description:
      - The default is V(true), which replaces the existing remote key if it is different than O(pubkey). If V(false), the
        key is only set if no key with the given O(name) exists.
    type: bool
    default: true

author: Robert Estelle (@erydo)
"""

RETURN = r"""
deleted_keys:
  description: An array of key objects that were deleted. Only present on state=absent.
  type: list
  returned: When state=absent
  sample:
    [
      {
        "id": 0,
        "key": "BASE64 encoded key",
        "url": "http://example.com/github key",
        "created_at": "YYYY-MM-DDTHH:MM:SZ",
        "read_only": false
      }
    ]
matching_keys:
  description: An array of keys matching the specified name. Only present on state=present.
  type: list
  returned: When state=present
  sample:
    [
      {
        "id": 0,
        "key": "BASE64 encoded key",
        "url": "http://example.com/github key",
        "created_at": "YYYY-MM-DDTHH:MM:SZ",
        "read_only": false
      }
    ]
key:
  description: Metadata about the key just created. Only present on state=present.
  type: dict
  returned: success
  sample:
    {
      "id": 0,
      "key": "BASE64 encoded key",
      "url": "http://example.com/github key",
      "created_at": "YYYY-MM-DDTHH:MM:SZ",
      "read_only": false
    }
"""

EXAMPLES = r"""
- name: Read SSH public key to authorize
  ansible.builtin.shell: cat /home/foo/.ssh/id_rsa.pub
  register: ssh_pub_key

- name: Authorize key with GitHub
  local_action:
    module: github_key
    name: Access Key for Some Machine
    token: '{{ github_access_token }}'
    pubkey: '{{ ssh_pub_key.stdout }}'

# Alternatively, a single task can be used reading a key from a file on the controller
- name: Authorize key with GitHub
  community.general.github_key:
    name: Access Key for Some Machine
    token: '{{ github_access_token }}'
    pubkey: "{{ lookup('ansible.builtin.file', '/home/foo/.ssh/id_rsa.pub') }}"
"""

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
            'Accept': 'application/vnd.github.v3+json',
        }
        response, info = fetch_url(
            self.module, url, method=method, data=data, headers=headers)
        if not (200 <= info['status'] < 400):
            self.module.fail_json(
                msg=(" failed to send request %s to %s: %s"
                     % (method, url, info['msg'])))
        return GitHubResponse(response, info)


def get_all_keys(session):
    url = API_BASE + '/user/keys'
    result = []
    while url:
        r = session.request('GET', url)
        result.extend(r.json())
        url = r.links().get('next')
    return result


def create_key(session, name, pubkey, check_mode):
    if check_mode:
        now_t = now()
        return {
            'id': 0,
            'key': pubkey,
            'title': name,
            'url': 'http://example.com/CHECK_MODE_GITHUB_KEY',
            'created_at': datetime.datetime.strftime(now_t, '%Y-%m-%dT%H:%M:%SZ'),
            'read_only': False,
            'verified': False
        }
    else:
        return session.request(
            'POST',
            API_BASE + '/user/keys',
            data=json.dumps({'title': name, 'key': pubkey})).json()


def delete_keys(session, to_delete, check_mode):
    if check_mode:
        return

    for key in to_delete:
        session.request('DELETE', API_BASE + '/user/keys/%s' % key["id"])


def ensure_key_absent(session, name, check_mode):
    to_delete = [key for key in get_all_keys(session) if key['title'] == name]
    delete_keys(session, to_delete, check_mode=check_mode)

    return {'changed': bool(to_delete),
            'deleted_keys': to_delete}


def ensure_key_present(module, session, name, pubkey, force, check_mode):
    all_keys = get_all_keys(session)
    matching_keys = [k for k in all_keys if k['title'] == name]
    deleted_keys = []

    new_signature = pubkey.split(' ')[1]
    for key in all_keys:
        existing_signature = key['key'].split(' ')[1]
        if new_signature == existing_signature and key['title'] != name:
            module.fail_json(msg=(
                "another key with the same content is already registered "
                "under the name |{0}|").format(key['title']))

    if matching_keys and force and matching_keys[0]['key'].split(' ')[1] != new_signature:
        delete_keys(session, matching_keys, check_mode=check_mode)
        (deleted_keys, matching_keys) = (matching_keys, [])

    if not matching_keys:
        key = create_key(session, name, pubkey, check_mode=check_mode)
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
        'pubkey': {},
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
    pubkey = module.params.get('pubkey')

    if pubkey:
        pubkey_parts = pubkey.split(' ')
        # Keys consist of a protocol, the key data, and an optional comment.
        if len(pubkey_parts) < 2:
            module.fail_json(msg='"pubkey" parameter has an invalid format')
    elif state == 'present':
        module.fail_json(msg='"pubkey" is required when state=present')

    session = GitHubSession(module, token)
    if state == 'present':
        result = ensure_key_present(module, session, name, pubkey, force=force,
                                    check_mode=module.check_mode)
    elif state == 'absent':
        result = ensure_key_absent(session, name, check_mode=module.check_mode)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
