#!/usr/bin/python
# -*- coding: utf-8 -*-

# Based on code:
# Copyright (c) 2023, Ondrej Zvara (ozvara1@gmail.com)
# Copyright (c) 2021, Lennert Mertens (lennert@nubera.be)
# Copyright (c) 2021, Werner Dijkerman (ikben@werner-dijkerman.nl)
# Copyright (c) 2015, Werner Dijkerman (ikben@werner-dijkerman.nl)
# Copyright (c) 2019, Guillaume Martinez (lunik@tiwabbit.fr)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: gitlab_merge_request_rule
short_description: Manage Gitlab Project merge request rules
version_added: 3.4.0
description:
  - Managing Gitlab Project merge request rules (requires Enterprise/Ultimate Edition).
author:
  - mil1i (!UNKNOWN) [liebhaber_sgl@gwto.me]
requirements:
  - python-gitlab >= 2.6.0
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
  project_group:
    description:
      - The name/path of the group the project resides in.
    required: true
    type: str
  project_name:
    description:
      - The name of the the project/repository.
    required: true
    type: str
  rule_name:
    description:
      - The name of the custom merge request rule to manage.
    required: true
    type: str
  approvals_required:
    description:
      - The number of approvals required before the rule passes to allow a merge.
    required: true
    type: int
  usernames:
    description:
      - List of usernames of who can approve merge requests for this rule.
    type: list
    elements: str
  user_ids:
    description:
      - List of user_ids of who can approve merge requests for this rule.
    type: list
    elements: int
  groups:
    description:
      - List of group ids of members who can approve merge requests for this rule.
    type: list
    elements: int
  protected_branch:
    description:
      - A protected branch name or branch id for this rule to apply to.
      - Defaults to ALL branches if none specified.
    type: str
  applies_to_all_protected_branches:
    description:
      - Flag to enable applying this rule to ALL protected branches.
      - Ignores "protected_branches" if this flag is set to True.
    default: False
    type: bool
"""


EXAMPLES = r"""
- name: Create merge request rule 'first-rule' on main and develop
  community.general.gitlab_merge_request_rule:
    api_url: "https://{{ gitlab_url }}/"
    api_token: "{{ api_token }}"
    validate_certs: false
    state: present
    project_group: 'group/subgroup'
    project_name: 'repo-name'
    rule_name: 'first-rule'
    approvals_required: 3
    applies_to_all_protected_branches: false
    protected_branch: main
    usernames:
        - someonesusername
    user_ids:
        - 290
    groups:
        - 743  # developers group
"""

RETURN = r"""
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.api import basic_auth_argument_spec

from ansible_collections.community.general.plugins.module_utils.version import (
    LooseVersion,
)

from ansible_collections.community.general.plugins.module_utils.gitlab import (
    auth_argument_spec,
    gitlab_authentication,
    gitlab,
)
from itertools import chain


