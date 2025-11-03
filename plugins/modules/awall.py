#!/usr/bin/python

# Copyright (c) 2017, Ted Trask <ttrask01@yahoo.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
module: awall
short_description: Manage awall policies
author: Ted Trask (@tdtrask) <ttrask01@yahoo.com>
description:
  - This modules allows for enable/disable/activate of C(awall) policies.
  - Alpine Wall (C(awall)) generates a firewall configuration from the enabled policy files and activates the configuration
    on the system.
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
      - One or more policy names.
    type: list
    elements: str
  state:
    description:
      - Whether the policies should be enabled or disabled.
    type: str
    choices: [disabled, enabled]
    default: enabled
  activate:
    description:
      - Activate the new firewall rules.
      - Can be run with other steps or on its own.
      - Idempotency is affected if O(activate=true), as the module always reports a changed state.
    type: bool
    default: false
notes:
  - At least one of O(name) and O(activate) is required.
"""

EXAMPLES = r"""
- name: Enable "foo" and "bar" policy
  community.general.awall:
    name: [foo bar]
    state: enabled

- name: Disable "foo" and "bar" policy and activate new rules
  community.general.awall:
    name:
      - foo
      - bar
    state: disabled
    activate: false

- name: Activate currently enabled firewall rules
  community.general.awall:
    activate: true
"""

RETURN = """ # """

import re
from ansible.module_utils.basic import AnsibleModule


def activate(module):
    cmd = f"{AWALL_PATH} activate --force"
    rc, stdout, stderr = module.run_command(cmd)
    if rc == 0:
        return True
    else:
        module.fail_json(msg="could not activate new rules", stdout=stdout, stderr=stderr)


def is_policy_enabled(module, name):
    cmd = f"{AWALL_PATH} list"
    rc, stdout, stderr = module.run_command(cmd)
    if re.search(rf"^{name}\s+enabled", stdout, re.MULTILINE):
        return True
    return False


def enable_policy(module, names, act):
    policies = []
    for name in names:
        if not is_policy_enabled(module, name):
            policies.append(name)
    if not policies:
        module.exit_json(changed=False, msg="policy(ies) already enabled")
    names = " ".join(policies)
    if module.check_mode:
        cmd = f"{AWALL_PATH} list"
    else:
        cmd = f"{AWALL_PATH} enable {names}"
    rc, stdout, stderr = module.run_command(cmd)
    if rc != 0:
        module.fail_json(msg=f"failed to enable {names}", stdout=stdout, stderr=stderr)
    if act and not module.check_mode:
        activate(module)
    module.exit_json(changed=True, msg=f"enabled awall policy(ies): {names}")


def disable_policy(module, names, act):
    policies = []
    for name in names:
        if is_policy_enabled(module, name):
            policies.append(name)
    if not policies:
        module.exit_json(changed=False, msg="policy(ies) already disabled")
    names = " ".join(policies)
    if module.check_mode:
        cmd = f"{AWALL_PATH} list"
    else:
        cmd = f"{AWALL_PATH} disable {names}"
    rc, stdout, stderr = module.run_command(cmd)
    if rc != 0:
        module.fail_json(msg=f"failed to disable {names}", stdout=stdout, stderr=stderr)
    if act and not module.check_mode:
        activate(module)
    module.exit_json(changed=True, msg=f"disabled awall policy(ies): {names}")


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type="str", default="enabled", choices=["disabled", "enabled"]),
            name=dict(type="list", elements="str"),
            activate=dict(type="bool", default=False),
        ),
        required_one_of=[["name", "activate"]],
        supports_check_mode=True,
    )

    global AWALL_PATH
    AWALL_PATH = module.get_bin_path("awall", required=True)

    p = module.params

    if p["name"]:
        if p["state"] == "enabled":
            enable_policy(module, p["name"], p["activate"])
        elif p["state"] == "disabled":
            disable_policy(module, p["name"], p["activate"])

    if p["activate"]:
        if not module.check_mode:
            activate(module)
        module.exit_json(changed=True, msg="activated awall rules")

    module.fail_json(msg="no action defined")


if __name__ == "__main__":
    main()
