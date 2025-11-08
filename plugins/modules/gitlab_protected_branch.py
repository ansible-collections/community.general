#!/usr/bin/python

# Copyright (c) 2021, Werner Dijkerman (ikben@werner-dijkerman.nl)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

DOCUMENTATION = r"""
module: gitlab_protected_branch
short_description: Manage protection of existing branches
version_added: 3.4.0
description:
  - (un)Marking existing branches for protection.
author:
  - "Werner Dijkerman (@dj-wasabi)"
requirements:
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
      - Can make use a wildcard character for like V(production/*) or just have V(main) or V(develop) as value.
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
  allow_force_push:
    description:
      - Whether or not to allow force pushes to the protected branch.
    type: bool
    version_added: '11.3.0'
  code_owner_approval_required:
    description:
      - Whether or not to require code owner approval to push.
    type: bool
    version_added: '11.3.0'
"""


EXAMPLES = r"""
- name: Create protected branch on main
  community.general.gitlab_protected_branch:
    api_url: https://gitlab.com
    api_token: secret_access_token
    project: "dj-wasabi/collection.general"
    name: main
    merge_access_levels: maintainer
    push_access_level: nobody
"""

RETURN = r"""
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.api import basic_auth_argument_spec

from ansible_collections.community.general.plugins.module_utils.version import LooseVersion

from ansible_collections.community.general.plugins.module_utils.gitlab import (
    auth_argument_spec,
    gitlab_authentication,
    gitlab,
)


class GitlabProtectedBranch:
    def __init__(self, module, project, gitlab_instance):
        self.repo = gitlab_instance
        self._module = module
        self.project = self.get_project(project)
        self.ACCESS_LEVEL = {
            "nobody": gitlab.const.NO_ACCESS,
            "developer": gitlab.const.DEVELOPER_ACCESS,
            "maintainer": gitlab.const.MAINTAINER_ACCESS,
        }

    def get_project(self, project_name):
        return self.repo.projects.get(project_name)

    def protected_branch_exist(self, name):
        try:
            return self.project.protectedbranches.get(name)
        except Exception:
            return False

    def create_or_update_protected_branch(self, name, options):
        protected_branch_options = {
            "name": name,
            "allow_force_push": options["allow_force_push"],
            "code_owner_approval_required": options["code_owner_approval_required"],
        }
        protected_branch = self.protected_branch_exist(name=name)
        changed = False
        if protected_branch and self.can_update(protected_branch, options):
            for arg_key, arg_value in protected_branch_options.items():
                if arg_value is not None:
                    if getattr(protected_branch, arg_key) != arg_value:
                        setattr(protected_branch, arg_key, arg_value)
                        changed = True
            if changed and not self._module.check_mode:
                protected_branch.save()
        else:
            # Set immutable options only on (re)creation
            protected_branch_options["merge_access_level"] = options["merge_access_levels"]
            protected_branch_options["push_access_level"] = options["push_access_level"]
            if protected_branch:
                # Exists, but couldn't update. So, delete first
                self.delete_protected_branch(name)
            if not self._module.check_mode:
                self.project.protectedbranches.create(protected_branch_options)
            changed = True

        return changed

    def can_update(self, protected_branch, options):
        # these keys are not set on update the same way they are on creation
        configured_merge = options["merge_access_levels"]
        configured_push = options["push_access_level"]
        current_merge = protected_branch.merge_access_levels[0]["access_level"]
        current_push = protected_branch.push_access_levels[0]["access_level"]
        return (configured_merge is None or current_merge == configured_merge) and (
            configured_push is None or current_push == configured_push
        )

    def delete_protected_branch(self, name):
        if self._module.check_mode:
            return True
        return self.project.protectedbranches.delete(name)


def main():
    argument_spec = basic_auth_argument_spec()
    argument_spec.update(auth_argument_spec())
    argument_spec.update(
        project=dict(type="str", required=True),
        name=dict(type="str", required=True),
        merge_access_levels=dict(type="str", default="maintainer", choices=["maintainer", "developer", "nobody"]),
        push_access_level=dict(type="str", default="maintainer", choices=["maintainer", "developer", "nobody"]),
        allow_force_push=dict(type="bool"),
        code_owner_approval_required=dict(type="bool"),
        state=dict(type="str", default="present", choices=["absent", "present"]),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[
            ["api_username", "api_token"],
            ["api_username", "api_oauth_token"],
            ["api_username", "api_job_token"],
            ["api_token", "api_oauth_token"],
            ["api_token", "api_job_token"],
        ],
        required_together=[
            ["api_username", "api_password"],
        ],
        required_one_of=[["api_username", "api_token", "api_oauth_token", "api_job_token"]],
        supports_check_mode=True,
    )

    # check prerequisites and connect to gitlab server
    gitlab_instance = gitlab_authentication(module)

    project = module.params["project"]
    name = module.params["name"]
    merge_access_levels = module.params["merge_access_levels"]
    push_access_level = module.params["push_access_level"]
    state = module.params["state"]

    gitlab_version = gitlab.__version__
    if LooseVersion(gitlab_version) < LooseVersion("2.3.0"):
        module.fail_json(
            msg=f"community.general.gitlab_protected_branch requires python-gitlab Python module >= 2.3.0 (installed version: [{gitlab_version}])."
            " Please upgrade python-gitlab to version 2.3.0 or above."
        )

    this_gitlab = GitlabProtectedBranch(module=module, project=project, gitlab_instance=gitlab_instance)

    p_branch = this_gitlab.protected_branch_exist(name=name)
    options = {
        "merge_access_levels": this_gitlab.ACCESS_LEVEL[merge_access_levels],
        "push_access_level": this_gitlab.ACCESS_LEVEL[push_access_level],
        "allow_force_push": module.params["allow_force_push"],
        "code_owner_approval_required": module.params["code_owner_approval_required"],
    }
    if state == "present":
        changed = this_gitlab.create_or_update_protected_branch(name, options)
        module.exit_json(changed=changed, msg="Created or updated the protected branch.")
    elif p_branch and state == "absent":
        this_gitlab.delete_protected_branch(name=name)
        module.exit_json(changed=True, msg="Deleted the protected branch.")
    module.exit_json(changed=False, msg="No changes are needed.")


if __name__ == "__main__":
    main()
