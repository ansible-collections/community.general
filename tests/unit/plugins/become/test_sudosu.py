# Copyright (c) 2012-2014, Michael DeHaan <michael.dehaan@gmail.com>
# Copyright (c) 2021 Ansible Project
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Make coding more python3-ish
from __future__ import annotations

import re

from ansible import context

from .helper import call_become_plugin


def test_sudosu(mocker, parser, reset_cli_args):
    options = parser.parse_args([])
    context._init_global_context(options)

    default_cmd = "/bin/foo"
    default_exe = "/bin/bash"
    sudo_exe = "sudo"
    sudo_flags = "-H -s -n"

    success = "BECOME-SUCCESS-.+?"

    task = {
        "become_user": "foo",
        "become_method": "community.general.sudosu",
        "become_flags": sudo_flags,
    }
    var_options = {}
    cmd = call_become_plugin(task, var_options, cmd=default_cmd, executable=default_exe)
    print(cmd)
    assert (
        re.match(
            f"""{sudo_exe} {sudo_flags}  su -l {task["become_user"]} {default_exe} -c 'echo {success}; {default_cmd}'""",
            cmd,
        )
        is not None
    )

    task = {
        "become_user": "foo",
        "become_method": "community.general.sudosu",
        "become_flags": sudo_flags,
        "become_pass": "testpass",
    }
    var_options = {}
    cmd = call_become_plugin(task, var_options, cmd=default_cmd, executable=default_exe)
    print(cmd)
    assert (
        re.match(
            """%s %s -p "%s" su -l %s %s -c 'echo %s; %s'"""
            % (
                sudo_exe,
                sudo_flags.replace("-n", ""),
                r"\[sudo via ansible, key=.+?\] password:",
                task["become_user"],
                default_exe,
                success,
                default_cmd,
            ),
            cmd,
        )
        is not None
    )
