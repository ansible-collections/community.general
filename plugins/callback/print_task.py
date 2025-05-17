# -*- coding: utf-8 -*-
# Copyright (c) 2025, Max Mitschke <maxmitschke@fastmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
name: print_task
type: aggregate
short_description: Prints playbook task snippet to job output
description:
  - This plugin prints the currently executing playbook task to the job output.
version_added: 10.7.0
requirements:
  - enable in configuration
'''

EXAMPLES = r'''
ansible.cfg: >
    # Enable plugin
    [defaults]
    callbacks_enabled=community.general.print_task
'''

from yaml import load, dump

try:
    from yaml import CSafeDumper as SafeDumper
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeDumper, SafeLoader

from ansible.plugins.callback import CallbackBase


class CallbackModule(CallbackBase):
    """
    This callback module tells you how long your plays ran for.
    """
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'community.general.print_task'

    CALLBACK_NEEDS_ENABLED = True

    def __init__(self):
        super(CallbackModule, self).__init__()
        self._printed_message = False

    def _print_task(self, task):
        if hasattr(task, '_ds'):
            task_snippet = load(str([task._ds.copy()]), Loader=SafeLoader)
            task_yaml = dump(task_snippet, sort_keys=False, Dumper=SafeDumper)
            self._display.display(f"\n{task_yaml}\n")
            self._printed_message = True

    def v2_playbook_on_task_start(self, task, is_conditional):
        self._printed_message = False

    def v2_runner_on_start(self, host, task):
        if not self._printed_message:
            self._print_task(task)
