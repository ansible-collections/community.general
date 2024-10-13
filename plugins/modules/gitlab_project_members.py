#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2021, Sergey Mikhaltsov <metanovii@gmail.com>
# Copyright (c) 2020, Zainab Alsaffar <Zainab.Alsaffar@mail.rit.edu>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gitlab_project_members
short_description: Manage project members on GitLab Server
version_added: 2.2.0
description:
  - This module allows to add and remove members to/from a project, or change a member's access level in a project on GitLab.
author:
  - Sergey Mikhaltsov (@metanovii)
  - Zainab Alsaffar (@zanssa)
requirements:
  - python-gitlab python module <= 1.15.0
  - owner or maintainer rights to project on the GitLab server
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
  project:
    description:
      - The name (or full path) of the GitLab project the member is added to/removed from.
    required: true
    type: str
  gitlab_user:
    description:
      - A username or a list of usernames to add to/remove from the GitLab project.
      - Mutually exclusive with O(gitlab_users_access) and O(gitlab_group).
    type: list
    elements: str
  access_level:
    description:
      - The access level for the user.
      - Required if O(state=present), user state is set to present.
    type: str
    choices: ['guest', 'reporter', 'developer', 'maintainer']
  gitlab_users_access:
    description:
      - Provide a list of user to access level mappings.
      - Every dictionary in this list specifies a user (by username) and the access level the user should have.
      - Mutually exclusive with O(gitlab_user), O(access_level), and O(gitlab_group).
      - Use together with O(purge_users) to remove all users not specified here from the project.
    type: list
    elements: dict
    suboptions:
      name:
        description: A username or a list of usernames to add to/remove from the GitLab project.
        type: str
        required: true
      access_level:
        description:
          - The access level for the user.
          - Required if O(state=present), user state is set to present.
        type: str
        choices: ['guest', 'reporter', 'developer', 'maintainer']
        required: true
    version_added: 3.7.0
  state:
    description:
      - State of the member in the project.
      - On V(present), it adds a user to a GitLab project.
      - On V(absent), it removes a user from a GitLab project.
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
    choices: ['guest', 'reporter', 'developer', 'maintainer']
    version_added: 3.7.0
  gitlab_group:
    description:
      - A list of IDs or the full paths of the groups to share/unshare the project with.
      - Every dictionary in this list specifies a group (by ID or full path) and the access level the group should have.
      - Mutually exclusive with O(gitlab_user), O(access_level) and O(gitlab_users_access).
    type: list
    elements: dict
    version_added: 9.3.0
    suboptions:
      name:
        description: ID or the full path of the group to share/unshare the project with.
        type: str
        required: true
      group_access_level:
        description:
          - The access level for the group.
          - Required if O(state=present), group state is set to present.
        type: str
        choices: ['guest', 'reporter', 'developer', 'maintainer']
        required: false

'''

EXAMPLES = r'''
- name: Add a user to a GitLab Project
  community.general.gitlab_project_members:
    api_url: 'https://gitlab.example.com'
    api_token: 'Your-Private-Token'
    validate_certs: true
    project: projectname
    gitlab_user: username
    access_level: developer
    state: present

- name: Remove a user from a GitLab project
  community.general.gitlab_project_members:
    api_url: 'https://gitlab.example.com'
    api_token: 'Your-Private-Token'
    project: projectname
    gitlab_user: username
    state: absent

- name: Add a list of Users to A GitLab project
  community.general.gitlab_project_members:
    api_url: 'https://gitlab.example.com'
    api_token: 'Your-Private-Token'
    gitlab_project: projectname
    gitlab_user:
      - user1
      - user2
    access_level: developer
    state: present

- name: Add a list of Users with Dedicated Access Levels to A GitLab project
  community.general.gitlab_project_members:
    api_url: 'https://gitlab.example.com'
    api_token: 'Your-Private-Token'
    project: projectname
    gitlab_users_access:
      - name: user1
        access_level: developer
      - name: user2
        access_level: maintainer
    state: present

- name: Add a user, remove all others which might be on this access level
  community.general.gitlab_project_members:
    api_url: 'https://gitlab.example.com'
    api_token: 'Your-Private-Token'
    project: projectname
    gitlab_user: username
    access_level: developer
    purge_users: developer
    state: present

