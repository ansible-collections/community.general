#!/usr/bin/python

# Copyright (c) 2026, Dexter Le <dextersydney2001@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: kopia_policy
short_description: Manage Kopia snapshot policies
author:
  - Dexter Le (@munchtoast)
version_added: "13.1.0"
description:
  - Manage Kopia snapshot policies using the Kopia CLI.
  - Supports setting, deleting, showing, and listing policies.
  - Policies control retention, scheduling, file exclusions, and compression for snapshots.
extends_documentation_fragment:
  - community.general._attributes
  - community.general._kopia
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  state:
    description:
      - Desired state of the Kopia policy.
    type: str
    choices:
      set: Creates or updates a policy. At least one policy option must be provided.
      deleted: Removes the policy for O(target) or the global policy when O(global_policy=true).
      listed: Lists all defined policies.
      shown: Displays the effective policy for O(target), including inherited values.
    default: set
  target:
    description:
      - Policy target in one of the following forms.
      - A per-path policy C(user@host:/path).
      - A per-host policy C(@host).
      - A per-user policy C(user@host).
      - Required if O(state=set), O(state=deleted), or O(state=shown), unless O(global_policy=true).
    type: str
  global_policy:
    description:
      - When V(true), operate on the global policy instead of a per-target policy.
      - When V(true), O(target) must not be set.
    type: bool
    default: false
  retention:
    description:
      - Snapshot retention settings. All sub-options accept an integer or the string C(inherit)
        to remove an override and fall back to the parent policy.
    type: dict
    suboptions:
      keep_latest:
        description:
          - Number of most-recent snapshots to keep.
          - Pass C(inherit) to remove this override.
        type: str
      keep_hourly:
        description:
          - Number of most-recent hourly snapshots to keep.
          - Pass C(inherit) to remove this override.
        type: str
      keep_daily:
        description:
          - Number of most-recent daily snapshots to keep.
          - Pass C(inherit) to remove this override.
        type: str
      keep_weekly:
        description:
          - Number of most-recent weekly snapshots to keep.
          - Pass C(inherit) to remove this override.
        type: str
      keep_monthly:
        description:
          - Number of most-recent monthly snapshots to keep.
          - Pass C(inherit) to remove this override.
        type: str
      keep_annual:
        description:
          - Number of most-recent annual snapshots to keep.
          - Pass C(inherit) to remove this override.
        type: str
      ignore_identical:
        description:
          - Do not save a new snapshot if its contents are identical to the previous one.
          - Accepts V(true), V(false), or C(inherit).
        type: str
  scheduling:
    description:
      - Snapshot scheduling settings.
    type: dict
    suboptions:
      interval:
        description:
          - Time between automatic snapshots, for example C(1h), C(30m), or C(24h).
        type: str
      times:
        description:
          - List of times of day at which to take snapshots, in C(HH:mm) format.
          - Pass C(inherit) as the only list entry to remove this override.
        type: list
        elements: str
      manual:
        description:
          - When V(true), only create snapshots manually and disable automatic scheduling.
        type: bool
  files:
    description:
      - File and directory exclusion settings.
    type: dict
    suboptions:
      add_ignore:
        description:
          - List of path patterns to add to the ignore list.
        type: list
        elements: str
      remove_ignore:
        description:
          - List of path patterns to remove from the ignore list.
        type: list
        elements: str
      max_file_size:
        description:
          - Exclude files larger than this size. Accepts a byte count or human-readable string
            such as C(100MB).
        type: str
      one_file_system:
        description:
          - When V(true), do not cross filesystem boundaries during backup.
          - Accepts V(true), V(false), or C(inherit).
        type: str
      ignore_cache_dirs:
        description:
          - When V(true), ignore directories containing a C(CACHEDIR.TAG) file.
          - Accepts V(true), V(false), or C(inherit).
        type: str
  compression:
    description:
      - Compression algorithm to apply to snapshot data.
      - Refer to C(kopia policy set --compression help) for the list of supported algorithms.
    type: str
"""

EXAMPLES = r"""
- name: Set a retention policy for a path
  community.general.kopia_policy:
    state: set
    target: "user@hostname:/home/user"
    retention:
      keep_latest: "10"
      keep_daily: "7"
      keep_weekly: "4"
      keep_monthly: "6"
    config: /etc/kopia/root.config

- name: Set a scheduled snapshot policy
  community.general.kopia_policy:
    state: set
    target: "user@hostname:/var/www"
    scheduling:
      times:
        - "02:00"
        - "14:00"
    config: /etc/kopia/root.config

- name: Set the global policy with compression and ignore rules
  community.general.kopia_policy:
    state: set
    global_policy: true
    compression: zstd
    files:
      add_ignore:
        - "*.tmp"
        - ".cache"
      ignore_cache_dirs: "true"
    config: /etc/kopia/root.config

- name: Inherit keep_daily from the parent policy
  community.general.kopia_policy:
    state: set
    target: "user@hostname:/home/user"
    retention:
      keep_daily: inherit
    config: /etc/kopia/root.config

- name: Show the effective policy for a target
  community.general.kopia_policy:
    state: shown
    target: "user@hostname:/home/user"
    config: /etc/kopia/root.config

- name: List all defined policies
  community.general.kopia_policy:
    state: listed
    config: /etc/kopia/root.config

- name: Delete a policy for a specific target
  community.general.kopia_policy:
    state: deleted
    target: "user@hostname:/home/user"
    config: /etc/kopia/root.config
"""

RETURN = r"""
kopia_policy:
  description: Output from the Kopia policy command.
  type: str
  sample: ""
  returned: always
