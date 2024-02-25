#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2024, Zoran Krleza (zoran.krleza@true-north.hr)
# Based on code:
# Copyright (c) 2019, Guillaume Martinez (lunik@tiwabbit.fr)
# Copyright (c) 2018, Marcus Watkins <marwatk@marcuswatkins.net>
# Copyright (c) 2013, Phillip Gentry <phillip@cx.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
module: gitlab_group_access_token
short_description: Manages GitLab group access tokens
version_added: 8.4.0
description:
  - Creates and revokes group access tokens.
author:
  - Zoran Krleza (@pixslx)
requirements:
  - python-gitlab >= 3.1.0
extends_documentation_fragment:
  - community.general.auth_basic
  - community.general.gitlab
  - community.general.attributes
notes:
  - Access tokens can not be changed. If a parameter needs to be changed, an acceess token has to be recreated.
    Whether tokens will be recreated is controlled by the O(recreate) option, which defaults to V(never).
  - Token string is contained in the result only when access token is created or recreated. It can not be fetched afterwards.
  - Token matching is done by comparing O(name) option.

attributes:
  check_mode:
    support: full
  diff_mode:
    support: none

options:
  group:
    description:
      - ID or full path of group in the form of group/subgroup.
    required: true
    type: str
  name:
    description:
      - Access token's name.
    required: true
    type: str
  scopes:
    description:
      - Scope of the access token.
    required: true
    type: list
    elements: str
    aliases: ["scope"]
    choices: ["api", "read_api", "read_registry", "write_registry", "read_repository", "write_repository", "create_runner", "ai_features", "k8s_proxy"]
  access_level:
    description:
      - Access level of the access token.
    type: str
    default: maintainer
    choices: ["guest", "reporter", "developer", "maintainer", "owner"]
  expires_at:
    description:
      - Expiration date of the access token in C(YYYY-MM-DD) format.
      - Make sure to quote this value in YAML to ensure it is kept as a string and not interpreted as a YAML date.
    type: str
    required: true
  recreate:
    description:
      - Whether the access token will be recreated if it already exists.
      - When V(never) the token will never be recreated.
      - When V(always) the token will always be recreated.
      - When V(state_change) the token will be recreated if there is a difference between desired state and actual state.
    type: str
    choices: ["never", "always", "state_change"]
    default: never
  state:
    description:
      - When V(present) the access token will be added to the group if it does not exist.
      - When V(absent) it will be removed from the group if it exists.
    default: present
    type: str
    choices: [ "present", "absent" ]
'''

EXAMPLES = r'''
- name: "Creating a group access token"
  community.general.gitlab_group_access_token:
    api_url: https://gitlab.example.com/
    api_token: "somegitlabapitoken"
    group: "my_group/my_subgroup"
    name: "group_token"
    expires_at: "2024-12-31"
    access_level: developer
    scopes:
      - api
      - read_api
      - read_repository
      - write_repository
    state: present

- name: "Revoking a group access token"
  community.general.gitlab_group_access_token:
    api_url: https://gitlab.example.com/
    api_token: "somegitlabapitoken"
    group: "my_group/my_group"
    name: "group_token"
    expires_at: "2024-12-31"
    scopes:
      - api
      - read_api
      - read_repository
      - write_repository
    state: absent

- name: "Change (recreate) existing token if its actual state is different than desired state"
  community.general.gitlab_group_access_token:
    api_url: https://gitlab.example.com/
    api_token: "somegitlabapitoken"
    group: "my_group/my_group"
    name: "group_token"
    expires_at: "2024-12-31"
    scopes:
      - api
      - read_api
      - read_repository
      - write_repository
    recreate: state_change
    state: present
'''

RETURN = r'''
access_token:
  description:
    - API object.
    - Only contains the value of the token if the token was created or recreated.
  returned: success and O(state=present)
  type: dict
