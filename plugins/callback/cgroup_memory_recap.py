# -*- coding: utf-8 -*-
# Copyright (c) 2018 Matt Martz <matt@sivel.net>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Make coding more python3-ish
from __future__ import annotations

DOCUMENTATION = r"""
author: Unknown (!UNKNOWN)
name: cgroup_memory_recap
type: aggregate
requirements:
  - whitelist in configuration
  - cgroups
short_description: Profiles maximum memory usage of tasks and full execution using cgroups
description:
  - This is an Ansible callback plugin that profiles maximum memory usage of Ansible and individual tasks, and displays a
    recap at the end using cgroups.
notes:
  - Requires ansible to be run from within a C(cgroup), such as with C(cgexec -g memory:ansible_profile ansible-playbook ...).
  - This C(cgroup) should only be used by Ansible to get accurate results.
  - To create the C(cgroup), first use a command such as C(sudo cgcreate -a ec2-user:ec2-user -t ec2-user:ec2-user -g memory:ansible_profile).
options:
  max_mem_file:
    required: true
    description: Path to cgroups C(memory.max_usage_in_bytes) file. Example V(/sys/fs/cgroup/memory/ansible_profile/memory.max_usage_in_bytes).
    type: str
    env:
      - name: CGROUP_MAX_MEM_FILE
    ini:
      - section: callback_cgroupmemrecap
        key: max_mem_file
  cur_mem_file:
    required: true
    description: Path to C(memory.usage_in_bytes) file. Example V(/sys/fs/cgroup/memory/ansible_profile/memory.usage_in_bytes).
    type: str
    env:
      - name: CGROUP_CUR_MEM_FILE
    ini:
      - section: callback_cgroupmemrecap
        key: cur_mem_file
"""

import time
import threading

from ansible.plugins.callback import CallbackBase


class MemProf(threading.Thread):
    """Python thread for recording memory usage"""
    def __init__(self, path, obj=None):
        threading.Thread.__init__(self)
        self.obj = obj
        self.path = path
        self.results = []
        self.running = True

    def run(self):
        while self.running:
            with open(self.path) as f:
                val = f.read()
            self.results.append(int(val.strip()) / 1024 / 1024)
            time.sleep(0.001)


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'community.general.cgroup_memory_recap'
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self, display=None):
        super(CallbackModule, self).__init__(display)

        self._task_memprof = None

        self.task_results = []

    def set_options(self, task_keys=None, var_options=None, direct=None):
        super(CallbackModule, self).set_options(task_keys=task_keys, var_options=var_options, direct=direct)

        self.cgroup_max_file = self.get_option('max_mem_file')
        self.cgroup_current_file = self.get_option('cur_mem_file')

        with open(self.cgroup_max_file, 'w+') as f:
            f.write('0')

    def _profile_memory(self, obj=None):
        prev_task = None
        results = None
        try:
            self._task_memprof.running = False
            results = self._task_memprof.results
            prev_task = self._task_memprof.obj
        except AttributeError:
            pass

        if obj is not None:
            self._task_memprof = MemProf(self.cgroup_current_file, obj=obj)
            self._task_memprof.start()

        if results is not None:
            self.task_results.append((prev_task, max(results)))

    def v2_playbook_on_task_start(self, task, is_conditional):
        self._profile_memory(task)

    def v2_playbook_on_stats(self, stats):
        self._profile_memory()

        with open(self.cgroup_max_file) as f:
            max_results = int(f.read().strip()) / 1024 / 1024

        self._display.banner('CGROUP MEMORY RECAP')
        self._display.display(f'Execution Maximum: {max_results:0.2f}MB\n\n')

        for task, memory in self.task_results:
            self._display.display(f'{task.get_name()} ({task._uuid}): {memory:0.2f}MB')
