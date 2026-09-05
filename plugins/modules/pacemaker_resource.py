#!/usr/bin/python

# Copyright (c) 2025, Dexter Le <dextersydney2001@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: pacemaker_resource
short_description: Manage pacemaker resources
author:
  - Dexter Le (@munchtoast)
version_added: 10.5.0
description:
  - This module can manage resources in a Pacemaker cluster using the pacemaker CLI.
extends_documentation_fragment:
  - community.general._attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  state:
    description:
      - Indicate desired state for cluster resource.
      - The states V(cleanup) and V(cloned) have been added in community.general 11.3.0.
      - If O(state=cloned) or O(state=present), you can set O(resource_clone_ids) and O(resource_clone_meta) to determine exactly what and how to clone.
      - V(present), V(absent), V(cloned), and V(cleanup) are B(configuration) states.
        They mutate the CIB and do not wait for the resource to reach a runtime state.
      - V(enabled) and V(disabled) are B(runtime) states. They change the resource's target-role
        and (when O(wait) is set) poll C(pcs resource status) until the resource reaches a running
        or stopped state respectively.
    choices: [present, absent, cloned, enabled, disabled, cleanup]
    default: present
    type: str
  name:
    description:
      - Specify the resource name to create or clone to.
      - This is required if O(state=present), O(state=absent), O(state=enabled), or O(state=disabled).
    type: str
  resource_type:
    description:
      - Resource type to create.
    type: dict
    suboptions:
      resource_name:
        description:
          - Specify the resource type name.
        type: str
      resource_standard:
        description:
          - Specify the resource type standard.
        type: str
      resource_provider:
        description:
          - Specify the resource type providers.
        type: str
  resource_option:
    description:
      - Specify the resource option to create.
    type: list
    elements: str
    default: []
  resource_operation:
    description:
      - List of operations to associate with resource.
    type: list
    elements: dict
    default: []
    suboptions:
      operation_action:
        description:
          - Operation action to associate with resource.
        type: str
      operation_option:
        description:
          - Operation option to associate with action.
        type: list
        elements: str
  resource_meta:
    description:
      - List of meta to associate with resource.
    type: list
    elements: str
  resource_argument:
    description:
      - Action to associate with resource.
    type: dict
    suboptions:
      argument_action:
        description:
          - Action to apply to resource.
        type: str
        choices: [clone, master, group, promotable]
      argument_option:
        description:
          - Options to associate with resource action.
        type: list
        elements: str
  resource_clone_ids:
    description:
      - List of clone resource IDs to clone from.
    type: list
    elements: str
    version_added: 11.3.0
  resource_clone_meta:
    description:
      - List of metadata to associate with clone resource.
    type: list
    elements: str
    version_added: 11.3.0
  wait:
    description:
      - Timeout period (seconds) for polling the resource's runtime state after O(state=enabled) or O(state=disabled).
      - Ignored on O(state=present), O(state=absent), O(state=cloned), and O(state=cleanup); setting it on those states emits a warning.
      - When O(state=enabled), the module polls until the resource reports V(Started), V(Promoted), or V(Unpromoted).
      - When O(state=disabled), the module polls until the resource reports V(Stopped).
      - The previous default of V(300) applied to O(state=present); it is now unset by default so
        that configuration states remain fast and only runtime states honour the poll budget.
    type: int
"""

EXAMPLES = r"""
---
- name: Create pacemaker resource
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Create virtual-ip resource
      community.general.pacemaker_resource:
        state: present
        name: virtual-ip
        resource_type:
          resource_name: IPaddr2
        resource_option:
          - "ip=[192.168.2.1]"
        resource_argument:
          argument_action: group
          argument_option:
            - master
        resource_operation:
          - operation_action: monitor
            operation_option:
              - interval=20

