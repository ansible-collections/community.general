#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# Copyright: Ansible Team
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
module: github_release
short_description: Interact with GitHub Releases
description:
    - Fetch metadata about GitHub Releases
version_added: 2.2
options:
    user:
        description:
            - The GitHub account that owns the repository
        required: true
        type: str
    repo:
        description:
            - Repository name
        required: true
        type: str
    action:
        description:
            - Action to perform
        required: true
        choices: [ 'latest_release', 'create_release' ]
        type: str
    tag:
        description:
            - Tag name when creating a release. Required when using action is set to C(create_release).
        version_added: 2.4
        type: str
    target:
        description:
            - Target of release when creating a release
        version_added: 2.4
        type: str
    name:
        description:
            - Name of release when creating a release
        version_added: 2.4
        type: str
    body:
        description:
            - Description of the release when creating a release
        version_added: 2.4
        type: str
    draft:
        description:
            - Sets if the release is a draft or not. (boolean)
        type: 'bool'
        default: 'no'
        version_added: 2.4
    prerelease:
        description:
            - Sets if the release is a prerelease or not. (boolean)
        type: bool
        default: 'no'
        version_added: 2.4

extends_documentation_fragment: community.general.github
author:
    - "Adrian Moisey (@adrianmoisey)"
"""

EXAMPLES = """
- name: Get latest release of a public repository
  github_release:
    user: ansible
    repo: ansible
    action: latest_release

- name: Get latest release of testuseer/testrepo
  github_release:
    token: tokenabc1234567890
    user: testuser
    repo: testrepo
    action: latest_release

- name: Get latest release of test repo using username and password. Ansible 2.4.
  github_release:
    user: testuser
    password: secret123
    repo: testrepo
    action: latest_release

- name: Create a new release
  github_release:
    token: tokenabc1234567890
    user: testuser
    repo: testrepo
    action: create_release
    tag: test
    target: master
    name: My Release
    body: Some description

"""

RETURN = """
create_release:
    description:
    - Version of the created release
    - "For Ansible version 2.5 and later, if specified release version already exists, then State is unchanged"
    - "For Ansible versions prior to 2.5, if specified release version already exists, then State is skipped"
    type: str
    returned: success
    sample: 1.1.0

latest_release:
    description: Version of the latest release
    type: str
    returned: success
    sample: 1.1.0
"""

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible_collections.community.general.plugins.module_utils import (
    github as github_utils,
)
from ansible.module_utils._text import to_native


class GithubRelease(github_utils.GitHubBase):
    def __init__(self, module):
        self.tag = module.params["tag"]
        self.target = module.params["target"]
        self.name = module.params["name"]
        self.body = module.params["body"]
        self.draft = module.params["draft"]
        self.prerelease = module.params["prerelease"]
        self.repo_full_name = "/".join([module.params["user"], module.params["repo"]])
        self.module = module

        if not self.name:
            self.name = self.tag

        super(GithubRelease, self).__init__(
            username=module.params["user"]
            if module.params["password"] is not None
            else None,
            password=module.params["password"],
            token=module.params["token"],
            server=module.params["server"],
            repo=self.repo_full_name,
        )

        self.auth()

        self.target_ref = self.repository.get_git_ref("heads/{0}".format(self.target))

    def create_release(self):
        try:
            self.repository.get_release(self.tag)
            return dict(
                changed=False,
                msg="Release for tag {0} already exists.".format(self.tag),
            )
        except github_utils.UnknownObjectException:
            pass

        try:
            tag_exists = self.repository.get_git_ref("tags/{0}".format(self.tag))
        except github_utils.UnknownObjectException:
            tag_exists = False

        if tag_exists:
            ret_state = dict(
                changed=True,
                msg="Release {0} created".format(self.name),
                tag=self.repository.create_git_release(
                    self.tag,
                    self.name,
                    self.body,
                    self.draft,
                    self.prerelease,
                    self.target,
                ).tag_name,
            )
        else:
            ret_state = dict(
                changed=True,
                msg="Release {0} and tag {1} created".format(self.name, self.tag),
                tag=self.repository.create_git_tag_and_release(
                    self.tag,
                    self.tag,
                    self.name,
                    self.body,
                    self.target_ref.object.sha,
                    "commit",
                    draft=self.draft,
                    prerelease=self.prerelease,
                ).tag_name,
            )

        return ret_state


def main():
    argument_spec = github_utils.github_common_argument_spec()
    argument_spec.update(
        dict(
            repo=dict(required=True),
            user=dict(required=True, aliases=["username"]),
            action=dict(required=True, choices=["latest_release", "create_release"]),
            tag=dict(type="str"),
            target=dict(type="str"),
            name=dict(type="str"),
            body=dict(type="str"),
            draft=dict(type="bool", default=False),
            prerelease=dict(type="bool", default=False),
        )
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=(("password", "token"),),
        required_if=[
            ("action", "create_release", ["tag"]),
            ("action", "create_release", ["password", "token"], True),
        ],
    )

    if not github_utils.HAS_GITHUB:
        module.fail_json(
            msg=missing_required_lib("PyGithub >= 1.3.5"),
            exception=github_utils.GITHUB_IMP_ERR,
        )

    action = module.params["action"]

    repo_release = GithubRelease(module)

    if action == "latest_release":
        try:
            release = repo_release.repository.get_latest_release()
        except github_utils.UnknownObjectException:
            release = None

        if release:
            module.exit_json(tag=release.tag_name)
        else:
            module.exit_json(tag=None)

    if action == "create_release":
        release = repo_release.create_release()
        module.exit_json(**release)


if __name__ == "__main__":
    main()
