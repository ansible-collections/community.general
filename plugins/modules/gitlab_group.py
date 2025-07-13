#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2019, Guillaume Martinez (lunik@tiwabbit.fr)
# Copyright (c) 2015, Werner Dijkerman (ikben@werner-dijkerman.nl)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: gitlab_group
short_description: Creates/updates/deletes GitLab Groups
description:
  - When the group does not exist in GitLab, it is created.
  - When the group does exist and O(state=absent), the group is deleted.
author:
  - Werner Dijkerman (@dj-wasabi)
  - Guillaume Martinez (@Lunik)
requirements:
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
  auto_devops_enabled:
    description:
      - Default to Auto DevOps pipeline for all projects within this group.
    type: bool
    version_added: 3.7.0
  avatar_path:
    description:
      - Absolute path image to configure avatar. File size should not exceed 200 kb.
      - This option is only used on creation, not for updates.
    type: path
    version_added: 4.2.0
  default_branch:
    description:
      - All merge requests and commits are made against this branch unless you specify a different one.
    type: str
    version_added: 9.5.0
  description:
    description:
      - A description for the group.
    type: str
  enabled_git_access_protocol:
    description:
      - V(all) means SSH and HTTP(S) is enabled.
      - V(ssh) means only SSH is enabled.
      - V(http) means only HTTP(S) is enabled.
      - Only available for top level groups.
    choices: ["all", "ssh", "http"]
    type: str
    version_added: 9.5.0
  force_delete:
    description:
      - Force delete group even if projects in it.
      - Used only when O(state=absent).
    type: bool
    default: false
    version_added: 7.5.0
  lfs_enabled:
    description:
      - Projects in this group can use Git LFS.
    type: bool
    version_added: 9.5.0
  lock_duo_features_enabled:
    description:
      - Enforce GitLab Duo features for all subgroups.
      - Only available for top level groups.
    type: bool
    version_added: 9.5.0
  membership_lock:
    description:
      - Users cannot be added to projects in this group.
    type: bool
    version_added: 9.5.0
  mentions_disabled:
    description:
      - Group mentions are disabled.
    type: bool
    version_added: 9.5.0
  name:
    description:
      - Name of the group you want to create.
    required: true
    type: str
  parent:
    description:
      - Allow to create subgroups.
      - ID or Full path of parent group in the form of group/name.
    type: str
  path:
    description:
      - The path of the group you want to create, this is O(api_url)/O(path).
      - If not supplied, O(name) is used.
    type: str
  prevent_forking_outside_group:
    description:
      - Prevent forking outside of the group.
    type: bool
    version_added: 9.5.0
  prevent_sharing_groups_outside_hierarchy:
    description:
      - Members cannot invite groups outside of this group and its subgroups.
      - Only available for top level groups.
    type: bool
    version_added: 9.5.0
  project_creation_level:
    description:
      - Determine if developers can create projects in the group.
    choices: ["developer", "maintainer", "noone"]
    type: str
    version_added: 3.7.0
  request_access_enabled:
    description:
      - Users can request access (if visibility is public or internal).
    type: bool
    version_added: 9.5.0
  service_access_tokens_expiration_enforced:
    description:
      - Service account token expiration.
      - Changes do not affect existing token expiration dates.
      - Only available for top level groups.
    type: bool
    version_added: 9.5.0
  share_with_group_lock:
    description:
      - Projects cannot be shared with other groups.
    type: bool
    version_added: 9.5.0
  require_two_factor_authentication:
    description:
      - Require all users in this group to setup two-factor authentication.
    type: bool
    version_added: 3.7.0
  state:
    description:
      - Create or delete group.
      - Possible values are present and absent.
    default: present
    type: str
    choices: ["present", "absent"]
  subgroup_creation_level:
    description:
      - Allowed to create subgroups.
    choices: ["maintainer", "owner"]
    type: str
    version_added: 3.7.0
  two_factor_grace_period:
    description:
      - Delay 2FA enforcement (hours).
    type: str
    version_added: 9.5.0
  visibility:
    description:
      - Default visibility of the group.
    choices: ["private", "internal", "public"]
    default: private
    type: str
  wiki_access_level:
    description:
      - V(enabled) means everyone can access the wiki.
      - V(private) means only members of this group can access the wiki.
      - V(disabled) means group-level wiki is disabled.
    choices: ["enabled", "private", "disabled"]
    type: str
    version_added: 9.5.0
"""

EXAMPLES = r"""
- name: "Delete GitLab Group"
  community.general.gitlab_group:
    api_url: https://gitlab.example.com/
    api_token: "{{ access_token }}"
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
"""

RETURN = r"""
msg:
  description: Success or failure message.
  returned: always
  type: str
  sample: "Success"

