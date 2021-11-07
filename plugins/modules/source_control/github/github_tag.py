#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: Ansible Team
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: github_tag
short_description: Create annotated GitHub tags for use with releases.
version_added: 4.1.0
description:
    - Allows for creation of annotated tags, by default a GitHub release only create lightweight tags.
    - Use this module with the the M(community.general.github_release) module to created a release linked to a annotated tag.
    - Note this module will only mark a task as changed if the requested tag doesn't already exist.
options:
    url:
        description:
            - Custom GitHub URL for self-hosted enterprise versions.
        type: str
    token:
        description:
            - GitHub access Token for authenticating.
            - Mutually exclusive with I(password).
        type: str
    username:
        description:
            - GitHub account username used for authentication.
            - This is only needed when not using I(access_token).
        type: str
    password:
        description:
            - The GitHub account password for the user.
            - This is only needed when not using I(access_token).
        type: str
    organization:
        description:
            - Repository organization name.
        type: str
        required: true
    repo:
        description:
            - Repository name.
        type: str
        required: true
    branch:
        description:
            - Name of the branch to create the tag on.
        type: str
        required: true
    tag:
        description:
            - Name of the tag to create.
        type: str
        required: true
    tagger:
        description:
            - Tagger details to apply to the tag.
        type: dict
        suboptions:
            name:
                description:
                    - Name of the tagger.
                type: str
                required: true
            email:
                description:
                    - Email of the tagger.
                type: str
                required: true
        required: true
    description:
        description:
            - Description message for the tag to be created with.
        type: str
        required: true

author:
    - "Mark Woolley (@marknet15)"
requirements:
    - "github3.py >= 1.0.0"
'''

EXAMPLES = r'''
- name: Create a annotated tag
  community.general.github_tag:
    token: tokenabc1234567890
    organization: someorg
    repo: testrepo
    branch: main
    tag: 1.0.0
    tagger:
      name: Some User
      email: some.user@example.com
    description: Some tag description message

'''

RETURN = r'''
tag:
    description:
    - The tag name created.
    - If the specified tag already exists, then State is unchanged
    type: str
    returned: when tag does not already exist and is successfully created.
    sample: 1.1.0
branch:
    description:
    - The branch used for the tag creation
    type: str
    returned: when tag does not already exist and is successfully created.
    sample: main
'''

import traceback

GITHUB_IMP_ERR = None
try:
    import github3

    HAS_GITHUB3_PACKAGE = True
except ImportError:
    GITHUB_IMP_ERR = traceback.format_exc()
    HAS_GITHUB3_PACKAGE = False

from datetime import datetime
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_native


def authenticate(module):
    '''
    Authenticate to either GitHub Cloud or GitHub Enterprise
    '''

    url = module.params.get('url')
    username = module.params.get('username')
    password = module.params.get('password')
    token = module.params.get('token')
    login_params = dict()

    if url:
        login_params['url'] = url
    else:
        login_params['user'] = username

    if password:
        login_params['password'] = password
    else:
        login_params['token'] = token

    # login to github
    try:
        if url:
            client = github3.enterprise_login(**login_params)
        elif password or token:
            client = github3.login(**login_params)
        else:
            client = github3.GitHub()

        # test if actually logged in
        if password or token:
            client.me()
    except github3.exceptions.AuthenticationFailed as e:
        module.fail_json(msg='Failed to connect to GitHub: %s' % to_native(e),
                         details="Please check username and password or token "
                                 "for repository %s" % module.params['repo'])

    return client


def get_repo(module, client):
    '''
    Check if tag already exists and return repository object
    '''

    org = module.params['organization']
    repo = module.params['repo']
    tag = module.params['tag']

    try:
        repository = client.repository(org, repo)
    except (github3.exceptions.ClientError, github3.exceptions.NotFoundError):
        module.fail_json(msg="Repository %s/%s doesn't exist" % (org, repo))

    tag_exists = False

    for tag_item in repository.tags():
        if tag_item.name == tag:
            tag_exists = True

    if tag_exists:
        return False

    return repository


def create_tag(module, repository):
    '''
    Create annotated git tag
    '''

    branch = module.params['branch']
    tag = module.params['tag']
    tagger = module.params['tagger']
    description = module.params['description']

    latest_commit = repository.commit(sha=branch)

    # Currently the github3.py library requires the date to be set,
    # eventhough not required by API.
    current_date = datetime.now()
    tagger['date'] = current_date.strftime('%Y-%m-%dT%H:%M:%SZ')

    tag_params = dict(
        tag=tag,
        tagger=tagger,
        sha=latest_commit.sha,
        message=description,
        obj_type="commit"
    )

    try:
        new_tag = repository.create_tag(**tag_params)
    except (github3.exceptions.ClientError, github3.exceptions.UnprocessableEntity) as err:
        module.fail_json(
            msg='Failed to create a annotated tag with the following error: %s' % to_native(err))

    return new_tag


def main():
    module = AnsibleModule(
        argument_spec=dict(
            url=dict(type='str'),
            username=dict(type='str'),
            password=dict(no_log=True),
            token=dict(no_log=True),
            organization=dict(required=True, type='str'),
            repo=dict(required=True),
            branch=dict(required=True, type='str'),
            tag=dict(required=True, type='str'),
            tagger=dict(required=True, type='dict'),
            description=dict(required=True, type='str')
        ),
        required_together=[('username', 'password')],
        required_one_of=[('password', 'token')],
        mutually_exclusive=[('password', 'token')]
    )

    if not HAS_GITHUB3_PACKAGE:
        module.fail_json(msg=missing_required_lib('github3.py >= 1.0.0'),
                         exception=GITHUB_IMP_ERR)

    client = authenticate(module)
    repository = get_repo(module, client)

    if not repository:
        module.exit_json(changed=False, msg="Tag %s already exists." % module.params['tag'])

    new_tag = create_tag(module, repository)

    module.exit_json(changed=True, tag=new_tag.tag, branch=module.params['branch'])


if __name__ == '__main__':
    main()
