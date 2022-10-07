#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright Ansible Team
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: github_release
short_description: Interact with GitHub Releases
description:
    - Fetch metadata about GitHub Releases
options:
    token:
        description:
            - GitHub Personal Access Token for authenticating. Mutually exclusive with C(password).
        type: str
    user:
        description:
            - The GitHub account that owns the repository
        type: str
        required: true
    password:
        description:
            - The GitHub account password for the user. Mutually exclusive with C(token).
        type: str
    repo:
        description:
            - Repository name
        type: str
        required: true
    action:
        description:
            - Action to perform
        type: str
        required: true
        choices: [ 'latest_release', 'create_release' ]
    tag:
        description:
            - Tag name when creating a release. Required when using action is set to C(create_release).
        type: str
    target:
        description:
            - Target of release when creating a release
        type: str
    name:
        description:
            - Name of release when creating a release
        type: str
    body:
        description:
            - Description of the release when creating a release
        type: str
    draft:
        description:
            - Sets if the release is a draft or not. (boolean)
        type: bool
        default: false
    prerelease:
        description:
            - Sets if the release is a prerelease or not. (boolean)
        type: bool
        default: false

author:
    - "Adrian Moisey (@adrianmoisey)"
requirements:
    - "github3.py >= 1.0.0a3"
'''

EXAMPLES = '''
- name: Get latest release of a public repository
  community.general.github_release:
    user: ansible
    repo: ansible
    action: latest_release

- name: Get latest release of testuseer/testrepo
  community.general.github_release:
    token: tokenabc1234567890
    user: testuser
    repo: testrepo
    action: latest_release

- name: Get latest release of test repo using username and password. Ansible 2.4.
  community.general.github_release:
    user: testuser
    password: secret123
    repo: testrepo
    action: latest_release

- name: Create a new release
  community.general.github_release:
    token: tokenabc1234567890
    user: testuser
    repo: testrepo
    action: create_release
    tag: test
    target: master
    name: My Release
    body: Some description

'''

RETURN = '''
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
'''

import traceback

GITHUB_IMP_ERR = None
try:
    import github3

    HAS_GITHUB_API = True
except ImportError:
    GITHUB_IMP_ERR = traceback.format_exc()
    HAS_GITHUB_API = False

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_native


def main():
    module = AnsibleModule(
        argument_spec=dict(
            repo=dict(required=True),
            user=dict(required=True),
            password=dict(no_log=True),
            token=dict(no_log=True),
            action=dict(
                required=True, choices=['latest_release', 'create_release']),
            tag=dict(type='str'),
            target=dict(type='str'),
            name=dict(type='str'),
            body=dict(type='str'),
            draft=dict(type='bool', default=False),
            prerelease=dict(type='bool', default=False),
        ),
        supports_check_mode=True,
        mutually_exclusive=(('password', 'token'),),
        required_if=[('action', 'create_release', ['tag']),
                     ('action', 'create_release', ['password', 'token'], True)],
    )

    if not HAS_GITHUB_API:
        module.fail_json(msg=missing_required_lib('github3.py >= 1.0.0a3'),
                         exception=GITHUB_IMP_ERR)

    repo = module.params['repo']
    user = module.params['user']
    password = module.params['password']
    login_token = module.params['token']
    action = module.params['action']
    tag = module.params.get('tag')
    target = module.params.get('target')
    name = module.params.get('name')
    body = module.params.get('body')
    draft = module.params.get('draft')
    prerelease = module.params.get('prerelease')

    # login to github
    try:
        if password:
            gh_obj = github3.login(user, password=password)
        elif login_token:
            gh_obj = github3.login(token=login_token)
        else:
            gh_obj = github3.GitHub()

        # test if we're actually logged in
        if password or login_token:
            gh_obj.me()
    except github3.exceptions.AuthenticationFailed as e:
        module.fail_json(msg='Failed to connect to GitHub: %s' % to_native(e),
                         details="Please check username and password or token "
                                 "for repository %s" % repo)

    repository = gh_obj.repository(user, repo)

    if not repository:
        module.fail_json(msg="Repository %s/%s doesn't exist" % (user, repo))

    if action == 'latest_release':
        release = repository.latest_release()
        if release:
            module.exit_json(tag=release.tag_name)
        else:
            module.exit_json(tag=None)

    if action == 'create_release':
        release_exists = repository.release_from_tag(tag)
        if release_exists:
            module.exit_json(changed=False, msg="Release for tag %s already exists." % tag)

        release = repository.create_release(
            tag, target, name, body, draft, prerelease)
        if release:
            module.exit_json(changed=True, tag=release.tag_name)
        else:
            module.exit_json(changed=False, tag=None)


if __name__ == '__main__':
    main()
