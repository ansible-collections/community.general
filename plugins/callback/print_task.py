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
  - This is an Ansible callback plugin that will print the currently executing
    playbook task to the job output.
requirements:
  - enable in configuration
'''


import yaml

from ansible.plugins.callback import CallbackBase


class CallbackModule(CallbackBase):
    """
    This callback module tells you how long your plays ran for.
    """
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'print_task'

    CALLBACK_NEEDS_ENABLED = True

    def __init__(self):
        super(CallbackModule, self).__init__()
        self._printed_message = False

    def _print_task(self, task):
        task_snippet = yaml.load(str([task._ds.copy()]), Loader=yaml.Loader)
        task_yaml = yaml.dump(task_snippet, sort_keys=False)
        self._display.v(f"\n{task_yaml}\n")
        self._printed_message = True

    def v2_playbook_on_task_start(self, task, is_conditional):
        self._printed_message = False

    def v2_runner_on_start(self, host, task):
        if not self._printed_message:
            self._print_task(task)
