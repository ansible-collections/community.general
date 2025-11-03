# Based on jail.py
# (c) 2013, Michael Scherer <misc@zarb.org>
# (c) 2015, Toshio Kuratomi <tkuratomi@ansible.com>
# (c) 2016, Stephan Lohse <dev-github@ploek.org>
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
author: Stephan Lohse (!UNKNOWN) <dev-github@ploek.org>
name: iocage
short_description: Run tasks in iocage jails
description:
  - Run commands or put/fetch files to an existing iocage jail.
options:
  remote_addr:
    description:
      - Path to the jail.
    type: string
    vars:
      - name: ansible_host
      - name: ansible_iocage_host
  remote_user:
    description:
      - User to execute as inside the jail.
    type: string
    vars:
      - name: ansible_user
      - name: ansible_iocage_user
"""

import subprocess

from ansible_collections.community.general.plugins.connection.jail import Connection as Jail
from ansible.module_utils.common.text.converters import to_native
from ansible.errors import AnsibleError
from ansible.utils.display import Display

display = Display()


class Connection(Jail):
    """Local iocage based connections"""

    transport = "community.general.iocage"

    def __init__(self, play_context, new_stdin, *args, **kwargs):
        self.ioc_jail = play_context.remote_addr

        self.iocage_cmd = Jail._search_executable("iocage")

        jail_uuid = self.get_jail_uuid()

        kwargs[Jail.modified_jailname_key] = f"ioc-{jail_uuid}"

        display.vvv(
            f"Jail {self.ioc_jail} has been translated to {kwargs[Jail.modified_jailname_key]}",
            host=kwargs[Jail.modified_jailname_key],
        )

        super().__init__(play_context, new_stdin, *args, **kwargs)

    def get_jail_uuid(self):
        p = subprocess.Popen(
            [self.iocage_cmd, "get", "host_hostuuid", self.ioc_jail],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        stdout, stderr = p.communicate()

        if stdout is not None:
            stdout = to_native(stdout)

        if stderr is not None:
            stderr = to_native(stderr)

        # otherwise p.returncode would not be set
        p.wait()

        if p.returncode != 0:
            raise AnsibleError(f"iocage returned an error: {stdout}")

        return stdout.strip("\n")
