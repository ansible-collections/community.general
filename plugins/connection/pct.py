# -*- coding: utf-8 -*-
# Based on lxc.py (c) 2015, Joerg Thalheim <joerg@higgsboson.tk>
# Based on lxd.py (c) 2016 Matt Clay <matt@mystile.com>
# Copyright (c) 2024 Nils Stein <github.nstein@mailbox.org>
# Copyright (c) 2024 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    author: Nils Stein (@mietzen) <github.nstein@mailbox.org>
    name: pct
    short_description: Run tasks in Proxmox LXC container instances via pct CLI
    description:
        - Run commands or put/fetch files to an existing Proxmox LXC container instance using pct CLI.
    options:
      remote_addr:
        description:
            - Container Name
        default: inventory_hostname
        vars:
            - name: inventory_hostname
            - name: ansible_host
            - name: ansible_pct_host
      vmid:
        description:
            - Container ID
        default: proxmox_vmid
        vars:
            - name: proxmox_vmid
      executable:
        default: /bin/sh
        description:
            - Shell executable
        vars:
            - name: ansible_executable
            - name: ansible_pct_executable
'''

import os
from subprocess import Popen, PIPE

from ansible.errors import AnsibleError, AnsibleConnectionFailure, AnsibleFileNotFound
from ansible.module_utils.common.process import get_bin_path
from ansible.module_utils.common.text.converters import to_bytes, to_text
from ansible.plugins.connection import ConnectionBase


class Connection(ConnectionBase):
    """ pct based connections """

    transport = 'community.general.pct'
    has_pipelining = True
    default_user = 'root'

    def __init__(self, play_context, new_stdin, *args, **kwargs):
        super(Connection, self).__init__(play_context, new_stdin, *args, **kwargs)

        self.container_name = None
        self.container_vmid = None

        try:
            self._pct_cmd = get_bin_path("pct")
        except ValueError:
            raise AnsibleError("pct command not found in PATH")
        try:
            self._pvesh_cmd = get_bin_path("pvesh")
        except ValueError:
            raise AnsibleError("pvesh command not found in PATH")

        if self._play_context.remote_user is not None and self._play_context.remote_user != 'root':
            self._display.warning('pct does not support remote_user, using default: root')

    def _vmid(self):
        """ Get the vmid via hostname """
        if not self.container_vmid:
            self.container_vmid = self.get_option('vmid')
        return self.container_vmid

    # def _vmid(self):
    #     """ Get the vmid via hostname """
    #     if not self.container_vmid:
    #         local_cmd = [self._pvesh_cmd]
    #         local_cmd.extend([
    #             "get", "/cluster/resources", "--output-format", "json"])
    #         self._display.vvvvv(u"EXEC {0}".format(local_cmd), host=self._host())

    #         local_cmd = [to_bytes(i, errors='surrogate_or_strict') for i in local_cmd]

    #         process = Popen(local_cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    #         stdout, stderr = process.communicate()

    #         stdout = to_text(stdout)
    #         stderr = to_text(stderr)

    #         self._display.vvvvv(u"EXEC pvesh output: {0} {1}".format(stdout, stderr), host=self._host())
    #         try:
    #             cluster_resources = json.loads(stdout)
    #             self.container_vmid = [x['vmid'] for x in cluster_resources if x['name'] == self.container_name][0]
    #         except KeyError:
    #             raise AnsibleError(f"Got unknow json structure, expected keys name name vmid to exist, instead got: {json.dumps(cluster_resources)}")
    #         except JSONDecodeError:
    #             raise AnsibleError(f"Output not parsable as json: {stdout}")
    #         if not self.container_vmid:
    #             raise AnsibleError(f"Containter: {self.container_name}, not found!")
    #     return self.container_vmid

    def _host(self):
        """ translate remote_addr to pct (short) hostname """
        if not self.container_name:
            self.container_name = self.get_option('remote_addr')
        return self.container_name

    def _connect(self):
        """connect to proxmox (nothing to do here) """
        super(Connection, self)._connect()

        if not self._connected:
            self._display.vvv(u"ESTABLISH PCT CONNECTION FOR USER: root", host=self._host())
            self._connected = True

    def exec_command(self, cmd, in_data=None, sudoable=True):
        """ execute a command inside the proxmox container """
        super(Connection, self).exec_command(cmd, in_data=in_data, sudoable=sudoable)

        self._display.vvv(u"EXEC {0}".format(cmd), host=self._host())

        local_cmd = [self._pct_cmd]
        local_cmd.extend([
            "exec",
            self._vmid(),
            "--",
            self.get_option("executable"), "-c", cmd
        ])

        self._display.vvvvv(u"EXEC {0}".format(local_cmd), host=self._host())

        local_cmd = [to_bytes(i, errors='surrogate_or_strict') for i in local_cmd]
        in_data = to_bytes(in_data, errors='surrogate_or_strict', nonstring='passthru')

        process = Popen(local_cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate(in_data)

        stdout = to_text(stdout)
        stderr = to_text(stderr)

        self._display.vvvvv(u"EXEC ptc output: {0} {1}".format(stdout, stderr), host=self._host())

        if "not running!" in stderr:
            raise AnsibleConnectionFailure("instance not running: %s" % self._host())

        if "does not exist" in stderr:
            raise AnsibleConnectionFailure("instance not found: %s" % self._host())

        return process.returncode, stdout, stderr

    def put_file(self, in_path, out_path):
        """ put a file from local into a proxmox container """
        super(Connection, self).put_file(in_path, out_path)

        self._display.vvv(u"PUT {0} TO {1}".format(in_path, out_path), host=self._host())

        if not os.path.isfile(to_bytes(in_path, errors='surrogate_or_strict')):
            raise AnsibleFileNotFound("input path is not a file: %s" % in_path)

        local_cmd = [self._pct_cmd]
        local_cmd.extend([
            "push",
            self._vmid(),
            in_path,
            out_path
        ])

        local_cmd = [to_bytes(i, errors='surrogate_or_strict') for i in local_cmd]

        process = Popen(local_cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        process.communicate()

    def fetch_file(self, in_path, out_path):
        """ fetch a file from a proxmox container to local """
        super(Connection, self).fetch_file(in_path, out_path)

        self._display.vvv(u"FETCH {0} TO {1}".format(in_path, out_path), host=self._host())

        local_cmd = [self._pct_cmd]
        local_cmd.extend([
            "pull",
            self._vmid(),
            in_path,
            out_path
        ])
        local_cmd = [to_bytes(i, errors='surrogate_or_strict') for i in local_cmd]

        process = Popen(local_cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        process.communicate()

    def close(self):
        """ close the connection (nothing to do here) """
        super(Connection, self).close()

        self._connected = False
