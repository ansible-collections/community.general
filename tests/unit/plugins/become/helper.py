# -*- coding: utf-8 -*-

# (c) 2012-2014, Michael DeHaan <michael.dehaan@gmail.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleError
from ansible.plugins.loader import become_loader, get_shell_plugin


def call_become_plugin(task, var_options, cmd, executable=None):
    """Helper function to call become plugin simiarly on how Ansible itself handles this."""
    plugin = become_loader.get(task['become_method'])
    plugin.set_options(task_keys=task, var_options=var_options)
    shell = get_shell_plugin(executable=executable)
    return plugin.build_become_command(cmd, shell)
