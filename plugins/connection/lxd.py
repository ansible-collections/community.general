# -*- coding: utf-8 -*-
# Copyright (c) 2016 Matt Clay <matt@mystile.com>
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
author: Matt Clay (@mattclay) <matt@mystile.com>
name: lxd
short_description: Run tasks in LXD instances using C(lxc) CLI
description:
  - Run commands or put/fetch files to an existing instance using C(lxc) CLI.
options:
  remote_addr:
    description:
      - Instance (container/VM) identifier.
      - Since community.general 8.0.0, a FQDN can be provided; in that case, the first component (the part before C(.)) is
        used as the instance identifier.
    type: string
    default: inventory_hostname
    vars:
      - name: inventory_hostname
      - name: ansible_host
      - name: ansible_lxd_host
  executable:
    description:
      - Shell to use for execution inside instance.
    type: string
    default: /bin/sh
    vars:
      - name: ansible_executable
      - name: ansible_lxd_executable
  lxd_become_method:
    description:
      - Become command used to switch to a non-root user.
      - Is only used when O(remote_user) is not V(root).
    type: str
    default: /bin/su
    vars:
      - name: lxd_become_method
    version_added: 10.4.0
  remote:
    description:
      - Name of the LXD remote to use.
    type: string
    default: local
    vars:
      - name: ansible_lxd_remote
    version_added: 2.0.0
  remote_user:
    description:
      - User to login/authenticate as.
      - Can be set from the CLI via the C(--user) or C(-u) options.
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
      - Name of the LXD project to use.
    type: string
    vars:
      - name: ansible_lxd_project
    version_added: 2.0.0
"""

import os
from subprocess import Popen, PIPE

from ansible.errors import AnsibleError, AnsibleConnectionFailure, AnsibleFileNotFound
from ansible.module_utils.common.process import get_bin_path
from ansible.module_utils.common.text.converters import to_bytes, to_text
from ansible.plugins.connection import ConnectionBase


class Connection(ConnectionBase):
    """ lxd based connections """

    transport = 'community.general.lxd'
    has_pipelining = True

    def __init__(self, play_context, new_stdin, *args, **kwargs):
        super(Connection, self).__init__(play_context, new_stdin, *args, **kwargs)

        try:
            self._lxc_cmd = get_bin_path("lxc")
        except ValueError:
            raise AnsibleError("lxc command not found in PATH")

    def _host(self):
        """ translate remote_addr to lxd (short) hostname """
        return self.get_option("remote_addr").split(".", 1)[0]

    def _connect(self):
        """connect to lxd (nothing to do here) """
        super(Connection, self)._connect()

        if not self._connected:
            self._display.vvv(f"ESTABLISH LXD CONNECTION FOR USER: {self.get_option('remote_user')}", host=self._host())
            self._connected = True

    def _build_command(self, cmd) -> str:
        """build the command to execute on the lxd host"""

        exec_cmd = [self._lxc_cmd]

        if self.get_option("project"):
            exec_cmd.extend(["--project", self.get_option("project")])

        exec_cmd.extend(["exec", f"{self.get_option('remote')}:{self._host()}", "--"])

        if self.get_option("remote_user") != "root":
            self._display.vvv(
                f"INFO: Running as non-root user: {self.get_option('remote_user')}, \
                trying to run 'lxc exec' with become method: {self.get_option('lxd_become_method')}",
                host=self._host(),
            )
            exec_cmd.extend(
                [self.get_option("lxd_become_method"), self.get_option("remote_user"), "-c"]
            )

        exec_cmd.extend([self.get_option("executable"), "-c", cmd])

        return exec_cmd

    def exec_command(self, cmd, in_data=None, sudoable=True):
        """ execute a command on the lxd host """
        super(Connection, self).exec_command(cmd, in_data=in_data, sudoable=sudoable)

        self._display.vvv(f"EXEC {cmd}", host=self._host())

        local_cmd = self._build_command(cmd)
        self._display.vvvvv(f"EXEC {local_cmd}", host=self._host())

        local_cmd = [to_bytes(i, errors='surrogate_or_strict') for i in local_cmd]
        in_data = to_bytes(in_data, errors='surrogate_or_strict', nonstring='passthru')

        process = Popen(local_cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate(in_data)

        stdout = to_text(stdout)
        stderr = to_text(stderr)

        self._display.vvvvv(f"EXEC lxc output: {stdout} {stderr}", host=self._host())

        if "is not running" in stderr:
            raise AnsibleConnectionFailure(f"instance not running: {self._host()}")

        if stderr.strip() == "Error: Instance not found" or stderr.strip() == "error: not found":
            raise AnsibleConnectionFailure(f"instance not found: {self._host()}")

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
        """ put a file from local to lxd """
        super(Connection, self).put_file(in_path, out_path)

        self._display.vvv(f"PUT {in_path} TO {out_path}", host=self._host())

        if not os.path.isfile(to_bytes(in_path, errors='surrogate_or_strict')):
            raise AnsibleFileNotFound(f"input path is not a file: {in_path}")

        local_cmd = [self._lxc_cmd]
        if self.get_option("project"):
            local_cmd.extend(["--project", self.get_option("project")])

        if self.get_option("remote_user") != "root":
            uid, gid = self._get_remote_uid_gid()
            local_cmd.extend(
                [
                    "file",
                    "push",
                    "--uid",
                    str(uid),
                    "--gid",
                    str(gid),
                    in_path,
                    f"{self.get_option('remote')}:{self._host()}/{out_path}",
                ]
            )
        else:
            local_cmd.extend(
                [
                    "file",
                    "push",
                    in_path,
                    f"{self.get_option('remote')}:{self._host()}/{out_path}",
                ]
            )

        self._display.vvvvv(f"PUT {local_cmd}", host=self._host())

        local_cmd = [to_bytes(i, errors='surrogate_or_strict') for i in local_cmd]

        process = Popen(local_cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        process.communicate()

    def fetch_file(self, in_path, out_path):
        """ fetch a file from lxd to local """
        super(Connection, self).fetch_file(in_path, out_path)

        self._display.vvv(f"FETCH {in_path} TO {out_path}", host=self._host())

        local_cmd = [self._lxc_cmd]
        if self.get_option("project"):
            local_cmd.extend(["--project", self.get_option("project")])
        local_cmd.extend([
            "file", "pull",
            f"{self.get_option('remote')}:{self._host()}/{in_path}",
            out_path
        ])

        local_cmd = [to_bytes(i, errors='surrogate_or_strict') for i in local_cmd]

        process = Popen(local_cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        process.communicate()

    def close(self):
        """ close the connection (nothing to do here) """
        super(Connection, self).close()

        self._connected = False
