#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2021, Lennert Mertens (lennert@nubera.be)
# Copyright (c) 2019, Guillaume Martinez (lunik@tiwabbit.fr)
# Copyright (c) 2015, Werner Dijkerman (ikben@werner-dijkerman.nl)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: gitlab_user
short_description: Creates/updates/deletes/blocks/unblocks GitLab Users
description:
  - When the user does not exist in GitLab, it will be created.
  - When the user exists and state=absent, the user will be deleted.
  - When the user exists and state=blocked, the user will be blocked.
  - When changes are made to user, the user will be updated.
notes:
  - From community.general 0.2.0 and onwards, name, email and password are optional while deleting the user.
author:
  - Werner Dijkerman (@dj-wasabi)
  - Guillaume Martinez (@Lunik)
  - Lennert Mertens (@LennertMertens)
  - Stef Graces (@stgrace)
requirements:
  - python-gitlab python module
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
  name:
    description:
      - Name of the user you want to create.
      - Required only if O(state=present).
    type: str
  username:
    description:
      - The username of the user.
    required: true
    type: str
  password:
    description:
      - The password of the user.
      - GitLab server enforces minimum password length to 8, set this value with 8 or more characters.
    type: str
  reset_password:
    description:
      - Whether the user can change its password or not.
    default: false
    type: bool
    version_added: 3.3.0
  email:
    description:
      - The email that belongs to the user.
      - Required only if O(state=present).
    type: str
  sshkey_name:
    description:
      - The name of the SSH public key.
    type: str
  sshkey_file:
    description:
      - The SSH public key itself.
    type: str
  sshkey_expires_at:
    description:
      - The expiration date of the SSH public key in ISO 8601 format C(YYYY-MM-DDTHH:MM:SSZ).
      - This is only used when adding new SSH public keys.
    type: str
    version_added: 3.1.0
  group:
    description:
      - Id or Full path of parent group in the form of group/name.
      - Add user as a member to this group.
    type: str
  access_level:
    description:
      - The access level to the group. One of the following can be used.
      - guest
      - reporter
      - developer
      - master (alias for maintainer)
      - maintainer
      - owner
    default: guest
    type: str
    choices: ["guest", "reporter", "developer", "master", "maintainer", "owner"]
  state:
    description:
      - Create, delete or block a user.
    default: present
    type: str
    choices: ["present", "absent", "blocked", "unblocked"]
  confirm:
    description:
      - Require confirmation.
    type: bool
    default: true
  isadmin:
    description:
      - Grant admin privileges to the user.
    type: bool
    default: false
  external:
    description:
      - Define external parameter for this user.
    type: bool
    default: false
  identities:
    description:
      - List of identities to be added/updated for this user.
      - To remove all other identities from this user, set O(overwrite_identities=true).
    type: list
    elements: dict
    suboptions:
      provider:
        description:
          - The name of the external identity provider
        type: str
      extern_uid:
        description:
          - User ID for external identity.
        type: str
    version_added: 3.3.0
  overwrite_identities:
    description:
      - Overwrite identities with identities added in this module.
      - This means that all identities that the user has and that are not listed in O(identities) are removed from the user.
      - This is only done if a list is provided for O(identities). To remove all identities, provide an empty list.
    type: bool
    default: false
    version_added: 3.3.0
'''

EXAMPLES = '''
- name: "Delete GitLab User"
  community.general.gitlab_user:
    api_url: https://gitlab.example.com/
    api_token: "{{ access_token }}"
    username: myusername
    state: absent

- name: "Create GitLab User"
  community.general.gitlab_user:
    api_url: https://gitlab.example.com/
    validate_certs: true
    api_username: dj-wasabi
    api_password: "MySecretPassword"
    name: My Name
    username: myusername
    password: mysecretpassword
    email: me@example.com
    sshkey_name: MySSH
    sshkey_file: ssh-rsa AAAAB3NzaC1yc...
    state: present
    group: super_group/mon_group
    access_level: owner

- name: "Create GitLab User using external identity provider"
  community.general.gitlab_user:
    api_url: https://gitlab.example.com/
    validate_certs: true
    api_token: "{{ access_token }}"
    name: My Name
    username: myusername
    password: mysecretpassword
    email: me@example.com
    identities:
    - provider: Keycloak
      extern_uid: f278f95c-12c7-4d51-996f-758cc2eb11bc
    state: present
    group: super_group/mon_group
    access_level: owner

- name: "Block GitLab User"
  community.general.gitlab_user:
    api_url: https://gitlab.example.com/
    api_token: "{{ access_token }}"
    username: myusername
    state: blocked

