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
  - community.general._attributes
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
      - V(present) and V(absent) are B(configuration) states. They mutate the CIB and do not wait for the STONITH device to reach a runtime state.
      - V(enabled) and V(disabled) are B(runtime) states. They change the STONITH device's target-role
        and (when O(wait) is set) poll C(pcs stonith status) until it reaches a started or stopped state respectively.
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
      - Timeout period (seconds) for polling the STONITH device's runtime state after O(state=enabled) or O(state=disabled).
      - Ignored on O(state=present) and O(state=absent); setting it on those states emits a warning.
      - When O(state=enabled), the module polls until the device reports V(Started).
      - When O(state=disabled), the module polls until the device reports V(Stopped).
      - The previous default of V(300) applied to O(state=present); it is now unset by default so
        that configuration states remain fast and only runtime states honour the poll budget.
    type: int
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

# state=present only ensures the STONITH device is defined in the CIB.
# Runtime start is delegated to a follow-up state=enabled task so that
# a missed start is reported as a runtime failure, not a config failure.
- name: Enable virtual-stonith and wait until it is Started
  community.general.pacemaker_stonith:
    state: enabled
    name: virtual-stonith
    wait: 60
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

from ansible_collections.community.general.plugins.module_utils._module_helper import StateModuleHelper
from ansible_collections.community.general.plugins.module_utils._pacemaker import (
    _DEFAULT_RESOURCE_READY_STATES,
    _STOPPED_READY_STATES,
    pacemaker_runner,
    wait_for_resource,
)

# Fallback poll budget used only when the caller sets state=enabled or state=disabled
# without an explicit wait. Matches the pre-fix default so runtime waits stay bounded.
_DEFAULT_RUNTIME_WAIT_SECONDS = 300

# States for which the wait parameter is meaningful (runtime state assertion).
_RUNTIME_STATES = frozenset({"enabled", "disabled"})


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
            wait=dict(type="int"),
        ),
        required_if=[("state", "present", ["stonith_type", "stonith_options"])],
        supports_check_mode=True,
    )

    def __init_module__(self):
        self.runner = pacemaker_runner(self.module)
        self.vars.set("previous_value", self._get()["out"])
        self.vars.set("value", self.vars.previous_value, change=True, diff=True)
        self._warn_if_wait_ignored()

    def _warn_if_wait_ignored(self):
        """Warn when ``wait`` is set on a state that does not perform runtime polling.

        ``wait`` is only meaningful for O(state=enabled) and O(state=disabled). On
        configuration-only states (present, absent) the parameter has no effect;
        emitting a warning surfaces the mismatch to callers upgrading from the previous
        API where O(state=present) also blocked until the STONITH device reached ``Started``.
        """
        if self.vars.wait is None:
            return
        if self.vars.state not in _RUNTIME_STATES:
            self.module.warn(
                f"The 'wait' parameter has no effect on state={self.vars.state!r}; "
                "runtime state assertions moved to state=enabled/disabled in community.general 13.4.0. "
                "Set state=enabled to poll until the device is Started, "
                "or state=disabled to poll until the device is Stopped."
            )

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
        # Configuration state: create the STONITH device in the CIB. Runtime state is not
        # asserted here — callers wanting to block until the device is running should follow
        # with state=enabled.
        with self.runner(
            "cli_action state name resource_type resource_option resource_operation resource_meta resource_argument agent_validation",
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
        # Runtime state: set target-role=Started and (if wait requested) poll until running.
        with self.runner(
            "cli_action state name", output_process=self._process_command_output(True, "Starting"), check_mode_skip=True
        ) as ctx:
            ctx.run(cli_action="stonith")
        self._wait_for_runtime_state(_DEFAULT_RESOURCE_READY_STATES)

    def state_disabled(self):
        # Runtime state: set target-role=Stopped and (if wait requested) poll until stopped.
        with self.runner(
            "cli_action state name", output_process=self._process_command_output(True, "Stopped"), check_mode_skip=True
        ) as ctx:
            ctx.run(cli_action="stonith")
        self._wait_for_runtime_state(_STOPPED_READY_STATES)

    def _wait_for_runtime_state(self, ready_states):
        """Poll the STONITH device until it reaches one of *ready_states* or the wait budget expires.

        Skipped in check mode (no state change was actually issued). An unset ``wait`` falls
        back to ``_DEFAULT_RUNTIME_WAIT_SECONDS`` so ``state=enabled`` still blocks by default
        the way an operator expects — configuration states now short-circuit instead.
        """
        if self.module.check_mode:
            return
        wait = self.vars.wait if self.vars.wait is not None else _DEFAULT_RUNTIME_WAIT_SECONDS
        if wait <= 0:
            return
        wait_for_resource(self.runner, "stonith", self.vars.name, wait, ready_states=ready_states)


def main():
    PacemakerStonith.execute()


if __name__ == "__main__":
    main()
