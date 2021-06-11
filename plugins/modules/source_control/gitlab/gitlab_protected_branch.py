#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Werner Dijkerman (ikben@werner-dijkerman.nl)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
module: gitlab_protected_branch
short_description: Creates/deletes proteched branches in Gitlab for an project.
description:
  - Create/Delete a protected branch in an project.
author:
  - "Werner Dijkerman (@dj-wasabi)"
requirements:
  - python >= 2.7
  - python-gitlab python module
extends_documentation_fragment:
- community.general.auth_basic

options:
  state:
    description:
      - Create or delete proteced branch.
      - Possible values are present and absent.
    default: present
    type: str
    choices: ["present", "absent"]
  api_token:
    description:
      - GitLab access token with API permissions.
    required: true
    type: str
  project:
    description:
      - The path and name of the project.
    required: true
    type: str
  name:
    description:
      - The name of the branch that needs to be protected.
      - Can make use a wildcard charachter for like 'production/*' or just have 'main' or 'develop' as value.
    required: true
    type: str
  merge_access_levels:
    description:
      - Access levels allowed to merge.
      - Possible values are "maintainer", "developer" or "no_access".
    default: maintainer
    type: str
    choices: ["maintainer", "developer", "no_access"]
  push_access_level:
    description:
      - Access levels allowed to push.
      - Possible values are "maintainer", "developer" or "no_access".
    default: maintainer
    type: str
    choices: ["maintainer", "developer", "no_access"]
'''


EXAMPLES = '''
- name: Create protected branch on main
  community.general.gitlab_protected_branch:
    api_url: https://gitlab.com
    api_token: secret_access_token
    project: "dj-wasabi/collection.general"
    name: main
    merge_access_levels: maintainer
    push_access_level: no_access

'''

RETURN = '''
'''

import traceback

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils._text import to_native
from ansible.module_utils.api import basic_auth_argument_spec
from ansible.module_utils.six import string_types
from ansible.module_utils.six import integer_types


GITLAB_IMP_ERR = None
try:
    import gitlab
    HAS_GITLAB_PACKAGE = True
except Exception:
    GITLAB_IMP_ERR = traceback.format_exc()
    HAS_GITLAB_PACKAGE = False

from ansible_collections.community.general.plugins.module_utils.gitlab import gitlabAuthentication


class GitlabProtectedBranch(object):

    def __init__(self, module, gitlab_instance):
        self.repo = gitlab_instance
        self._module = module
        self.project = self.get_project(self._module.params['project'])
        self.ACCESS_LEVEL = {
            'no_access': gitlab.NO_ACCESS,
            'developer': gitlab.DEVELOPER_ACCESS,
            'maintainer': gitlab.MAINTAINER_ACCESS
        }

    def get_project(self, project_name):
        return self.repo.projects.get(project_name)

    def protected_branch_exist(self):
        try:
            return self.project.protectedbranches.get(self._module.params['name'])
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
        current = self.protected_branch_exist()
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
    argument_spec.update(
        api_token=dict(type='str', required=True, no_log=True),
        project=dict(type='str', required=True),
        name=dict(type='str', required=True),
        merge_access_levels=dict(type='str', default="maintainer", choices=["maintainer", "developer", "no_access"]),
        push_access_level=dict(type='str', default="maintainer", choices=["maintainer", "developer", "no_access"]),
        state=dict(type='str', default="present", choices=["absent", "present"]),
    )

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
        supports_check_mode=True
    )

    name = module.params['name']
    merge_access_levels = module.params['merge_access_levels']
    push_access_level = module.params['push_access_level']
    state = module.params['state']

    if not HAS_GITLAB_PACKAGE:
        module.fail_json(msg=missing_required_lib("python-gitlab"), exception=GITLAB_IMP_ERR)

    gitlab_instance = gitlabAuthentication(module)
    this_gitlab = GitlabProtectedBranch(module=module, gitlab_instance=gitlab_instance)

    p_branch = this_gitlab.protected_branch_exist()
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
