# -*- coding: utf-8 -*-
# Based on lxd.py (c) 2016, Matt Clay <matt@mystile.com>
# (c) 2023, Stephane Graber <stgraber@stgraber.org>
# Copyright (c) 2023 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
author: Stéphane Graber (@stgraber)
name: incus
short_description: Run tasks in Incus instances using the Incus CLI
description:
  - Run commands or put/fetch files to an existing Incus instance using Incus CLI.
version_added: "8.2.0"
options:
  remote_addr:
    description:
      - The instance identifier.
    type: string
    default: inventory_hostname
    vars:
      - name: inventory_hostname
      - name: ansible_host
      - name: ansible_incus_host
  executable:
    description:
      - The shell to use for execution inside the instance.
    type: string
    default: /bin/sh
    vars:
      - name: ansible_executable
      - name: ansible_incus_executable
  incus_become_method:
    description:
      - Become command used to switch to a non-root user.
      - Is only used when O(remote_user) is not V(root).
    type: str
    default: /bin/su
    vars:
      - name: incus_become_method
    version_added: 10.4.0
  remote:
    description:
      - The name of the Incus remote to use (per C(incus remote list)).
      - Remotes are used to access multiple servers from a single client.
    type: string
    default: local
    vars:
      - name: ansible_incus_remote
  remote_user:
    description:
      - User to login/authenticate as.
      - Can be set from the CLI with the C(--user) or C(-u) options.
    type: string
    default: root
    vars:
      - name: ansible_user
    env:
      - name: ANSIBLE_REMOTE_USER
    ini:
      - section: defaults
        key: remote_user
    keyword:
      - name: remote_user
    version_added: 10.4.0
  project:
    description:
      - The name of the Incus project to use (per C(incus project list)).
      - Projects are used to divide the instances running on a server.
    type: string
    default: default
    vars:
      - name: ansible_incus_project
