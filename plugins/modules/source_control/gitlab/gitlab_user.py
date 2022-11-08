#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Guillaume Martinez (lunik@tiwabbit.fr)
# Copyright: (c) 2015, Werner Dijkerman (ikben@werner-dijkerman.nl)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

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
requirements:
  - python >= 2.7
  - python-gitlab python module
  - administrator rights on the GitLab server
extends_documentation_fragment:
- community.general.auth_basic

options:
  api_token:
    description:
      - GitLab token for logging in.
    type: str
  name:
    description:
      - Name of the user you want to create.
      - Required only if C(state) is set to C(present).
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
      - Required only if C(state) is set to C(present).
    type: str
  email:
    description:
      - The email that belongs to the user.
      - Required only if C(state) is set to C(present).
    type: str
  sshkey_name:
    description:
      - The name of the sshkey
    type: str
  sshkey_file:
    description:
      - The ssh key itself.
    type: str
  group:
    description:
      - Id or Full path of parent group in the form of group/name.
      - Add user as an member to this group.
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
    default: yes
  isadmin:
    description:
      - Grant admin privileges to the user.
    type: bool
    default: no
  external:
    description:
      - Define external parameter for this user.
    type: bool
    default: no
'''

EXAMPLES = '''
- name: "Delete GitLab User"
  community.general.gitlab_user:
    api_url: https://gitlab.example.com/
    api_token: "{{ access_token }}"
    validate_certs: False
    username: myusername
    state: absent

- name: "Create GitLab User"
  community.general.gitlab_user:
    api_url: https://gitlab.example.com/
    validate_certs: True
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

- name: "Block GitLab User"
  community.general.gitlab_user:
    api_url: https://gitlab.example.com/
    api_token: "{{ access_token }}"
    validate_certs: False
    username: myusername
    state: blocked

- name: "Unblock GitLab User"
  community.general.gitlab_user:
    api_url: https://gitlab.example.com/
    api_token: "{{ access_token }}"
    validate_certs: False
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

import traceback

GITLAB_IMP_ERR = None
try:
    import gitlab
    HAS_GITLAB_PACKAGE = True
except Exception:
    GITLAB_IMP_ERR = traceback.format_exc()
    HAS_GITLAB_PACKAGE = False

from ansible.module_utils.api import basic_auth_argument_spec
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils._text import to_native

from ansible_collections.community.general.plugins.module_utils.gitlab import findGroup, gitlabAuthentication


