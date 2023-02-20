#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2019, Guillaume Martinez (lunik@tiwabbit.fr)
# Copyright (c) 2015, Werner Dijkerman (ikben@werner-dijkerman.nl)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: gitlab_group
short_description: Creates/updates/deletes GitLab Groups
description:
  - When the group does not exist in GitLab, it will be created.
  - When the group does exist and state=absent, the group will be deleted.
author:
  - Werner Dijkerman (@dj-wasabi)
  - Guillaume Martinez (@Lunik)
requirements:
  - python >= 2.7
  - python-gitlab python module
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
      - Name of the group you want to create.
    required: true
    type: str
  path:
    description:
      - The path of the group you want to create, this will be api_url/group_path
      - If not supplied, the group_name will be used.
    type: str
  description:
    description:
      - A description for the group.
    type: str
  state:
    description:
      - create or delete group.
      - Possible values are present and absent.
    default: present
    type: str
    choices: ["present", "absent"]
  parent:
    description:
      - Allow to create subgroups
      - Id or Full path of parent group in the form of group/name
    type: str
  visibility:
    description:
      - Default visibility of the group
    choices: ["private", "internal", "public"]
    default: private
    type: str
  project_creation_level:
    description:
      - Determine if developers can create projects in the group.
    choices: ["developer", "maintainer", "noone"]
    type: str
    version_added: 3.7.0
  auto_devops_enabled:
    description:
      - Default to Auto DevOps pipeline for all projects within this group.
    type: bool
    version_added: 3.7.0
  subgroup_creation_level:
    description:
      - Allowed to create subgroups.
    choices: ["maintainer", "owner"]
    type: str
    version_added: 3.7.0
  require_two_factor_authentication:
    description:
      - Require all users in this group to setup two-factor authentication.
    type: bool
    version_added: 3.7.0
  avatar_path:
    description:
      - Absolute path image to configure avatar. File size should not exceed 200 kb.
      - This option is only used on creation, not for updates.
    type: path
    version_added: 4.2.0
'''

EXAMPLES = '''
- name: "Delete GitLab Group"
  community.general.gitlab_group:
    api_url: https://gitlab.example.com/
    api_token: "{{ access_token }}"
    validate_certs: false
    name: my_first_group
    state: absent

- name: "Create GitLab Group"
  community.general.gitlab_group:
    api_url: https://gitlab.example.com/
    validate_certs: true
    api_username: dj-wasabi
    api_password: "MySecretPassword"
    name: my_first_group
    path: my_first_group
    state: present

# The group will by created at https://gitlab.dj-wasabi.local/super_parent/parent/my_first_group
- name: "Create GitLab SubGroup"
  community.general.gitlab_group:
    api_url: https://gitlab.example.com/
    validate_certs: true
    api_username: dj-wasabi
    api_password: "MySecretPassword"
    name: my_first_group
    path: my_first_group
    state: present
    parent: "super_parent/parent"

# Other group which only allows sub-groups - no projects
- name: "Create GitLab Group for SubGroups only"
  community.general.gitlab_group:
    api_url: https://gitlab.example.com/
    validate_certs: true
    api_username: dj-wasabi
    api_password: "MySecretPassword"
    name: my_main_group
    path: my_main_group
    state: present
    project_creation_level: noone
    auto_devops_enabled: false
    subgroup_creation_level: maintainer
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

group:
  description: API object
  returned: always
  type: dict
