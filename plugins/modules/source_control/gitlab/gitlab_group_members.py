#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Zainab Alsaffar <Zainab.Alsaffar@mail.rit.edu>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

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
extends_documentation_fragment: community.general.auth_basic
options:
    api_token:
        description:
            - A personal access token to authenticate with the GitLab API.
        required: true
        type: str
    gitlab_group:
        description:
            - The name of the GitLab group the member is added to/removed from.
        required: true
        type: str
    gitlab_user:
        description:
            - A username or a list of usernames to add to/remove from the GitLab group.
        required: true
        type: list
        elements: str
    access_level:
        description:
            - The access level for the user.
            - Required if I(state=present), user state is set to present.
        type: str
        choices: ['guest', 'reporter', 'developer', 'maintainer', 'owner']
    state:
        description:
            - State of the member in the group.
            - On C(present), it adds a user to a GitLab group.
            - On C(absent), it removes a user from a GitLab group.
        choices: ['present', 'absent']
        default: 'present'
        type: str
    purge_users:
        description:
            - Adds/remove users of the given access_level to match the given gitlab_user list.
        type: bool
        default: False
        version_added: 3.6.0
notes:
    - Supports C(check_mode).
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
'''

RETURN = r''' # '''

from ansible.module_utils.api import basic_auth_argument_spec
from ansible.module_utils.basic import AnsibleModule, missing_required_lib

from ansible_collections.community.general.plugins.module_utils.gitlab import gitlabAuthentication

import traceback

try:
    import gitlab
    HAS_PY_GITLAB = True
except ImportError:
    GITLAB_IMP_ERR = traceback.format_exc()
    HAS_PY_GITLAB = False


class GitLabGroup(object):
    def __init__(self, module, gl):
        self._module = module
        self._gitlab = gl

    # get user id if the user exists
    def get_user_id(self, gitlab_user):
        user_exists = self._gitlab.users.list(username=gitlab_user)
        if user_exists:
            return user_exists[0].id

    # get group id if group exists
    def get_group_id(self, gitlab_group):
        group_exists = self._gitlab.groups.list(search=gitlab_group)
        if group_exists:
            return group_exists[0].id

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
        try:
            group = self._gitlab.groups.get(gitlab_group_id)
            add_member = group.members.create(
                {'user_id': gitlab_user_id, 'access_level': access_level})

            if add_member:
                return add_member.username

        except (gitlab.exceptions.GitlabCreateError) as e:
            self._module.fail_json(
                msg="Failed to add member to the Group, Group ID %s: %s" % (gitlab_group_id, e))

    # remove user from a group
    def remove_user_from_group(self, gitlab_user_id, gitlab_group_id):
        try:
            group = self._gitlab.groups.get(gitlab_group_id)
            group.members.delete(gitlab_user_id)

        except (gitlab.exceptions.GitlabDeleteError) as e:
            self._module.fail_json(
                msg="Failed to remove member from GitLab group, ID %s: %s" % (gitlab_group_id, e))

    # get user's access level
    def get_user_access_level(self, members, gitlab_user_id):
        for member in members:
            if member.id == gitlab_user_id:
                return member.access_level

    # update user's access level in a group
    def update_user_access_level(self, members, gitlab_user_id, access_level):
        for member in members:
            if member.id == gitlab_user_id:
                try:
                    member.access_level = access_level
                    member.save()
                except (gitlab.exceptions.GitlabCreateError) as e:
                    self._module.fail_json(
                        msg="Failed to update the access level for the member, %s: %s" % (gitlab_user_id, e))


