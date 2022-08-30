# Copyright (c) 2012-2014, Michael DeHaan <michael.dehaan@gmail.com>
# Copyright (c) 2020 Ansible Project
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import re

from ansible import context

from .helper import call_become_plugin


def test_dzdo_basic(mocker, parser, reset_cli_args):
    options = parser.parse_args([])
    context._init_global_context(options)

    default_cmd = "/bin/foo"
    default_exe = "/bin/bash"
    dzdo_exe = 'dzdo'
    dzdo_flags = '-H -S -n'

    success = 'BECOME-SUCCESS-.+?'

    task = {
        'become_method': 'community.general.dzdo',
    }
    var_options = {}
    cmd = call_become_plugin(task, var_options, cmd=default_cmd, executable=default_exe)
    print(cmd)
    assert re.match("""%s %s  %s -c 'echo %s; %s'""" % (dzdo_exe, dzdo_flags, default_exe,
                                                        success, default_cmd), cmd) is not None


def test_dzdo(mocker, parser, reset_cli_args):
    options = parser.parse_args([])
    context._init_global_context(options)

    default_cmd = "/bin/foo"
    default_exe = "/bin/bash"
    dzdo_exe = 'dzdo'
    dzdo_flags = ''

    success = 'BECOME-SUCCESS-.+?'

    task = {
        'become_user': 'foo',
        'become_method': 'community.general.dzdo',
        'become_flags': dzdo_flags,
    }
    var_options = {}
    cmd = call_become_plugin(task, var_options, cmd=default_cmd, executable=default_exe)
    print(cmd)
    assert re.match("""%s %s -u %s %s -c 'echo %s; %s'""" % (dzdo_exe, dzdo_flags, task['become_user'], default_exe,
                                                             success, default_cmd), cmd) is not None
    task['become_pass'] = 'testpass'
    cmd = call_become_plugin(task, var_options, cmd=default_cmd, executable=default_exe)
    print(cmd)
    assert re.match("""%s %s -p %s -u %s %s -c 'echo %s; %s'""" % (dzdo_exe, dzdo_flags, r'\"\[dzdo via ansible, key=.+?\] password:\"',
                                                                   task['become_user'], default_exe, success, default_cmd), cmd) is not None


def test_dzdo_varoptions(mocker, parser, reset_cli_args):
    options = parser.parse_args([])
    context._init_global_context(options)

    default_cmd = "/bin/foo"
    default_exe = "/bin/bash"
    dzdo_exe = 'dzdo'
    dzdo_flags = ''

    success = 'BECOME-SUCCESS-.+?'

    task = {
        'become_user': 'foo',
        'become_method': 'community.general.dzdo',
        'become_flags': 'xxx',
    }
    var_options = {
        'ansible_become_user': 'bar',
        'ansible_become_flags': dzdo_flags,
    }
    cmd = call_become_plugin(task, var_options, cmd=default_cmd, executable=default_exe)
    print(cmd)
    assert re.match("""%s %s -u %s %s -c 'echo %s; %s'""" % (dzdo_exe, dzdo_flags, var_options['ansible_become_user'], default_exe,
                                                             success, default_cmd), cmd) is not None
    var_options['ansible_become_pass'] = 'testpass'
    cmd = call_become_plugin(task, var_options, cmd=default_cmd, executable=default_exe)
    print(cmd)
    assert re.match("""%s %s -p %s -u %s %s -c 'echo %s; %s'""" % (dzdo_exe, dzdo_flags, r'\"\[dzdo via ansible, key=.+?\] password:\"',
                                                                   var_options['ansible_become_user'], default_exe, success, default_cmd), cmd) is not None
