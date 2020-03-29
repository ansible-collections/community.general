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
from ansible.plugins.loader import become_loader

from .helper import make_become_cmd


def test_dzdo(mocker, parser, reset_cli_args):
    options = parser.parse_args([])
    context._init_global_context(options)
    play_context = PlayContext()

    default_cmd = "/bin/foo"
    default_exe = "/bin/bash"
    dzdo_exe = 'dzdo'
    dzdo_flags = ''

    cmd = make_become_cmd(play_context, cmd=default_cmd, executable=default_exe)
    assert cmd == default_cmd

    success = 'BECOME-SUCCESS-.+?'

    play_context.become = True
    play_context.become_user = 'foo'
    play_context.set_become_plugin(become_loader.get('community.general.dzdo'))
    play_context.become_method = 'community.general.dzdo'
    play_context.become_flags = dzdo_flags
    cmd = make_become_cmd(play_context, cmd=default_cmd, executable=default_exe)
    assert re.match("""%s %s -u %s %s -c 'echo %s; %s'""" % (dzdo_exe, dzdo_flags, play_context.become_user, default_exe,
                                                             success, default_cmd), cmd) is not None
    play_context.become_pass = 'testpass'
    play_context.set_become_plugin(become_loader.get('community.general.dzdo'))
    cmd = make_become_cmd(play_context, cmd=default_cmd, executable=default_exe)
    assert re.match("""%s %s -p %s -u %s %s -c 'echo %s; %s'""" % (dzdo_exe, dzdo_flags, r'\"\[dzdo via ansible, key=.+?\] password:\"',
                                                                   play_context.become_user, default_exe, success, default_cmd), cmd) is not None