- name: Remove a list of Users with Dedicated Access Levels to A GitLab project
  community.general.gitlab_project_members:
    api_url: 'https://gitlab.example.com'
    api_token: 'Your-Private-Token'
    project: projectname
    gitlab_users_access:
      - name: user1
        access_level: developer
      - name: user2
        access_level: maintainer
    state: absent

- name: Share a project with a list of Groups with Dedicated Access Levels to A GitLab project
  community.general.gitlab_project_members:
    api_url: 'https://gitlab.example.com'
    api_token: 'Your-Private-Token'
    project: projectname
    gitlab_group:
      - name: group1
        group_access_level: developer
      - name: group2
        group_access_level: maintainer
    state: present

- name: Unshare a project with a group
  community.general.gitlab_project_members:
    api_url: 'https://gitlab.example.com'
    api_token: 'Your-Private-Token'
    project: projectname
    gitlab_group:
      - name: group1
    state: absent
'''

RETURN = r''' # '''

from ansible.module_utils.api import basic_auth_argument_spec
from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.general.plugins.module_utils.gitlab import (
    auth_argument_spec, gitlab_authentication, gitlab
)


class GitLabProjectMembers(object):
    def __init__(self, module, gl):
        self._module = module
        self._gitlab = gl

    def get_project(self, project_name):
        try:
            project_exists = self._gitlab.projects.get(project_name)
            return project_exists.id
        except gitlab.exceptions.GitlabGetError as e:
            project_exists = self._gitlab.projects.list(search=project_name, all=False)
            if project_exists:
                return project_exists[0].id

    def get_user_id(self, gitlab_user):
        user_exists = self._gitlab.users.list(username=gitlab_user, all=False)
        if user_exists:
            return user_exists[0].id

    # get all members in a project
    def get_members_in_a_project(self, gitlab_project_id):
        project = self._gitlab.projects.get(gitlab_project_id)
        return project.members.list(all=True)

    # get all groups in a project
    def get_groups_in_a_project(self, gitlab_project_id):
        project = self._gitlab.projects.get(gitlab_project_id)
        return [group['group_id'] for group in project.shared_with_groups]

    # get single member in a project by user name
    def get_member_in_a_project(self, gitlab_project_id, gitlab_user_id):
        member = None
        project = self._gitlab.projects.get(gitlab_project_id)
        try:
            member = project.members.get(gitlab_user_id)
            if member:
                return member
        except gitlab.exceptions.GitlabGetError as e:
            return None

    # check if the user is a member of the project
    def is_user_a_member(self, members, gitlab_user_id):
        for member in members:
            if member.id == gitlab_user_id:
                return True
        return False

    # check if the group is in the project
    def is_group_in_project(self, groups, group_id):
        for gid in groups:
            if gid == group_id:
                return True
        return False

    # add user to a project
    def add_member_to_project(self, gitlab_user_id, gitlab_project_id, access_level):
        project = self._gitlab.projects.get(gitlab_project_id)
        add_member = project.members.create(
            {'user_id': gitlab_user_id, 'access_level': access_level})

    # remove user from a project
    def remove_user_from_project(self, gitlab_user_id, gitlab_project_id):
        project = self._gitlab.projects.get(gitlab_project_id)
        project.members.delete(gitlab_user_id)

    # get user's access level
    def get_user_access_level(self, members, gitlab_user_id):
        for member in members:
            if member.id == gitlab_user_id:
                return member.access_level

    # update user's access level in a project
    def update_user_access_level(self, members, gitlab_user_id, access_level):
        for member in members:
            if member.id == gitlab_user_id:
                member.access_level = access_level
                member.save()

    def get_group_id(self, group_name):
        try:
            group_exists = self._gitlab.groups.get(group_name)
            return group_exists.id
        except gitlab.exceptions.GitlabGetError as e:
            return None

    # share project with a group
    def share_project_with_group(self, gitlab_project_id, group_id, access_level):
        project = self._gitlab.projects.get(gitlab_project_id)
        project.share(group_id, access_level)

    # unshare project with a group
    def unshare_project_with_group(self, gitlab_project_id, group_id):
        project = self._gitlab.projects.get(gitlab_project_id)
        project.unshare(group_id)