class GitLabUser(object):
    def __init__(self, module, gitlab_instance):
        self._module = module
        self._gitlab = gitlab_instance
        self.userObject = None
        self.ACCESS_LEVEL = {
            'guest': gitlab.GUEST_ACCESS,
            'reporter': gitlab.REPORTER_ACCESS,
            'developer': gitlab.DEVELOPER_ACCESS,
            'master': gitlab.MAINTAINER_ACCESS,
            'maintainer': gitlab.MAINTAINER_ACCESS,
            'owner': gitlab.OWNER_ACCESS}

    '''
    @param username Username of the user
    @param options User options
    '''
    def createOrUpdateUser(self, username, options):
        changed = False

        # Because we have already call userExists in main()
        if self.userObject is None:
            user = self.createUser({
                'name': options['name'],
                'username': username,
                'password': options['password'],
                'email': options['email'],
                'skip_confirmation': not options['confirm'],
                'admin': options['isadmin'],
                'external': options['external']})
            changed = True
        else:
            changed, user = self.updateUser(self.userObject, {
                'name': options['name'],
                'email': options['email'],
                'is_admin': options['isadmin'],
                'external': options['external']})

        # Assign ssh keys
        if options['sshkey_name'] and options['sshkey_file']:
            key_changed = self.addSshKeyToUser(user, {
                'name': options['sshkey_name'],
                'file': options['sshkey_file']})
            changed = changed or key_changed

        # Assign group
        if options['group_path']:
            group_changed = self.assignUserToGroup(user, options['group_path'], options['access_level'])
            changed = changed or group_changed

        self.userObject = user
        if changed:
            if self._module.check_mode:
                self._module.exit_json(changed=True, msg="Successfully created or updated the user %s" % username)

            try:
                user.save()
            except Exception as e:
                self._module.fail_json(msg="Failed to update user: %s " % to_native(e))
            return True
        else:
            return False

    '''
    @param group User object
    '''
    def getUserId(self, user):
        if user is not None:
            return user.id
        return None

    '''
    @param user User object
    @param sshkey_name Name of the ssh key
    '''
    def sshKeyExists(self, user, sshkey_name):
        keyList = map(lambda k: k.title, user.keys.list())

        return sshkey_name in keyList

    '''
    @param user User object
    @param sshkey Dict containing sshkey infos {"name": "", "file": ""}
    '''
    def addSshKeyToUser(self, user, sshkey):
        if not self.sshKeyExists(user, sshkey['name']):
            if self._module.check_mode:
                return True

            try:
                user.keys.create({
                    'title': sshkey['name'],
                    'key': sshkey['file']})
            except gitlab.exceptions.GitlabCreateError as e:
                self._module.fail_json(msg="Failed to assign sshkey to user: %s" % to_native(e))
            return True
        return False

    '''
    @param group Group object
    @param user_id Id of the user to find
    '''
    def findMember(self, group, user_id):
        try:
            member = group.members.get(user_id)
        except gitlab.exceptions.GitlabGetError:
            return None
        return member

    '''
    @param group Group object
    @param user_id Id of the user to check
    '''
    def memberExists(self, group, user_id):
        member = self.findMember(group, user_id)

        return member is not None

    '''
    @param group Group object
    @param user_id Id of the user to check
    @param access_level GitLab access_level to check
    '''
    def memberAsGoodAccessLevel(self, group, user_id, access_level):
        member = self.findMember(group, user_id)

        return member.access_level == access_level

    '''
    @param user User object
    @param group_path Complete path of the Group including parent group path. <parent_path>/<group_path>
    @param access_level GitLab access_level to assign
    '''
    def assignUserToGroup(self, user, group_identifier, access_level):
        group = findGroup(self._gitlab, group_identifier)

        if self._module.check_mode:
            return True

        if group is None:
            return False

        if self.memberExists(group, self.getUserId(user)):
            member = self.findMember(group, self.getUserId(user))
            if not self.memberAsGoodAccessLevel(group, member.id, self.ACCESS_LEVEL[access_level]):
                member.access_level = self.ACCESS_LEVEL[access_level]
                member.save()
                return True
        else:
            try:
                group.members.create({
                    'user_id': self.getUserId(user),
                    'access_level': self.ACCESS_LEVEL[access_level]})
            except gitlab.exceptions.GitlabCreateError as e:
                self._module.fail_json(msg="Failed to assign user to group: %s" % to_native(e))
            return True
        return False

    '''
    @param user User object
    @param arguments User attributes
    '''
    def updateUser(self, user, arguments):
        changed = False

        for arg_key, arg_value in arguments.items():
            if arguments[arg_key] is not None:
                if getattr(user, arg_key) != arguments[arg_key]:
                    setattr(user, arg_key, arguments[arg_key])
                    changed = True

        return (changed, user)

    '''
    @param arguments User attributes
    '''
    def createUser(self, arguments):
        if self._module.check_mode:
            return True

        try:
            user = self._gitlab.users.create(arguments)
        except (gitlab.exceptions.GitlabCreateError) as e:
            self._module.fail_json(msg="Failed to create user: %s " % to_native(e))

        return user

    '''
    @param username Username of the user
    '''
    def findUser(self, username):
        users = self._gitlab.users.list(search=username)
        for user in users:
            if (user.username == username):
                return user

    '''
    @param username Username of the user
    '''
    def existsUser(self, username):
        # When user exists, object will be stored in self.userObject.
        user = self.findUser(username)
        if user:
            self.userObject = user
            return True
        return False

    '''
    @param username Username of the user
    '''
    def isActive(self, username):
        user = self.findUser(username)
        return user.attributes['state'] == 'active'

    def deleteUser(self):
        if self._module.check_mode:
            return True

        user = self.userObject

        return user.delete()

    def blockUser(self):
        if self._module.check_mode:
            return True

        user = self.userObject

        return user.block()

    def unblockUser(self):
        if self._module.check_mode:
            return True

        user = self.userObject

        return user.unblock()