class GitlabMergeRequestRule(object):
    def __init__(
        self,
        module,
        gitlab_instance,
        group,
        project,
        rule_name,
        rule_approvals_required=0,
        rule_groups=None,
        rule_user_ids=None,
        rule_usernames=None,
        rule_branches=None,
        rule_all_protected_branches=False,
    ):
        self._module = module
        self.gitlab = gitlab_instance
        self.group = self.get_project_group(group)
        self.project = self.get_project(group, project)
        self.protected_branches = self.project.protectedbranches.list(all=True)
        self.rules = self.list_approval_rules()
        self.rule_name = rule_name
        self.rule_groups = (
            self.build_groups(self._string_to_set(rule_groups))
            if rule_groups is not None
            else []
        )
        self.rule_usernames = (
            self._string_to_set(rule_usernames) if rule_usernames is not None else []
        )
        self.rule_user_ids = (
            self._string_to_set(rule_user_ids) if rule_user_ids is not None else []
        )
        self.rule_users = self.build_users()
        self.rule_apporvals_required = rule_approvals_required
        self.rule_branches = (
            self._gather_ids_for_protected_branches(rule_branches)
            if rule_branches is not None
            else []
        )
        self.rule_all_protected_branches = rule_all_protected_branches
        self.rule_exists, self.existing_rule = self.check_rule_exists(rule_name)
        if self.rule_exists:
            self._updates = False
            self.rule_updated = self.check_for_updates_to_existing_rule()

    def _gather_ids_for_protected_branches(self, wanted_branches):
        final_branches = set()
        string_branches = self._string_to_set(wanted_branches)
        for b in string_branches:
            _id = b
            if not b.isdigit():
                try:
                    _id = self._check_protected_branch_exists(b)
                except gitlab.GitlabError as gerr:
                    self._module.log(
                        msg="Failed to find protected branch id for branch ({})".format(
                            b
                        ),
                        err=gerr.error_message,
                    )
            final_branches.add(_id)
        return final_branches

    def _check_protected_branch_exists(self, protected_branch):
        try:
            return next(
                pb.id for pb in self.protected_branches if pb.name == protected_branch
            )
        except StopIteration:
            return None

    def _string_to_set(self, string):
        try:
            return set(string.strip().split(",")) if string is not None else None
        except AttributeError:
            if isinstance(string, int):
                return set([string]) if string is not None else None
            elif isinstance(string, list):
                return set(string) if string is not None else None
            return None

    def _set_to_string(self, selfset):
        return ",".join(str(s) for s in selfset) if selfset is not None else None

    def build_groups(self, wanted_groups):
        final_groups = set()
        for grp in wanted_groups:
            try:
                final_groups.add(GitlabGroup(self._module, self.gitlab, grp).id)
            except gitlab.GitlabError as err:
                self._module.fail_json(
                    msg="Failed to determine specified group ({})".format(grp), err=err
                )
        return final_groups

    def build_users(self):
        final_users = set()
        if self.rule_user_ids is not None:
            if self.rule_usernames is not None:
                combined_users = set(chain(self.rule_user_ids, self.rule_usernames))
            else:
                combined_users = self.rule_user_ids
        elif self.rule_usernames is not None:
            combined_users = self.rule_usernames
        else:
            return None
        for usr in combined_users:
            try:
                found_user = GitlabUser(self._module, self.gitlab, usr)
                final_users.add(found_user.id)
            except gitlab.GitlabError as err:
                self._module.fail_json(
                    msg="Failed to determine specified user ({})".format(usr), err=err
                )
        return final_users

    def get_project(self, group_name, project_name):
        return self.gitlab.projects.get("{}/{}".format(group_name, project_name))

    def get_project_group(self, group_name):
        return self.gitlab.groups.get(group_name)

    def list_approval_rules(self):
        return self.project.approvalrules.list()

    def check_rule_exists(self, rule_name):
        try:
            return True, next(r for r in self.rules if r.name == rule_name)
        except StopIteration:
            return False, None

    def _generated_data(self):
        _name = str(self.rule_name)
        _approvals_required = int(self.rule_apporvals_required)
        _protected_branch_ids = (
            list(self.rule_branches) if self.rule_branches is not None else []
        )
        _user_ids = list(self.rule_users) if self.rule_users is not None else []
        _group_ids = list(self.rule_groups) if self.rule_groups is not None else []
        _applies_to_all_protected_branches = bool(self.rule_all_protected_branches)
        return {
            "name": _name,
            "approvals_required": _approvals_required,
            "protected_branch_ids": _protected_branch_ids,
            "user_ids": _user_ids,
            "group_ids": _group_ids,
            "applies_to_all_protected_branches": _applies_to_all_protected_branches,
        }

    def create_approval_rule(self):
        if self._module.check_mode:
            return True
        return self.project.approvalrules.create(data=self._generated_data())

    def update_approval_rule(self):
        if self._module.check_mode:
            return True
        self.existing_rule.approvals_required = int(self.rule_apporvals_required)
        self.existing_rule.protected_branch_ids = (
            list(self.rule_branches) if self.rule_branches is not None else []
        )
        self.existing_rule.user_ids = (
            list(self.rule_users) if self.rule_users is not None else []
        )
        self.existing_rule.group_ids = (
            list(self.rule_groups) if self.rule_groups is not None else []
        )
        self.existing_rule.applies_to_all_protected_branches = bool(
            self.rule_all_protected_branches
        )
        return self.existing_rule.save()

    def _check_changed_members(self, updated_bool, new_members, previous_members):
        for m in new_members:
            try:
                if not any(pm.get("id") == m for pm in previous_members):
                    updated_bool = True
            except AttributeError:
                if not any(pm == m["id"] for pm in previous_members):
                    updated_bool = True
        return updated_bool

    def check_for_updates_to_existing_rule(self):
        updated = False
        if (
            self.existing_rule.applies_to_all_protected_branches
            != self.rule_all_protected_branches
        ):
            updated = True
        if int(self.existing_rule.approvals_required) != int(
            self.rule_apporvals_required
        ):
            updated = True

        # Check for changed / removed protected branches
        updated = self._check_changed_members(
            updated, self.rule_branches, self.existing_rule.protected_branches
        )
        updated = self._check_changed_members(
            updated, self.existing_rule.protected_branches, self.rule_branches
        )

        # Check for changed /removed users
        updated = self._check_changed_members(
            updated, self.rule_users, self.existing_rule.users
        )
        updated = self._check_changed_members(
            updated, self.existing_rule.users, self.rule_users
        )

        # Check for changed / removed groups
        updated = self._check_changed_members(
            updated, self.rule_groups, self.existing_rule.groups
        )
        updated = self._check_changed_members(
            updated, self.existing_rule.groups, self.rule_groups
        )

        return updated

    def delete_approval_rule(self):
        if self._module.check_mode:
            return True
        if self.rule_exists:
            return self.existing_rule.delete()
        return False


