#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2023, Guenther Grill <grill.guenther@gmail.com>
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r"""
module: git_config_info
author:
  - Guenther Grill (@guenhter)
version_added: 8.1.0
requirements: ['git']
short_description: Read git configuration
description:
  - The M(community.general.git_config_info) module reads the git configuration by invoking C(git config).
extends_documentation_fragment:
  - community.general.attributes
  - community.general.attributes.info_module
options:
  name:
    description:
      - The name of the setting to read.
      - If not provided, all settings are returned as RV(config_values).
    type: str
  path:
    description:
      - Path to a git repository or file for reading values from a specific repo.
      - If O(scope) is V(local), this must point to a repository to read from.
      - If O(scope) is V(file), this must point to specific git config file to read from.
      - Otherwise O(path) is ignored if set.
    type: path
  scope:
    description:
      - Specify which scope to read values from.
      - If set to V(global), the global git config is used. O(path) is ignored.
      - If set to V(system), the system git config is used. O(path) is ignored.
      - If set to V(local), O(path) must be set to the repo to read from.
      - If set to V(file), O(path) must be set to the config file to read from.
    choices: ["global", "system", "local", "file"]
    default: "system"
    type: str
"""

EXAMPLES = r"""
- name: Read a system wide config
  community.general.git_config_info:
    name: core.editor
  register: result

- name: Show value of core.editor
  ansible.builtin.debug:
    msg: "{{ result.config_value | default('(not set)', true) }}"

- name: Read a global config from ~/.gitconfig
  community.general.git_config_info:
    name: alias.remotev
    scope: global

- name: Read a project specific config
  community.general.git_config_info:
    name: color.ui
    scope: local
    path: /etc

- name: Read all global values
  community.general.git_config_info:
    scope: global

- name: Read all system wide values
  community.general.git_config_info:

- name: Read all values of a specific file
  community.general.git_config_info:
    scope: file
    path: /etc/gitconfig
"""

RETURN = r"""
config_value:
  description: >-
    When O(name) is set, a string containing the value of the setting in name. If O(name) is not set, empty. If a config key
    such as V(push.pushoption) has more then one entry, just the first one is returned here.
  returned: success if O(name) is set
  type: str
  sample: "vim"

config_values:
  description:
    - This is a dictionary mapping a git configuration setting to a list of its values.
    - When O(name) is not set, all configuration settings are returned here.
    - When O(name) is set, only the setting specified in O(name) is returned here. If that setting is not set, the key is
      still present, and its value is an empty list.
  returned: success
  type: dict
  sample:
    core.editor: ["vim"]
    color.ui: ["auto"]
    push.pushoption: ["merge_request.create", "merge_request.draft"]
    alias.remotev: ["remote -v"]
"""

from ansible.module_utils.basic import AnsibleModule


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type="str"),
            path=dict(type="path"),
            scope=dict(required=False, type="str", default="system", choices=["global", "system", "local", "file"]),
        ),
        required_if=[
            ("scope", "local", ["path"]),
            ("scope", "file", ["path"]),
        ],
        required_one_of=[],
        supports_check_mode=True,
    )

    # We check error message for a pattern, so we need to make sure the messages appear in the form we're expecting.
    # Set the locale to C to ensure consistent messages.
    module.run_command_environ_update = dict(LANG='C', LC_ALL='C', LC_MESSAGES='C', LC_CTYPE='C')

    name = module.params["name"]
    path = module.params["path"]
    scope = module.params["scope"]

    run_cwd = path if scope == "local" else "/"
    args = build_args(module, name, path, scope)

    (rc, out, err) = module.run_command(args, cwd=run_cwd, expand_user_and_vars=False)

    if rc == 128 and "unable to read config file" in err:
        # This just means nothing has been set at the given scope
        pass
    elif rc >= 2:
        # If the return code is 1, it just means the option hasn't been set yet, which is fine.
        module.fail_json(rc=rc, msg=err, cmd=" ".join(args))

    output_lines = out.strip("\0").split("\0") if out else []

    if name:
        first_value = output_lines[0] if output_lines else ""
        config_values = {name: output_lines}
        module.exit_json(changed=False, msg="", config_value=first_value, config_values=config_values)
    else:
        config_values = text_to_dict(output_lines)
        module.exit_json(changed=False, msg="", config_value="", config_values=config_values)


def build_args(module, name, path, scope):
    git_path = module.get_bin_path("git", True)
    args = [git_path, "config", "--includes", "--null", "--" + scope]

    if scope == "file":
        args.append(path)

    if name:
        args.extend(["--get-all", name])
    else:
        args.append("--list")

    return args


def text_to_dict(text_lines):
    config_values = {}
    for value in text_lines:
        k, v = value.split("\n", 1)
        if k in config_values:
            config_values[k].append(v)
        else:
            config_values[k] = [v]
    return config_values


if __name__ == "__main__":
    main()
