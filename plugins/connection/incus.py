# -*- coding: utf-8 -*-
# Based on lxd.py (c) 2016, Matt Clay <matt@mystile.com>
# (c) 2023, Stephane Graber <stgraber@stgraber.org>
# Copyright (c) 2023 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
    author: Stéphane Graber (@stgraber)
    name: incus
    short_description: Run tasks in Incus instances via the Incus CLI.
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
      remote:
        description:
            - The name of the Incus remote to use (per C(incus remote list)).
            - Remotes are used to access multiple servers from a single client.
        type: string
        default: local
        vars:
            - name: ansible_incus_remote
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
from ansible.module_utils._text import to_bytes, to_text
from ansible.plugins.connection import ConnectionBase


class Connection(ConnectionBase):
    """ Incus based connections """

    transport = "incus"
    has_pipelining = True
    default_user = 'root'

    def __init__(self, play_context, new_stdin, *args, **kwargs):
        super(Connection, self).__init__(play_context, new_stdin, *args, **kwargs)

        self._incus_cmd = get_bin_path("incus")

        if not self._incus_cmd:
            raise AnsibleError("incus command not found in PATH")

    def _connect(self):
        """connect to Incus (nothing to do here) """
        super(Connection, self)._connect()

        if not self._connected:
            self._display.vvv(u"ESTABLISH Incus CONNECTION FOR USER: root",
                              host=self._instance())
            self._connected = True

    def _instance(self):
        # Return only the leading part of the FQDN as the instance name
        # as Incus instance names cannot be a FQDN.
        return self.get_option('remote_addr').split(".")[0]

    def exec_command(self, cmd, in_data=None, sudoable=True):
        """ execute a command on the Incus host """
        super(Connection, self).exec_command(cmd, in_data=in_data, sudoable=sudoable)

        self._display.vvv(u"EXEC {0}".format(cmd),
                          host=self._instance())

        local_cmd = [
            self._incus_cmd,
            "--project", self.get_option("project"),
            "exec",
            "%s:%s" % (self.get_option("remote"), self._instance()),
            "--",
            self._play_context.executable, "-c", cmd]

        local_cmd = [to_bytes(i, errors='surrogate_or_strict') for i in local_cmd]
        in_data = to_bytes(in_data, errors='surrogate_or_strict', nonstring='passthru')

        process = Popen(local_cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate(in_data)

        stdout = to_text(stdout)
        stderr = to_text(stderr)

        if stderr == "Error: Instance is not running.\n":
            raise AnsibleConnectionFailure("instance not running: %s" %
                                           self._instance())

        if stderr == "Error: Instance not found\n":
            raise AnsibleConnectionFailure("instance not found: %s" %
                                           self._instance())

        return process.returncode, stdout, stderr

    def put_file(self, in_path, out_path):
        """ put a file from local to Incus """
        super(Connection, self).put_file(in_path, out_path)

        self._display.vvv(u"PUT {0} TO {1}".format(in_path, out_path),
                          host=self._instance())

        if not os.path.isfile(to_bytes(in_path, errors='surrogate_or_strict')):
            raise AnsibleFileNotFound("input path is not a file: %s" % in_path)

        local_cmd = [
            self._incus_cmd,
            "--project", self.get_option("project"),
            "file", "push", "--quiet",
            in_path,
            "%s:%s/%s" % (self.get_option("remote"),
                          self._instance(),
                          out_path)]

        local_cmd = [to_bytes(i, errors='surrogate_or_strict') for i in local_cmd]

        call(local_cmd)

    def fetch_file(self, in_path, out_path):
        """ fetch a file from Incus to local """
        super(Connection, self).fetch_file(in_path, out_path)

        self._display.vvv(u"FETCH {0} TO {1}".format(in_path, out_path),
                          host=self._instance())

        local_cmd = [
            self._incus_cmd,
            "--project", self.get_option("project"),
            "file", "pull", "--quiet",
            "%s:%s/%s" % (self.get_option("remote"),
                          self._instance(),
                          in_path),
            out_path]

        local_cmd = [to_bytes(i, errors='surrogate_or_strict') for i in local_cmd]

        call(local_cmd)

    def close(self):
        """ close the connection (nothing to do here) """
        super(Connection, self).close()

        self._connected = False