class GitlabUser(object):
    def __init__(self, module, gitlab_instance, user):
        self._module = module
        self.gitlab = gitlab_instance
        self.given_user = user
        self.id, self.name, self.full = self.get_id()

    def get_id(self):
        if isinstance(self.given_user, str) and not self.given_user.isdigit():
            try:
                found_user = self.gitlab.users.list(username=self.given_user)
                num_found = len(found_user)
                if num_found == 1:
                    return found_user[0].id, found_user[0].username, found_user[0]
                elif num_found > 1:
                    self._module.fail_json(
                        msg="More than one matching user found, unable to determine correct user ({})".format(
                            self.given_user
                        ),
                        query_result=found_user,
                    )
                else:
                    self._module.fail_json(
                        msg="User could not be found ({})".format(self.given_user)
                    )
            except gitlab.GitlabError as gerr:
                self._module.fail_json(
                    msg="User could not be found ({})".format(self.given_user),
                    err=gerr.error_message,
                )

        else:
            if isinstance(self.given_user, int) or self.given_user.isdigit():
                try:
                    found_user = self.gitlab.users.get(self.given_user)
                    return found_user.id, found_user.username, found_user
                except gitlab.GitlabError as gerr:
                    self._module.fail_json(
                        msg="User could not be found ({})".format(self.given_user),
                        err=gerr.error_message,
                    )


class GitlabGroup(object):
    def __init__(self, module, gitlab_instance, group):
        self._module = module
        self.gitlab = gitlab_instance
        self.given_group = group
        self.full = self.get()
        self.id = self.full.id
        self.name = self.full.name
        self.full_path = self.full.full_path
        self.full_name = self.full.full_name
        self.members = self.full.members.list(get_all=True)

    def get(self):
        if isinstance(self.given_group, int) or self.given_group.isdigit():
            try:
                return self.gitlab.groups.get(self.given_group)
            except gitlab.GitlabError as gerr:
                self._module.fail_json(
                    msg="Group could not be found ({})".format(self.given_group),
                    err=gerr.error_message,
                )

        else:
            try:
                found_groups = self.gitlab.groups.list(search=self.given_group)
                num_groups = len(found_groups)
                if num_groups == 1:
                    return found_groups[0]
                elif num_groups > 1:
                    self._module.fail_json(
                        msg="More than one matching group found, unable to determine correct group ({})".format(
                            self.given_group
                        ),
                        query_result=found_groups,
                    )
                else:
                    self._module.fail_json(
                        msg="Group could not be found ({})".format(self.given_group)
                    )
            except gitlab.GitlabError as gerr:
                self._module.fail_json(
                    msg="Group could not be found ({})".format(self.given_group),
                    err=gerr.error_message,
                )