- name: Create and start virtual-ip resource
  hosts: localhost
  gather_facts: false
  tasks:
    # state=present only ensures the resource is defined in the CIB.
    # Runtime start is delegated to a follow-up state=enabled task so that
    # a missed start is reported as a runtime failure, not a config failure.
    - name: Ensure virtual-ip is defined in the CIB
      community.general.pacemaker_resource:
        state: present
        name: virtual-ip
        resource_type:
          resource_name: IPaddr2
        resource_option:
          - "ip=192.168.2.1"

    - name: Enable virtual-ip and wait until it is Started
      community.general.pacemaker_resource:
        state: enabled
        name: virtual-ip
        wait: 60
"""

RETURN = r"""
cluster_resources:
  description: The cluster resource output message.
  type: str
  sample: "Assumed agent name ocf:heartbeat:IPaddr2 (deduced from IPaddr2)"
  returned: always
"""

from ansible_collections.community.general.plugins.module_utils._module_helper import StateModuleHelper
from ansible_collections.community.general.plugins.module_utils._pacemaker import (
    _STOPPED_READY_STATES,
    get_pacemaker_maintenance_mode,
    pacemaker_runner,
    wait_for_resource,
)

# Ready states used when O(state=enabled) waits for the resource to start.
# Covers both non-promotable (Started) and promotable (Promoted/Unpromoted) resources.
_RUNNING_READY_STATES = ("Started", "Promoted", "Unpromoted")

# Fallback poll budget used only when the caller sets state=enabled or state=disabled
# without an explicit wait. Matches the pre-fix default so runtime waits stay bounded.
_DEFAULT_RUNTIME_WAIT_SECONDS = 300

# States for which the wait parameter is meaningful (runtime state assertion).
_RUNTIME_STATES = frozenset({"enabled", "disabled"})


class PacemakerResource(StateModuleHelper):
    module = dict(
        argument_spec=dict(
            state=dict(
                type="str", default="present", choices=["present", "absent", "cloned", "enabled", "disabled", "cleanup"]
            ),
            name=dict(type="str"),
            resource_type=dict(
                type="dict",
                options=dict(
                    resource_name=dict(type="str"),
                    resource_standard=dict(type="str"),
                    resource_provider=dict(type="str"),
                ),
            ),
            resource_option=dict(type="list", elements="str", default=list()),
            resource_operation=dict(
                type="list",
                elements="dict",
                default=list(),
                options=dict(
                    operation_action=dict(type="str"),
                    operation_option=dict(type="list", elements="str"),
                ),
            ),
            resource_meta=dict(type="list", elements="str"),
            resource_argument=dict(
                type="dict",
                options=dict(
                    argument_action=dict(type="str", choices=["clone", "master", "group", "promotable"]),
                    argument_option=dict(type="list", elements="str"),
                ),
            ),
            resource_clone_ids=dict(type="list", elements="str"),
            resource_clone_meta=dict(type="list", elements="str"),
            wait=dict(type="int"),
        ),
        required_if=[
            ("state", "present", ["resource_type", "resource_option", "name"]),
            ("state", "absent", ["name"]),
            ("state", "enabled", ["name"]),
            ("state", "disabled", ["name"]),
        ],
        supports_check_mode=True,
    )

    def __init_module__(self):
        self.runner = pacemaker_runner(self.module)
        self.vars.set("previous_value", self._get()["out"])
        self.vars.set("value", self.vars.previous_value, change=True, diff=True)
        self.module.params["name"] = self.module.params["name"] or None
        self._warn_if_wait_ignored()

    def _warn_if_wait_ignored(self):
        """Warn when ``wait`` is set on a state that does not perform runtime polling.

        ``wait`` is only meaningful for O(state=enabled) and O(state=disabled). On
        configuration-only states (present, cloned, absent, cleanup) the parameter has
        no effect; emitting a warning surfaces the mismatch to callers upgrading from
        the previous API where O(state=present) also blocked until the resource
        reached ``Started``.
        """
        if self.vars.wait is None:
            return
        if self.vars.state not in _RUNTIME_STATES:
            self.module.warn(
                f"The 'wait' parameter has no effect on state={self.vars.state!r}; "
                "runtime state assertions moved to state=enabled/disabled in community.general 13.4.0. "
                "Set state=enabled to poll until the resource is Started/Promoted/Unpromoted, "
                "or state=disabled to poll until the resource is Stopped."
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
            result = ctx.run(cli_action="resource", state="status")
            return dict(rc=result[0], out=(result[1] if result[1] != "" else None), err=result[2])

    def fmt_as_stack_argument(self, value, arg):
        if value is not None:
            return [x for k in value for x in (arg, k)]

    def state_absent(self):
        force = get_pacemaker_maintenance_mode(self.runner)
        with self.runner(
            "cli_action state name force",
            output_process=self._process_command_output(True, "does not exist"),
            check_mode_skip=True,
        ) as ctx:
            ctx.run(cli_action="resource", force=force)

    def state_present(self):
        # Configuration state: create the resource in the CIB. Runtime state is not asserted here.
        # Callers wanting to block until the resource is running should follow with state=enabled.
        with self.runner(
            "cli_action state name resource_type resource_option resource_operation resource_meta resource_argument "
            "resource_clone_ids resource_clone_meta",
            output_process=self._process_command_output(
                not get_pacemaker_maintenance_mode(self.runner), "already exists"
            ),
            check_mode_skip=True,
        ) as ctx:
            ctx.run(
                cli_action="resource",
                resource_clone_ids=self.fmt_as_stack_argument(self.module.params["resource_clone_ids"], "clone"),
            )

    def state_cloned(self):
        # Configuration state: wrap the resource in a clone. Runtime state is not asserted here.
        with self.runner(
            "cli_action state name resource_clone_ids resource_clone_meta",
            output_process=self._process_command_output(
                not get_pacemaker_maintenance_mode(self.runner), "already a clone resource"
            ),
            check_mode_skip=True,
        ) as ctx:
            ctx.run(
                cli_action="resource",
                resource_clone_meta=self.fmt_as_stack_argument(self.module.params["resource_clone_meta"], "meta"),
            )

    def state_enabled(self):
        # Runtime state: set target-role=Started and (if wait requested) poll until running.
        with self.runner(
            "cli_action state name", output_process=self._process_command_output(True, "Starting"), check_mode_skip=True
        ) as ctx:
            ctx.run(cli_action="resource")
        self._wait_for_runtime_state(_RUNNING_READY_STATES)

    def state_disabled(self):
        # Runtime state: set target-role=Stopped and (if wait requested) poll until stopped.
        with self.runner(
            "cli_action state name", output_process=self._process_command_output(True, "Stopped"), check_mode_skip=True
        ) as ctx:
            ctx.run(cli_action="resource")
        self._wait_for_runtime_state(_STOPPED_READY_STATES)

    def _wait_for_runtime_state(self, ready_states):
        """Poll the resource until it reaches one of *ready_states* or the wait budget expires.

        Skipped entirely in check mode (no state change was actually issued) and when the
        cluster is in maintenance mode (target-role changes are not acted on). An unset
        ``wait`` falls back to ``_DEFAULT_RUNTIME_WAIT_SECONDS`` so ``state=enabled`` still
        blocks by default the way an operator expects — configuration states now short-circuit
        instead.
        """
        if self.module.check_mode:
            return
        if get_pacemaker_maintenance_mode(self.runner):
            return
        wait = self.vars.wait if self.vars.wait is not None else _DEFAULT_RUNTIME_WAIT_SECONDS
        if wait <= 0:
            return
        wait_for_resource(self.runner, "resource", self.vars.name, wait, ready_states=ready_states)

    def state_cleanup(self):
        runner_args = ["cli_action", "state"]
        if self.module.params["name"]:
            runner_args.append("name")
        with self.runner(
            runner_args, output_process=self._process_command_output(True, "Clean"), check_mode_skip=True
        ) as ctx:
            ctx.run(cli_action="resource")


def main():
    PacemakerResource.execute()


if __name__ == "__main__":
    main()
