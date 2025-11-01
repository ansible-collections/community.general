#!/usr/bin/python

# Copyright (c) 2025, Dexter Le <dextersydney2001@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = """
module: pacemaker_stonith
short_description: Manage Pacemaker STONITH
author:
  - Dexter Le (@munchtoast)
version_added: 11.3.0
description:
  - This module manages STONITH in a Pacemaker cluster using the Pacemaker CLI.
seealso:
  - name: Pacemaker STONITH documentation
    description: Complete documentation for Pacemaker STONITH.
    link: https://clusterlabs.org/projects/pacemaker/doc/3.0/Pacemaker_Explained/html/resources.html#stonith
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: partial
    details:
      - Only works when check mode is not enabled.
options:
  state:
    description:
      - Indicate desired state for cluster STONITH.
    choices: [present, absent, enabled, disabled]
    default: present
    type: str
  name:
    description:
      - Specify the STONITH name to create.
    required: true
    type: str
  stonith_type:
    description:
      - Specify the STONITH device type.
    type: str
  stonith_options:
    description:
      - Specify the STONITH option to create.
    type: list
    elements: str
    default: []
  stonith_operations:
    description:
      - List of operations to associate with STONITH.
    type: list
    elements: dict
    default: []
    suboptions:
      operation_action:
        description:
          - Operation action to associate with STONITH.
        type: str
      operation_options:
        description:
          - Operation options to associate with action.
        type: list
        elements: str
  stonith_metas:
    description:
      - List of metadata to associate with STONITH.
    type: list
    elements: str
  stonith_argument:
    description:
      - Action to associate with STONITH.
    type: dict
    suboptions:
      argument_action:
        description:
          - Action to apply to STONITH.
        type: str
        choices: [group, before, after]
      argument_options:
        description:
          - Options to associate with STONITH action.
        type: list
        elements: str
  agent_validation:
    description:
      - Enabled agent validation for STONITH creation.
    type: bool
    default: false
  wait:
    description:
      - Timeout period for polling the STONITH creation.
    type: int
    default: 300
"""

EXAMPLES = """
- name: Create virtual-ip STONITH
  community.general.pacemaker_stonith:
    state: present
    name: virtual-stonith
    stonith_type: fence_virt
    stonith_options:
      - "pcmk_host_list=f1"
    stonith_operations:
      - operation_action: monitor
        operation_options:
          - "interval=30s"
"""

RETURN = """
previous_value:
  description: The value of the STONITH before executing the module.
  type: str
  sample: "  * virtual-stonith\t(stonith:fence_virt):\t Started"
  returned: on success
value:
  description: The value of the STONITH after executing the module.
  type: str
  sample: "  * virtual-stonith\t(stonith:fence_virt):\t Started"
  returned: on success
"""

from ansible_collections.community.general.plugins.module_utils.module_helper import StateModuleHelper
from ansible_collections.community.general.plugins.module_utils.pacemaker import pacemaker_runner


class PacemakerStonith(StateModuleHelper):
    module = dict(
        argument_spec=dict(
            state=dict(type="str", default="present", choices=["present", "absent", "enabled", "disabled"]),
            name=dict(type="str", required=True),
            stonith_type=dict(type="str"),
            stonith_options=dict(type="list", elements="str", default=[]),
            stonith_operations=dict(
                type="list",
                elements="dict",
                default=[],
                options=dict(
                    operation_action=dict(type="str"),
                    operation_options=dict(type="list", elements="str"),
                ),
            ),
            stonith_metas=dict(type="list", elements="str"),
            stonith_argument=dict(
                type="dict",
                options=dict(
                    argument_action=dict(type="str", choices=["before", "after", "group"]),
                    argument_options=dict(type="list", elements="str"),
                ),
            ),
            agent_validation=dict(type="bool", default=False),
            wait=dict(type="int", default=300),
        ),
        required_if=[("state", "present", ["stonith_type", "stonith_options"])],
        supports_check_mode=True,
    )

    def __init_module__(self):
        self.runner = pacemaker_runner(self.module)
        self.vars.set("previous_value", self._get()["out"])
        self.vars.set("value", self.vars.previous_value, change=True, diff=True)

    def __quit_module__(self):
        self.vars.set("value", self._get()["out"])

    def _process_command_output(self, fail_on_err, ignore_err_msg=""):
        def process(rc, out, err):
            if fail_on_err and rc != 0 and err and ignore_err_msg not in err:
                self.do_raise(f"pcs failed with error (rc={rc}): {err}")
            out = out.rstrip()
            return None if out == "" else out

        return process

    def _get(self):
        with self.runner("cli_action state name") as ctx:
            result = ctx.run(cli_action="stonith", state="status")
            return dict(rc=result[0], out=result[1] if result[1] != "" else None, err=result[2])

    def fmt_stonith_resource(self):
        return dict(resource_name=self.vars.stonith_type)

    # TODO: Pluralize operation_options in separate PR and remove this helper fmt function
    def fmt_stonith_operations(self):
        modified_stonith_operations = []
        for stonith_operation in self.vars.stonith_operations:
            modified_stonith_operations.append(
                dict(
                    operation_action=stonith_operation.get("operation_action"),
                    operation_option=stonith_operation.get("operation_options"),
                )
            )
        return modified_stonith_operations

    def state_absent(self):
        with self.runner(
            "cli_action state name",
            output_process=self._process_command_output(True, "does not exist"),
            check_mode_skip=True,
        ) as ctx:
            ctx.run(cli_action="stonith")

    def state_present(self):
        with self.runner(
            "cli_action state name resource_type resource_option resource_operation resource_meta resource_argument agent_validation wait",
            output_process=self._process_command_output(True, "already exists"),
            check_mode_skip=True,
        ) as ctx:
            ctx.run(
                cli_action="stonith",
                resource_type=self.fmt_stonith_resource(),
                resource_option=self.vars.stonith_options,
                resource_operation=self.fmt_stonith_operations(),
                resource_meta=self.vars.stonith_metas,
                resource_argument=self.vars.stonith_argument,
            )

    def state_enabled(self):
        with self.runner(
            "cli_action state name", output_process=self._process_command_output(True, "Starting"), check_mode_skip=True
        ) as ctx:
            ctx.run(cli_action="stonith")

    def state_disabled(self):
        with self.runner(
            "cli_action state name", output_process=self._process_command_output(True, "Stopped"), check_mode_skip=True
        ) as ctx:
            ctx.run(cli_action="stonith")


def main():
    PacemakerStonith.execute()


if __name__ == "__main__":
    main()
