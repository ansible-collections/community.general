#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2020, Zainab Alsaffar <Zainab.Alsaffar@mail.rit.edu>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gitlab_group_members
short_description: Manage group members on GitLab Server
description:
  - This module allows to add and remove members to/from a group, or change a member's access level in a group on GitLab.
version_added: '1.2.0'
author: Zainab Alsaffar (@zanssa)
requirements:
  - python-gitlab python module <= 1.15.0
  - administrator rights on the GitLab server
extends_documentation_fragment:
  - community.general.auth_basic
  - community.general.gitlab
  - community.general.attributes

attributes:
  check_mode:
    support: full
  diff_mode:
    support: none

options:
  gitlab_group:
    description:
      - The C(full_path) of the GitLab group the member is added to/removed from.
      - Setting this to C(name) or C(path) has been disallowed since community.general 6.0.0. Use C(full_path) instead.
    required: true
    type: str
  gitlab_user:
    description:
      - A username or a list of usernames to add to/remove from the GitLab group.
      - Mutually exclusive with O(gitlab_users_access).
    type: list
    elements: str
  access_level:
    description:
      - The access level for the user.
      - Required if O(state=present), user state is set to present.
      - Mutually exclusive with O(gitlab_users_access).
    type: str
    choices: ['guest', 'reporter', 'developer', 'maintainer', 'owner']
  gitlab_users_access:
    description:
      - Provide a list of user to access level mappings.
      - Every dictionary in this list specifies a user (by username) and the access level the user should have.
      - Mutually exclusive with O(gitlab_user) and O(access_level).
      - Use together with O(purge_users) to remove all users not specified here from the group.
    type: list
    elements: dict
    suboptions:
      name:
        description: A username or a list of usernames to add to/remove from the GitLab group.
        type: str
        required: true
      access_level:
        description:
          - The access level for the user.
          - Required if O(state=present), user state is set to present.
        type: str
        choices: ['guest', 'reporter', 'developer', 'maintainer', 'owner']
        required: true
    version_added: 3.6.0
  state:
    description:
      - State of the member in the group.
      - On V(present), it adds a user to a GitLab group.
      - On V(absent), it removes a user from a GitLab group.
    choices: ['present', 'absent']
    default: 'present'
    type: str
  purge_users:
    description:
      - Adds/remove users of the given access_level to match the given O(gitlab_user)/O(gitlab_users_access) list.
        If omitted do not purge orphaned members.
      - Is only used when O(state=present).
    type: list
    elements: str
    choices: ['guest', 'reporter', 'developer', 'maintainer', 'owner']
    version_added: 3.6.0
'''

EXAMPLES = r'''
- name: Add a user to a GitLab Group
  community.general.gitlab_group_members:
    api_url: 'https://gitlab.example.com'
    api_token: 'Your-Private-Token'
    gitlab_group: groupname
    gitlab_user: username
    access_level: developer
    state: present

- name: Remove a user from a GitLab Group
  community.general.gitlab_group_members:
    api_url: 'https://gitlab.example.com'
    api_token: 'Your-Private-Token'
    gitlab_group: groupname
    gitlab_user: username
    state: absent

- name: Add a list of Users to A GitLab Group
  community.general.gitlab_group_members:
    api_url: 'https://gitlab.example.com'
    api_token: 'Your-Private-Token'
    gitlab_group: groupname
    gitlab_user:
      - user1
      - user2
    access_level: developer
    state: present

- name: Add a list of Users with Dedicated Access Levels to A GitLab Group
  community.general.gitlab_group_members:
    api_url: 'https://gitlab.example.com'
    api_token: 'Your-Private-Token'
    gitlab_group: groupname
    gitlab_users_access:
      - name: user1
        access_level: developer
      - name: user2
        access_level: maintainer
    state: present

- name: Add a user, remove all others which might be on this access level
  community.general.gitlab_group_members:
    api_url: 'https://gitlab.example.com'
    api_token: 'Your-Private-Token'
    gitlab_group: groupname
    gitlab_user: username
    access_level: developer
    pruge_users: developer
    state: present