- name: "Unblock GitLab User"
  community.general.gitlab_user:
    api_url: https://gitlab.example.com/
    api_token: "{{ access_token }}"
    username: myusername
    state: unblocked
'''

RETURN = '''
msg:
  description: Success or failure message
  returned: always
  type: str
  sample: "Success"

result:
  description: json parsed response from the server
  returned: always
  type: dict

error:
  description: the error message returned by the GitLab API
  returned: failed
  type: str
  sample: "400: path is already in use"

user:
  description: API object
  returned: always
  type: dict
'''


from ansible.module_utils.api import basic_auth_argument_spec
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native

from ansible_collections.community.general.plugins.module_utils.gitlab import (
    auth_argument_spec, find_group, gitlab_authentication, gitlab, list_all_kwargs
)


class GitLabUser(object):
    def __init__(self, module, gitlab_instance):
        self._module = module
        self._gitlab = gitlab_instance
        self.user_object = None
        self.ACCESS_LEVEL = {
            'guest': gitlab.const.GUEST_ACCESS,
            'reporter': gitlab.const.REPORTER_ACCESS,
            'developer': gitlab.const.DEVELOPER_ACCESS,
            'master': gitlab.const.MAINTAINER_ACCESS,
            'maintainer': gitlab.const.MAINTAINER_ACCESS,
            'owner': gitlab.const.OWNER_ACCESS,
        }

    '''
    @param username Username of the user
    @param options User options
    '''
    def create_or_update_user(self, username, options):
        changed = False
        potentionally_changed = False

        # Because we have already call userExists in main()
        if self.user_object is None:
            user = self.create_user({
                'name': options['name'],
                'username': username,
                'password': options['password'],
                'reset_password': options['reset_password'],
                'email': options['email'],
                'skip_confirmation': not options['confirm'],
                'admin': options['isadmin'],
                'external': options['external'],
                'identities': options['identities'],
            })
            changed = True
        else:
            changed, user = self.update_user(
                self.user_object, {
                    # add "normal" parameters here, put uncheckable
                    # params in the dict below
                    'name': {'value': options['name']},
                    'email': {'value': options['email']},

                    # note: for some attributes like this one the key
                    #   from reading back from server is unfortunately
                    #   different to the one needed for pushing/writing,
                    #   in that case use the optional setter key
                    'is_admin': {
                        'value': options['isadmin'], 'setter': 'admin'
                    },
                    'external': {'value': options['external']},
                    'identities': {'value': options['identities']},
                },
                {
                    # put "uncheckable" params here, this means params
                    # which the gitlab does accept for setting but does
                    # not return any information about it
                    'skip_reconfirmation': {'value': not options['confirm']},
                    'password': {'value': options['password']},
                    'reset_password': {'value': options['reset_password']},
                    'overwrite_identities': {'value': options['overwrite_identities']},
                }
            )

            # note: as we unfortunately have some uncheckable parameters
            #   where it is not possible to determine if the update
            #   changed something or not, we must assume here that a
            #   changed happened and that an user object update is needed
            potentionally_changed = True

        # Assign ssh keys
        if options['sshkey_name'] and options['sshkey_file']:
            key_changed = self.add_ssh_key_to_user(user, {
                'name': options['sshkey_name'],
                'file': options['sshkey_file'],
                'expires_at': options['sshkey_expires_at']})
            changed = changed or key_changed

        # Assign group
        if options['group_path']:
            group_changed = self.assign_user_to_group(user, options['group_path'], options['access_level'])
            changed = changed or group_changed

        self.user_object = user
        if (changed or potentionally_changed) and not self._module.check_mode:
            try:
                user.save()
            except Exception as e:
                self._module.fail_json(msg="Failed to update user: %s " % to_native(e))

        if changed:
            if self._module.check_mode:
                self._module.exit_json(changed=True, msg="Successfully created or updated the user %s" % username)
            return True
        else:
            return False

    '''
    @param group User object
    '''
    def get_user_id(self, user):
        if user is not None:
            return user.id
        return None

    '''
    @param user User object
    @param sshkey_name Name of the ssh key
    '''
    def ssh_key_exists(self, user, sshkey_name):
        return any(
            k.title == sshkey_name
            for k in user.keys.list(**list_all_kwargs)
        )

    '''
    @param user User object
    @param sshkey Dict containing sshkey infos {"name": "", "file": "", "expires_at": ""}
    '''
    def add_ssh_key_to_user(self, user, sshkey):
        if not self.ssh_key_exists(user, sshkey['name']):
            if self._module.check_mode:
                return True

            try:
                parameter = {
                    'title': sshkey['name'],
                    'key': sshkey['file'],
                }
                if sshkey['expires_at'] is not None:
                    parameter['expires_at'] = sshkey['expires_at']
                user.keys.create(parameter)
            except gitlab.exceptions.GitlabCreateError as e:
                self._module.fail_json(msg="Failed to assign sshkey to user: %s" % to_native(e))
            return True
        return False

    '''
    @param group Group object
    @param user_id Id of the user to find
    '''
    def find_member(self, group, user_id):
        try:
            member = group.members.get(user_id)
        except gitlab.exceptions.GitlabGetError:
            return None
        return member

    '''
    @param group Group object
    @param user_id Id of the user to check
    '''
    def member_exists(self, group, user_id):
        member = self.find_member(group, user_id)

        return member is not None

    '''
    @param group Group object
    @param user_id Id of the user to check
    @param access_level GitLab access_level to check
    '''
    def member_as_good_access_level(self, group, user_id, access_level):
        member = self.find_member(group, user_id)

        return member.access_level == access_level

    '''
    @param user User object
    @param group_path Complete path of the Group including parent group path. <parent_path>/<group_path>
    @param access_level GitLab access_level to assign
    '''
    def assign_user_to_group(self, user, group_identifier, access_level):
        group = find_group(self._gitlab, group_identifier)

        if self._module.check_mode:
            return True

        if group is None:
            return False

        if self.member_exists(group, self.get_user_id(user)):
            member = self.find_member(group, self.get_user_id(user))
            if not self.member_as_good_access_level(group, member.id, self.ACCESS_LEVEL[access_level]):
                member.access_level = self.ACCESS_LEVEL[access_level]
                member.save()
                return True
        else:
            try:
                group.members.create({
                    'user_id': self.get_user_id(user),
                    'access_level': self.ACCESS_LEVEL[access_level]})
            except gitlab.exceptions.GitlabCreateError as e:
                self._module.fail_json(msg="Failed to assign user to group: %s" % to_native(e))
            return True
        return False

    '''
    @param user User object
    @param arguments User attributes
    '''
    def update_user(self, user, arguments, uncheckable_args):
        changed = False

        for arg_key, arg_value in arguments.items():
            av = arg_value['value']

            if av is not None:
                if arg_key == "identities":
                    changed = self.add_identities(user, av, uncheckable_args['overwrite_identities']['value'])

                elif getattr(user, arg_key) != av:
                    setattr(user, arg_value.get('setter', arg_key), av)
                    changed = True

        for arg_key, arg_value in uncheckable_args.items():
            av = arg_value['value']

            if av is not None:
                setattr(user, arg_value.get('setter', arg_key), av)

        return (changed, user)

    '''
    @param arguments User attributes
    '''
    def create_user(self, arguments):
        if self._module.check_mode:
            return True

        identities = None
        if 'identities' in arguments:
            identities = arguments['identities']
            del arguments['identities']

        try:
            user = self._gitlab.users.create(arguments)
            if identities:
                self.add_identities(user, identities)

        except (gitlab.exceptions.GitlabCreateError) as e:
            self._module.fail_json(msg="Failed to create user: %s " % to_native(e))

        return user

    '''
    @param user User object
    @param identities List of identities to be added/updated
    @param overwrite_identities Overwrite user identities with identities passed to this module
    '''
    def add_identities(self, user, identities, overwrite_identities=False):
        changed = False
        if overwrite_identities:
            changed = self.delete_identities(user, identities)

        for identity in identities:
            if identity not in user.identities:
                setattr(user, 'provider', identity['provider'])
                setattr(user, 'extern_uid', identity['extern_uid'])
                if not self._module.check_mode:
                    user.save()
                changed = True
        return changed

    '''
    @param user User object
    @param identities List of identities to be added/updated
    '''
    def delete_identities(self, user, identities):
        changed = False
        for identity in user.identities:
            if identity not in identities:
                if not self._module.check_mode:
                    user.identityproviders.delete(identity['provider'])
                changed = True
        return changed

    '''
    @param username Username of the user
    '''
    def find_user(self, username):
        return next(
            (
                user for user in self._gitlab.users.list(search=username, **list_all_kwargs)
                if user.username == username
            ),
            None
        )

    '''
    @param username Username of the user
    '''
    def exists_user(self, username):
        # When user exists, object will be stored in self.user_object.
        user = self.find_user(username)
        if user:
            self.user_object = user
            return True
        return False

    '''
    @param username Username of the user
    '''
    def is_active(self, username):
        user = self.find_user(username)
        return user.attributes['state'] == 'active'

    def delete_user(self):
        if self._module.check_mode:
            return True

        user = self.user_object

        return user.delete()

    def block_user(self):
        if self._module.check_mode:
            return True

        user = self.user_object

        return user.block()

    def unblock_user(self):
        if self._module.check_mode:
            return True

        user = self.user_object

        return user.unblock()


def sanitize_arguments(arguments):
    for key, value in list(arguments.items()):
        if value is None:
            del arguments[key]
    return arguments


def main():
    argument_spec = basic_auth_argument_spec()
    argument_spec.update(auth_argument_spec())
    argument_spec.update(dict(
        name=dict(type='str'),
        state=dict(type='str', default="present", choices=["absent", "present", "blocked", "unblocked"]),
        username=dict(type='str', required=True),
        password=dict(type='str', no_log=True),
        reset_password=dict(type='bool', default=False, no_log=False),
        email=dict(type='str'),
        sshkey_name=dict(type='str'),
        sshkey_file=dict(type='str', no_log=False),
        sshkey_expires_at=dict(type='str', no_log=False),
        group=dict(type='str'),
        access_level=dict(type='str', default="guest", choices=["developer", "guest", "maintainer", "master", "owner", "reporter"]),
        confirm=dict(type='bool', default=True),
        isadmin=dict(type='bool', default=False),
        external=dict(type='bool', default=False),
        identities=dict(type='list', elements='dict'),
        overwrite_identities=dict(type='bool', default=False),
    ))

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[
            ['api_username', 'api_token'],
            ['api_username', 'api_oauth_token'],
            ['api_username', 'api_job_token'],
            ['api_token', 'api_oauth_token'],
            ['api_token', 'api_job_token'],
        ],
        required_together=[
            ['api_username', 'api_password'],
        ],
        required_one_of=[
            ['api_username', 'api_token', 'api_oauth_token', 'api_job_token']
        ],
        supports_check_mode=True,
        required_if=(
            ('state', 'present', ['name', 'email']),
        )
    )

    # check prerequisites and connect to gitlab server
    gitlab_instance = gitlab_authentication(module)

    user_name = module.params['name']
    state = module.params['state']
    user_username = module.params['username'].lower()
    user_password = module.params['password']
    user_reset_password = module.params['reset_password']
    user_email = module.params['email']
    user_sshkey_name = module.params['sshkey_name']
    user_sshkey_file = module.params['sshkey_file']
    user_sshkey_expires_at = module.params['sshkey_expires_at']
    group_path = module.params['group']
    access_level = module.params['access_level']
    confirm = module.params['confirm']
    user_isadmin = module.params['isadmin']
    user_external = module.params['external']
    user_identities = module.params['identities']
    overwrite_identities = module.params['overwrite_identities']

    gitlab_user = GitLabUser(module, gitlab_instance)
    user_exists = gitlab_user.exists_user(user_username)
    if user_exists:
        user_is_active = gitlab_user.is_active(user_username)
    else:
        user_is_active = False

    if state == 'absent':
        if user_exists:
            gitlab_user.delete_user()
            module.exit_json(changed=True, msg="Successfully deleted user %s" % user_username)
        else:
            module.exit_json(changed=False, msg="User deleted or does not exists")

    if state == 'blocked':
        if user_exists and user_is_active:
            gitlab_user.block_user()
            module.exit_json(changed=True, msg="Successfully blocked user %s" % user_username)
        else:
            module.exit_json(changed=False, msg="User already blocked or does not exists")

    if state == 'unblocked':
        if user_exists and not user_is_active:
            gitlab_user.unblock_user()
            module.exit_json(changed=True, msg="Successfully unblocked user %s" % user_username)
        else:
            module.exit_json(changed=False, msg="User is not blocked or does not exists")

    if state == 'present':
        if gitlab_user.create_or_update_user(user_username, {
            "name": user_name,
            "password": user_password,
            "reset_password": user_reset_password,
            "email": user_email,
            "sshkey_name": user_sshkey_name,
            "sshkey_file": user_sshkey_file,
            "sshkey_expires_at": user_sshkey_expires_at,
            "group_path": group_path,
            "access_level": access_level,
            "confirm": confirm,
            "isadmin": user_isadmin,
            "external": user_external,
            "identities": user_identities,
            "overwrite_identities": overwrite_identities,
        }):
            module.exit_json(changed=True, msg="Successfully created or updated the user %s" % user_username, user=gitlab_user.user_object._attrs)
        else:
            module.exit_json(changed=False, msg="No need to update the user %s" % user_username, user=gitlab_user.user_object._attrs)


if __name__ == '__main__':
    main()