def run_module():
    module_args = basic_auth_argument_spec()
    module_args.update(auth_argument_spec())
    module_args.update(
        project_group=dict(type="str", required=True),
        project_name=dict(type="str", required=True),
        rule_name=dict(type="str", required=True),
        approvals_required=dict(type="int", required=True),
        usernames=dict(type="list", elements="str", default=None, required=False),
        user_ids=dict(type="list", elements="int", default=None, required=False),
        groups=dict(type="list", elements="int", default=None, required=False),
        protected_branch=dict(type="str", default=None, required=False),
        applies_to_all_protected_branches=dict(
            type="bool", default=False, required=False
        ),
        state=dict(type="str", default="present", choices=["absent", "present"]),
    )

    module = AnsibleModule(
        argument_spec=module_args,
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
        required_one_of=[
            ["api_username", "api_token", "api_oauth_token", "api_job_token"]
        ],
        supports_check_mode=True,
    )

    # check prerequisites and connect to gitlab server
    gitlab_instance = gitlab_authentication(module)

    gitlab_version = gitlab.__version__
    if LooseVersion(gitlab_version) < LooseVersion("2.6.0"):
        module.fail_json(
            msg="community.general.gitlab_proteched_branch requires python-gitlab Python module >= 2.6.0 (installed version: [%s])."
            " Please upgrade python-gitlab to version 2.6.0 or above." % gitlab_version
        )

    gmmr = GitlabMergeRequestRule(
        module=module,
        gitlab_instance=gitlab_instance,
        group=module.params["project_group"],
        project=module.params["project_name"],
        rule_name=module.params["rule_name"],
        rule_approvals_required=module.params["approvals_required"],
        rule_usernames=module.params["usernames"],
        rule_user_ids=module.params["user_ids"],
        rule_groups=module.params["groups"],
        rule_branches=module.params["protected_branch"],
        rule_all_protected_branches=module.params["applies_to_all_protected_branches"],
    )

    if not gmmr.rule_exists:
        if module.params["state"] == "absent":
            module.exit_json(
                changed=False,
                msg="Merge Request Rule ({}) does not exist for {}, no changes made.".format(
                    module.params["rule_name"], module.params["project_name"]
                ),
            )

        elif module.params["state"] == "present":
            gmmr.create_approval_rule()
            gmmr.rules = gmmr.list_approval_rules()
            gmmr.rule_exists, new_mmr = gmmr.check_rule_exists(gmmr.rule_name)
            module.exit_json(
                changed=True,
                msg="Merge Request Rule ({}) has been successfully created.".format(
                    module.params["rule_name"]
                ),
                merge_request_rule=new_mmr.asdict(),
            )

    elif gmmr.rule_exists:
        if module.params["state"] == "absent":
            gmmr.delete_approval_rule()
            module.exit_json(
                changed=True,
                msg="Merge Request Rule ({}) has been removed from {}.".format(
                    module.params["rule_name"], module.params["project_name"]
                ),
            )

        elif module.params["state"] == "present" and gmmr.rule_updated:
            gmmr.update_approval_rule()
            gmmr.rule_exists, new_mmr = gmmr.check_rule_exists(gmmr.rule_name)
            module.exit_json(
                changed=True,
                msg="Merge Request Rule ({}) changes were found, rule has been updated.".format(
                    module.params["rule_name"]
                ),
                merge_request_rule=new_mmr.asdict(),
            )

        else:
            module.exit_json(
                changed=False,
                msg="No changes were detected.",
                merge_request_rule=gmmr.existing_rule.asdict(),
            )


def main():
    run_module()


if __name__ == "__main__":
    main()