result:
  description: JSON-parsed response from the server.
  returned: always
  type: dict

error:
  description: The error message returned by the GitLab API.
  returned: failed
  type: str
  sample: "400: path is already in use"

group:
  description: API object.
  returned: always
  type: dict
"""

from ansible.module_utils.api import basic_auth_argument_spec
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native

from ansible_collections.community.general.plugins.module_utils.gitlab import (
    auth_argument_spec, find_group, gitlab_authentication, gitlab
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

        payload = {
            'auto_devops_enabled': options['auto_devops_enabled'],
            'default_branch': options['default_branch'],
            'description': options['description'],
            'lfs_enabled': options['lfs_enabled'],
            'membership_lock': options['membership_lock'],
            'mentions_disabled': options['mentions_disabled'],
            'name': name,
            'path': options['path'],
            'prevent_forking_outside_group': options['prevent_forking_outside_group'],
            'project_creation_level': options['project_creation_level'],
            'request_access_enabled': options['request_access_enabled'],
            'require_two_factor_authentication': options['require_two_factor_authentication'],
            'share_with_group_lock': options['share_with_group_lock'],
            'subgroup_creation_level': options['subgroup_creation_level'],
            'visibility': options['visibility'],
            'wiki_access_level': options['wiki_access_level'],
        }
        if options.get('enabled_git_access_protocol') and parent is None:
            payload['enabled_git_access_protocol'] = options['enabled_git_access_protocol']
        if options.get('lock_duo_features_enabled') and parent is None:
            payload['lock_duo_features_enabled'] = options['lock_duo_features_enabled']
        if options.get('prevent_sharing_groups_outside_hierarchy') and parent is None:
            payload['prevent_sharing_groups_outside_hierarchy'] = options['prevent_sharing_groups_outside_hierarchy']
        if options.get('service_access_tokens_expiration_enforced') and parent is None:
            payload['service_access_tokens_expiration_enforced'] = options['service_access_tokens_expiration_enforced']
        if options.get('two_factor_grace_period'):
            payload['two_factor_grace_period'] = int(options['two_factor_grace_period'])

        # Because we have already call userExists in main()
        if self.group_object is None:
            payload['parent_id'] = self.get_group_id(parent)
            group = self.create_group(payload)

            # add avatar to group
            if options['avatar_path']:
                try:
                    group.avatar = open(options['avatar_path'], 'rb')
                except IOError as e:
                    self._module.fail_json(msg='Cannot open {0}: {1}'.format(options['avatar_path'], e))
            changed = True
        else:
            changed, group = self.update_group(self.group_object, payload)

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
            # Filter out None values
            filtered = {arg_key: arg_value for arg_key, arg_value in arguments.items() if arg_value is not None}

            group = self._gitlab.groups.create(filtered)
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
            if arg_value is not None:
                if getattr(group, arg_key) != arg_value:
                    setattr(group, arg_key, arg_value)
                    changed = True

        return (changed, group)

    '''
    @param force To delete even if projects inside
    '''
    def delete_group(self, force=False):
        group = self.group_object

        if not force and len(group.projects.list(all=False)) >= 1:
            self._module.fail_json(
                msg=("There are still projects in this group. "
                     "These needs to be moved or deleted before this group can be removed. "
                     "Use 'force_delete' to 'true' to force deletion of existing projects.")
            )
        else:
            if self._module.check_mode:
                return True

            try:
                group.delete()
            except Exception as e:
                self._module.fail_json(msg="Failed to delete group: %s " % to_native(e))

    '''
    @param name Name of the group
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
        auto_devops_enabled=dict(type='bool'),
        avatar_path=dict(type='path'),
        default_branch=dict(type='str'),
        description=dict(type='str'),
        enabled_git_access_protocol=dict(type='str', choices=['all', 'ssh', 'http']),
        force_delete=dict(type='bool', default=False),
        lfs_enabled=dict(type='bool'),
        lock_duo_features_enabled=dict(type='bool'),
        membership_lock=dict(type='bool'),
        mentions_disabled=dict(type='bool'),
        name=dict(type='str', required=True),
        parent=dict(type='str'),
        path=dict(type='str'),
        prevent_forking_outside_group=dict(type='bool'),
        prevent_sharing_groups_outside_hierarchy=dict(type='bool'),
        project_creation_level=dict(type='str', choices=['developer', 'maintainer', 'noone']),
        request_access_enabled=dict(type='bool'),
        require_two_factor_authentication=dict(type='bool'),
        service_access_tokens_expiration_enforced=dict(type='bool'),
        share_with_group_lock=dict(type='bool'),
        state=dict(type='str', default="present", choices=["absent", "present"]),
        subgroup_creation_level=dict(type='str', choices=['maintainer', 'owner']),
        two_factor_grace_period=dict(type='str'),
        visibility=dict(type='str', default="private", choices=["internal", "private", "public"]),
        wiki_access_level=dict(type='str', choices=['enabled', 'private', 'disabled']),
    ))

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[
            ['api_token', 'api_job_token'],
            ['api_token', 'api_oauth_token'],
            ['api_username', 'api_job_token'],
            ['api_username', 'api_oauth_token'],
            ['api_username', 'api_token'],
        ],
        required_together=[
            ['api_username', 'api_password'],
        ],
        required_one_of=[
            ['api_username', 'api_token', 'api_oauth_token', 'api_job_token']
        ],
        supports_check_mode=True,
    )

    # check prerequisites and connect to gitlab server
    gitlab_instance = gitlab_authentication(module)

    auto_devops_enabled = module.params['auto_devops_enabled']
    avatar_path = module.params['avatar_path']
    default_branch = module.params['default_branch']
    description = module.params['description']
    enabled_git_access_protocol = module.params['enabled_git_access_protocol']
    force_delete = module.params['force_delete']
    group_name = module.params['name']
    group_path = module.params['path']
    group_visibility = module.params['visibility']
    lfs_enabled = module.params['lfs_enabled']
    lock_duo_features_enabled = module.params['lock_duo_features_enabled']
    membership_lock = module.params['membership_lock']
    mentions_disabled = module.params['mentions_disabled']
    parent_identifier = module.params['parent']
    prevent_forking_outside_group = module.params['prevent_forking_outside_group']
    prevent_sharing_groups_outside_hierarchy = module.params['prevent_sharing_groups_outside_hierarchy']
    project_creation_level = module.params['project_creation_level']
    request_access_enabled = module.params['request_access_enabled']
    require_two_factor_authentication = module.params['require_two_factor_authentication']
    service_access_tokens_expiration_enforced = module.params['service_access_tokens_expiration_enforced']
    share_with_group_lock = module.params['share_with_group_lock']
    state = module.params['state']
    subgroup_creation_level = module.params['subgroup_creation_level']
    two_factor_grace_period = module.params['two_factor_grace_period']
    wiki_access_level = module.params['wiki_access_level']

    # Define default group_path based on group_name
    if group_path is None:
        group_path = group_name.replace(" ", "_")

    gitlab_group = GitLabGroup(module, gitlab_instance)

    parent_group = None
    if parent_identifier:
        parent_group = find_group(gitlab_instance, parent_identifier)
        if not parent_group:
            module.fail_json(msg="Failed to create GitLab group: Parent group doesn't exist")

        group_exists = gitlab_group.exists_group(parent_group.full_path + '/' + group_path)
    else:
        group_exists = gitlab_group.exists_group(group_path)

    if state == 'absent':
        if group_exists:
            gitlab_group.delete_group(force=force_delete)
            module.exit_json(changed=True, msg="Successfully deleted group %s" % group_name)
        else:
            module.exit_json(changed=False, msg="Group deleted or does not exist")

    if state == 'present':
        if gitlab_group.create_or_update_group(group_name, parent_group, {
            "auto_devops_enabled": auto_devops_enabled,
            "avatar_path": avatar_path,
            "default_branch": default_branch,
            "description": description,
            "enabled_git_access_protocol": enabled_git_access_protocol,
            "lfs_enabled": lfs_enabled,
            "lock_duo_features_enabled": lock_duo_features_enabled,
            "membership_lock": membership_lock,
            "mentions_disabled": mentions_disabled,
            "path": group_path,
            "prevent_forking_outside_group": prevent_forking_outside_group,
            "prevent_sharing_groups_outside_hierarchy": prevent_sharing_groups_outside_hierarchy,
            "project_creation_level": project_creation_level,
            "request_access_enabled": request_access_enabled,
            "require_two_factor_authentication": require_two_factor_authentication,
            "service_access_tokens_expiration_enforced": service_access_tokens_expiration_enforced,
            "share_with_group_lock": share_with_group_lock,
            "subgroup_creation_level": subgroup_creation_level,
            "two_factor_grace_period": two_factor_grace_period,
            "visibility": group_visibility,
            "wiki_access_level": wiki_access_level,
        }):
            module.exit_json(changed=True, msg="Successfully created or updated the group %s" % group_name, group=gitlab_group.group_object._attrs)
        else:
            module.exit_json(changed=False, msg="No need to update the group %s" % group_name, group=gitlab_group.group_object._attrs)


if __name__ == '__main__':
    main()
