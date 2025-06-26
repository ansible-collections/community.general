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
            state=dict(type='str', choices=[
                'cleanup', 'offline', 'online', 'restart', 'maintenance']),
            name=dict(type='str', aliases=['node']),
            wait=dict(type='int', default=300),
            force=dict(type='bool', default=True)
        ),
        supports_check_mode=True,
    )
    default_state = ""

    def __init_module__(self):
        self.runner = pacemaker_runner(self.module)
        self.vars.set('apply_all', True if not self.module.params['name'] else False)
        get_args = dict([('cli_action', 'cluster'), ('state', 'status'), ('name', None), ('apply_all', self.vars.apply_all)])
        if self.module.params['state'] == "maintenance":
            get_args['cli_action'] = "property"
            get_args['state'] = "config"
            get_args['name'] = "maintenance-mode"
        elif self.module.params['state'] == "cleanup":
            get_args['cli_action'] = "resource"
            get_args['name'] = self.module.params['name']

        self.vars.set('get_args', get_args)
        self.vars.set('previous_value', self._get())
        self.vars.set('value', self.vars.previous_value, change=True, diff=True)

        if self.module.params['state'] == "cleanup":
            self.module.deprecate(
                'The value `cleanup` for "state" is being deprecated',
                version='12.0.0',
                collection_name='community.general'
            )

        if not self.module.params['state']:
            self.module.deprecate(
                'Parameter "state" values not defined is being deprecated',
                version='12.0.0',
                collection_name='community.general'
            )

    def _process_command_output(self, fail_on_err, ignore_err_msg=""):
        def process(rc, out, err):
            if fail_on_err and rc != 0 and err and ignore_err_msg not in err:
                self.do_raise('pcs failed with error (rc={0}): {1}'.format(rc, err))
            out = out.rstrip()
            return None if out == "" else out
        return process

    def _get(self):
        with self.runner('cli_action state name', output_process=self._process_command_output(False)) as ctx:
            return ctx.run(cli_action=self.vars.get_args['cli_action'], state=self.vars.get_args['state'], name=self.vars.get_args['name'])

    def state_cleanup(self):
        with self.runner('cli_action state name', output_process=self._process_command_output(True, "Fail"), check_mode_skip=True) as ctx:
            ctx.run(cli_action='resource')
            self.vars.set('value', self._get())
            self.vars.stdout = ctx.results_out
            self.vars.stderr = ctx.results_err
            self.vars.cmd = ctx.cmd

    def state_offline(self):
        with self.runner('cli_action state name apply_all wait',
                         output_process=self._process_command_output(True, "not currently running"),
                         check_mode_skip=True) as ctx:
            ctx.run(cli_action='cluster', apply_all=self.vars.apply_all)
            self.vars.set('value', self._get())
            self.vars.stdout = ctx.results_out
            self.vars.stderr = ctx.results_err
            self.vars.cmd = ctx.cmd

    def state_online(self):
        with self.runner('cli_action state name apply_all wait',
                         output_process=self._process_command_output(True, "currently running"),
                         check_mode_skip=True) as ctx:
            ctx.run(cli_action='cluster', apply_all=self.vars.apply_all)
            self.vars.set('value', self._get())
            self.vars.stdout = ctx.results_out
            self.vars.stderr = ctx.results_err
            self.vars.cmd = ctx.cmd

        if get_pacemaker_maintenance_mode(self.runner):
            with self.runner('cli_action state name', output_process=self._process_command_output(True, "Fail"), check_mode_skip=True) as ctx:
                ctx.run(cli_action='property', state='maintenance', name='maintenance-mode=false')

    def state_maintenance(self):
        with self.runner('cli_action state name',
                         output_process=self._process_command_output(True, "Fail"),
                         check_mode_skip=True) as ctx:
            ctx.run(cli_action='property', name='maintenance-mode=true')
            self.vars.set('value', self._get())
            self.vars.stdout = ctx.results_out
            self.vars.stderr = ctx.results_err
            self.vars.cmd = ctx.cmd

    def state_restart(self):
        with self.runner('cli_action state name apply_all wait',
                         output_process=self._process_command_output(True, "not currently running"),
                         check_mode_skip=True) as ctx:
            ctx.run(cli_action='cluster', state='offline', apply_all=self.vars.apply_all)
            ctx.run(cli_action='cluster', state='online', apply_all=self.vars.apply_all)
            self.vars.set('value', self._get())
            self.vars.stdout = ctx.results_out
            self.vars.stderr = ctx.results_err
            self.vars.cmd = ctx.cmd

        if get_pacemaker_maintenance_mode(self.runner):
            with self.runner('cli_action state name', output_process=self._process_command_output(True, "Fail"), check_mode_skip=True) as ctx:
                ctx.run(cli_action='property', state='maintenance', name='maintenance-mode=false')


def main():
    PacemakerCluster.execute()


if __name__ == '__main__':
    main()