"""

import os
from subprocess import call, Popen, PIPE

from ansible.errors import AnsibleError, AnsibleConnectionFailure, AnsibleFileNotFound
from ansible.module_utils.common.process import get_bin_path
from ansible.module_utils.common.text.converters import to_bytes, to_text
from ansible.plugins.connection import ConnectionBase


class Connection(ConnectionBase):
    """ Incus based connections """

    transport = "incus"
    has_pipelining = True

    def __init__(self, play_context, new_stdin, *args, **kwargs):
        super(Connection, self).__init__(play_context, new_stdin, *args, **kwargs)

        self._incus_cmd = get_bin_path("incus")

        if not self._incus_cmd:
            raise AnsibleError("incus command not found in PATH")

    def _connect(self):
        """connect to Incus (nothing to do here) """
        super(Connection, self)._connect()

        if not self._connected:
            self._display.vvv(f"ESTABLISH Incus CONNECTION FOR USER: {self.get_option('remote_user')}",
                              host=self._instance())
            self._connected = True

    def _build_command(self, cmd) -> str:
        """build the command to execute on the incus host"""

        exec_cmd = [
            self._incus_cmd,
            "--project", self.get_option("project"),
            "exec",
            f"{self.get_option('remote')}:{self._instance()}",
            "--"]

        if self.get_option("remote_user") != "root":
            self._display.vvv(
                f"INFO: Running as non-root user: {self.get_option('remote_user')}, \
                trying to run 'incus exec' with become method: {self.get_option('incus_become_method')}",
                host=self._instance(),
            )
            exec_cmd.extend(
                [self.get_option("incus_become_method"), self.get_option("remote_user"), "-c"]
            )

        exec_cmd.extend([self.get_option("executable"), "-c", cmd])

        return exec_cmd

    def _instance(self):
        # Return only the leading part of the FQDN as the instance name
        # as Incus instance names cannot be a FQDN.
        return self.get_option('remote_addr').split(".")[0]

    def exec_command(self, cmd, in_data=None, sudoable=True):
        """ execute a command on the Incus host """
        super(Connection, self).exec_command(cmd, in_data=in_data, sudoable=sudoable)

        self._display.vvv(f"EXEC {cmd}",
                          host=self._instance())

        local_cmd = self._build_command(cmd)
        self._display.vvvvv(f"EXEC {local_cmd}", host=self._instance())

        local_cmd = [to_bytes(i, errors='surrogate_or_strict') for i in local_cmd]
        in_data = to_bytes(in_data, errors='surrogate_or_strict', nonstring='passthru')

        process = Popen(local_cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate(in_data)

        stdout = to_text(stdout)
        stderr = to_text(stderr)

        if stderr.startswith("Error: ") and stderr.rstrip().endswith(
            ": Instance is not running"
        ):
            raise AnsibleConnectionFailure(
                f"instance not running: {self._instance()} (remote={self.get_option('remote')}, project={self.get_option('project')})"
            )

        if stderr.startswith("Error: ") and stderr.rstrip().endswith(
            ": Instance not found"
        ):
            raise AnsibleConnectionFailure(
                f"instance not found: {self._instance()} (remote={self.get_option('remote')}, project={self.get_option('project')})"
            )

        if (
            stderr.startswith("Error: ")
            and ": User does not have permission " in stderr
        ):
            raise AnsibleConnectionFailure(
                f"instance access denied: {self._instance()} (remote={self.get_option('remote')}, project={self.get_option('project')})"
            )

        if (
            stderr.startswith("Error: ")
            and ": User does not have entitlement " in stderr
        ):
            raise AnsibleConnectionFailure(
                f"instance access denied: {self._instance()} (remote={self.get_option('remote')}, project={self.get_option('project')})"
            )

        return process.returncode, stdout, stderr

    def _get_remote_uid_gid(self) -> tuple[int, int]:
        """Get the user and group ID of 'remote_user' from the instance."""

        rc, uid_out, err = self.exec_command("/bin/id -u")
        if rc != 0:
            raise AnsibleError(
                f"Failed to get remote uid for user {self.get_option('remote_user')}: {err}"
            )
        uid = uid_out.strip()

        rc, gid_out, err = self.exec_command("/bin/id -g")
        if rc != 0:
            raise AnsibleError(
                f"Failed to get remote gid for user {self.get_option('remote_user')}: {err}"
            )
        gid = gid_out.strip()

        return int(uid), int(gid)

    def put_file(self, in_path, out_path):
        """ put a file from local to Incus """
        super(Connection, self).put_file(in_path, out_path)

        self._display.vvv(f"PUT {in_path} TO {out_path}",
                          host=self._instance())

        if not os.path.isfile(to_bytes(in_path, errors='surrogate_or_strict')):
            raise AnsibleFileNotFound(f"input path is not a file: {in_path}")

        if self.get_option("remote_user") != "root":
            uid, gid = self._get_remote_uid_gid()
            local_cmd = [
                self._incus_cmd,
                "--project",
                self.get_option("project"),
                "file",
                "push",
                "--uid",
                str(uid),
                "--gid",
                str(gid),
                "--quiet",
                in_path,
                f"{self.get_option('remote')}:{self._instance()}/{out_path}",
            ]
        else:
            local_cmd = [
                self._incus_cmd,
                "--project",
                self.get_option("project"),
                "file",
                "push",
                "--quiet",
                in_path,
                f"{self.get_option('remote')}:{self._instance()}/{out_path}",
            ]

        self._display.vvvvv(f"PUT {local_cmd}", host=self._instance())

        local_cmd = [to_bytes(i, errors='surrogate_or_strict') for i in local_cmd]

        call(local_cmd)

    def fetch_file(self, in_path, out_path):
        """ fetch a file from Incus to local """
        super(Connection, self).fetch_file(in_path, out_path)

        self._display.vvv(f"FETCH {in_path} TO {out_path}",
                          host=self._instance())

        local_cmd = [
            self._incus_cmd,
            "--project", self.get_option("project"),
            "file", "pull", "--quiet",
            f"{self.get_option('remote')}:{self._instance()}/{in_path}",
            out_path]

        local_cmd = [to_bytes(i, errors='surrogate_or_strict') for i in local_cmd]

        call(local_cmd)

    def close(self):
        """ close the connection (nothing to do here) """
        super(Connection, self).close()

        self._connected = False
