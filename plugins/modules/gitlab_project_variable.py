#!/usr/bin/python

# Copyright (c) 2019, Markus Bergholz (markuman@gmail.com)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

DOCUMENTATION = r"""
module: gitlab_project_variable
short_description: Creates/updates/deletes GitLab Projects Variables
description:
  - When a project variable does not exist, it is created.
  - When a project variable does exist and is not hidden, its value is updated when the values are different.
    When a project variable does exist and is hidden, its value is updated. In this case, the module is B(not idempotent).
  - Variables which are untouched in the playbook, but are not untouched in the GitLab project, they stay untouched (O(purge=false))
    or are deleted (O(purge=true)).
author:
  - "Markus Bergholz (@markuman)"
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
  state:
    description:
      - Create or delete project variable.
      - Possible values are present and absent.
    default: present
    type: str
    choices: ["present", "absent"]
  project:
    description:
      - The path and name of the project.
    required: true
    type: str
  purge:
    description:
      - When set to V(true), all variables which are not untouched in the task are deleted.
    default: false
    type: bool
  vars:
    description:
      - When the list element is a simple key-value pair, C(masked), C(hidden), C(raw), and C(protected) are set to V(false).
      - When the list element is a dict with the keys C(value), C(masked), C(hidden), C(raw), and C(protected), the user can have full
        control about whether a value should be masked, hidden, raw, protected, or a combination.
      - Support for protected values requires GitLab >= 9.3.
      - Support for masked values requires GitLab >= 11.10.
      - Support for hidden values requires GitLab >= 17.4, and was added in community.general 11.3.0.
      - Support for raw values requires GitLab >= 15.7.
      - Support for environment_scope requires GitLab Premium >= 13.11.
      - Support for variable_type requires GitLab >= 11.11.
      - A C(value) must be a string or a number.
      - Field C(variable_type) must be a string with either V(env_var), which is the default, or V(file).
      - Field C(environment_scope) must be a string defined by scope environment.
      - When a value is masked, it must be in Base64 and have a length of at least 8 characters. See GitLab documentation
        on acceptable values for a masked variable (https://docs.gitlab.com/ce/ci/variables/#masked-variables).
    default: {}
    type: dict
  variables:
    version_added: 4.4.0
    description:
      - A list of dictionaries that represents CI/CD variables.
      - This module works internal with this structure, even if the older O(vars) parameter is used.
    default: []
    type: list
    elements: dict
    suboptions:
      name:
        description:
          - The name of the variable.
        type: str
        required: true
      value:
        description:
          - The variable value.
          - Required when O(state=present).
        type: str
      description:
        description:
          - A description for the variable.
          - Support for descriptions requires GitLab >= 16.2.
        type: str
        version_added: '11.4.0'
      masked:
        description:
          - Whether variable value is masked or not.
          - Support for masked values requires GitLab >= 11.10.
        type: bool
        default: false
      hidden:
        description:
          - Whether variable value is hidden or not.
          - Implies C(masked).
          - Support for hidden values requires GitLab >= 17.4.
        type: bool
        default: false
        version_added: '11.3.0'
      protected:
        description:
          - Whether variable value is protected or not.
          - Support for protected values requires GitLab >= 9.3.
        type: bool
        default: false
      raw:
        description:
          - Whether variable value is raw or not.
          - Support for raw values requires GitLab >= 15.7.
        type: bool
        default: false
        version_added: '7.4.0'
      variable_type:
        description:
          - Whether a variable is an environment variable (V(env_var)) or a file (V(file)).
          - Support for O(variables[].variable_type) requires GitLab >= 11.11.
        type: str
        choices: ["env_var", "file"]
        default: env_var
      environment_scope:
        description:
          - The scope for the variable.
          - Support for O(variables[].environment_scope) requires GitLab Premium >= 13.11.
        type: str
        default: '*'
"""


