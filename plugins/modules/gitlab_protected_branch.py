#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2021, Werner Dijkerman (ikben@werner-dijkerman.nl)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
module: gitlab_protected_branch
short_description: Manage protection of existing branches
version_added: 3.4.0
description:
  - (un)Marking existing branches for protection.
author:
  - "Werner Dijkerman (@dj-wasabi)"
requirements:
  - python >= 2.7
  - python-gitlab >= 2.3.0
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
  state:
    description:
      - Create or delete protected branch.
    default: present
    type: str
    choices: ["present", "absent"]
  project:
    description:
      - The path and name of the project.
    required: true
    type: str
  name:
    description:
      - The name of the branch that needs to be protected.
      - Can make use a wildcard character for like C(production/*) or just have C(main) or C(develop) as value.
    required: true
    type: str
  merge_access_levels:
    description:
      - Access levels allowed to merge.
    default: maintainer
    type: str
    choices: ["maintainer", "developer", "nobody"]
  push_access_level:
    description:
      - Access levels allowed to push.
    default: maintainer
    type: str
    choices: ["maintainer", "developer", "nobody"]
'''


EXAMPLES = '''
- name: Create protected branch on main
  community.general.gitlab_protected_branch:
    api_url: https://gitlab.com
    api_token: secret_access_token
    project: "dj-wasabi/collection.general"
    name: main
    merge_access_levels: maintainer
    push_access_level: nobody

'''

RETURN = '''
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.api import basic_auth_argument_spec

from ansible_collections.community.general.plugins.module_utils.version import LooseVersion

from ansible_collections.community.general.plugins.module_utils.gitlab import (
    auth_argument_spec, gitlab_authentication, gitlab, ensure_gitlab_package
)


class GitlabProtectedBranch(object):

    def __init__(self, module, project, gitlab_instance):
        self.repo = gitlab_instance
        self._module = module
        self.project = self.get_project(project)
        self.ACCESS_LEVEL = {
            'nobody': gitlab.NO_ACCESS,
            'developer': gitlab.DEVELOPER_ACCESS,
            'maintainer': gitlab.MAINTAINER_ACCESS
        }

    def get_project(self, project_name):
        return self.repo.projects.get(project_name)

    def protected_branch_exist(self, name):
        try:
            return self.project.protectedbranches.get(name)
        except Exception as e:
            return False

    def create_protected_branch(self, name, merge_access_levels, push_access_level):
        if self._module.check_mode:
            return True
        merge = self.ACCESS_LEVEL[merge_access_levels]
        push = self.ACCESS_LEVEL[push_access_level]
        self.project.protectedbranches.create({
            'name': name,
            'merge_access_level': merge,
            'push_access_level': push
        })

    def compare_protected_branch(self, name, merge_access_levels, push_access_level):
        configured_merge = self.ACCESS_LEVEL[merge_access_levels]
        configured_push = self.ACCESS_LEVEL[push_access_level]
        current = self.protected_branch_exist(name=name)
        current_merge = current.merge_access_levels[0]['access_level']
        current_push = current.push_access_levels[0]['access_level']
        if current:
            if current.name == name and current_merge == configured_merge and current_push == configured_push:
                return True
        return False

    def delete_protected_branch(self, name):
        if self._module.check_mode:
            return True
        return self.project.protectedbranches.delete(name)


def main():
    argument_spec = basic_auth_argument_spec()
    argument_spec.update(auth_argument_spec())
    argument_spec.update(
        project=dict(type='str', required=True),
        name=dict(type='str', required=True),
        merge_access_levels=dict(type='str', default="maintainer", choices=["maintainer", "developer", "nobody"]),
        push_access_level=dict(type='str', default="maintainer", choices=["maintainer", "developer", "nobody"]),
        state=dict(type='str', default="present", choices=["absent", "present"]),
    )

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
        supports_check_mode=True
    )
    ensure_gitlab_package(module)

    project = module.params['project']
    name = module.params['name']
    merge_access_levels = module.params['merge_access_levels']
    push_access_level = module.params['push_access_level']
    state = module.params['state']

    gitlab_version = gitlab.__version__
    if LooseVersion(gitlab_version) < LooseVersion('2.3.0'):
        module.fail_json(msg="community.general.gitlab_proteched_branch requires python-gitlab Python module >= 2.3.0 (installed version: [%s])."
                             " Please upgrade python-gitlab to version 2.3.0 or above." % gitlab_version)

    gitlab_instance = gitlab_authentication(module)
    this_gitlab = GitlabProtectedBranch(module=module, project=project, gitlab_instance=gitlab_instance)

    p_branch = this_gitlab.protected_branch_exist(name=name)
    if not p_branch and state == "present":
        this_gitlab.create_protected_branch(name=name, merge_access_levels=merge_access_levels, push_access_level=push_access_level)
        module.exit_json(changed=True, msg="Created the proteched branch.")
    elif p_branch and state == "present":
        if not this_gitlab.compare_protected_branch(name, merge_access_levels, push_access_level):
            this_gitlab.delete_protected_branch(name=name)
            this_gitlab.create_protected_branch(name=name, merge_access_levels=merge_access_levels, push_access_level=push_access_level)
            module.exit_json(changed=True, msg="Recreated the proteched branch.")
    elif p_branch and state == "absent":
        this_gitlab.delete_protected_branch(name=name)
        module.exit_json(changed=True, msg="Deleted the proteched branch.")
    module.exit_json(changed=False, msg="No changes are needed.")


if __name__ == '__main__':
    main()
