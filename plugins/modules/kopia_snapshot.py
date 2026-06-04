#!/usr/bin/python

# Copyright (c) 2026, Dexter Le <dextersydney2001@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: kopia_snapshot
short_description: Manage Kopia snapshots
author:
  - Dexter Le (@munchtoast)
version_added: "13.1.0"
description:
  - Manage Kopia snapshots using the Kopia CLI.
  - Supports creating, deleting, and verifying snapshots, as well as listing and expiring them.
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
      - Desired state of the Kopia snapshot.
      - V(created) takes a new snapshot of O(source).
      - V(deleted) deletes the snapshot identified by O(snapshot_id).
      - V(expired) applies retention policy and deletes snapshots that no longer meet it.
        This is a dry-run unless O(delete=true).
      - V(listed) lists snapshots for O(source) or all sources when O(source) is not set.
      - V(verified) verifies the integrity of snapshots identified by O(snapshot_id),
        or all snapshots when O(snapshot_id) is not set.
    type: str
    choices: [created, deleted, expired, listed, verified]
    default: created
  source:
    description:
      - Path of the source directory or file to snapshot.
      - Required if O(state=created).
      - When O(state=listed) or O(state=expired), limits the operation to this source path.
    type: str
  snapshot_id:
    description:
      - One or more snapshot manifest IDs to operate on.
      - Required if O(state=deleted).
      - Optional if O(state=verified); verifies all snapshots when omitted.
    type: list
    elements: str
  description:
    description:
      - Free-form description to attach to the snapshot.
      - Optional if O(state=created).
    type: str
  tags:
    description:
      - List of tags to attach to or filter snapshots by, in C(key:value) format.
      - Optional if O(state=created) or O(state=listed).
    type: list
    elements: str
  all_sources:
    description:
      - When V(true), operate on all snapshot sources rather than only the current user and host.
      - Optional if O(state=listed) or O(state=expired).
    type: bool
    default: false
  delete:
    description:
      - When V(true), actually delete snapshots that have expired according to the retention policy.
      - When V(false) the expiration is a dry-run and no snapshots are removed.
      - Required to be V(true) to perform deletion when O(state=expired).
      - Required to be V(true) to confirm deletion when O(state=deleted).
    type: bool
    default: false
  parallel:
    description:
      - Number of parallel upload or verification workers.
      - Optional if O(state=created) or O(state=verified).
    type: int
  fail_fast:
    description:
      - When V(true), abort the snapshot on the first error encountered.
      - Optional if O(state=created).
    type: bool
    default: false
  ignore_identical:
    description:
      - When V(true), skip saving a new snapshot if the contents are identical to the previous one.
      - Optional if O(state=created).
    type: bool
    default: false
  verify_files_percent:
    description:
      - Randomly verify this percentage of files during verification.
      - Value must be between C(0.0) and C(100.0).
      - Optional if O(state=verified).
    type: float
"""

EXAMPLES = r"""
- name: Create a snapshot of /home/user
  community.general.kopia_snapshot:
    state: created
    source: /home/user
    password: secret
    config: /etc/kopia/root.config

- name: Create a tagged snapshot with a description
  community.general.kopia_snapshot:
    state: created
    source: /var/www
    password: secret
    description: "pre-deploy backup"
    tags:
      - env:production
      - app:web

- name: List all snapshots for a source
  community.general.kopia_snapshot:
    state: listed
    source: /home/user
    config: /etc/kopia/root.config

- name: List snapshots across all users and hosts
  community.general.kopia_snapshot:
    state: listed
    all_sources: true
    config: /etc/kopia/root.config

- name: Delete a specific snapshot
  community.general.kopia_snapshot:
    state: deleted
    snapshot_id:
      - abc1234def5678
    delete: true
    config: /etc/kopia/root.config

- name: Expire snapshots (dry run)
  community.general.kopia_snapshot:
    state: expired
    source: /home/user
    config: /etc/kopia/root.config

- name: Expire snapshots (apply deletion)
  community.general.kopia_snapshot:
    state: expired
    source: /home/user
    delete: true
    config: /etc/kopia/root.config

