#!/usr/bin/python

# Copyright (c) 2026, Dexter Le <dextersydney2001@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: kopia_server
short_description: Manage Kopia server users and ACL entries
author:
  - Dexter Le (@munchtoast)
version_added: "13.1.0"
description:
  - Manage users and access control list (ACL) entries on a Kopia repository server.
  - Supports creating, updating, and deleting server users, and adding, listing,
    and deleting ACL rules.
  - This module targets the repository-side user and ACL configuration stored inside
    the repository itself, not the running server process.
  - To manage the server process lifecycle use your system's service manager (for
    example C(ansible.builtin.systemd)).
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
      - Desired state of the resource.
    type: str
    choices:
      user_present: Creates or updates a server user. Requires O(username).
      user_absent: Removes a server user. Requires O(username).
      users_listed: Lists all server users. No additional options required.
      acl_present: Adds an ACL entry. Requires O(acl_user) and O(acl_access).
      acl_absent: Removes an ACL entry. Requires O(acl_user).
      acl_listed: Lists all ACL entries. No additional options required.
      acl_enabled: >-
        Enables ACL enforcement and installs default entries.
        No additional options required.
    default: user_present
  username:
    description:
      - Repository server username in C(user@hostname) format.
      - Required if O(state=user_present) or O(state=user_absent).
    type: str
  user_password:
    description:
      - Password for the server user.
      - Required when O(state=user_present) and O(user_password_hash) is not set.
      - Mutually exclusive with O(user_password_hash).
    type: str
  user_password_hash:
    description:
      - Pre-hashed password for the server user.
      - Required when O(state=user_present) and O(user_password) is not set.
      - Mutually exclusive with O(user_password).
    type: str
  acl_user:
    description:
      - User the ACL rule applies to, in C(user@hostname) format.
      - Required if O(state=acl_present) or O(state=acl_absent).
    type: str
  acl_access:
    description:
      - Access level granted to O(acl_user).
      - Required if O(state=acl_present).
      - Refer to Kopia documentation for supported access level values.
    type: str
  acl_target:
    description:
      - Manifests targeted by the ACL rule, in C(type:T,key1:value1,...) format.
      - Optional if O(state=acl_present).
    type: str
  acl_no_overwrite:
    description:
      - When V(true), do not overwrite an existing rule with the same user and target.
      - Optional if O(state=acl_present).
    type: bool
    default: false
"""

EXAMPLES = r"""
- name: Add a repository server user
  community.general.kopia_server:
    state: user_present
    username: alice@backuphost
    user_password: secretpassword
    config: /etc/kopia/root.config

- name: Update a user with a pre-hashed password
  community.general.kopia_server:
    state: user_present
    username: alice@backuphost
    user_password_hash: "$2a$12$..."
    config: /etc/kopia/root.config

- name: Remove a repository server user
  community.general.kopia_server:
    state: user_absent
    username: alice@backuphost
    config: /etc/kopia/root.config

- name: List all server users
  community.general.kopia_server:
    state: users_listed
    config: /etc/kopia/root.config

- name: Enable ACL enforcement with default entries
  community.general.kopia_server:
    state: acl_enabled
    config: /etc/kopia/root.config

- name: Add an ACL entry granting full access
  community.general.kopia_server:
    state: acl_present
    acl_user: alice@backuphost
    acl_access: FULL
    config: /etc/kopia/root.config

- name: Add a targeted ACL entry
  community.general.kopia_server:
    state: acl_present
    acl_user: bob@backuphost
    acl_access: READ
    acl_target: "type:snapshot,username:bob"
    config: /etc/kopia/root.config

- name: Delete an ACL entry
  community.general.kopia_server:
    state: acl_absent
    acl_user: alice@backuphost
    config: /etc/kopia/root.config

- name: List all ACL entries
  community.general.kopia_server:
    state: acl_listed
    config: /etc/kopia/root.config
"""

RETURN = r"""
kopia_server:
  description: Output from the Kopia server command.
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