"""

from ansible_collections.community.general.plugins.module_utils._cmd_runner import cmd_runner_fmt
from ansible_collections.community.general.plugins.module_utils._kopia import (
    KOPIA_COMMON_ARGUMENT_SPEC,
    kopia_runner,
)
from ansible_collections.community.general.plugins.module_utils._module_helper import StateModuleHelper


def _fmt_retention(value):
    """Expand the retention dict into --keep-* and --ignore-identical-snapshots flags."""
    if not value:
        return []
    flag_map = {
        "keep_latest": "--keep-latest",
        "keep_hourly": "--keep-hourly",
        "keep_daily": "--keep-daily",
        "keep_weekly": "--keep-weekly",
        "keep_monthly": "--keep-monthly",
        "keep_annual": "--keep-annual",
        "ignore_identical": "--ignore-identical-snapshots",
    }
    result = []
    for param, flag in flag_map.items():
        v = value.get(param)
        if v is not None:
            result.extend([flag, str(v)])
    return result


def _fmt_scheduling(value):
    """Expand the scheduling dict into --snapshot-interval, --snapshot-time, --manual flags."""
    if not value:
        return []
    result = []
    if value.get("interval") is not None:
        result.extend(["--snapshot-interval", value["interval"]])
    if value.get("times") is not None:
        result.extend(["--snapshot-time", ",".join(value["times"])])
    if value.get("manual"):
        result.append("--manual")
    return result


def _fmt_files(value):
    """Expand the files dict into file-handling flags."""
    if not value:
        return []
    result = []
    for path in value.get("add_ignore") or []:
        result.extend(["--add-ignore", path])
    for path in value.get("remove_ignore") or []:
        result.extend(["--remove-ignore", path])
    if value.get("max_file_size") is not None:
        result.extend(["--max-file-size", value["max_file_size"]])
    if value.get("one_file_system") is not None:
        result.extend(["--one-file-system", value["one_file_system"]])
    if value.get("ignore_cache_dirs") is not None:
        result.extend(["--ignore-cache-dirs", value["ignore_cache_dirs"]])
    return result


class KopiaPolicy(StateModuleHelper):
    module = dict(
        supports_check_mode=True,
        argument_spec=dict(
            **KOPIA_COMMON_ARGUMENT_SPEC,
            state=dict(
                type="str",
                default="set",
                choices=["set", "deleted", "listed", "shown"],
            ),
            target=dict(type="str"),
            global_policy=dict(type="bool", default=False),
            retention=dict(
                type="dict",
                options=dict(
                    keep_latest=dict(type="str"),
                    keep_hourly=dict(type="str"),
                    keep_daily=dict(type="str"),
                    keep_weekly=dict(type="str"),
                    keep_monthly=dict(type="str"),
                    keep_annual=dict(type="str"),
                    ignore_identical=dict(type="str"),
                ),
            ),
            scheduling=dict(
                type="dict",
                options=dict(
                    interval=dict(type="str"),
                    times=dict(type="list", elements="str"),
                    manual=dict(type="bool"),
                ),
            ),
            files=dict(
                type="dict",
                options=dict(
                    add_ignore=dict(type="list", elements="str"),
                    remove_ignore=dict(type="list", elements="str"),
                    max_file_size=dict(type="str"),
                    one_file_system=dict(type="str"),
                    ignore_cache_dirs=dict(type="str"),
                ),
            ),
            compression=dict(type="str"),
        ),
        required_if=[
            ("state", "set", ["target", "global_policy"], True),
            ("state", "deleted", ["target", "global_policy"], True),
            ("state", "shown", ["target", "global_policy"], True),
        ],
    )

    def __init_module__(self):
        self.runner = kopia_runner(
            self.module,
            extra_formats=dict(
                list_policies=cmd_runner_fmt.as_fixed("policy", "list"),
                target=cmd_runner_fmt.as_list(),
                global_policy=cmd_runner_fmt.as_bool("--global"),
                retention=cmd_runner_fmt.as_func(_fmt_retention),
                scheduling=cmd_runner_fmt.as_func(_fmt_scheduling),
                files=cmd_runner_fmt.as_func(_fmt_files),
                compression=cmd_runner_fmt.as_opt_val("--compression"),
            ),
        )
        self.vars.set("previous_value", self._get()["out"])
        self.vars.set("value", self.vars.previous_value, change=True, diff=True)

    def __quit_module__(self):
        self.vars.set("value", self._get()["out"])

    def _get(self):
        with self.runner("list_policies config") as ctx:
            result = ctx.run()
            return dict(
                rc=result[0],
                out=(result[1].rstrip() if result[1] else None),
                err=result[2],
            )

    def _process_command_output(self, fail_on_err, ignore_err_msg=""):
        def process(rc, out, err):
            if fail_on_err and rc != 0 and err and ignore_err_msg not in err:
                self.do_raise(f"kopia failed with error (rc={rc}): {err}")
            out = out.rstrip() if out else ""
            return None if out == "" else out

        return process

    def state_set(self):
        with self.runner(
            "cli_action state target global_policy retention scheduling files compression config",
            output_process=self._process_command_output(True),
            check_mode_skip=True,
        ) as ctx:
            ctx.run(cli_action="policy")

    def state_deleted(self):
        with self.runner(
            "cli_action state target global_policy config",
            output_process=self._process_command_output(True, "no such policy"),
            check_mode_skip=True,
        ) as ctx:
            ctx.run(cli_action="policy")

    def state_listed(self):
        with self.runner(
            "cli_action state config",
            output_process=self._process_command_output(True),
        ) as ctx:
            ctx.run(cli_action="policy")

    def state_shown(self):
        with self.runner(
            "cli_action state target global_policy config",
            output_process=self._process_command_output(True),
        ) as ctx:
            ctx.run(cli_action="policy")


def main():
    KopiaPolicy.execute()


if __name__ == "__main__":
    main()
