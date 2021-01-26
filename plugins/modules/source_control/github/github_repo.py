#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Álvaro Torres Cogollo
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from ansible.module_utils.basic import AnsibleModule
from github import Github, GithubException
import sys

DOCUMENTATION = r'''
---
module: github_repo
short_description: Manage your repos on Github
description:
- Manages Github repos using PyGithub library
- Authentication can be done with access_token or with username and password
options:
  username:
    description:
    - Username parameter for authentication.
    - This is only needed when not using access_token.
    type: str
    required: false
  password:
    description:
    - Password parameter for authentication.
    - This is only needed when not using access_token.
    type: str
    required: false
  access_token:
    description:
    - Token parameter for authentication.
    - This is only needed when not using username and password.
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
    - This is only makes sense when creating the new repository.
    type: str
    default: ''
    required: false
  private:
    description:
    - Whether the new repository should be private or not.
    - This is only makes sense when creating the new repository.
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
    - If not provided, the repository will be created in the current user profile.
    type: str
    default: None
    required: false
requirements:
- PyGithub>=1.54
notes:
- For python3, PyGithub>=1.54 should be used.
- For python3.5, PyGithub==1.54 should be used. More info: https://pygithub.readthedocs.io/en/latest/changes.html#version-1-54-november-30-2020
- For python2, PyGithub==1.45 should be used. More info: https://pygithub.readthedocs.io/en/latest/changes.html#version-1-45-december-29-2019
author:
- Álvaro Torres Cogollo (@atorrescogollo)
'''

EXAMPLES = r'''
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

RETURN = r'''
repo:
  description: repo as json. Only present when creating repository. See https://docs.github.com/en/rest/reference/repos#get-a-repository.
  type: json
'''


def authenticate(username=None, password=None, access_token=None):
    if access_token: return Github(access_token)
    else: Github(username,password)

def create_repo(gh, name, organization=None, private=False, description=''):
    result = dict(
            changed=False,
            repo=None
        )
    target = gh.get_organization(organization) if organization else gh.get_user()

    repo = None
    try:
        repo = target.get_repo(name=name)
    except GithubException as e:
        if e.args[0] == 404:
            repo = target.create_repo(name=name, private=private, description=description)
            result['changed']=True
        else: raise e

    result['repo'] = repo.raw_data
    return result

def delete_repo(gh, name, organization=None):
    result = dict(
            changed=False
        )
    target = gh.get_organization(organization) if organization else gh.get_user()
    try:
        repo = target.get_repo(name=name)
        repo.delete()
        result['changed'] = True
    except GithubException as e:
        if e.args[0] == 404: pass
        else: raise e

    return result


def main(params):
    gh = authenticate(username=params['username'], password=params['password'], access_token=params['access_token'])
    if params['state'] == "absent":
        args = {
            "gh": gh,
            "name": params['name'],
            "organization": params['organization']
        }
        return delete_repo(**args)
    else:
        args = {
            "gh": gh,
            "name": params['name'],
            "organization": params['organization'],
            "private": params['private'],
            "description": params['description']
        }
        return create_repo(**args)

if __name__ == '__main__':
    module_args = dict(
        username=dict(    type='str',  required=False, default=None, no_log=True),
        password=dict(    type='str',  required=False, default=None, no_log=True),
        access_token=dict(type='str',  required=False, default=None, no_log=True),
        name=dict(        type='str',  required=True),
        state=dict(       type='str',  required=False, default="present", choices=["present","absent"]),
        organization=dict(type='str',  required=False, default=None),
        private=dict(     type='bool', required=False, default=False),
        description=dict( type='str',  required=False, default=''),
    )
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    assert module.params['access_token'] or ( module.params['username'] and module.params['password'] )

    try:
        result = dict(
            changed=False
        )
        result = main(module.params)
        module.exit_json(**result)
    except GithubException as e:
        module.fail_json(msg="Github error. {}".format(repr(e)), **result)
    except Exception as e:
        module.fail_json(msg="Unexpected error. {}".format(repr(e)), **result)
