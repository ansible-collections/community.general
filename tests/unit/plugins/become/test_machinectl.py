# Copyright (c) 2026 Ansible Project
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import re

from ansible import context

from .helper import call_become_plugin


def test_machinectl_basic(mocker, parser, reset_cli_args):
    options = parser.parse_args([])
    context._init_global_context(options)

    default_cmd = "/bin/foo"
    default_exe = "/bin/sh"
    machinectl_exe = "machinectl"

    success = "BECOME-SUCCESS-.+?"

    task = {
        "become_method": "community.general.machinectl",
        "become_user": "root",
    }
    var_options = {}
    cmd = call_become_plugin(task, var_options, cmd=default_cmd, executable=default_exe)
    assert (
        re.match(
            f"SYSTEMD_COLORS=0 {machinectl_exe} -q shell  root@ {default_exe} -c 'echo {success}; {default_cmd}'",
            cmd,
        )
        is not None
    )


def test_machinectl_flags(mocker, parser, reset_cli_args):
    options = parser.parse_args([])
    context._init_global_context(options)

    default_cmd = "/bin/foo"
    default_exe = "/bin/sh"
    machinectl_exe = "machinectl"
    machinectl_flags = "--setenv=FOO=bar"

    success = "BECOME-SUCCESS-.+?"

    task = {
        "become_method": "community.general.machinectl",
        "become_user": "root",
        "become_flags": machinectl_flags,
    }
    var_options = {}
    cmd = call_become_plugin(task, var_options, cmd=default_cmd, executable=default_exe)
    assert (
        re.match(
            f"SYSTEMD_COLORS=0 {machinectl_exe} -q shell --setenv=FOO=bar root@ {default_exe} -c 'echo {success}; {default_cmd}'",
            cmd,
        )
        is not None
    )