def main():
    argument_spec = basic_auth_argument_spec()
    argument_spec.update(dict(
        api_token=dict(type='str', no_log=True),
        name=dict(type='str'),
        state=dict(type='str', default="present", choices=["absent", "present", "blocked", "unblocked"]),
        username=dict(type='str', required=True),
        password=dict(type='str', no_log=True),
        email=dict(type='str'),
        sshkey_name=dict(type='str'),
        sshkey_file=dict(type='str'),
        group=dict(type='str'),
        access_level=dict(type='str', default="guest", choices=["developer", "guest", "maintainer", "master", "owner", "reporter"]),
        confirm=dict(type='bool', default=True),
        isadmin=dict(type='bool', default=False),
        external=dict(type='bool', default=False),
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
            ['api_username', 'api_token']
        ],
        supports_check_mode=True,
        required_if=(
            ('state', 'present', ['name', 'email', 'password']),
        )
    )

    user_name = module.params['name']
    state = module.params['state']
    user_username = module.params['username'].lower()
    user_password = module.params['password']
    user_email = module.params['email']
    user_sshkey_name = module.params['sshkey_name']
    user_sshkey_file = module.params['sshkey_file']
    group_path = module.params['group']
    access_level = module.params['access_level']
    confirm = module.params['confirm']
    user_isadmin = module.params['isadmin']
    user_external = module.params['external']

    if not HAS_GITLAB_PACKAGE:
        module.fail_json(msg=missing_required_lib("python-gitlab"), exception=GITLAB_IMP_ERR)

    gitlab_instance = gitlabAuthentication(module)

    gitlab_user = GitLabUser(module, gitlab_instance)
    user_exists = gitlab_user.existsUser(user_username)
    if user_exists:
        user_is_active = gitlab_user.isActive(user_username)
    else:
        user_is_active = False

    if state == 'absent':
        if user_exists:
            gitlab_user.deleteUser()
            module.exit_json(changed=True, msg="Successfully deleted user %s" % user_username)
        else:
            module.exit_json(changed=False, msg="User deleted or does not exists")

    if state == 'blocked':
        if user_exists and user_is_active:
            gitlab_user.blockUser()
            module.exit_json(changed=True, msg="Successfully blocked user %s" % user_username)
        else:
            module.exit_json(changed=False, msg="User already blocked or does not exists")

    if state == 'unblocked':
        if user_exists and not user_is_active:
            gitlab_user.unblockUser()
            module.exit_json(changed=True, msg="Successfully unblocked user %s" % user_username)
        else:
            module.exit_json(changed=False, msg="User is not blocked or does not exists")

    if state == 'present':
        if gitlab_user.createOrUpdateUser(user_username, {
                                          "name": user_name,
                                          "password": user_password,
                                          "email": user_email,
                                          "sshkey_name": user_sshkey_name,
                                          "sshkey_file": user_sshkey_file,
                                          "group_path": group_path,
                                          "access_level": access_level,
                                          "confirm": confirm,
                                          "isadmin": user_isadmin,
                                          "external": user_external}):
            module.exit_json(changed=True, msg="Successfully created or updated the user %s" % user_username, user=gitlab_user.userObject._attrs)
        else:
            module.exit_json(changed=False, msg="No need to update the user %s" % user_username, user=gitlab_user.userObject._attrs)


if __name__ == '__main__':
    main()