'''

from datetime import datetime

from ansible.module_utils.api import basic_auth_argument_spec
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native

from ansible_collections.community.general.plugins.module_utils.gitlab import (
    auth_argument_spec, find_group, gitlab_authentication, gitlab
)

ACCESS_LEVELS = dict(guest=10, reporter=20, developer=30, maintainer=40, owner=50)


class GitLabGroupAccessToken(object):
    def __init__(self, module, gitlab_instance):
        self._module = module
        self._gitlab = gitlab_instance
        self.access_token_object = None

    '''
    @param project Project Object
    @param group Group Object
    @param arguments Attributes of the access_token
    '''
    def create_access_token(self, group, arguments):
        changed = False
        if self._module.check_mode:
            return True

        try:
            self.access_token_object = group.access_tokens.create(arguments)
            changed = True
        except (gitlab.exceptions.GitlabCreateError) as e:
            self._module.fail_json(msg="Failed to create access token: %s " % to_native(e))

        return changed

    '''
    @param project Project object
    @param group Group Object
    @param name of the access token
    '''
    def find_access_token(self, group, name):
        access_tokens = group.access_tokens.list(all=True)
        for access_token in access_tokens:
            if (access_token.name == name):
                self.access_token_object = access_token
                return False
        return False

    def revoke_access_token(self):
        if self._module.check_mode:
            return True

        changed = False
        try:
            self.access_token_object.delete()
            changed = True
        except (gitlab.exceptions.GitlabCreateError) as e:
            self._module.fail_json(msg="Failed to revoke access token: %s " % to_native(e))

        return changed

    def access_tokens_equal(self):
        if self.access_token_object.name != self._module.params['name']:
            return False
        if self.access_token_object.scopes != self._module.params['scopes']:
            return False
        if self.access_token_object.access_level != ACCESS_LEVELS[self._module.params['access_level']]:
            return False
        if self.access_token_object.expires_at != self._module.params['expires_at']:
            return False
        return True


def main():
    argument_spec = basic_auth_argument_spec()
    argument_spec.update(auth_argument_spec())
    argument_spec.update(dict(
        state=dict(type='str', default="present", choices=["absent", "present"]),
        group=dict(type='str', required=True),
        name=dict(type='str', required=True),
        scopes=dict(type='list',
                    required=True,
                    aliases=['scope'],
                    elements='str',
                    choices=['api',
                             'read_api',
                             'read_registry',
                             'write_registry',
                             'read_repository',
                             'write_repository',
                             'create_runner',
                             'ai_features',
                             'k8s_proxy']),
        access_level=dict(type='str', required=False, default='maintainer', choices=['guest', 'reporter', 'developer', 'maintainer', 'owner']),
        expires_at=dict(type='str', required=True),
        recreate=dict(type='str', default='never', choices=['never', 'always', 'state_change'])
    ))

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[
            ['api_username', 'api_token'],
            ['api_username', 'api_oauth_token'],
            ['api_username', 'api_job_token'],
            ['api_token', 'api_oauth_token'],
            ['api_token', 'api_job_token']
        ],
        required_together=[
            ['api_username', 'api_password']
        ],
        required_one_of=[
            ['api_username', 'api_token', 'api_oauth_token', 'api_job_token']
        ],
        supports_check_mode=True
    )

    state = module.params['state']
    group_identifier = module.params['group']
    name = module.params['name']
    scopes = module.params['scopes']
    access_level_str = module.params['access_level']
    expires_at = module.params['expires_at']
    recreate = module.params['recreate']

    access_level = ACCESS_LEVELS[access_level_str]

    try:
        datetime.strptime(expires_at, '%Y-%m-%d')
    except ValueError:
        module.fail_json(msg="Argument expires_at is not in required format YYYY-MM-DD")

    gitlab_instance = gitlab_authentication(module)

    gitlab_access_token = GitLabGroupAccessToken(module, gitlab_instance)

    group = find_group(gitlab_instance, group_identifier)
    if group is None:
        module.fail_json(msg="Failed to create access token: group %s does not exists" % group_identifier)

    gitlab_access_token_exists = False
    gitlab_access_token.find_access_token(group, name)
    if gitlab_access_token.access_token_object is not None:
        gitlab_access_token_exists = True

    if state == 'absent':
        if gitlab_access_token_exists:
            gitlab_access_token.revoke_access_token()
            module.exit_json(changed=True, msg="Successfully deleted access token %s" % name)
        else:
            module.exit_json(changed=False, msg="Access token does not exists")

    if state == 'present':
        if gitlab_access_token_exists:
            if gitlab_access_token.access_tokens_equal():
                if recreate == 'always':
                    gitlab_access_token.revoke_access_token()
                    gitlab_access_token.create_access_token(group, {'name': name, 'scopes': scopes, 'access_level': access_level, 'expires_at': expires_at})
                    module.exit_json(changed=True, msg="Successfully recreated access token", access_token=gitlab_access_token.access_token_object._attrs)
                else:
                    module.exit_json(changed=False, msg="Access token already exists", access_token=gitlab_access_token.access_token_object._attrs)
            else:
                if recreate == 'never':
                    module.fail_json(msg="Access token already exists and its state is different. It can not be updated without recreating.")
                else:
                    gitlab_access_token.revoke_access_token()
                    gitlab_access_token.create_access_token(group, {'name': name, 'scopes': scopes, 'access_level': access_level, 'expires_at': expires_at})
                    module.exit_json(changed=True, msg="Successfully recreated access token", access_token=gitlab_access_token.access_token_object._attrs)
        else:
            gitlab_access_token.create_access_token(group, {'name': name, 'scopes': scopes, 'access_level': access_level, 'expires_at': expires_at})
            module.exit_json(changed=True, msg="Successfully created access token", access_token=gitlab_access_token.access_token_object._attrs)


if __name__ == '__main__':
    main()
