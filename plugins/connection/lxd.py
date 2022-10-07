# -*- coding: utf-8 -*-
# Copyright (c) 2016 Matt Clay <matt@mystile.com>
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    author: Matt Clay (@mattclay) <matt@mystile.com>
    name: lxd
    short_description: Run tasks in lxc containers via lxc CLI
    description:
        - Run commands or put/fetch files to an existing lxc container using lxc CLI
    options:
      remote_addr:
        description:
            - Container identifier.
        default: inventory_hostname
        vars:
            - name: inventory_hostname
            - name: ansible_host
            - name: ansible_lxd_host
      executable:
        description:
            - shell to use for execution inside container
        default: /bin/sh
        vars:
            - name: ansible_executable
            - name: ansible_lxd_executable
      remote:
        description:
            - Name of the LXD remote to use.
        default: local
        vars:
            - name: ansible_lxd_remote
        version_added: 2.0.0
      project:
        description:
            - Name of the LXD project to use.
        vars:
            - name: ansible_lxd_project
        version_added: 2.0.0
'''

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
    default_user = 'root'

    def __init__(self, play_context, new_stdin, *args, **kwargs):
        super(Connection, self).__init__(play_context, new_stdin, *args, **kwargs)

        try:
            self._lxc_cmd = get_bin_path("lxc")
        except ValueError:
            raise AnsibleError("lxc command not found in PATH")

        if self._play_context.remote_user is not None and self._play_context.remote_user != 'root':
            self._display.warning('lxd does not support remote_user, using container default: root')

    def _connect(self):
        """connect to lxd (nothing to do here) """
        super(Connection, self)._connect()

        if not self._connected:
            self._display.vvv(u"ESTABLISH LXD CONNECTION FOR USER: root", host=self.get_option('remote_addr'))
            self._connected = True

    def exec_command(self, cmd, in_data=None, sudoable=True):
        """ execute a command on the lxd host """
        super(Connection, self).exec_command(cmd, in_data=in_data, sudoable=sudoable)

        self._display.vvv(u"EXEC {0}".format(cmd), host=self.get_option('remote_addr'))

        local_cmd = [self._lxc_cmd]
        if self.get_option("project"):
            local_cmd.extend(["--project", self.get_option("project")])
        local_cmd.extend([
            "exec",
            "%s:%s" % (self.get_option("remote"), self.get_option("remote_addr")),
            "--",
            self.get_option("executable"), "-c", cmd
        ])

        local_cmd = [to_bytes(i, errors='surrogate_or_strict') for i in local_cmd]
        in_data = to_bytes(in_data, errors='surrogate_or_strict', nonstring='passthru')

        process = Popen(local_cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate(in_data)

        stdout = to_text(stdout)
        stderr = to_text(stderr)

        if stderr == "error: Container is not running.\n":
            raise AnsibleConnectionFailure("container not running: %s" % self.get_option('remote_addr'))

        if stderr == "error: not found\n":
            raise AnsibleConnectionFailure("container not found: %s" % self.get_option('remote_addr'))

        return process.returncode, stdout, stderr

    def put_file(self, in_path, out_path):
        """ put a file from local to lxd """
        super(Connection, self).put_file(in_path, out_path)

        self._display.vvv(u"PUT {0} TO {1}".format(in_path, out_path), host=self.get_option('remote_addr'))

        if not os.path.isfile(to_bytes(in_path, errors='surrogate_or_strict')):
            raise AnsibleFileNotFound("input path is not a file: %s" % in_path)

        local_cmd = [self._lxc_cmd]
        if self.get_option("project"):
            local_cmd.extend(["--project", self.get_option("project")])
        local_cmd.extend([
            "file", "push",
            in_path,
            "%s:%s/%s" % (self.get_option("remote"), self.get_option("remote_addr"), out_path)
        ])

        local_cmd = [to_bytes(i, errors='surrogate_or_strict') for i in local_cmd]

        process = Popen(local_cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        process.communicate()

    def fetch_file(self, in_path, out_path):
        """ fetch a file from lxd to local """
        super(Connection, self).fetch_file(in_path, out_path)

        self._display.vvv(u"FETCH {0} TO {1}".format(in_path, out_path), host=self.get_option('remote_addr'))

        local_cmd = [self._lxc_cmd]
        if self.get_option("project"):
            local_cmd.extend(["--project", self.get_option("project")])
        local_cmd.extend([
            "file", "pull",
            "%s:%s/%s" % (self.get_option("remote"), self.get_option("remote_addr"), in_path),
            out_path
        ])

        local_cmd = [to_bytes(i, errors='surrogate_or_strict') for i in local_cmd]

        process = Popen(local_cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        process.communicate()

    def close(self):
        """ close the connection (nothing to do here) """
        super(Connection, self).close()

        self._connected = False
