# Make coding more python3-ish, this is required for contributions to Ansible
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
author: Max Mitschke
name: print_task
callback_type: aggregate
requirements:
  - enable in configuration
short_description: Prints playbook task snippet to job output
version_added: "2.0"
description:
  - This is an Ansible callback plugin that will print the currently executing
    playbook task to the job output.
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
      task_yaml = yaml.dump(yaml.load(str([task._ds.copy()]), 
                            Loader=yaml.Loader), 
                            sort_keys=False)
      
      self._display.v(f"\n{task_yaml}\n")
      self._printed_message = True

    def v2_playbook_on_task_start(self, task, is_conditional):
       self._printed_message = False

    def v2_runner_on_start(self, host, task):
        if not self._printed_message:
          self._print_task(task)