EXAMPLES = r"""
- name: Set or update some CI/CD variables
  community.general.gitlab_project_variable:
    api_url: https://gitlab.com
    api_token: secret_access_token
    project: markuman/dotfiles
    purge: false
    variables:
      - name: ACCESS_KEY_ID
        value: abc123
      - name: SECRET_ACCESS_KEY
        value: dassgrfaeui8989
        masked: true
        protected: true
        environment_scope: production

- name: Set or update some CI/CD variables
  community.general.gitlab_project_variable:
    api_url: https://gitlab.com
    api_token: secret_access_token
    project: markuman/dotfiles
    purge: false
    vars:
      ACCESS_KEY_ID: abc123
      SECRET_ACCESS_KEY:
        value: 3214cbad
        masked: true
        protected: true
        variable_type: env_var
        environment_scope: '*'

- name: Set or update some CI/CD variables with raw value
  community.general.gitlab_project_variable:
    api_url: https://gitlab.com
    api_token: secret_access_token
    project: markuman/dotfiles
    purge: false
    vars:
      ACCESS_KEY_ID: abc123
      SECRET_ACCESS_KEY:
        value: 3214cbad
        masked: true
        protected: true
        raw: true
        variable_type: env_var
        environment_scope: '*'

- name: Set or update some CI/CD variables with expandable value
  community.general.gitlab_project_variable:
    api_url: https://gitlab.com
    api_token: secret_access_token
    project: markuman/dotfiles
    purge: false
    vars:
      ACCESS_KEY_ID: abc123
      SECRET_ACCESS_KEY:
        value: '$MY_OTHER_VARIABLE'
        masked: true
        protected: true
        raw: false
        variable_type: env_var
        environment_scope: '*'

- name: Delete one variable
  community.general.gitlab_project_variable:
    api_url: https://gitlab.com
    api_token: secret_access_token
    project: markuman/dotfiles
    state: absent
    vars:
      ACCESS_KEY_ID: abc123
"""

