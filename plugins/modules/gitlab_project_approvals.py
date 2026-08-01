#!/usr/bin/python

# Copyright (c) 2026, Masaru Onodera (@masa-orca)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: gitlab_project_approvals
short_description: Manage project-level merge request approvals settings on GitLab Server
version_added: 13.1.0
description:
  - This module allows to manage project-level merge request approval configurations.
author:
  - "Masaru Onodera (@masa-orca)"
requirements:
  - python-gitlab python module
extends_documentation_fragment:
  - community.general._auth_basic
  - community.general._gitlab
  - community.general._attributes

attributes:
  check_mode:
    support: full
  diff_mode:
    support: none

options:
  project:
    description:
      - The name or full path of the GitLab project.
    required: true
    type: str

  approvals_before_merge:
    description:
      - The number of approvals required before a merge request can be merged.
      - Deprecated in GitLab 12.3.
    type: int

  reset_approvals_on_push:
    description:
      - Reset approvals on new commit.
    type: bool

  disable_overriding_approvers_per_merge_request:
    description:
      - Disable overriding approvers per merge request.
    type: bool

  merge_requests_author_approval:
    description:
      - Allow authors to self-approve merge requests.
    type: bool

  merge_requests_disable_committers_approval:
    description:
      - Prevent committers from approving merge requests.
    type: bool

  selective_code_owner_removals:
    description:
      - Reset approvals from Code Owners if their files are changed.
    type: bool

  require_password_to_approve:
    description:
      - Require password reauthentication to approve a merge request.
      - Deprecated in GitLab 16.9.
    type: bool

  require_reauthentication_to_approve:
    description:
      - Require user reauthentication to approve a merge request.
    type: bool
"""

EXAMPLES = r"""
- name: Configure GitLab Project approval settings
  community.general.gitlab_project_approvals:
    api_url: https://gitlab.example.com/
    api_token: "{{ api_token }}"
    project: my_group/my_project
    reset_approvals_on_push: true
    merge_requests_author_approval: false
    merge_requests_disable_committers_approval: true
"""

RETURN = r"""
project_approvals:
  description: The updated GitLab project approval settings.
  returned: always
  type: dict
  sample:
    approvals_before_merge: 2
    reset_approvals_on_push: true
    disable_overriding_approvers_per_merge_request: false
    merge_requests_author_approval: false
    merge_requests_disable_committers_approval: true
"""


from ansible.module_utils.api import basic_auth_argument_spec
from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.general.plugins.module_utils._gitlab import (
    auth_argument_spec,
    find_project,
    gitlab_authentication,
)


class GitlabProjectApprovals:
    def __init__(self, module, gitlab_instance):
        self._module = module
        self._gitlab = gitlab_instance
        self.project = self.get_project(module.params["project"])

    def get_project(self, project_name):
        project = find_project(self._gitlab, project_name)
        if project is None:
            self._module.fail_json(msg=f"Project {project_name} not found or insufficient permissions.")
        return project

    def update_approval_settings(self, options):
        changed = False
        try:
            approval_settings = self.project.approvals.get()
        except Exception as e:
            self._module.fail_json(msg=f"Failed to get project approval settings: {e}")

        # Check which options differ from current settings and apply them
        for key, value in options.items():
            if value is not None:
                current_value = getattr(approval_settings, key, None)
                if current_value != value:
                    setattr(approval_settings, key, value)
                    changed = True

        if changed:
            if not self._module.check_mode:
                try:
                    approval_settings.save()
                except Exception as e:
                    self._module.fail_json(msg=f"Failed to update project approval settings: {e}")

        return changed, approval_settings.attributes


def main():
    argument_spec = basic_auth_argument_spec()
    argument_spec.update(auth_argument_spec())
    argument_spec.update(
        dict(
            project=dict(type="str", required=True),
            approvals_before_merge=dict(type="int"),
            reset_approvals_on_push=dict(type="bool"),
            disable_overriding_approvers_per_merge_request=dict(type="bool"),
            merge_requests_author_approval=dict(type="bool"),
            merge_requests_disable_committers_approval=dict(type="bool"),
            selective_code_owner_removals=dict(type="bool"),
            require_password_to_approve=dict(type="bool"),
            require_reauthentication_to_approve=dict(type="bool"),
        )
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

    gitlab_instance = gitlab_authentication(module)

    gitlab_project_approvals = GitlabProjectApprovals(module, gitlab_instance)

    options = {
        "approvals_before_merge": module.params["approvals_before_merge"],
        "reset_approvals_on_push": module.params["reset_approvals_on_push"],
        "disable_overriding_approvers_per_merge_request": module.params[
            "disable_overriding_approvers_per_merge_request"
        ],
        "merge_requests_author_approval": module.params["merge_requests_author_approval"],
        "merge_requests_disable_committers_approval": module.params["merge_requests_disable_committers_approval"],
        "selective_code_owner_removals": module.params["selective_code_owner_removals"],
        "require_password_to_approve": module.params["require_password_to_approve"],
        "require_reauthentication_to_approve": module.params["require_reauthentication_to_approve"],
    }

    changed, approval_attrs = gitlab_project_approvals.update_approval_settings(options)

    module.exit_json(changed=changed, project_approvals=approval_attrs)


if __name__ == "__main__":
    main()
