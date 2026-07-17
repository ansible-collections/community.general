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


def test_pbrun_basic(mocker, parser, reset_cli_args):
    options = parser.parse_args([])
    context._init_global_context(options)

    default_cmd = "/bin/foo"
    default_exe = "/bin/bash"
    pbrun_exe = "pbrun"
    pbrun_flags = ""

    success = "BECOME-SUCCESS-.+?"

    task = {
        "become_method": "community.general.pbrun",
    }
    var_options = {}
    cmd = call_become_plugin(task, var_options, cmd=default_cmd, executable=default_exe)
    print(cmd)
    assert re.match(f"""{pbrun_exe} {pbrun_flags}  'echo {success}; {default_cmd}'""", cmd) is not None


def test_pbrun(mocker, parser, reset_cli_args):
    options = parser.parse_args([])
    context._init_global_context(options)

    default_cmd = "/bin/foo"
    default_exe = "/bin/bash"
    pbrun_exe = "pbrun"
    pbrun_flags = ""

    success = "BECOME-SUCCESS-.+?"

    task = {
        "become_user": "foo",
        "become_method": "community.general.pbrun",
        "become_flags": pbrun_flags,
    }
    var_options = {}
    cmd = call_become_plugin(task, var_options, cmd=default_cmd, executable=default_exe)
    print(cmd)
    assert (
        re.match(f"""{pbrun_exe} {pbrun_flags} -u {task["become_user"]} 'echo {success}; {default_cmd}'""", cmd)
        is not None
    )


def test_pbrun_var_varoptions(mocker, parser, reset_cli_args):
    options = parser.parse_args([])
    context._init_global_context(options)

    default_cmd = "/bin/foo"
    default_exe = "/bin/bash"
    pbrun_exe = "pbrun"
    pbrun_flags = ""

    success = "BECOME-SUCCESS-.+?"

    task = {
        "become_user": "foo",
        "become_method": "community.general.pbrun",
        "become_flags": "xxx",
    }
    var_options = {
        "ansible_become_user": "bar",
        "ansible_become_flags": pbrun_flags,
    }
    cmd = call_become_plugin(task, var_options, cmd=default_cmd, executable=default_exe)
    print(cmd)
    assert (
        re.match(
            f"""{pbrun_exe} {pbrun_flags} -u {var_options["ansible_become_user"]} 'echo {success}; {default_cmd}'""",
            cmd,
        )
        is not None
    )