def main():
    argument_spec = basic_auth_argument_spec()
    argument_spec.update(auth_argument_spec())
    argument_spec.update(dict(
        project=dict(type='str', required=True),
        gitlab_user=dict(type='list', elements='str'),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        access_level=dict(type='str', choices=['guest', 'reporter', 'developer', 'maintainer']),
        purge_users=dict(type='list', elements='str', choices=[
                         'guest', 'reporter', 'developer', 'maintainer']),
        gitlab_users_access=dict(
            type='list',
            elements='dict',
            options=dict(
                name=dict(type='str', required=True),
                access_level=dict(type='str', choices=[
                                  'guest', 'reporter', 'developer', 'maintainer'], required=True),
            )
        ),
        gitlab_group=dict(
            type='list',
            elements='dict',
            options=dict(
                name=dict(type='str', required=True),
                group_access_level=dict(type='str', choices=[
                    'guest', 'reporter', 'developer', 'maintainer'], required=False),
            )
        ),
    ))

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[
            ['api_username', 'api_token'],
            ['api_username', 'api_oauth_token'],
            ['api_username', 'api_job_token'],
            ['api_token', 'api_oauth_token'],
            ['api_token', 'api_job_token'],
            ['gitlab_user', 'gitlab_users_access', 'gitlab_group'],
            ['access_level', 'gitlab_users_access', 'gitlab_group'],
        ],
        required_together=[
            ['api_username', 'api_password'],
            ['gitlab_user', 'access_level'],
        ],
        required_one_of=[
            ['api_username', 'api_token', 'api_oauth_token', 'api_job_token'],
            ['gitlab_user', 'gitlab_users_access', 'gitlab_group'],
        ],
        required_if=[
            ['state', 'present', ['access_level', 'gitlab_users_access', 'gitlab_group'], True],
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
    }

    gitlab_project = module.params['project']
    state = module.params['state']
    access_level = module.params['access_level']
    purge_users = module.params['purge_users']
    gitlab_users_access = []
    # initializing for the main loop
    gitlab_groups = []

    if purge_users:
        purge_users = [access_level_int[level] for level in purge_users]

    project = GitLabProjectMembers(module, gl)

    gitlab_project_id = project.get_project(gitlab_project)

    # project doesn't exist
    if not gitlab_project_id:
        module.fail_json(msg="project '%s' not found." % gitlab_project)

    members = []
    groups = []
    if module.params['gitlab_user'] is not None:
        gitlab_users = module.params['gitlab_user']
        for gl_user in gitlab_users:
            gitlab_users_access.append(
                {'name': gl_user, 'access_level': access_level_int[access_level] if access_level else None})
    elif module.params['gitlab_users_access'] is not None:
        gitlab_users_access = module.params['gitlab_users_access']
        for user_level in gitlab_users_access:
            user_level['access_level'] = access_level_int[user_level['access_level']]
    elif module.params['gitlab_group'] is not None:
        gitlab_groups = module.params['gitlab_group']
        groups = project.get_groups_in_a_project(gitlab_project_id)

    if gitlab_groups:
        pass
    elif len(gitlab_users_access) == 1 and not purge_users:
        # only single user given
        members = [project.get_member_in_a_project(
            gitlab_project_id, project.get_user_id(gitlab_users_access[0]['name']))]
        if members[0] is None:
            members = []
    elif len(gitlab_users_access) > 1 or purge_users:
        # list of users given
        members = project.get_members_in_a_project(gitlab_project_id)
    else:
        module.exit_json(changed='OK', result="Nothing to do, please give at least one user or group or set purge_users true.",
                         result_data=[])

    changed = False
    error = False
    changed_users = []
    changed_groups = []
    changed_data = []

    if gitlab_users_access:
        for gitlab_user in gitlab_users_access:
            gitlab_user_id = project.get_user_id(gitlab_user['name'])

            # user doesn't exist
            if not gitlab_user_id:
                if state == 'absent':
                    changed_users.append("user '%s' not found, and thus also not part of the project" % gitlab_user['name'])
                    changed_data.append({'gitlab_user': gitlab_user['name'], 'result': 'OK',
                                        'msg': "user '%s' not found, and thus also not part of the project" % gitlab_user['name']})
                else:
                    error = True
                    changed_users.append("user '%s' not found." % gitlab_user['name'])
                    changed_data.append({'gitlab_user': gitlab_user['name'], 'result': 'FAILED',
                                        'msg': "user '%s' not found." % gitlab_user['name']})
                continue

            is_user_a_member = project.is_user_a_member(members, gitlab_user_id)

            # check if the user is a member in the project
            if not is_user_a_member:
                if state == 'present':
                    # add user to the project
                    try:
                        if not module.check_mode:
                            project.add_member_to_project(gitlab_user_id, gitlab_project_id, gitlab_user['access_level'])
                        changed = True
                        changed_users.append("Successfully added user '%s' to project" % gitlab_user['name'])
                        changed_data.append({'gitlab_user': gitlab_user['name'], 'result': 'CHANGED',
                                            'msg': "Successfully added user '%s' to project" % gitlab_user['name']})
                    except (gitlab.exceptions.GitlabCreateError) as e:
                        error = True
                        changed_users.append("Failed to updated the access level for the user, '%s'" % gitlab_user['name'])
                        changed_data.append({'gitlab_user': gitlab_user['name'], 'result': 'FAILED',
                                            'msg': "Not allowed to add the access level for the member, %s: %s" % (gitlab_user['name'], e)})
                # state as absent
                else:
                    changed_users.append("User, '%s', is not a member in the project. No change to report" % gitlab_user['name'])
                    changed_data.append({'gitlab_user': gitlab_user['name'], 'result': 'OK',
                                        'msg': "User, '%s', is not a member in the project. No change to report" % gitlab_user['name']})
            # in case that a user is a member
            else:
                if state == 'present':
                    # compare the access level
                    user_access_level = project.get_user_access_level(members, gitlab_user_id)
                    if user_access_level == gitlab_user['access_level']:
                        changed_users.append("User, '%s', is already a member in the project. No change to report" % gitlab_user['name'])
                        changed_data.append({'gitlab_user': gitlab_user['name'], 'result': 'OK',
                                            'msg': "User, '%s', is already a member in the project. No change to report" % gitlab_user['name']})
                    else:
                        # update the access level for the user
                        try:
                            if not module.check_mode:
                                project.update_user_access_level(members, gitlab_user_id, gitlab_user['access_level'])
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
                    # remove the user from the project
                    try:
                        if not module.check_mode:
                            project.remove_user_from_project(gitlab_user_id, gitlab_project_id)
                        changed = True
                        changed_users.append("Successfully removed user, '%s', from the project" % gitlab_user['name'])
                        changed_data.append({'gitlab_user': gitlab_user['name'], 'result': 'CHANGED',
                                            'msg': "Successfully removed user, '%s', from the project" % gitlab_user['name']})
                    except (gitlab.exceptions.GitlabDeleteError) as e:
                        error = True
                        changed_users.append("Failed to removed user, '%s', from the project" % gitlab_user['name'])
                        changed_data.append({'gitlab_user': gitlab_user['name'], 'result': 'FAILED',
                                            'msg': "Failed to remove user, '%s' from the project: %s" % (gitlab_user['name'], e)})

        # if state = present and purge_users set delete users which are in members having give access level but not in gitlab_users
        if state == 'present' and purge_users:
            uppercase_names_in_gitlab_users_access = []
            for name in gitlab_users_access:
                uppercase_names_in_gitlab_users_access.append(name['name'].upper())

            for member in members:
                if member.access_level in purge_users and member.username.upper() not in uppercase_names_in_gitlab_users_access:
                    try:
                        if not module.check_mode:
                            project.remove_user_from_project(member.id, gitlab_project_id)
                        changed = True
                        changed_users.append("Successfully removed user '%s', from project. Was not in given list" % member.username)
                        changed_data.append({'gitlab_user': member.username, 'result': 'CHANGED',
                                            'msg': "Successfully removed user '%s', from project. Was not in given list" % member.username})
                    except (gitlab.exceptions.GitlabDeleteError) as e:
                        error = True
                        changed_users.append("Failed to removed user, '%s', from the project" % gitlab_user['name'])
                        changed_data.append({'gitlab_user': gitlab_user['name'], 'result': 'FAILED',
                                            'msg': "Failed to remove user, '%s' from the project: %s" % (gitlab_user['name'], e)})

        if len(gitlab_users_access) == 1 and error:
            # if single user given and an error occurred return error for list errors will be per user
            module.fail_json(msg="FAILED: '%s '" % changed_users[0], result_data=changed_data)
        elif error:
            module.fail_json(
                msg='FAILED: At least one given user/permission could not be set', result_data=changed_data)

        module.exit_json(changed=changed, msg='Successfully set memberships', result="\n".join(changed_users), result_data=changed_data)
    elif gitlab_groups:
        # group logic goes here
        for gitlab_group in gitlab_groups:
            group_id = project.get_group_id(gitlab_group['name'])

            # group doesn't exist
            if not group_id:
                if state == 'absent':
                    changed_groups.append("group '%s' not found, and thus also not part of the project" % gitlab_group['name'])
                    changed_data.append({'gitlab_group': gitlab_group['name'], 'result': 'OK',
                                        'msg': "group '%s' not found, and thus also not part of the project" % gitlab_group['name']})
                else:
                    error = True
                    changed_groups.append("group '%s' not found." % gitlab_group['name'])
                    changed_data.append({'gitlab_group': gitlab_group['name'], 'result': 'FAILED',
                                        'msg': "group '%s' not found." % gitlab_group['name']})
                continue
            is_group_in_project = project.is_group_in_project(groups, group_id)

            # check if the group is in the project
            if not is_group_in_project:
                if state == 'present':
                    # share project with the group
                    try:
                        if not module.check_mode:
                            project.share_project_with_group(gitlab_project_id, group_id, access_level_int[gitlab_group['group_access_level']])
                        changed = True
                        changed_groups.append("Successfully shared project with group '%s'" % gitlab_group['name'])
                        changed_data.append({'gitlab_group': gitlab_group['name'], 'result': 'CHANGED',
                                            'msg': "Successfully shared project with group '%s'" % gitlab_group['name']})
                    except (gitlab.exceptions.GitlabCreateError) as e:
                        error = False
                        changed_groups.append("Failed to share project with group '%s'" % gitlab_group['name'])
                        changed_data.append({'gitlab_group': gitlab_group['name'], 'result': 'OK',
                                            'msg': "Failed to share project with group '%s': %s. No change to report." % (gitlab_group['name'], e)})
                # state as absent
                else:
                    changed_groups.append("Group, '%s', is not in the project. No change to report" % gitlab_group['name'])
                    changed_data.append({'gitlab_group': gitlab_group['name'], 'result': 'OK',
                                        'msg': "Group, '%s', is not in the project. No change to report" % gitlab_group['name']})
            # in case that a group is in the project
            else:
                if state == 'present':
                    # i have not seen a way to get/update the access level for a group in a project, we are skipping this
                    changed_groups.append("Group, '%s', is already in the project. No change to report" % gitlab_group['name'])
                    changed_data.append({'gitlab_group': gitlab_group['name'], 'result': 'OK',
                                        'msg': "Group, '%s', is already in the project. No change to report" % gitlab_group['name']})
                else:
                    # unshare the project with the group
                    try:
                        if not module.check_mode:
                            project.unshare_project_with_group(gitlab_project_id, group_id)
                        changed = True
                        changed_groups.append("Successfully unshared project with group, '%s'" % gitlab_group['name'])
                        changed_data.append({'gitlab_group': gitlab_group['name'], 'result': 'CHANGED',
                                            'msg': "Successfully unshared project with group, '%s'" % gitlab_group['name']})
                    except (gitlab.exceptions.GitlabDeleteError) as e:
                        error = True
                        changed_groups.append("Failed to unshare project with group, '%s'" % gitlab_group['name'])
                        changed_data.append({'gitlab_group': gitlab_group['name'], 'result': 'FAILED',
                                            'msg': "Failed to unshare project with group, '%s': %s" % (gitlab_group['name'], e)})
        if len(gitlab_groups) == 1 and error:
            # if single group given and an error occurred return error for list errors will be per group
            module.fail_json(msg="FAILED: '%s '" % changed_groups[0], result_data=changed_data)
        elif error:
            module.fail_json(
                msg='FAILED: At least one given group could not be set', result_data=changed_data)

        module.exit_json(changed=changed, msg='Successfully set memberships', result="\n".join(changed_groups), result_data=changed_data)


if __name__ == '__main__':
    main()
