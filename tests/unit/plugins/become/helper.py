# -*- coding: utf-8 -*-

# (c) 2012-2014, Michael DeHaan <michael.dehaan@gmail.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleError
from ansible.plugins.loader import become_loader, get_shell_plugin


def call_become_plugin(play_context, cmd, executable=None):
    """Helper function to call become plugin simiarly on how Ansible itself handles this."""
    if not cmd or not play_context.become:
        return cmd

    plugin = become_loader.get(play_context.become_method)
    if not plugin:
        raise AnsibleError("Privilege escalation method not found: %s" % play_context.become_method)

    play_context.set_become_plugin(plugin)

    options = {
        'become_exe': play_context.become_exe,
        'become_flags': play_context.become_flags,
        'become_user': play_context.become_user,
        'become_pass': play_context.become_pass,
    }
    task_keys = {}
    for k, v in options.items():
        if v is not None:
            task_keys[k] = v
    plugin.set_options(task_keys=options, var_options={})

    if not executable:
        executable = play_context.executable

    shell = get_shell_plugin(executable=executable)
    return plugin.build_become_command(cmd, shell)