- name: Remove a list of Users with Dedicated Access Levels to A GitLab Group
  community.general.gitlab_group_members:
    api_url: 'https://gitlab.example.com'
    api_token: 'Your-Private-Token'
    gitlab_group: groupname
    gitlab_users_access:
      - name: user1
        access_level: developer
      - name: user2
        access_level: maintainer
    state: absent
'''

RETURN = r''' # '''

from ansible.module_utils.api import basic_auth_argument_spec
from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.general.plugins.module_utils.gitlab import (
    auth_argument_spec, gitlab_authentication, gitlab, list_all_kwargs
)


class GitLabGroup(object):
    def __init__(self, module, gl):
        self._module = module
        self._gitlab = gl

    # get user id if the user exists
    def get_user_id(self, gitlab_user):
        return next(
            (u.id for u in self._gitlab.users.list(username=gitlab_user, **list_all_kwargs)),
            None
        )

    # get group id if group exists
    def get_group_id(self, gitlab_group):
        return next(
            (
                g.id for g in self._gitlab.groups.list(search=gitlab_group, **list_all_kwargs)
                if g.full_path == gitlab_group
            ),
            None
        )

    # get all members in a group
    def get_members_in_a_group(self, gitlab_group_id):
        group = self._gitlab.groups.get(gitlab_group_id)
        return group.members.list(all=True)

    # get single member in a group by user name
    def get_member_in_a_group(self, gitlab_group_id, gitlab_user_id):
        member = None
        group = self._gitlab.groups.get(gitlab_group_id)
        try:
            member = group.members.get(gitlab_user_id)
            if member:
                return member
        except gitlab.exceptions.GitlabGetError as e:
            return None

    # check if the user is a member of the group
    def is_user_a_member(self, members, gitlab_user_id):
        for member in members:
            if member.id == gitlab_user_id:
                return True
        return False

    # add user to a group
    def add_member_to_group(self, gitlab_user_id, gitlab_group_id, access_level):
        group = self._gitlab.groups.get(gitlab_group_id)
        add_member = group.members.create(
            {'user_id': gitlab_user_id, 'access_level': access_level})

    # remove user from a group
    def remove_user_from_group(self, gitlab_user_id, gitlab_group_id):
        group = self._gitlab.groups.get(gitlab_group_id)
        group.members.delete(gitlab_user_id)

    # get user's access level
    def get_user_access_level(self, members, gitlab_user_id):
        for member in members:
            if member.id == gitlab_user_id:
                return member.access_level

    # update user's access level in a group
    def update_user_access_level(self, members, gitlab_user_id, access_level):
        for member in members:
            if member.id == gitlab_user_id:
                member.access_level = access_level
                member.save()