def main():
    argument_spec = basic_auth_argument_spec()
    argument_spec.update(dict(
        api_token=dict(type='str', required=True, no_log=True),
        gitlab_group=dict(type='str', required=True),
        gitlab_user=dict(type='list', elements='str', required=True),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        access_level=dict(type='str', required=False, choices=['guest', 'reporter', 'developer', 'maintainer', 'owner']),
        purge_users=dict(type='bool', required=False, default=False)
    ))

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[
            ['api_username', 'api_token'],
            ['api_password', 'api_token'],
        ],
        required_together=[
            ['api_username', 'api_password'],
        ],
        required_one_of=[
            ['api_username', 'api_token'],
        ],
        required_if=[
            ['state', 'present', ['access_level']],
        ],
        supports_check_mode=True,
    )

    if not HAS_PY_GITLAB:
        module.fail_json(msg=missing_required_lib('python-gitlab', url='https://python-gitlab.readthedocs.io/en/stable/'), exception=GITLAB_IMP_ERR)

    gitlab_group = module.params['gitlab_group']
    state = module.params['state']
    access_level = module.params['access_level']

    # convert access level string input to int
    if access_level:
        access_level_int = {
            'guest': gitlab.GUEST_ACCESS,
            'reporter': gitlab.REPORTER_ACCESS,
            'developer': gitlab.DEVELOPER_ACCESS,
            'maintainer': gitlab.MAINTAINER_ACCESS,
            'owner': gitlab.OWNER_ACCESS
        }
        access_level = access_level_int[access_level]

    # connect to gitlab server
    gl = gitlabAuthentication(module)

    group = GitLabGroup(module, gl)

    gitlab_group_id = group.get_group_id(gitlab_group)

    # group doesn't exist
    if not gitlab_group_id:
        module.fail_json(msg="group '%s' not found." % gitlab_group)

    members = []
    gitlab_users = module.params['gitlab_user']
    purge_users = module.params['purge_users']
    if len(gitlab_users) == 1:
        # only single user given
        members = [group.get_member_in_a_group(gitlab_group_id, group.get_user_id(gitlab_users[0]))]
        if members[0] is None:
            members = []
    elif len(gitlab_users) > 1 or purge_users:
        # list of users given
        members = group.get_members_in_a_group(gitlab_group_id)
    else:
        # something went wrong
        module.fail_json(msg="Please give at least one user or set purge_users true.")

    changed = False
    error = False
    changed_users = []
    changed_data = []

    for gitlab_user in gitlab_users:
        gitlab_user_id = group.get_user_id(gitlab_user)

        # user doesn't exist
        if not gitlab_user_id:
            if state == 'absent':
                changed_users.append("user '%s' not found, and thus also not part of the group" % gitlab_user)
                changed_data.append({'gitlab_user': gitlab_user, 'result': 'OK',
                                     'msg': "user '%s' not found, and thus also not part of the group" % gitlab_user})
            else:
                error = True
                changed_users.append("user '%s' not found." % gitlab_user)
                changed_data.append({'gitlab_user': gitlab_user, 'result': 'FAILED',
                                     'msg': "user '%s' not found." % gitlab_user})

        is_user_a_member = group.is_user_a_member(members, gitlab_user_id)

        # check if the user is a member in the group
        if not is_user_a_member:
            if state == 'present':
                # add user to the group
                if not module.check_mode:
                    group.add_member_to_group(gitlab_user_id, gitlab_group_id, access_level)
                changed = True
                changed_users.append("Successfully added user '%s' to group" % gitlab_user)
                changed_data.append({'gitlab_user': gitlab_user, 'result': 'CHANGED',
                                     'msg': "Successfully added user '%s' to group" % gitlab_user})
            # state as absent
            else:
                changed_users.append("User, '%s', is not a member in the group. No change to report" % gitlab_user)
                changed_data.append({'gitlab_user': gitlab_user, 'result': 'OK',
                                     'msg': "User, '%s', is not a member in the group. No change to report" % gitlab_user})
        # in case that a user is a member
        else:
            if state == 'present':
                # compare the access level
                user_access_level = group.get_user_access_level(members, gitlab_user_id)
                if user_access_level == access_level:
                    changed_users.append("User, '%s', is already a member in the group. No change to report" % gitlab_user)
                    changed_data.append({'gitlab_user': gitlab_user, 'result': 'OK',
                                         'msg': "User, '%s', is already a member in the group. No change to report" % gitlab_user})
                else:
                    # update the access level for the user
                    if not module.check_mode:
                        group.update_user_access_level(members, gitlab_user_id, access_level)
                    changed = True
                    changed_users.append("Successfully updated the access level for the user, '%s'" % gitlab_user)
                    changed_data.append({'gitlab_user': gitlab_user, 'result': 'CHANGED',
                                         'msg': "Successfully updated the access level for the user, '%s'" % gitlab_user})
            else:
                # remove the user from the group
                if not module.check_mode:
                    group.remove_user_from_group(gitlab_user_id, gitlab_group_id)
                changed = True
                changed_users.append("Successfully removed user, '%s', from the group" % gitlab_user)
                changed_data.append({'gitlab_user': gitlab_user, 'result': 'CHANGED',
                                     'msg': "Successfully removed user, '%s', from the group" % gitlab_user})

    # if state = present and purge_users set delete users which are in members having give access level but not in gitlab_users
    if state == 'present' and purge_users:
        for member in members:
            if member.access_level == access_level and member.username.upper() not in [name.upper() for name in gitlab_users]:
                group.remove_user_from_group(member.id, gitlab_group_id)
                changed = True
                changed_users.append("Successfully removed user '%s', from group. Was not in given list" % member.username)
                changed_data.append({'gitlab_user': gitlab_user, 'result': 'CHANGED',
                                     'msg': "Successfully removed user '%s', from group. Was not in given list" % member.username})

    if len(gitlab_user) == 1 and error:
        # if single user given and an error occurred return error for list errors will be per user
        module.fail_json(msg=changed_users[0])
    elif error:
        # iterate results, if all failed set to failed
        single_good = False
        for cd in changed_data:
            if cd.result != 'FAILED':
                single_good = True
        if not single_good:
            module.fail_json(msg='All tasks for all users given failed', result_data=changed_data)

    module.exit_json(changed=changed, result="\n".join(changed_users), result_data=changed_data)


if __name__ == '__main__':
    main()