# Maps module states to (cli_group, cli_subcommand) pairs used in _run_server_cmd().
_STATE_CLI_MAP = {
    "user_present": ("users", "set"),
    "user_absent": ("users", "delete"),
    "users_listed": ("users", "list"),
    "acl_present": ("acl", "add"),
    "acl_absent": ("acl", "delete"),
    "acl_listed": ("acl", "list"),
    "acl_enabled": ("acl", "enable"),
}


class KopiaServer(StateModuleHelper):
    module = dict(
        supports_check_mode=True,
        argument_spec=dict(
            **KOPIA_COMMON_ARGUMENT_SPEC,
            state=dict(
                type="str",
                default="user_present",
                choices=[
                    "user_present",
                    "user_absent",
                    "users_listed",
                    "acl_present",
                    "acl_absent",
                    "acl_listed",
                    "acl_enabled",
                ],
            ),
            username=dict(type="str"),
            user_password=dict(type="str", no_log=True),
            user_password_hash=dict(type="str", no_log=True),
            acl_user=dict(type="str"),
            acl_access=dict(type="str"),
            acl_target=dict(type="str"),
            acl_no_overwrite=dict(type="bool", default=False),
        ),
        required_if=[
            ("state", "user_present", ["username"]),
            ("state", "user_absent", ["username"]),
            ("state", "acl_present", ["acl_user", "acl_access"]),
            ("state", "acl_absent", ["acl_user"]),
        ],
        mutually_exclusive=[
            ("user_password", "user_password_hash"),
        ],
    )

    def __init_module__(self):
        self.runner = kopia_runner(
            self.module,
            extra_formats=dict(
                list_users=cmd_runner_fmt.as_fixed("server", "users", "list"),
                server_group=cmd_runner_fmt.as_list(),
                server_subcommand=cmd_runner_fmt.as_list(),
                username=cmd_runner_fmt.as_list(),
                user_password=cmd_runner_fmt.as_opt_val("--user-password"),
                user_password_hash=cmd_runner_fmt.as_opt_val("--user-password-hash"),
                acl_user=cmd_runner_fmt.as_opt_val("--user"),
                acl_access=cmd_runner_fmt.as_opt_val("--access"),
                acl_target=cmd_runner_fmt.as_opt_val("--target"),
                acl_no_overwrite=cmd_runner_fmt.as_bool("--no-overwrite"),
            ),
        )
        self.vars.set("previous_value", self._get()["out"])
        self.vars.set("value", self.vars.previous_value, change=True, diff=True)

    def __quit_module__(self):
        self.vars.set("value", self._get()["out"])

    def _get(self):
        with self.runner("list_users config") as ctx:
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

    def _run_server_cmd(self, args_order, ignore_err_msg="", check_mode_skip=True, **run_kwargs):
        group, subcommand = _STATE_CLI_MAP[self.vars.state]
        with self.runner(
            args_order,
            output_process=self._process_command_output(True, ignore_err_msg),
            check_mode_skip=check_mode_skip,
        ) as ctx:
            ctx.run(cli_action="server", server_group=group, server_subcommand=subcommand, **run_kwargs)

    def state_user_present(self):
        self._run_server_cmd(
            "cli_action server_group server_subcommand username user_password user_password_hash config",
            ignore_err_msg="already exists",
        )

    def state_user_absent(self):
        self._run_server_cmd(
            "cli_action server_group server_subcommand username config",
            ignore_err_msg="no such user",
        )

    def state_users_listed(self):
        self._run_server_cmd(
            "cli_action server_group server_subcommand config",
            check_mode_skip=False,
        )

    def state_acl_present(self):
        self._run_server_cmd(
            "cli_action server_group server_subcommand acl_user acl_access acl_target acl_no_overwrite config",
        )

    def state_acl_absent(self):
        self._run_server_cmd(
            "cli_action server_group server_subcommand acl_user config",
            ignore_err_msg="no such rule",
        )

    def state_acl_listed(self):
        self._run_server_cmd(
            "cli_action server_group server_subcommand config",
            check_mode_skip=False,
        )

    def state_acl_enabled(self):
        self._run_server_cmd(
            "cli_action server_group server_subcommand config",
        )


def main():
    KopiaServer.execute()


if __name__ == "__main__":
    main()
