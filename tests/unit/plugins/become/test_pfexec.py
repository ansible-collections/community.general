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


def test_pfexec_wrap(mocker, parser, reset_cli_args):
    """Test pfexec with wrap_exe explicitly enabled."""
    options = parser.parse_args([])
    context._init_global_context(options)

    default_cmd = "/bin/foo"
    default_exe = "/bin/bash"
    pfexec_exe = "pfexec"

    success = "BECOME-SUCCESS-.+?"

    task = {
        "become_method": "community.general.pfexec",
    }
    var_options = {
        "ansible_pfexec_wrap_execution": "true",
    }
    cmd = call_become_plugin(task, var_options, cmd=default_cmd, executable=default_exe)
    print(cmd)
    assert re.match(f"""{pfexec_exe} {default_exe} -c 'echo {success}; {default_cmd}'""", cmd) is not None


def test_pfexec_no_wrap(mocker, parser, reset_cli_args):
    """Test pfexec with wrap_exe explicitly disabled."""
    options = parser.parse_args([])
    context._init_global_context(options)

    default_cmd = "/bin/foo"
    default_exe = "/bin/bash"
    pfexec_exe = "pfexec"

    success = "BECOME-SUCCESS-.+?"

    task = {
        "become_method": "community.general.pfexec",
        "become_flags": "",
    }
    var_options = {
        "ansible_pfexec_wrap_execution": "false",
    }
    cmd = call_become_plugin(task, var_options, cmd=default_cmd, executable=default_exe)
    print(cmd)
    assert re.match(f"""{pfexec_exe} 'echo {success}; {default_cmd}'""", cmd) is not None


def test_pfexec_custom_flags(mocker, parser, reset_cli_args):
    """Test pfexec with custom flags and wrap_exe enabled."""
    options = parser.parse_args([])
    context._init_global_context(options)

    default_cmd = "/bin/foo"
    default_exe = "/bin/bash"
    pfexec_exe = "pfexec"
    pfexec_flags = "-P basic"

    success = "BECOME-SUCCESS-.+?"

    task = {
        "become_method": "community.general.pfexec",
        "become_flags": pfexec_flags,
    }
    var_options = {
        "ansible_pfexec_wrap_execution": "true",
    }
    cmd = call_become_plugin(task, var_options, cmd=default_cmd, executable=default_exe)
    print(cmd)
    assert (
        re.match(f"""{pfexec_exe} {pfexec_flags} {default_exe} -c 'echo {success}; {default_cmd}'""", cmd) is not None
    )


def test_pfexec_varoptions(mocker, parser, reset_cli_args):
    """Test that var_options override task options."""
    options = parser.parse_args([])
    context._init_global_context(options)

    default_cmd = "/bin/foo"
    default_exe = "/bin/bash"
    pfexec_exe = "pfexec"

    success = "BECOME-SUCCESS-.+?"

    task = {
        "become_user": "foo",
        "become_method": "community.general.pfexec",
        "become_flags": "xxx",
    }
    var_options = {
        "ansible_become_user": "bar",
        "ansible_become_flags": "",
        "ansible_pfexec_wrap_execution": "true",
    }
    cmd = call_become_plugin(task, var_options, cmd=default_cmd, executable=default_exe)
    print(cmd)
    # var_options override task flags, so flags should be empty
    assert re.match(f"""{pfexec_exe} {default_exe} -c 'echo {success}; {default_cmd}'""", cmd) is not None
