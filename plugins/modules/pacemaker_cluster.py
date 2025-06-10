#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Mathieu Bultel <mbultel@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: pacemaker_cluster
short_description: Manage pacemaker clusters
author:
  - Mathieu Bultel (@matbu)
  - Dexter Le (@munchtoast)
version_added: 1.0.0
description:
  - This module can manage a pacemaker cluster and nodes from Ansible using the pacemaker CLI.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  state:
    description:
      - Indicate desired state of the cluster.
    choices: [cleanup, offline, online, restart, maintenance]
    type: str
  name:
    description:
      - Specify which node of the cluster you want to manage. V(null) == the cluster status itself, V(all) == check the status
        of all nodes.
    type: str
    default: all
    aliases: ['node']
  wait:
    description:
      - Timeout period for polling the cluster operation.
    type: int
    default: 300
  force:
    description:
      - Force the change of the cluster state.
    type: bool
    default: true
'''

EXAMPLES = '''
---
- name: Set cluster Online
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Get cluster state
      community.general.pacemaker_cluster:
        state: online
'''

RETURN = '''
out:
  description: The output of the current state of the cluster. It returns a list of the nodes state.
  type: str
  sample: 'out: [["  overcloud-controller-0", " Online"]]}'
  returned: always
'''

from ansible_collections.community.general.plugins.module_utils.module_helper import StateModuleHelper
from ansible_collections.community.general.plugins.module_utils.pacemaker import pacemaker_runner, get_pacemaker_maintenance_mode


class PacemakerCluster(StateModuleHelper):
    module = dict(
        argument_spec=dict(
            state=dict(type='str', default='present', choices=[
                'cleanup', 'offline', 'online', 'restart']),
            name=dict(type='str', default='all', aliases=['node']),
            wait=dict(type='int', default=300),
            force=dict(type='bool', default=True)
        ),
        supports_check_mode=True,
    )
    default_state = "online"

    def __init_module__(self):
        self.runner = pacemaker_runner(self.module, cli_action='cluster')
        self._daemon_runner = pacemaker_runner(self.module, cli_action='pcsd')
        self._maintenance_mode_runner = pacemaker_runner(self.module, cli_action='property')
        self.vars.set('previous_value', self._get())
        self.vars.set('value', self.vars.previous_value, change=True, diff=True)

    def _process_command_output(self, fail_on_err, ignore_err_msg=""):
        def process(rc, out, err):
            if fail_on_err and rc != 0 and err and ignore_err_msg not in err:
                self.do_raise('pcs failed with error (rc={0}): {1}'.format(rc, err))
            out = out.rstrip()
            return None if out == "" else out
        return process

    def _get(self):
        with self._daemon_runner('state', output_process=self._process_command_output(False)) as ctx:
            return ctx.run(state='status')

    def state_offline(self):
        with self.runner('state name wait', output_process=self._process_command_output(True, ""), check_mode_skip=True) as ctx:
            ctx.run()
            self.vars.set('value', self._get())
            self.vars.stdout = ctx.results_out
            self.vars.stderr = ctx.results_err
            self.vars.cmd = ctx.cmd

    def state_online(self):
        with self.runner('state name wait', output_process=self._process_command_output(True, ""), check_mode_skip=True) as ctx:
            ctx.run()
            self.vars.set('value', self._get())
            self.vars.stdout = ctx.results_out
            self.vars.stderr = ctx.results_err
            self.vars.cmd = ctx.cmd

    def state_maintenance(self):
        with self._maintenance_mode_runner('state', output_process=self._process_command_output(True, ""), check_mode_skip=True) as ctx:
            ctx.run()
            self.vars.set('value', self._get())
            self.vars.stdout = ctx.results_out
            self.vars.stderr = ctx.results_err
            self.vars.cmd = ctx.cmd

    def state_restart(self):
        self.state_offline()
        self.state_online()

    def state_cleanup(self):
        with self.runner('state name', output_process=self._process_command_output(True, ""), check_mode_skip=True) as ctx:
            ctx.run()
            self.vars.set('value', self._get())
            self.vars.stdout = ctx.results_out
            self.vars.stderr = ctx.results_err
            self.vars.cmd = ctx.cmd


def main():
    PacemakerCluster.execute()


if __name__ == '__main__':
    main()
