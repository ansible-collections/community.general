#!/usr/bin/python

# Copyright (c) 2023, Andrew Hyatt <andy@hyatt.xyz>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

DOCUMENTATION = r"""
module: dnf_config_manager
short_description: Enable or disable dnf repositories using config-manager
version_added: 8.2.0
description:
  - This module enables or disables repositories using the C(dnf config-manager) sub-command.
author: Andrew Hyatt (@ahyattdev) <andy@hyatt.xyz>
requirements:
  - dnf
  - dnf-plugins-core
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  name:
    description:
      - Repository ID, for example V(crb).
    default: []
    type: list
    elements: str
  state:
    description:
      - Whether the repositories should be V(enabled) or V(disabled).
    default: enabled
    type: str
    choices: [enabled, disabled]
notes:
  - Does not work with C(dnf5).
seealso:
  - module: ansible.builtin.dnf
  - module: ansible.builtin.yum_repository
"""

EXAMPLES = r"""
- name: Ensure the crb repository is enabled
  community.general.dnf_config_manager:
    name: crb
    state: enabled

- name: Ensure the appstream and zfs repositories are disabled
  community.general.dnf_config_manager:
    name:
      - appstream
      - zfs
    state: disabled
"""

RETURN = r"""
repo_states_pre:
  description: Repo IDs before action taken.
  returned: success
  type: dict
  contains:
    enabled:
      description: Enabled repository IDs.
      returned: success
      type: list
      elements: str
    disabled:
      description: Disabled repository IDs.
      returned: success
      type: list
      elements: str
  sample:
    enabled:
      - appstream
      - baseos
      - crb
    disabled:
      - appstream-debuginfo
      - appstream-source
      - baseos-debuginfo
      - baseos-source
      - crb-debug
      - crb-source
repo_states_post:
  description: Repository states after action taken.
  returned: success
  type: dict
  contains:
    enabled:
      description: Enabled repository IDs.
      returned: success
      type: list
      elements: str
    disabled:
      description: Disabled repository IDs.
      returned: success
      type: list
      elements: str
  sample:
    enabled:
      - appstream
      - baseos
      - crb
    disabled:
      - appstream-debuginfo
      - appstream-source
      - baseos-debuginfo
      - baseos-source
      - crb-debug
      - crb-source
changed_repos:
  description: Repositories changed.
  returned: success
  type: list
  elements: str
  sample: ["crb"]
"""

from ansible.module_utils.basic import AnsibleModule
import os
import re

DNF_BIN = "/usr/bin/dnf"
REPO_ID_RE = re.compile(r"^Repo-id\s*:\s*(\S+)$")
REPO_STATUS_RE = re.compile(r"^Repo-status\s*:\s*(disabled|enabled)$")


def get_repo_states(module):
    rc, out, err = module.run_command([DNF_BIN, "repolist", "--all", "--verbose"], check_rc=True)

    repos = dict()
    last_repo = ""
    for i, line in enumerate(out.split("\n")):
        m = REPO_ID_RE.match(line)
        if m:
            if len(last_repo) > 0:
                module.fail_json(msg="dnf repolist parse failure: parsed another repo id before next status")
            last_repo = m.group(1)
            continue
        m = REPO_STATUS_RE.match(line)
        if m:
            if len(last_repo) == 0:
                module.fail_json(msg="dnf repolist parse failure: parsed status before repo id")
            repos[last_repo] = m.group(1)
            last_repo = ""
    return repos


def set_repo_states(module, repo_ids, state):
    module.run_command([DNF_BIN, "config-manager", "--assumeyes", f"--set-{state}"] + repo_ids, check_rc=True)


def pack_repo_states_for_return(states):
    enabled = []
    disabled = []
    for repo_id in states:
        if states[repo_id] == "enabled":
            enabled.append(repo_id)
        else:
            disabled.append(repo_id)

    # Sort for consistent results
    enabled.sort()
    disabled.sort()

    return {"enabled": enabled, "disabled": disabled}


def main():
    module_args = dict(
        name=dict(type="list", elements="str", default=[]),
        state=dict(type="str", choices=["enabled", "disabled"], default="enabled"),
    )

    result = dict(changed=False)

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
    module.run_command_environ_update = dict(LANGUAGE="C", LC_ALL="C")

    if not os.path.exists(DNF_BIN):
        module.fail_json(msg=f"{DNF_BIN} was not found")

    repo_states = get_repo_states(module)
    result["repo_states_pre"] = pack_repo_states_for_return(repo_states)

    desired_repo_state = module.params["state"]
    names = module.params["name"]

    to_change = []
    for repo_id in names:
        if repo_id not in repo_states:
            module.fail_json(msg=f"did not find repo with ID '{repo_id}' in dnf repolist --all --verbose")
        if repo_states[repo_id] != desired_repo_state:
            to_change.append(repo_id)
    result["changed"] = len(to_change) > 0
    result["changed_repos"] = to_change

    if module.check_mode:
        module.exit_json(**result)

    if len(to_change) > 0:
        set_repo_states(module, to_change, desired_repo_state)

    repo_states_post = get_repo_states(module)
    result["repo_states_post"] = pack_repo_states_for_return(repo_states_post)

    for repo_id in to_change:
        if repo_states_post[repo_id] != desired_repo_state:
            module.fail_json(msg=f"dnf config-manager failed to make '{repo_id}' {desired_repo_state}")

    module.exit_json(**result)


if __name__ == "__main__":
    main()