'''

from ansible.module_utils.api import basic_auth_argument_spec
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native

from ansible_collections.community.general.plugins.module_utils.gitlab import (
    auth_argument_spec, find_group, gitlab_authentication, gitlab, ensure_gitlab_package
)


class GitLabGroup(object):
    def __init__(self, module, gitlab_instance):
        self._module = module
        self._gitlab = gitlab_instance
        self.group_object = None

    '''
    @param group Group object
    '''
    def get_group_id(self, group):
        if group is not None:
            return group.id
        return None

    '''
    @param name Name of the group
    @param parent Parent group full path
    @param options Group options
    '''
    def create_or_update_group(self, name, parent, options):
        changed = False

        # Because we have already call userExists in main()
        if self.group_object is None:
            parent_id = self.get_group_id(parent)

            payload = {
                'name': name,
                'path': options['path'],
                'parent_id': parent_id,
                'visibility': options['visibility'],
                'project_creation_level': options['project_creation_level'],
                'auto_devops_enabled': options['auto_devops_enabled'],
                'subgroup_creation_level': options['subgroup_creation_level'],
            }
            if options.get('description'):
                payload['description'] = options['description']
            if options.get('require_two_factor_authentication'):
                payload['require_two_factor_authentication'] = options['require_two_factor_authentication']
            group = self.create_group(payload)

            # add avatar to group
            if options['avatar_path']:
                try:
                    group.avatar = open(options['avatar_path'], 'rb')
                except IOError as e:
                    self._module.fail_json(msg='Cannot open {0}: {1}'.format(options['avatar_path'], e))
            changed = True
        else:
            changed, group = self.update_group(self.group_object, {
                'name': name,
                'description': options['description'],
                'visibility': options['visibility'],
                'project_creation_level': options['project_creation_level'],
                'auto_devops_enabled': options['auto_devops_enabled'],
                'subgroup_creation_level': options['subgroup_creation_level'],
                'require_two_factor_authentication': options['require_two_factor_authentication'],
            })

        self.group_object = group
        if changed:
            if self._module.check_mode:
                self._module.exit_json(changed=True, msg="Successfully created or updated the group %s" % name)

            try:
                group.save()
            except Exception as e:
                self._module.fail_json(msg="Failed to update group: %s " % e)
            return True
        else:
            return False

    '''
    @param arguments Attributes of the group
    '''
    def create_group(self, arguments):
        if self._module.check_mode:
            return True

        try:
            group = self._gitlab.groups.create(arguments)
        except (gitlab.exceptions.GitlabCreateError) as e:
            self._module.fail_json(msg="Failed to create group: %s " % to_native(e))

        return group

    '''
    @param group Group Object
    @param arguments Attributes of the group
    '''
    def update_group(self, group, arguments):
        changed = False

        for arg_key, arg_value in arguments.items():
            if arguments[arg_key] is not None:
                if getattr(group, arg_key) != arguments[arg_key]:
                    setattr(group, arg_key, arguments[arg_key])
                    changed = True

        return (changed, group)

    def delete_group(self):
        group = self.group_object

        if len(group.projects.list(all=False)) >= 1:
            self._module.fail_json(
                msg="There are still projects in this group. These needs to be moved or deleted before this group can be removed.")
        else:
            if self._module.check_mode:
                return True

            try:
                group.delete()
            except Exception as e:
                self._module.fail_json(msg="Failed to delete group: %s " % to_native(e))

    '''
    @param name Name of the groupe
    @param full_path Complete path of the Group including parent group path. <parent_path>/<group_path>
    '''
    def exists_group(self, project_identifier):
        # When group/user exists, object will be stored in self.group_object.
        group = find_group(self._gitlab, project_identifier)
        if group:
            self.group_object = group
            return True
        return False


def main():
    argument_spec = basic_auth_argument_spec()
    argument_spec.update(auth_argument_spec())
    argument_spec.update(dict(
        name=dict(type='str', required=True),
        path=dict(type='str'),
        description=dict(type='str'),
        state=dict(type='str', default="present", choices=["absent", "present"]),
        parent=dict(type='str'),
        visibility=dict(type='str', default="private", choices=["internal", "private", "public"]),
        project_creation_level=dict(type='str', choices=['developer', 'maintainer', 'noone']),
        auto_devops_enabled=dict(type='bool'),
        subgroup_creation_level=dict(type='str', choices=['maintainer', 'owner']),
        require_two_factor_authentication=dict(type='bool'),
        avatar_path=dict(type='path'),
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
    )
    ensure_gitlab_package(module)

    group_name = module.params['name']
    group_path = module.params['path']
    description = module.params['description']
    state = module.params['state']
    parent_identifier = module.params['parent']
    group_visibility = module.params['visibility']
    project_creation_level = module.params['project_creation_level']
    auto_devops_enabled = module.params['auto_devops_enabled']
    subgroup_creation_level = module.params['subgroup_creation_level']
    require_two_factor_authentication = module.params['require_two_factor_authentication']
    avatar_path = module.params['avatar_path']

    gitlab_instance = gitlab_authentication(module)

    # Define default group_path based on group_name
    if group_path is None:
        group_path = group_name.replace(" ", "_")

    gitlab_group = GitLabGroup(module, gitlab_instance)

    parent_group = None
    if parent_identifier:
        parent_group = find_group(gitlab_instance, parent_identifier)
        if not parent_group:
            module.fail_json(msg="Failed create GitLab group: Parent group doesn't exists")

        group_exists = gitlab_group.exists_group(parent_group.full_path + '/' + group_path)
    else:
        group_exists = gitlab_group.exists_group(group_path)

    if state == 'absent':
        if group_exists:
            gitlab_group.delete_group()
            module.exit_json(changed=True, msg="Successfully deleted group %s" % group_name)
        else:
            module.exit_json(changed=False, msg="Group deleted or does not exists")

    if state == 'present':
        if gitlab_group.create_or_update_group(group_name, parent_group, {
            "path": group_path,
            "description": description,
            "visibility": group_visibility,
            "project_creation_level": project_creation_level,
            "auto_devops_enabled": auto_devops_enabled,
            "subgroup_creation_level": subgroup_creation_level,
            "require_two_factor_authentication": require_two_factor_authentication,
            "avatar_path": avatar_path,
        }):
            module.exit_json(changed=True, msg="Successfully created or updated the group %s" % group_name, group=gitlab_group.group_object._attrs)
        else:
            module.exit_json(changed=False, msg="No need to update the group %s" % group_name, group=gitlab_group.group_object._attrs)


if __name__ == '__main__':
    main()
