# Copyright (c) 2012-2014, Michael DeHaan <michael.dehaan@gmail.com>
# Copyright (c) 2020 Ansible Project
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Make coding more python3-ish
from __future__ import annotations

import re

from ansible import context

from .helper import call_become_plugin


def test_ksu_basic(mocker, parser, reset_cli_args):
    options = parser.parse_args([])
    context._init_global_context(options)

    default_cmd = "/bin/foo"
    default_exe = "/bin/bash"
    ksu_exe = "ksu"
    ksu_flags = ""

    success = "BECOME-SUCCESS-.+?"

    task = {
        "become_user": "foo",
        "become_method": "community.general.ksu",
    }
    var_options = {}
    cmd = call_become_plugin(task, var_options, cmd=default_cmd, executable=default_exe)
    print(cmd)
    assert (
        re.match(
            f"""{ksu_exe} {task["become_user"]} {ksu_flags} -e {default_exe} -c 'echo {success}; {default_cmd}'""", cmd
        )
        is not None
    )


def test_ksu(mocker, parser, reset_cli_args):
    options = parser.parse_args([])
    context._init_global_context(options)

    default_cmd = "/bin/foo"
    default_exe = "/bin/bash"
    ksu_exe = "ksu"
    ksu_flags = ""

    success = "BECOME-SUCCESS-.+?"

    task = {
        "become_user": "foo",
        "become_method": "community.general.ksu",
        "become_flags": ksu_flags,
    }
    var_options = {}
    cmd = call_become_plugin(task, var_options, cmd=default_cmd, executable=default_exe)
    print(cmd)
    assert (
        re.match(
            f"""{ksu_exe} {task["become_user"]} {ksu_flags} -e {default_exe} -c 'echo {success}; {default_cmd}'""", cmd
        )
        is not None
    )


def test_ksu_varoptions(mocker, parser, reset_cli_args):
    options = parser.parse_args([])
    context._init_global_context(options)

    default_cmd = "/bin/foo"
    default_exe = "/bin/bash"
    ksu_exe = "ksu"
    ksu_flags = ""

    success = "BECOME-SUCCESS-.+?"

    task = {
        "become_user": "foo",
        "become_method": "community.general.ksu",
        "become_flags": "xxx",
    }
    var_options = {
        "ansible_become_user": "bar",
        "ansible_become_flags": ksu_flags,
    }
    cmd = call_become_plugin(task, var_options, cmd=default_cmd, executable=default_exe)
    print(cmd)
    assert (
        re.match(
            f"""{ksu_exe} {var_options["ansible_become_user"]} {ksu_flags} -e {default_exe} -c 'echo {success}; {default_cmd}'""",
            cmd,
        )
        is not None
    )