- name: Verify all snapshots
  community.general.kopia_snapshot:
    state: verified
    password: secret
    config: /etc/kopia/root.config

- name: Verify specific snapshots and check 10 percent of files
  community.general.kopia_snapshot:
    state: verified
    snapshot_id:
      - abc1234def5678
      - def5678abc1234
    verify_files_percent: 10.0
    config: /etc/kopia/root.config
"""

RETURN = r"""
kopia_snapshot:
  description: Output from the Kopia snapshot command.
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


class KopiaSnapshot(StateModuleHelper):
    module = dict(
        supports_check_mode=True,
        argument_spec=dict(
            **KOPIA_COMMON_ARGUMENT_SPEC,
            state=dict(
                type="str",
                default="created",
                choices=["created", "deleted", "expired", "listed", "verified"],
            ),
            source=dict(type="str"),
            snapshot_id=dict(type="list", elements="str"),
            description=dict(type="str"),
            tags=dict(type="list", elements="str"),
            all_sources=dict(type="bool", default=False),
            delete=dict(type="bool", default=False),
            parallel=dict(type="int"),
            fail_fast=dict(type="bool", default=False),
            ignore_identical=dict(type="bool", default=False),
            verify_files_percent=dict(type="float"),
        ),
        required_if=[
            ("state", "created", ["source"]),
            ("state", "deleted", ["snapshot_id"]),
        ],
    )

    def __init_module__(self):
        self.runner = kopia_runner(
            self.module,
            extra_formats=dict(
                list_snapshots=cmd_runner_fmt.as_fixed("snapshot", "list"),
                source=cmd_runner_fmt.as_list(),
                snapshot_id=cmd_runner_fmt.as_list(),
                description=cmd_runner_fmt.as_opt_eq_val("--description"),
                tags=cmd_runner_fmt.as_func(lambda v: [x for tag in v for x in ("--tags", tag)]),
                all_sources=cmd_runner_fmt.as_bool("--all"),
                delete=cmd_runner_fmt.as_bool("--delete"),
                parallel=cmd_runner_fmt.as_opt_eq_val("--parallel"),
                fail_fast=cmd_runner_fmt.as_bool("--fail-fast"),
                ignore_identical=cmd_runner_fmt.as_bool("--ignore-identical-snapshots"),
                verify_files_percent=cmd_runner_fmt.as_opt_eq_val("--verify-files-percent"),
            ),
        )
        self.vars.set("previous_value", self._get()["out"])
        self.vars.set("value", self.vars.previous_value, change=True, diff=True)

    def __quit_module__(self):
        self.vars.set("value", self._get()["out"])

    def _get(self):
        with self.runner("list_snapshots config") as ctx:
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

    def state_created(self):
        with self.runner(
            "cli_action state source description tags parallel fail_fast ignore_identical password config",
            output_process=self._process_command_output(True),
            check_mode_skip=True,
        ) as ctx:
            ctx.run(cli_action="snapshot")

    def state_deleted(self):
        with self.runner(
            "cli_action state snapshot_id delete config",
            output_process=self._process_command_output(True),
            check_mode_skip=True,
        ) as ctx:
            ctx.run(cli_action="snapshot")

    def state_expired(self):
        with self.runner(
            "cli_action state source all_sources delete config",
            output_process=self._process_command_output(True),
            check_mode_skip=True,
        ) as ctx:
            ctx.run(cli_action="snapshot")

    def state_listed(self):
        with self.runner(
            "cli_action state source all_sources tags config",
            output_process=self._process_command_output(True),
        ) as ctx:
            ctx.run(cli_action="snapshot")

    def state_verified(self):
        with self.runner(
            "cli_action state snapshot_id parallel verify_files_percent password config",
            output_process=self._process_command_output(True),
            check_mode_skip=True,
        ) as ctx:
            ctx.run(cli_action="snapshot")


def main():
    KopiaSnapshot.execute()


if __name__ == "__main__":
    main()