def main():
    argument_spec = basic_auth_argument_spec()
    argument_spec.update(auth_argument_spec())
    argument_spec.update(dict(
        gitlab_group=dict(type='str', required=True),
        gitlab_user=dict(type='list', elements='str'),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        access_level=dict(type='str', choices=['guest', 'reporter', 'developer', 'maintainer', 'owner']),
        purge_users=dict(type='list', elements='str', choices=['guest', 'reporter', 'developer', 'maintainer', 'owner']),
        gitlab_users_access=dict(
            type='list',
            elements='dict',
            options=dict(
                name=dict(type='str', required=True),
                access_level=dict(type='str', choices=['guest', 'reporter', 'developer', 'maintainer', 'owner'], required=True),
            )
        ),
    ))

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[
            ['api_username', 'api_token'],
            ['gitlab_user', 'gitlab_users_access'],
            ['access_level', 'gitlab_users_access'],
            ['api_username', 'api_oauth_token'],
            ['api_username', 'api_job_token'],
            ['api_token', 'api_oauth_token'],
            ['api_token', 'api_job_token'],
        ],
        required_together=[
            ['api_username', 'api_password'],
            ['gitlab_user', 'access_level'],
        ],
        required_one_of=[
            ['api_username', 'api_token', 'api_oauth_token', 'api_job_token'],
            ['gitlab_user', 'gitlab_users_access'],
        ],
        required_if=[
            ['state', 'present', ['access_level', 'gitlab_users_access'], True],
        ],
        supports_check_mode=True,
    )

    # check prerequisites and connect to gitlab server
    gl = gitlab_authentication(module)

    access_level_int = {
        'guest': gitlab.const.GUEST_ACCESS,
        'reporter': gitlab.const.REPORTER_ACCESS,
        'developer': gitlab.const.DEVELOPER_ACCESS,
        'maintainer': gitlab.const.MAINTAINER_ACCESS,
        'owner': gitlab.const.OWNER_ACCESS,
    }

    gitlab_group = module.params['gitlab_group']
    state = module.params['state']
    access_level = module.params['access_level']
    purge_users = module.params['purge_users']

    if purge_users:
        purge_users = [access_level_int[level] for level in purge_users]

    group = GitLabGroup(module, gl)

    gitlab_group_id = group.get_group_id(gitlab_group)

    # group doesn't exist
    if not gitlab_group_id:
        module.fail_json(msg="group '%s' not found." % gitlab_group)

    members = []
    if module.params['gitlab_user'] is not None:
        gitlab_users_access = []
        gitlab_users = module.params['gitlab_user']
        for gl_user in gitlab_users:
            gitlab_users_access.append({'name': gl_user, 'access_level': access_level_int[access_level] if access_level else None})
    elif module.params['gitlab_users_access'] is not None:
        gitlab_users_access = module.params['gitlab_users_access']
        for user_level in gitlab_users_access:
            user_level['access_level'] = access_level_int[user_level['access_level']]

    if len(gitlab_users_access) == 1 and not purge_users:
        # only single user given
        members = [group.get_member_in_a_group(gitlab_group_id, group.get_user_id(gitlab_users_access[0]['name']))]
        if members[0] is None:
            members = []
    elif len(gitlab_users_access) > 1 or purge_users:
        # list of users given
        members = group.get_members_in_a_group(gitlab_group_id)
    else:
        module.exit_json(changed='OK', result="Nothing to do, please give at least one user or set purge_users true.",
                         result_data=[])

    changed = False
    error = False
    changed_users = []
    changed_data = []

    for gitlab_user in gitlab_users_access:
        gitlab_user_id = group.get_user_id(gitlab_user['name'])

        # user doesn't exist
        if not gitlab_user_id:
            if state == 'absent':
                changed_users.append("user '%s' not found, and thus also not part of the group" % gitlab_user['name'])
                changed_data.append({'gitlab_user': gitlab_user['name'], 'result': 'OK',
                                     'msg': "user '%s' not found, and thus also not part of the group" % gitlab_user['name']})
            else:
                error = True
                changed_users.append("user '%s' not found." % gitlab_user['name'])
                changed_data.append({'gitlab_user': gitlab_user['name'], 'result': 'FAILED',
                                     'msg': "user '%s' not found." % gitlab_user['name']})
            continue

        is_user_a_member = group.is_user_a_member(members, gitlab_user_id)

        # check if the user is a member in the group
        if not is_user_a_member:
            if state == 'present':
                # add user to the group
                try:
                    if not module.check_mode:
                        group.add_member_to_group(gitlab_user_id, gitlab_group_id, gitlab_user['access_level'])
                    changed = True
                    changed_users.append("Successfully added user '%s' to group" % gitlab_user['name'])
                    changed_data.append({'gitlab_user': gitlab_user['name'], 'result': 'CHANGED',
                                         'msg': "Successfully added user '%s' to group" % gitlab_user['name']})
                except (gitlab.exceptions.GitlabCreateError) as e:
                    error = True
                    changed_users.append("Failed to updated the access level for the user, '%s'" % gitlab_user['name'])
                    changed_data.append({'gitlab_user': gitlab_user['name'], 'result': 'FAILED',
                                         'msg': "Not allowed to add the access level for the member, %s: %s" % (gitlab_user['name'], e)})
            # state as absent
            else:
                changed_users.append("User, '%s', is not a member in the group. No change to report" % gitlab_user['name'])
                changed_data.append({'gitlab_user': gitlab_user['name'], 'result': 'OK',
                                     'msg': "User, '%s', is not a member in the group. No change to report" % gitlab_user['name']})
        # in case that a user is a member
        else:
            if state == 'present':
                # compare the access level
                user_access_level = group.get_user_access_level(members, gitlab_user_id)
                if user_access_level == gitlab_user['access_level']:
                    changed_users.append("User, '%s', is already a member in the group. No change to report" % gitlab_user['name'])
                    changed_data.append({'gitlab_user': gitlab_user['name'], 'result': 'OK',
                                         'msg': "User, '%s', is already a member in the group. No change to report" % gitlab_user['name']})
                else:
                    # update the access level for the user
                    try:
                        if not module.check_mode:
                            group.update_user_access_level(members, gitlab_user_id, gitlab_user['access_level'])
                        changed = True
                        changed_users.append("Successfully updated the access level for the user, '%s'" % gitlab_user['name'])
                        changed_data.append({'gitlab_user': gitlab_user['name'], 'result': 'CHANGED',
                                             'msg': "Successfully updated the access level for the user, '%s'" % gitlab_user['name']})
                    except (gitlab.exceptions.GitlabUpdateError) as e:
                        error = True
                        changed_users.append("Failed to updated the access level for the user, '%s'" % gitlab_user['name'])
                        changed_data.append({'gitlab_user': gitlab_user['name'], 'result': 'FAILED',
                                             'msg': "Not allowed to update the access level for the member, %s: %s" % (gitlab_user['name'], e)})
            else:
                # remove the user from the group
                try:
                    if not module.check_mode:
                        group.remove_user_from_group(gitlab_user_id, gitlab_group_id)
                    changed = True
                    changed_users.append("Successfully removed user, '%s', from the group" % gitlab_user['name'])
                    changed_data.append({'gitlab_user': gitlab_user['name'], 'result': 'CHANGED',
                                         'msg': "Successfully removed user, '%s', from the group" % gitlab_user['name']})
                except (gitlab.exceptions.GitlabDeleteError) as e:
                    error = True
                    changed_users.append("Failed to removed user, '%s', from the group" % gitlab_user['name'])
                    changed_data.append({'gitlab_user': gitlab_user['name'], 'result': 'FAILED',
                                         'msg': "Failed to remove user, '%s' from the group: %s" % (gitlab_user['name'], e)})

    # if state = present and purge_users set delete users which are in members having give access level but not in gitlab_users
    if state == 'present' and purge_users:
        uppercase_names_in_gitlab_users_access = []
        for name in gitlab_users_access:
            uppercase_names_in_gitlab_users_access.append(name['name'].upper())

        for member in members:
            if member.access_level in purge_users and member.username.upper() not in uppercase_names_in_gitlab_users_access:
                try:
                    if not module.check_mode:
                        group.remove_user_from_group(member.id, gitlab_group_id)
                    changed = True
                    changed_users.append("Successfully removed user '%s', from group. Was not in given list" % member.username)
                    changed_data.append({'gitlab_user': member.username, 'result': 'CHANGED',
                                         'msg': "Successfully removed user '%s', from group. Was not in given list" % member.username})
                except (gitlab.exceptions.GitlabDeleteError) as e:
                    error = True
                    changed_users.append("Failed to removed user, '%s', from the group" % gitlab_user['name'])
                    changed_data.append({'gitlab_user': gitlab_user['name'], 'result': 'FAILED',
                                         'msg': "Failed to remove user, '%s' from the group: %s" % (gitlab_user['name'], e)})

    if len(gitlab_users_access) == 1 and error:
        # if single user given and an error occurred return error for list errors will be per user
        module.fail_json(msg="FAILED: '%s '" % changed_users[0], result_data=changed_data)
    elif error:
        module.fail_json(msg='FAILED: At least one given user/permission could not be set', result_data=changed_data)

    module.exit_json(changed=changed, msg='Successfully set memberships', result="\n".join(changed_users), result_data=changed_data)


if __name__ == '__main__':
    main()
