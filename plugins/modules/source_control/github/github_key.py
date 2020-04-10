#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# Copyright: (c) 2020, Andrea Tartaglia <andrea@braingap.uk>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}


DOCUMENTATION = r"""
module: github_key
short_description: Manage GitHub access keys.
description:
    - Creates, removes, or updates GitHub access keys.
options:
  name:
    description:
      - SSH key name
    required: true
    type: str
  pubkey:
    description:
      - SSH public key value. Required when C(state=present).
    type: str
  state:
    description:
      - Whether to remove a key, ensure that it exists, or update its value.
    choices: ['present', 'absent']
    default: 'present'
    type: str
  force:
    description:
      - The default is C(yes), which will replace the existing remote key
        if it's different than C(pubkey). If C(no), the key will only be
        set if no key with the given C(name) exists.
    type: bool
    default: 'yes'

extends_documentation_fragment: community.general.github
author: Robert Estelle (@erydo)
"""

RETURN = r"""
deleted_keys:
    description: An array of key objects that were deleted. Only present on state=absent
    type: list
    returned: When state=absent
    sample: [{'id': 0, 'key': 'BASE64 encoded key', 'url': 'http://example.com/github key', 'created_at': 'YYYY-MM-DDTHH:MM:SZ', 'read_only': False}]
matching_keys:
    description: An array of keys matching the specified name. Only present on state=present
    type: list
    returned: When state=present
    sample: [{'id': 0, 'key': 'BASE64 encoded key', 'url': 'http://example.com/github key', 'created_at': 'YYYY-MM-DDTHH:MM:SZ', 'read_only': False}]
key:
    description: Metadata about the key just created. Only present on state=present
    type: dict
    returned: success
    sample: {'id': 0, 'key': 'BASE64 encoded key', 'url': 'http://example.com/github key', 'created_at': 'YYYY-MM-DDTHH:MM:SZ', 'read_only': False}
"""

EXAMPLES = """
- name: Authorize key with GitHub
  community.general.github_key:
    name: Access Key for Some Machine
    token: '{{ github_access_token }}'
    pubkey: '{{ lookup("file", "/home/foo/.ssh/id_rsa.pub") }}'
  delegate_to: localhost

- name: Remove key from GitHub
  community.general.github_key:
    name: Access Key for Some Machine
    token: '{{ github_access_token }}'
    state: absent
  delegate_to: localhost
"""


import base64

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible_collections.community.general.plugins.module_utils import (
    github as github_utils,
)


class GithubKey(github_utils.GitHubBase):
    def __init__(self, module):
        self.name = module.params["name"]
        self.pubkey = module.params["pubkey"]
        self.state = module.params["state"]
        self.force = module.params["force"]
        self.module = module

        super(GithubKey, self).__init__(
            username=module.params["user"]
            if module.params["password"] is not None
            else None,
            password=module.params["password"],
            token=module.params["token"],
            server=module.params["server"],
        )

        self.auth()

        self.user = self.github_conn.get_user()

    def _key_exists(self):
        for user_key in self.get_all_keys():
            if (user_key.title == self.name) and (
                base64.b64decode(user_key.key) == self.pubkey
            ):
                return True
        return False

    def _get_key(self):
        for user_key in self.get_all_keys():
            if (user_key.title == self.name) and (
                base64.b64decode(user_key.key) == self.pubkey
            ):
                return user_key
        return None

    def get_all_keys(self):
        return self.user.get_keys()

    def create_key(self):
        if self.module.check_mode:
            if self._key_exists():
                return dict(changed=False, key=self._get_key())
            else:
                return dict(changed=True, key={"name": self.name, "key": self.pubkey})
        else:
            return dict(changed=True, key=self.user.create_key(self.name, self.pubkey))

    def delete_key(self):
        if self.module.check_mode:
            return dict(changed=not self._key_exists(), deleted_key=self._get_key())
        else:
            if self._key_exists():
                user_key = self._get_key()
                deleted_key = user_key
                user_key.delete()

        return dict(changed=bool(deleted_key), deleted_key=deleted_key)


def main():
    argument_spec = github_utils.github_common_argument_spec()
    argument_spec.update(
        dict(
            name=dict(type="str", required=True),
            pubkey=dict(type="str"),
            state=dict(choices=["present", "absent"], default="present"),
            force=dict(type="bool", default=True),
        )
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[("state", "present", ["pubkey"])],
    )

    if not github_utils.HAS_GITHUB:
        module.fail_json(
            msg=missing_required_lib("PyGithub >= 1.3.5"),
            exception=github_utils.GITHUB_IMP_ERR,
        )

    state = module.params["state"]

    github_key = GithubKey(module)

    if state == "present":
        result = github_key.create_key()
    elif state == "absent":
        result = github_key.delete_key()

    module.exit_json(**result)


if __name__ == "__main__":
    main()
