#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Zainab Alsaffar <Zainab.Alsaffar@mail.rit.edu>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
---
module: gitlab_group_members
short_description: Manage group members on GitLab Server
description:
    - This module allows to add and remove members to/from a group, or change a member's access level in a group on GitLab.
version_added: '1.2.0'
author: 'Zainab Alsaffar (@zanssa)'
requirments:
    - python-gitlab python module <= 1.15.0
    - administrator rights on the GitLab server
options:
    server_url:
        description:
            - URL of a GitLab server.
        required: true
        type: str
    access_token:
        description:
            - A personal access token to authenticate with the GitLab API.
        required: true
        type: str
    gitlab_group:
        description:
            - The name of the GitLab group you want to add a member to.
        required: true
        type: str
    gitlab_user:
        description:
            - The username of the member you want to add to the GitLab group.
        required: true
        type: str
    access_level:
        description:
            - The access level for the user.
            - Required if I(state=present), user state is set to present.
        type: str
        choices: ['guest', 'reporter', 'developer', 'maintainer', 'owner']
    state:
        description:
            - State of the member in the group.
            - On C(present), it will add a user to a GitLab group.
            - On C(absent), will remove a user from a GitLab group.
        choices: ['present', 'absent']
        default: 'present'
        type: str
notes: Supports C(check_mode).
'''

EXAMPLES = '''
- name: Add a user to a GitLab Group
  community.general.gitlab_group_members:
    server_url: 'https://gitlab.example.com'
    access_token: 'Your-Private-Token'
    gitlab_group: groupname
    gitlab_user: username
    access_level: developer
    state: present

- name: Remove a user from a GitLab Group
  community.general.gitlab_group_members:
    server_url: 'https://gitlab.example.com'
    access_token: 'Your-Private-Token'
    gitlab_group: groupname
    gitlab_user: username
    state: absent
'''

RETURN = '''
'''

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
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

    # check if user exists
    def does_user_exist(self, gitlab_user):
        return self._gitlab.users.list(username=gitlab_user)[0]

    # check if group exists
    def does_group_exist(self, gitlab_group):
        return self._gitlab.groups.list(search=gitlab_group)[0]

    # check if the user is a member of the group
    def is_user_a_member(self, gitlab_group_id, gitlab_user_id):
        group = self._gitlab.groups.get(gitlab_group_id)
        members = group.members.list()
        for member in members:
            if member.id == gitlab_user_id:
                return True
        return False

    # add user to a group
    def add_member_to_group(self, gitlab_user_id, gitlab_group_id, access_level):
        try:
            if self._module.check_mode:
                self._module.exit_json(changed=True)

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
            if self._module.check_mode:
                self._module.exit_json(changed=True)

            group = self._gitlab.groups.get(gitlab_group_id)
            group.members.delete(gitlab_user_id)

        except (gitlab.exceptions.GitlabDeleteError) as e:
            self._module.fail_json(
                msg="Failed to remove member from GitLab group, ID %s: %s" % (gitlab_group_id, e))


def main():
    module = AnsibleModule(
        argument_spec=dict(
            server_url=dict(type='str', required=True),
            access_token=dict(type='str', required=True, no_log=True),
            gitlab_group=dict(type='str', required=True),
            gitlab_user=dict(type='str', required=True),
            state=dict(type='str', default='present', choices=['present', 'absent']),
            access_level=dict(typr='str', required=False, choices=['guest', 'reporter', 'developer', 'maintainer', 'owner'])
        ),
        supports_check_mode=True
    )

    if not HAS_PY_GITLAB:
        module.fail_json(msg=missing_required_lib('python-gitlab', url='https://python-gitlab.readthedocs.io/en/stable/'), exception=GITLAB_IMP_ERR)

    server_url = module.params['server_url']
    access_token = module.params['access_token']
    gitlab_group = module.params['gitlab_group']
    gitlab_user = module.params['gitlab_user']
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
    try:
        gl = gitlab.Gitlab(server_url, private_token=access_token)
    except (gitlab.exceptions.GitlabAuthenticationError, gitlab.exceptions.GitlabGetError) as e:
        module.fail_json(msg="Failed to authenticate to GitLab Server: %s: %s" % (server_url, e))

    group = GitLabGroup(module, gl)

    user_exists = group.does_user_exist(gitlab_user)
    group_exists = group.does_group_exist(gitlab_group)

    # group doesn't exist
    if not group_exists:
        module.fail_json(msg="group '%s' not found." % gitlab_group)

    # user doesn't exist
    if not user_exists:
        module.fail_json(msg="user '%s' not found." % gitlab_user)

    if group_exists:
        # get group id
        gitlab_group_id = group_exists.id

        if user_exists:
            #get user id
            gitlab_user_id = user_exists.id
            is_user_a_member = group.is_user_a_member(gitlab_group_id, gitlab_user_id)

            # check if the user is a member in the group
            if not is_user_a_member:
                if state == 'present':
                    if not access_level:
                        module.fail_json(msg="Access level must be entered for adding member to GitLab group '%s'." % gitlab_user)

                    # add user to the group
                    group.add_member_to_group(gitlab_user_id, gitlab_group_id, access_level)
                    module.exit_json(changed=True, result="Successfully added user to the group '%s'." % gitlab_user)

                else:
                    module.exit_json(changed=False, result="User is not a member in the group. No change to report '%s'" % gitlab_user)
            # in case that a user is a member
            else:
                if state == 'present':
                    module.exit_json(changed=False, result="User is already a member in the group. No change to report '%s'" % gitlab_user)
                else:
                    # remove the user from the group
                    group.remove_user_from_group(gitlab_user_id, gitlab_group_id)
                    module.exit_json(changed=True, result="Successfully removed user from the group '%s'" % gitlab_user)


if __name__ == '__main__':
    main()
