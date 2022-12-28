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

def _test_ksu_task(mocker, parser, task, shell='/bin/bash', cmd='/bin/foo'):
    context._init_global_context(parser.parse_args([]))

    # Task arguments and defaults
    become_user_ksu = task.get('become_user_ksu', 'root')
    become_user = task.get('become_user', 'root')
    become_exe_ksu = task.get('become_exe_ksu', 'ksu')
    become_exe_su = task.get('become_exe_su', '/bin/su')
    become_flags_ksu = task.get('become_flags_ksu', '-Z\\s+-q' )
    become_flags = task.get('become_flags', '')
    become_pass = task.get('become_pass', None)
    prompt_l10n = task.get('prompt_l10n', [])

    task['become_method'] = 'community.general.ksusu' # force this

    # We are appending here instead of formatting so the parts are easily understood
    regex  = become_exe_ksu
    regex += '\\s+' + become_user_ksu
    regex += '\\s+' + become_flags_ksu
    regex += '\\s+-e\\s+' + become_exe_su
    regex += '\\s+-l\\s+' + become_flags
    regex += '\\s+' + become_user
    regex += '\\s+' + shell
    regex += "\\s+-c\\s+'echo\\s+BECOME-SUCCESS-.+?\\s*;\\s*" + cmd
    regex += "\\s*'"
    print('regex: %s' % regex)

    var_options = {}
    call_result = call_become_plugin(task, var_options, cmd=cmd, executable=shell)
    print('cmd:   %s' % call_result)

    assert (re.match(regex, call_result) is not None)


def test_ksusu_defaults(mocker, parser, reset_cli_args):

    task = {
    }

    _test_ksu_task(mocker, parser, task)

def test_ksusu_user_ksu(mocker, parser, reset_cli_args):

    task = {
        'become_user_ksu': 'test_user'
    }

    _test_ksu_task(mocker, parser, task)

def test_ksusu_user(mocker, parser, reset_cli_args):

    task = {
        'become_user': 'test_user'
    }

    _test_ksu_task(mocker, parser, task)

def test_ksusu_exe_ksu(mocker, parser, reset_cli_args):

    task = {
        'become_exe_ksu': 'test_ksu'
    }

    _test_ksu_task(mocker, parser, task)

def test_ksusu_exe_su(mocker, parser, reset_cli_args):

    task = {
        'become_exe_su': '/bin/test_su'
    }

    _test_ksu_task(mocker, parser, task)

def test_ksusu_flags_ksu(mocker, parser, reset_cli_args):

    task = {
        'become_flags_ksu': '-Z -q --test_flag'
    }

    _test_ksu_task(mocker, parser, task)

def test_ksusu_flags(mocker, parser, reset_cli_args):

    task = {
        'become_flags': '--test_flag'
    }

    _test_ksu_task(mocker, parser, task)
