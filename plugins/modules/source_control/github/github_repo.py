#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Álvaro Torres Cogollo
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: github_repo
short_description: Manage your repos on Github
version_added: 2.1.0
description:
- Manages Github repos using PyGithub library.
- Authentication can be done with I(access_token) or with I(username) and I(password).
options:
  username:
    description:
    - I(username) parameter for authentication.
    - This is only needed when not using I(access_token).
    type: str
    required: false
  password:
    description:
    - I(password) parameter for authentication.
    - This is only needed when not using I(access_token).
    type: str
    required: false
  access_token:
    description:
    - Token parameter for authentication.
    - This is only needed when not using I(username) and I(password).
    type: str
    required: false
  name:
    description:
    - Repository name.
    type: str
    required: true
  description:
    description:
    - Description for the repository.
    - This is only used when I(state) is C(present).
    type: str
    default: ''
    required: false
  private:
    description:
    - Whether the new repository should be private or not.
    - This is only used when I(state) is C(present).
    type: bool
    default: no
    required: false
  state:
    description:
    - Whether the repository should exist or not.
    type: str
    default: present
    choices: [ absent, present ]
    required: false
  organization:
    description:
    - Organization for the repository.
    - When I(state) is C(present), the repository will be created in the current user profile.
    type: str
    required: false
requirements:
- PyGithub>=1.54
notes:
- For python3, PyGithub>=1.54 should be used.
- "For python3.5, PyGithub==1.54 should be used. More info: https://pygithub.readthedocs.io/en/latest/changes.html#version-1-54-november-30-2020."
- "For python2.7, PyGithub==1.45 should be used. More info: https://pygithub.readthedocs.io/en/latest/changes.html#version-1-45-december-29-2019."
author:
- Álvaro Torres Cogollo (@atorrescogollo)
'''

EXAMPLES = '''
- name: Create a Github Repo
  github_repo:
    access_token: mytoken
    organization: MyOrganization
    name: myrepo
    description: "Just for fun"
    private: yes
    state: present
  register: result
- name: Delete the repo
  github_repo:
    username: octocat
    password: password
    organization: MyOrganization
    name: myrepo
    state: absent
  register: result
'''

RETURN = '''
repo:
  description: Repository information as JSON. See U(https://docs.github.com/en/rest/reference/repos#get-a-repository).
  returned: success and I(state) is C(present)
  type: dict
'''

import traceback
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
import sys

GITHUB_IMP_ERR = None
try:
    from github import Github, GithubException
    from github.GithubException import UnknownObjectException
    HAS_GITHUB_PACKAGE = True
except Exception:
    GITHUB_IMP_ERR = traceback.format_exc()
    HAS_GITHUB_PACKAGE = False


def authenticate(username=None, password=None, access_token=None):
    if access_token:
        return Github(base_url="https://api.github.com:443", login_or_token=access_token)
    else:
        return Github(base_url="https://api.github.com:443", login_or_token=username, password=password)


def create_repo(gh, name, organization=None, private=False, description='', check_mode=False):
    result = dict(
        changed=False,
        repo=dict())
    if organization:
        target = gh.get_organization(organization)
    else:
        target = gh.get_user()

    repo = None
    try:
        repo = target.get_repo(name=name)
        result['repo'] = repo.raw_data
    except UnknownObjectException:
        if not check_mode:
            repo = target.create_repo(
                name=name, private=private, description=description)
            result['repo'] = repo.raw_data

        result['changed'] = True

    changes = {}
    if check_mode or repo.raw_data['private'] != private:
        changes['private'] = private
    if check_mode or repo.raw_data['description'] != description:
        changes['description'] = description

    if changes:
        if not check_mode:
            repo.edit(**changes)

        result['repo'].update({
            'private': repo._private.value if not check_mode else private,
            'description': repo._description.value if not check_mode else description
        })
        result['changed'] = True

    return result


def delete_repo(gh, name, organization=None, check_mode=False):
    result = dict(changed=False)
    if organization:
        target = gh.get_organization(organization)
    else:
        target = gh.get_user()
    try:
        repo = target.get_repo(name=name)
        if not check_mode:
            repo.delete()
        result['changed'] = True
    except UnknownObjectException:
        pass

    return result


def run_module(params, check_mode=False):
    gh = authenticate(
        username=params['username'], password=params['password'], access_token=params['access_token'])
    if params['state'] == "absent":
        args = {
            "gh": gh,
            "name": params['name'],
            "organization": params['organization'],
            "check_mode": check_mode
        }
        return delete_repo(**args)
    else:
        args = {
            "gh": gh,
            "name": params['name'],
            "organization": params['organization'],
            "private": params['private'],
            "description": params['description'],
            "check_mode": check_mode
        }
        return create_repo(**args)


def main():
    module_args = dict(
        username=dict(type='str', required=False, default=None),
        password=dict(type='str', required=False, default=None, no_log=True),
        access_token=dict(type='str', required=False,
                          default=None, no_log=True),
        name=dict(type='str', required=True),
        state=dict(type='str', required=False, default="present",
                   choices=["present", "absent"]),
        organization=dict(type='str', required=False, default=None),
        private=dict(type='bool', required=False, default=False),
        description=dict(type='str', required=False, default=''),
    )
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if not HAS_GITHUB_PACKAGE:
        module.fail_json(msg=missing_required_lib(
            "PyGithub"), exception=GITHUB_IMP_ERR)

    if not module.params['access_token'] and not (module.params['username'] and module.params['password']):
        raise AssertionError(
            "Access token must be provided for authentation. Username and password are also valid, instead.")

    try:
        result = dict(
            changed=False
        )
        result = run_module(module.params, module.check_mode)
        module.exit_json(**result)
    except GithubException as e:
        module.fail_json(msg="Github error. {0}".format(repr(e)), **result)
    except Exception as e:
        module.fail_json(msg="Unexpected error. {0}".format(repr(e)), **result)


if __name__ == '__main__':
    main()
