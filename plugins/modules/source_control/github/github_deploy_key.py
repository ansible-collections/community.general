#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Andrea Tartaglia <andrea@braingap.uk>

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = """
---
module: github_deploy_key
version_added: "2.4"
author: "Ali (@bincyber)"
short_description: Manages deploy keys for GitHub repositories.
description:
  - "Adds or removes deploy keys for GitHub repositories. Supports authentication using username and password,
  username and password and 2-factor authentication code (OTP), OAuth2 token, or personal access token. Admin
  rights on the repository are required."
options:
  owner:
    description:
      - The name of the individual account or organization that owns the GitHub repository.
    required: true
    aliases: [ 'account', 'organization' ]
    type: str
  repo:
    description:
      - The name of the GitHub repository.
    required: true
    aliases: [ 'repository' ]
    type: str
  name:
    description:
      - The name for the deploy key.
    required: true
    aliases: [ 'title', 'label' ]
    type: str
  key:
    description:
      - The SSH public key to add to the repository as a deploy key.
    type: str
    required: true
  read_only:
    description:
      - If C(true), the deploy key will only be able to read repository contents. Otherwise, the deploy key will be able to read and write.
    type: bool
    default: 'yes'
  state:
    description:
      - The state of the deploy key.
    default: "present"
    choices: [ "present", "absent" ]
    type: str
  force:
    description:
      - If C(true), forcefully adds the deploy key by deleting any existing deploy key with the same public key or title.
    type: bool
    default: 'no'
  otp:
    description:
      - The 6 digit One Time Password for 2-Factor Authentication. Required together with I(username) and I(password).
    type: int
extends_documentation_fragment: community.general.github
notes:
   - "Refer to GitHub's API documentation here: https://developer.github.com/v3/repos/keys/."
"""

EXAMPLES = """
# add a new read-only deploy key to a GitHub repository using basic authentication
- github_deploy_key:
    owner: "johndoe"
    repo: "example"
    name: "new-deploy-key"
    key: "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDAwXxn7kIMNWzcDfou..."
    read_only: yes
    username: "johndoe"
    password: "supersecretpassword"

# remove an existing deploy key from a GitHub repository
- github_deploy_key:
    owner: "johndoe"
    repository: "example"
    name: "new-deploy-key"
    key: "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDAwXxn7kIMNWzcDfou..."
    force: yes
    username: "johndoe"
    password: "supersecretpassword"
    state: absent

# add a new deploy key to a GitHub repository, replace an existing key, use an OAuth2 token to authenticate
- github_deploy_key:
    owner: "johndoe"
    repository: "example"
    name: "new-deploy-key"
    key: "{{ lookup('file', '~/.ssh/github.pub') }}"
    force: yes
    token: "ABAQDAwXxn7kIMNWzcDfo..."

# re-add a deploy key to a GitHub repository but with a different name
- github_deploy_key:
    owner: "johndoe"
    repository: "example"
    name: "replace-deploy-key"
    key: "{{ lookup('file', '~/.ssh/github.pub') }}"
    username: "johndoe"
    password: "supersecretpassword"

# add a new deploy key to a GitHub repository using 2FA
- github_deploy_key:
    owner: "johndoe"
    repo: "example"
    name: "new-deploy-key-2"
    key: "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDAwXxn7kIMNWzcDfou..."
    username: "johndoe"
    password: "supersecretpassword"
    otp: 123456

# Create a deploy key in a GitHub enterprise repository
- github_deploy_key:
    owner: "johndoe"
    repository: "example"
    name: "new-deploy-key"
    key: "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDAwXxn7kIMNWzcDfou..."
    force: yes
    username: "johndoe"
    password: "supersecretpassword"
    state: present
    server: https://my-internal-github-server.example.com

"""

RETURN = """
msg:
    description: the status message describing what occurred
    returned: always
    type: str
    sample: "Deploy key added successfully"
id:
    description: the key identifier assigned by GitHub for the deploy key
    returned: changed
    type: int
    sample: 24381901
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url
from ansible_collections.community.general.plugins.module_utils import (
    github as github_utils,
)
from re import findall


class GithubDeployKey(github_utils.GitHubBase):
    def __init__(self, module):
        self.module = module

        self.name = module.params["name"]
        self.key = module.params["key"]
        self.state = module.params["state"]
        self.read_only = module.params.get("read_only", True)
        self.force = module.params.get("force", False)
        self.username = module.params.get("username", None)
        self.password = module.params.get("password", None)
        self.token = module.params.get("token", None)
        self.otp = module.params.get("otp", None)
        self.server = module.params["server"]
        self.repo = module.params["repo"]
        self.owner = module.params["owner"]

        super(GithubDeployKey, self).__init__(
            self.username,
            self.password,
            self.token,
            self.otp,
            self.server,
            self.repo,
            self.owner,
        )

        self.auth()

    def get_existing_key(self):
        for key in self.repository.get_keys():
            existing_key_id = str(key.id)
            if key.key.split() == self.key.split()[:2]:
                return int(existing_key_id)
            if key.title == self.name and self.force:
                return int(existing_key_id)

        return None

    def add_new_key(self):
        new_key = self.repository.create_key(self.name, self.key, self.read_only)

        self.module.exit_json(
            changed=True, msg="Deploy key successfully added", id=new_key.id
        )

    def remove_existing_key(self, key_id):
        key = self.repository.get_key(key_id)
        key.delete()
        if self.state == "absent":
            self.module.exit_json(
                changed=True, msg="Deploy key successfully deleted", id=key_id
            )


def main():
    argument_spec = github_utils.github_common_argument_spec()
    argument_spec.update(
        dict(
            owner=dict(required=True, type="str", aliases=["account", "organization"]),
            repo=dict(required=True, type="str", aliases=["repository"]),
            name=dict(required=True, type="str", aliases=["title", "label"]),
            key=dict(required=True, type="str"),
            read_only=dict(required=False, type="bool", default=True),
            state=dict(type="str", default="present", choices=["present", "absent"]),
            force=dict(required=False, type="bool", default=False),
            otp=dict(required=False, type="int", no_log=True),
        )
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[["password", "token"]],
        required_together=[["user", "password"], ["otp", "user", "password"]],
        required_one_of=[["user", "token"]],
        required_if=[("state", "present", ["key"])],
        supports_check_mode=True,
    )

    deploy_key = GithubDeployKey(module)
    key_id = deploy_key.get_existing_key()

    if module.check_mode:
        if deploy_key.state == "present" and key_id is None:
            module.exit_json(changed=True)
        elif deploy_key.state == "present" and key_id is not None:
            module.exit_json(changed=False)

    # to forcefully modify an existing key, the existing key must be deleted first
    if deploy_key.state == "absent" or deploy_key.force:
        if key_id is not None:
            deploy_key.remove_existing_key(key_id)
        elif deploy_key.state == "absent":
            module.exit_json(changed=False, msg="Deploy key does not exist")

    if deploy_key.state == "present":
        if deploy_key.get_existing_key() is None:
            deploy_key.add_new_key()
        else:
            module.exit_json(changed=False, msg="Deploy key already exists")


if __name__ == "__main__":
    main()