RETURN = r"""
project_variable:
  description: Four lists of the variablenames which were added, updated, removed or exist.
  returned: always
  type: dict
  contains:
    added:
      description: A list of variables which were created.
      returned: always
      type: list
      sample: ["ACCESS_KEY_ID", "SECRET_ACCESS_KEY"]
    untouched:
      description: A list of variables which exist.
      returned: always
      type: list
      sample: ["ACCESS_KEY_ID", "SECRET_ACCESS_KEY"]
    removed:
      description: A list of variables which were deleted.
      returned: always
      type: list
      sample: ["ACCESS_KEY_ID", "SECRET_ACCESS_KEY"]
    updated:
      description: A list of variables whose values were changed.
      returned: always
      type: list
      sample: ["ACCESS_KEY_ID", "SECRET_ACCESS_KEY"]
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.api import basic_auth_argument_spec


from ansible_collections.community.general.plugins.module_utils.gitlab import (
    auth_argument_spec,
    gitlab_authentication,
    filter_returned_variables,
    vars_to_variables,
    list_all_kwargs,
)


class GitlabProjectVariables:
    def __init__(self, module, gitlab_instance):
        self.repo = gitlab_instance
        self.project = self.get_project(module.params["project"])
        self._module = module

    def get_project(self, project_name):
        return self.repo.projects.get(project_name)

    def list_all_project_variables(self):
        return list(self.project.variables.list(**list_all_kwargs))

    def create_variable(self, var_obj):
        if self._module.check_mode:
            return True

        var = {
            "key": var_obj.get("key"),
            "value": var_obj.get("value"),
            "description": var_obj.get("description"),
            "masked": var_obj.get("masked"),
            "masked_and_hidden": var_obj.get("hidden"),
            "protected": var_obj.get("protected"),
            "raw": var_obj.get("raw"),
            "variable_type": var_obj.get("variable_type"),
        }

        if var_obj.get("environment_scope") is not None:
            var["environment_scope"] = var_obj.get("environment_scope")

        self.project.variables.create(var)
        return True

    def update_variable(self, var_obj):
        if self._module.check_mode:
            return True
        self.delete_variable(var_obj)
        self.create_variable(var_obj)
        return True

    def delete_variable(self, var_obj):
        if self._module.check_mode:
            return True
        self.project.variables.delete(
            var_obj.get("key"), filter={"environment_scope": var_obj.get("environment_scope")}
        )
        return True


def compare(requested_variables, existing_variables, state):
    # we need to do this, because it was determined in a previous version - more or less buggy
    # basically it is not necessary and might results in more/other bugs!
    # but it is required  and only relevant for check mode!!
    # logic represents state 'present' when not purge. all other can be derived from that
    # untouched => equal in both
    # updated => name and scope are equal
    # added => name and scope does not exist
    untouched = list()
    updated = list()
    added = list()

    if state == "present":
        existing_key_scope_vars = list()
        for item in existing_variables:
            existing_key_scope_vars.append({"key": item.get("key"), "environment_scope": item.get("environment_scope")})

        for var in requested_variables:
            if var in existing_variables:
                untouched.append(var)
            else:
                compare_item = {"key": var.get("name"), "environment_scope": var.get("environment_scope")}
                if compare_item in existing_key_scope_vars:
                    updated.append(var)
                else:
                    added.append(var)

    return untouched, updated, added


def native_python_main(this_gitlab, purge, requested_variables, state, module):
    change = False
    return_value = dict(added=[], updated=[], removed=[], untouched=[])

    gitlab_keys = this_gitlab.list_all_project_variables()
    before = [x.attributes for x in gitlab_keys]

    gitlab_keys = this_gitlab.list_all_project_variables()
    existing_variables = filter_returned_variables(gitlab_keys)

    # filter out and enrich before compare
    for item in requested_variables:
        item["key"] = item.pop("name")
        item["value"] = str(item.get("value"))
        if item.get("protected") is None:
            item["protected"] = False
        if item.get("raw") is None:
            item["raw"] = False
        if item.get("masked") is None:
            item["masked"] = False
        if item.get("hidden") is None:
            item["hidden"] = False
        if item.get("environment_scope") is None:
            item["environment_scope"] = "*"
        if item.get("variable_type") is None:
            item["variable_type"] = "env_var"

    if module.check_mode:
        untouched, updated, added = compare(requested_variables, existing_variables, state)

    if state == "present":
        add_or_update = [x for x in requested_variables if x not in existing_variables]
        for item in add_or_update:
            try:
                if this_gitlab.create_variable(item):
                    return_value["added"].append(item)

            except Exception:
                if this_gitlab.update_variable(item):
                    return_value["updated"].append(item)

        if purge:
            # refetch and filter
            gitlab_keys = this_gitlab.list_all_project_variables()
            existing_variables = filter_returned_variables(gitlab_keys)

            remove = [x for x in existing_variables if x not in requested_variables]
            for item in remove:
                if this_gitlab.delete_variable(item):
                    return_value["removed"].append(item)

    elif state == "absent":
        # value, type, and description do not matter on removing variables.
        keys_ignored_on_deletion = ["value", "variable_type", "description"]
        for key in keys_ignored_on_deletion:
            for item in existing_variables:
                item.pop(key)
            for item in requested_variables:
                item.pop(key)

        if not purge:
            remove_requested = [x for x in requested_variables if x in existing_variables]
            for item in remove_requested:
                if this_gitlab.delete_variable(item):
                    return_value["removed"].append(item)

        else:
            for item in existing_variables:
                if this_gitlab.delete_variable(item):
                    return_value["removed"].append(item)

    if module.check_mode:
        return_value = dict(added=added, updated=updated, removed=return_value["removed"], untouched=untouched)

    if any(return_value[x] for x in ["added", "removed", "updated"]):
        change = True

    gitlab_keys = this_gitlab.list_all_project_variables()
    after = [x.attributes for x in gitlab_keys]

    return change, return_value, before, after


def main():
    argument_spec = basic_auth_argument_spec()
    argument_spec.update(auth_argument_spec())
    argument_spec.update(
        project=dict(type="str", required=True),
        purge=dict(type="bool", default=False),
        vars=dict(type="dict", default=dict(), no_log=True),
        # please mind whenever changing the variables dict to also change module_utils/gitlab.py's
        # KNOWN dict in filter_returned_variables or bad evil will happen
        variables=dict(
            type="list",
            elements="dict",
            default=list(),
            options=dict(
                name=dict(type="str", required=True),
                value=dict(type="str", no_log=True),
                description=dict(type="str"),
                masked=dict(type="bool", default=False),
                hidden=dict(type="bool", default=False),
                protected=dict(type="bool", default=False),
                raw=dict(type="bool", default=False),
                environment_scope=dict(type="str", default="*"),
                variable_type=dict(type="str", default="env_var", choices=["env_var", "file"]),
            ),
        ),
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
            ["vars", "variables"],
        ],
        required_together=[
            ["api_username", "api_password"],
        ],
        required_one_of=[["api_username", "api_token", "api_oauth_token", "api_job_token"]],
        supports_check_mode=True,
    )

    # check prerequisites and connect to gitlab server
    gitlab_instance = gitlab_authentication(module)

    purge = module.params["purge"]
    var_list = module.params["vars"]
    state = module.params["state"]

    if var_list:
        variables = vars_to_variables(var_list, module)
    else:
        variables = module.params["variables"]

    if state == "present":
        if any(x["value"] is None for x in variables):
            module.fail_json(msg="value parameter is required for all variables in state present")

    this_gitlab = GitlabProjectVariables(module=module, gitlab_instance=gitlab_instance)

    change, raw_return_value, before, after = native_python_main(this_gitlab, purge, variables, state, module)

    # postprocessing
    for item in after:
        item.pop("project_id")
        item["name"] = item.pop("key")
    for item in before:
        item.pop("project_id")
        item["name"] = item.pop("key")

    untouched_key_name = "key"
    if not module.check_mode:
        untouched_key_name = "name"
        raw_return_value["untouched"] = [x for x in before if x in after]

    added = [x.get("key") for x in raw_return_value["added"]]
    updated = [x.get("key") for x in raw_return_value["updated"]]
    removed = [x.get("key") for x in raw_return_value["removed"]]
    untouched = [x.get(untouched_key_name) for x in raw_return_value["untouched"]]
    return_value = dict(added=added, updated=updated, removed=removed, untouched=untouched)

    module.exit_json(changed=change, project_variable=return_value)


if __name__ == "__main__":
    main()
