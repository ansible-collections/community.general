# Copyright (c) 2024 Ansible Project
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible import context

from .helper import call_become_plugin


def test_run0_basic(mocker, parser, reset_cli_args):
    options = parser.parse_args([])
    context._init_global_context(options)

    default_cmd = "/bin/foo"
    default_exe = "/bin/bash"
    run0_exe = "run0"
    run0_flags = "--user=root"

    success = "BECOME-SUCCESS-.+?"

    task = {
        "become_method": "community.general.run0",
    }
    var_options = {}
    cmd = call_become_plugin(task, var_options, cmd=default_cmd, executable=default_exe)
    print(cmd)
    assert (
        re.match(
            """%s %s  'echo %s; %s'""" % (run0_exe, run0_flags, success, default_cmd),
            cmd,
        )
        is not None
    )
