# Based on local.py (c) 2012, Michael DeHaan <michael.dehaan@gmail.com>
# Based on chroot.py (c) 2013, Maykel Moya <mmoya@speedyrails.com>
# Based on func.py
# Copyright (c) 2014, Michael Scherer <misc@zarb.org>
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
author: Michael Scherer (@mscherer) <misc@zarb.org>
name: saltstack
short_description: Allow ansible to piggyback on salt minions
description:
  - Run commands or put/fetch files to Salt minions by using the local Salt master as transport.
  - Ansible must run directly on the Salt master; this plugin uses C(salt.client.LocalClient)
    and does not support connecting to a remote Salt master.
requirements:
  - the C(salt) Python package must be installed on the Salt master (the Ansible controller)
options:
  remote_addr:
    description:
      - The Salt minion ID to target.
    type: string
    default: inventory_hostname
    vars:
      - name: inventory_hostname
      - name: ansible_host
notes:
  - Ansible must be run from the Salt master host; the plugin cannot reach a remote Salt master.
  - The inventory hostname (or O(remote_addr)) is treated as the Salt minion ID, not as a DNS
    name or IP address.
  - The Salt master and its minion keys must already be configured and accepted before using
    this connection plugin.
  - File transfer via P(community.general.saltstack#connection) uses C(hashutil.base64_decodefile)
    (put) and C(cp.get_file_str) (fetch); these Salt execution modules must be available on
    the targeted minions.
"""

import base64
import os

from ansible import errors
from ansible.plugins.connection import ConnectionBase

HAVE_SALTSTACK = False
try:
    import salt.client as sc

    HAVE_SALTSTACK = True
except ImportError:
    pass


class Connection(ConnectionBase):
    """Salt-based connections"""

    has_pipelining = False
    # while the name of the product is salt, naming that module salt cause
    # trouble with module import
    transport = "community.general.saltstack"

    def __init__(self, play_context, new_stdin, *args, **kwargs):
        super().__init__(play_context, new_stdin, *args, **kwargs)
        self.host = self._play_context.remote_addr

    def _connect(self):
        if not HAVE_SALTSTACK:
            raise errors.AnsibleError("saltstack is not installed")

        self.client = sc.LocalClient()
        self._connected = True
        return self

    def exec_command(self, cmd, in_data=None, sudoable=False):
        """run a command on the remote minion"""
        super().exec_command(cmd, in_data=in_data, sudoable=sudoable)

        if in_data:
            raise errors.AnsibleError("Internal Error: this module does not support optimized module pipelining")

        self._display.vvv(f"EXEC {cmd}", host=self.host)
        # need to add 'true;' to work around https://github.com/saltstack/salt/issues/28077
        res = self.client.cmd(self.host, "cmd.exec_code_all", ["bash", f"true;{cmd}"])
        if self.host not in res:
            raise errors.AnsibleError(
                f"Minion {self.host} didn't answer, check if salt-minion is running and the name is correct"
            )

        p = res[self.host]
        return p["retcode"], p["stdout"], p["stderr"]

    @staticmethod
    def _normalize_path(path, prefix):
        if not path.startswith(os.path.sep):
            path = os.path.join(os.path.sep, path)
        normpath = os.path.normpath(path)
        return os.path.join(prefix, normpath[1:])

    def put_file(self, in_path, out_path):
        """transfer a file from local to remote"""

        super().put_file(in_path, out_path)

        out_path = self._normalize_path(out_path, "/")
        self._display.vvv(f"PUT {in_path} TO {out_path}", host=self.host)
        with open(in_path, "rb") as in_fh:
            content = in_fh.read()
        self.client.cmd(self.host, "hashutil.base64_decodefile", [base64.b64encode(content), out_path])

    # TODO test it
    def fetch_file(self, in_path, out_path):
        """fetch a file from remote to local"""

        super().fetch_file(in_path, out_path)

        in_path = self._normalize_path(in_path, "/")
        self._display.vvv(f"FETCH {in_path} TO {out_path}", host=self.host)
        content = self.client.cmd(self.host, "cp.get_file_str", [in_path])[self.host]
        open(out_path, "wb").write(content)

    def close(self):
        """terminate the connection; nothing to do here"""
        pass
