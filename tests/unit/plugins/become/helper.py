# -*- coding: utf-8 -*-

# (c) 2012-2014, Michael DeHaan <michael.dehaan@gmail.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleError
from ansible.plugins.loader import get_shell_plugin


def make_become_cmd(play_context, cmd, executable=None):
    """ helper function to create privilege escalation commands """
    if not cmd or not play_context.become:
        return cmd

    become_method = play_context.become_method

    # load/call become plugins here
    plugin = play_context._become_plugin

    if plugin:
        options = {
            'become_exe': play_context.become_exe or '',
            'become_flags': play_context.become_flags or '',
            'become_user': play_context.become_user,
            'become_pass': play_context.become_pass
        }
        plugin.set_options(direct=options)

        if not executable:
            executable = play_context.executable

        shell = get_shell_plugin(executable=executable)
        cmd = plugin.build_become_command(cmd, shell)
        # for backwards compat:
        if play_context.become_pass:
            play_context.prompt = plugin.prompt
    else:
        raise AnsibleError("Privilege escalation method not found: %s" % become_method)

    return cmd
