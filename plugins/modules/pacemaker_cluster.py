#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Mathieu Bultel <mbultel@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: pacemaker_cluster
short_description: Manage pacemaker clusters
author:
  - Mathieu Bultel (@matbu)
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
    choices: [cleanup, offline, online, restart]
    type: str
  node:
    description:
      - Specify which node of the cluster you want to manage. V(null) == the cluster status itself, V(all) == check the status
        of all nodes.
    type: str
  timeout:
    description:
      - Timeout when the module should considered that the action has failed.
    default: 300
    type: int
  force:
    description:
      - Force the change of the cluster state.
    type: bool
    default: true
"""

EXAMPLES = r"""
- name: Set cluster Online
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Get cluster state
      community.general.pacemaker_cluster:
        state: online
"""

RETURN = r"""
out:
  description: The output of the current state of the cluster. It returns a list of the nodes state.
  type: str
  sample: 'out: [["  overcloud-controller-0", " Online"]]}'
  returned: always
"""

import time

from ansible.module_utils.basic import AnsibleModule


_PCS_CLUSTER_DOWN = "Error: cluster is not currently running on this node"


def get_cluster_status(module):
    cmd = ["pcs", "cluster", "status"]
    rc, out, err = module.run_command(cmd)
    if out in _PCS_CLUSTER_DOWN:
        return 'offline'
    else:
        return 'online'


def get_node_status(module, node='all'):
    node_l = ["all"] if node == "all" else []
    cmd = ["pcs", "cluster", "pcsd-status"] + node_l
    rc, out, err = module.run_command(cmd)
    if rc == 1:
        module.fail_json(msg="Command execution failed.\nCommand: `%s`\nError: %s" % (cmd, err))
    status = []
    for o in out.splitlines():
        status.append(o.split(':'))
    return status


def clean_cluster(module, timeout):
    cmd = ["pcs", "resource", "cleanup"]
    rc, out, err = module.run_command(cmd)
    if rc == 1:
        module.fail_json(msg="Command execution failed.\nCommand: `%s`\nError: %s" % (cmd, err))


def set_cluster(module, state, timeout, force):
    if state == 'online':
        cmd = ["pcs", "cluster", "start"]
    if state == 'offline':
        cmd = ["pcs", "cluster", "stop"]
        if force:
            cmd = cmd + ["--force"]
    rc, out, err = module.run_command(cmd)
    if rc == 1:
        module.fail_json(msg="Command execution failed.\nCommand: `%s`\nError: %s" % (cmd, err))

    t = time.time()
    ready = False
    while time.time() < t + timeout:
        cluster_state = get_cluster_status(module)
        if cluster_state == state:
            ready = True
            break
    if not ready:
        module.fail_json(msg="Failed to set the state `%s` on the cluster\n" % (state))


def main():
    argument_spec = dict(
        state=dict(type='str', choices=['online', 'offline', 'restart', 'cleanup']),
        node=dict(type='str'),
        timeout=dict(type='int', default=300),
        force=dict(type='bool', default=True),
    )

    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
    )
    changed = False
    state = module.params['state']
    node = module.params['node']
    force = module.params['force']
    timeout = module.params['timeout']

    if state in ['online', 'offline']:
        # Get cluster status
        if node is None:
            cluster_state = get_cluster_status(module)
            if cluster_state == state:
                module.exit_json(changed=changed, out=cluster_state)
            else:
                if module.check_mode:
                    module.exit_json(changed=True)
                set_cluster(module, state, timeout, force)
                cluster_state = get_cluster_status(module)
                if cluster_state == state:
                    module.exit_json(changed=True, out=cluster_state)
                else:
                    module.fail_json(msg="Fail to bring the cluster %s" % state)
        else:
            cluster_state = get_node_status(module, node)
            # Check cluster state
            for node_state in cluster_state:
                if node_state[1].strip().lower() == state:
                    module.exit_json(changed=changed, out=cluster_state)
                else:
                    if module.check_mode:
                        module.exit_json(changed=True)
                    # Set cluster status if needed
                    set_cluster(module, state, timeout, force)
                    cluster_state = get_node_status(module, node)
                    module.exit_json(changed=True, out=cluster_state)

    elif state == 'restart':
        if module.check_mode:
            module.exit_json(changed=True)
        set_cluster(module, 'offline', timeout, force)
        cluster_state = get_cluster_status(module)
        if cluster_state == 'offline':
            set_cluster(module, 'online', timeout, force)
            cluster_state = get_cluster_status(module)
            if cluster_state == 'online':
                module.exit_json(changed=True, out=cluster_state)
            else:
                module.fail_json(msg="Failed during the restart of the cluster, the cluster cannot be started")
        else:
            module.fail_json(msg="Failed during the restart of the cluster, the cluster cannot be stopped")

    elif state == 'cleanup':
        if module.check_mode:
            module.exit_json(changed=True)
        clean_cluster(module, timeout)
        cluster_state = get_cluster_status(module)
        module.exit_json(changed=True, out=cluster_state)


if __name__ == '__main__':
    main()
