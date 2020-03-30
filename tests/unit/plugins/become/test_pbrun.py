# (c) 2012-2014, Michael DeHaan <michael.dehaan@gmail.com>
# (c) 2020 Ansible Project
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import re

from ansible import context
from ansible.playbook.play_context import PlayContext

from .helper import call_become_plugin


def test_pbrun(mocker, parser, reset_cli_args):
    options = parser.parse_args([])
    context._init_global_context(options)
    play_context = PlayContext()

    default_cmd = "/bin/foo"
    default_exe = "/bin/bash"
    pbrun_exe = 'pbrun'
    pbrun_flags = ''

    cmd = call_become_plugin(play_context, cmd=default_cmd, executable=default_exe)
    assert cmd == default_cmd

    success = 'BECOME-SUCCESS-.+?'

    play_context.become = True
    play_context.become_user = 'foo'
    play_context.become_method = 'community.general.pbrun'
    play_context.become_flags = pbrun_flags
    cmd = call_become_plugin(play_context, cmd=default_cmd, executable=default_exe)
    print(cmd)
    assert re.match("""%s %s -u %s 'echo %s; %s'""" % (pbrun_exe, pbrun_flags, play_context.become_user,
                                                       success, default_cmd), cmd) is not None
