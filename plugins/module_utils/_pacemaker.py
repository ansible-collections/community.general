# Copyright (c) 2025, Dexter Le <dextersydney2001@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Note that this module util is **PRIVATE** to the collection. It can have breaking changes at any time.
# Do not use this from other collections or standalone plugins/modules!

from __future__ import annotations

import json
import time
import typing as t

from ansible_collections.community.general.plugins.module_utils._cmd_runner import CmdRunner, cmd_runner_fmt

if t.TYPE_CHECKING:
    from ansible.module_utils.basic import AnsibleModule


_state_map = {
    "present": "create",
    "absent": "remove",
    "cloned": "clone",
    "status": "status",
    "enabled": "enable",
    "disabled": "disable",
    "online": "start",
    "offline": "stop",
    "maintenance": "set",
    "config": "config",
    "cleanup": "cleanup",
}


def fmt_resource_type(value):
    return [
        ":".join(
            value[k] for k in ["resource_standard", "resource_provider", "resource_name"] if value.get(k) is not None
        )
    ]


def fmt_resource_operation(value):
    cmd = []
    for op in value:
        cmd.append("op")
        cmd.append(op.get("operation_action"))
        for operation_option in op.get("operation_option"):
            cmd.append(operation_option)

    return cmd


def fmt_resource_argument(value):
    return ["--group" if value["argument_action"] == "group" else value["argument_action"]] + value["argument_option"]


def get_pacemaker_maintenance_mode(runner: CmdRunner) -> bool:
    """Return True if cluster property ``maintenance-mode`` is set to ``true``.

    Uses ``pcs property config --output-format=json`` (pcs >= 0.11.6) and parses the
    structured output rather than scraping plaintext, so locale-dependent or version-
    dependent text formatting cannot affect the result.
    """
    with runner("cli_action config output_format") as ctx:
        rc, out, err = ctx.run(cli_action="property")
    try:
        data = json.loads(out)
    except (TypeError, ValueError):
        return False
    for nvset in data.get("nvsets") or []:
        for nvpair in nvset.get("nvpairs") or []:
            if nvpair.get("name") == "maintenance-mode" and nvpair.get("value") == "true":
                return True
    return False


def get_pacemaker_resource_config(runner: CmdRunner) -> t.Optional[dict]:
    """Return parsed ``pcs resource config <name> --output-format=json`` for the
    runner-bound ``name``, or ``None`` if the resource does not exist or the output
    cannot be parsed.

    Requires pcs >= 0.11.3.
    """
    with runner("cli_action state name output_format") as ctx:
        rc, out, err = ctx.run(cli_action="resource", state="config")
    if rc != 0 or not out:
        return None
    try:
        return json.loads(out)
    except (TypeError, ValueError):
        return None


def is_resource_cloned(config: t.Mapping, name: str) -> bool:
    """Return True if *name* appears as a clone ``member_id`` in the given resource
    config DTO. Matches both directly-cloned primitives and cloned groups, since pcs
    represents cloned-group membership the same way (``clones[].member_id == <group_id>``).
    """
    return any(clone.get("member_id") == name for clone in config.get("clones") or [])


def wait_for_resource(runner: CmdRunner, cli_noun: str, name: str, wait: int, sleep_interval: int = 5) -> None:
    """Poll ``pcs <cli_noun> status <name>`` until the resource reports Started or the wait budget expires.

    Raises an exception if the resource does not reach the Started state within *wait* seconds.
    """
    deadline = time.monotonic() + wait
    while True:
        with runner("cli_action state name") as ctx:
            rc, out, err = ctx.run(cli_action=cli_noun, state="status")
        if out and "Started" in out:
            return
        if time.monotonic() >= deadline:
            raise Exception(f"Timed out waiting {wait}s for {cli_noun} resource '{name}' to start")
        time.sleep(sleep_interval)


def pacemaker_runner(module: AnsibleModule, **kwargs) -> CmdRunner:
    runner_command = ["pcs"]
    runner = CmdRunner(
        module,
        command=runner_command,
        arg_formats=dict(
            cli_action=cmd_runner_fmt.as_list(),
            state=cmd_runner_fmt.as_map(_state_map),
            name=cmd_runner_fmt.as_list(),
            resource_type=cmd_runner_fmt.as_func(fmt_resource_type),
            resource_option=cmd_runner_fmt.as_list(),
            resource_operation=cmd_runner_fmt.as_func(fmt_resource_operation),
            resource_meta=cmd_runner_fmt.stack(cmd_runner_fmt.as_opt_val)("meta"),
            resource_argument=cmd_runner_fmt.as_func(fmt_resource_argument),
            resource_clone_ids=cmd_runner_fmt.as_list(),
            resource_clone_meta=cmd_runner_fmt.as_list(),
            apply_all=cmd_runner_fmt.as_bool("--all"),
            agent_validation=cmd_runner_fmt.as_bool("--agent-validation"),
            wait=cmd_runner_fmt.as_opt_eq_val("--wait"),
            config=cmd_runner_fmt.as_fixed("config"),
            force=cmd_runner_fmt.as_bool("--force"),
            version=cmd_runner_fmt.as_fixed("--version"),
            output_format=cmd_runner_fmt.as_fixed("--output-format=json"),
        ),
        **kwargs,
    )
    return runner
