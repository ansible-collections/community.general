#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2016, Mathieu Bultel <mbultel@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: pacemaker_cluster
short_description: Manage pacemaker clusters
author:
- Mathieu Bultel (@mbultel)
- Hani Audah (@haudah)
description:
   - This module can manage a pacemaker cluster and nodes from Ansible using
     the pacemaker cli.
options:
    state:
      description:
        - Indicate desired state of the cluster
      choices: [ cleanup, offline, online, restart, present, absent ]
      type: str
    node:
      description:
        - Specify which node of the cluster you want to manage. None == the
          cluster status itself, 'all' == check the status of all nodes.
      type: str
    pcs_user:
      description:
        - The username used to authenticate with new nodes being added to the cluster
      type: str
    pcs_password:
      description:
        - The password used to authenticate with new nodes being added to the cluster
      type: str
    timeout:
      description:
        - Timeout when the module should considered that the action has failed
      default: 300
      type: int
    force:
      description:
        - Force the change of the cluster state
      type: bool
      default: 'yes'
    properties:
      description:
        - Properties to be applied onto the pacemaker cluster
      type: dict
    enable:
      description:
        - Enable automatic cluster startup on the specified nodes
      type: bool
      default: 'yes'
'''
EXAMPLES = '''
---
- name: Create pacemaker cluster
  hosts: localhost
  gather_facts: no
  tasks:
  - name: Ensure cluster exists
    community.general.pacemaker_cluster:
      state: present
      nodes:
        - node1
        - node2
      pcs_user: username
      pcs_password: password
  - name: Bring the cluster online
    community.general.pacemaker_cluster:
      state: online
      nodes:
        - node1
        - node2
'''

RETURN = '''
changed:
    description: True if the cluster state has changed
    type: bool
    returned: always
out:
    description: The output of the current state of the cluster. It return a
                 list of the nodes state.
    type: str
    sample: 'out: [["  overcloud-controller-0", " Online"]]}'
    returned: always
rc:
    description: exit code of the module
    type: bool
    returned: always
'''

import time, re

from ansible.module_utils.basic import AnsibleModule


_PCS_CLUSTER_DOWN = "Error: cluster is not currently running on this node"
_PCS_NO_CLUSTER = "Error: unable to get crm_config"


def get_cluster_status(module):
    cmd = "pcs cluster status"
    rc, out, err = module.run_command(cmd)
    if _PCS_CLUSTER_DOWN in err:
        return 'offline'
    else:
        return 'online'


def authenticate_nodes(module, nodes, pcs_user, pcs_password):
    cmd = "pcs host auth %s -u %s -p %s" % (" ".join(nodes), pcs_user, pcs_password)
    rc, out, err = module.run_command(cmd)
    if rc == 1:
        module.fail_json(msg="Failed to authenticate with some cluster nodes.\nCommand: `%s`\nError: %s" % (cmd, err))


# the status of a node is determined both by its:
# i. PCSD status
# ii. Pacemaker status
# iii. Corosync status
def get_nodes_status(module):
    online_nodes = set()
    # once a node is counted as offline by any of these tests, it'll stay there
    offline_nodes = set()
    cmd = "pcs status nodes both"
    rc, out, err = module.run_command(cmd)
    if rc == 1:
        module.fail_json(msg="Failed to get cluster node status.\nCommand: `%s`\nError: %s" % (cmd, err))

    # helper function to avoid duplicate code
    def helper(match_object):
        for online_node in match_object.group(1).split(" "):
            if not(online_node in offline_nodes):
                online_nodes.add(online_node)
        for offline_node in match_object.group(2).split(" "):
            online_nodes.discard(offline_node)
            offline_nodes.add(offline_node)

    match_object = re.search(r'Corosync Nodes:[\s\S]*?Online:((?: \S+)*)\n Offline:((?: \S+)*)\n', out)
    helper(match_object)

    match_object = re.search(r'Pacemaker Nodes:[\s\S]*?Online:((?: \S+)*)[\s\S]*?Offline:((?: \S+)*)\n', out)
    helper(match_object)
    
    match_object = re.search(r'Pacemaker Remote Nodes:[\s\S]*?Online:((?: \S+)*)[\s\S]*?Offline:((?: \S+)*)\n', out)
    helper(match_object)

    # return a tuple of the online, offline nodes
    return (online_nodes, offline_nodes)


def set_cluster(module, state, timeout, force):
    if state == 'online':
        cmd = "pcs cluster start"
    if state == 'offline':
        cmd = "pcs cluster stop"
        if force:
            cmd = "%s --force" % cmd
    rc, out, err = module.run_command(cmd)
    if rc == 1:
        module.fail_json(msg="Failed to change cluster state.\nCommand: `%s`\nError: %s" % (cmd, err))

    t = time.time()
    ready = False
    while time.time() < t + timeout:
        cluster_state = get_cluster_status(module)
        if cluster_state == state:
            ready = True
            break
    if not ready:
        module.fail_json(msg="Failed to set the state `%s` on the cluster\n" % (state))


def set_nodes(module, state, nodes, timeout, force):
    if state == 'online':
        cmd = "pcs cluster start %s" % " ".join(nodes)
        rc, out, err = module.run_command(cmd)
        if rc == 1:
            # if the cluster is up but still failed to get cluster config => error
            module.fail_json(msg="Failed to start the cluster on one or more nodes.\nCommand: `%s`\nError: %s" % (cmd, err))
    elif state == 'offline':
        cmd = "pcs cluster stop %s" % " ".join(nodes)
        if force:
            cmd = "%s --force" % cmd
        rc, out, err = module.run_command(cmd)
        if rc == 1:
            # if the cluster is up but still failed to get cluster config => error
            module.fail_json(msg="Failed to stop the cluster on one or more nodes.\nCommand: `%s`\nError: %s" % (cmd, err))

    online_nodes, offline_nodes = get_node_status(module, nodes)
    t = time.time()
    ready = False
    while time.time() < t + timeout:
        online_nodes, offline_nodes = get_node_status(module, nodes)
        if (state == 'online' and len(offline_nodes) == 0) or (state == 'offline' and len(online_nodes) == 0):
            ready = True
            break
    if not ready:
        module.fail_json(msg="Failed to set the state `%s` on the cluster\n" % (state))


def create_cluster(module, timeout, name, cluster_nodes, pcs_user, pcs_password, properties):
    changed = False
    # we'll be modifying the list of nodes
    nodes = list(cluster_nodes)
    # first check if cluster is running on this node
    status = get_cluster_status(module)
    # parse output of 'pcs config'
    cmd = "pcs config"
    rc, out, err = module.run_command(cmd)
    if rc == 1 and status == 'online':
        # if the cluster is up but still failed to get cluster config => error
        module.fail_json(msg="Failed to get cluster configuration.\nCommand: `%s`\nError: %s" % (cmd, err))
    match_object = re.search(r'Cluster Name: (.*?)\n', out)
    existing_name = match_object.group(1)
    if len(existing_name) > 0 and existing_name != name:
        module.fail_json(msg="The node is currently part of a cluster of a different name: %s.\nCommand: `%s`\nError: %s" % (existing_name, cmd, err))

    # if the cluster needs to be created, no need to check existing config
    if len(existing_name) == 0:
        # first authenticate with all nodes
        authenticate_nodes(module, nodes, pcs_user, pcs_password)
        cmd = "pcs cluster setup %s --start %s" % (name, " ".join(nodes))
        rc, out, err = module.run_command(cmd)
        if rc == 1:
            module.fail_json(msg="Failed to create cluster.\nCommand: `%s`\nError: %s" % (cmd, err))
        cmd = "pcs property set %s" % " ".join(["%s=%s" % props for props in properties.items()])
        rc, out, err = module.run_command(cmd)
        if rc == 1:
            # if the cluster is up but still failed to get cluster config => error
            module.fail_json(msg="Failed to set cluster properties.\nCommand: `%s`\nError: %s" % (cmd, err))
        return True
    else:
        # if cluster is offline but with same name, start it up to configure it
        if status == 'offline':
            changed = True
            set_cluster(module, 'online', timeout, False)
            cmd = "pcs config"
            rc, out, err = module.run_command(cmd)
            if rc == 1:
                # if the cluster is up but still failed to get cluster config => error
                module.fail_json(msg="Failed to get cluster configuration.\nCommand: `%s`\nError: %s" % (cmd, err))

        match_object = re.search(r'Corosync Nodes:\n((?:\s\S+)*?)\n', out)
        corosync_nodes = match_object.group(1).strip().split(' ')
        match_object = re.search(r'Pacemaker Nodes:\n((?:\s\S+)*?)\n', out)
        pacemaker_nodes = match_object.group(1).strip().split(' ')
        # only include nodes in both corosync_nodes and pacemaker_nodes
        existing_nodes = [node for node in corosync_nodes if node in pacemaker_nodes]
        for existing_node in existing_nodes:
            if existing_node in nodes:
                nodes.remove(existing_node)
        # if there are still nodes unaccounted for, add them to the cluster
        if len(nodes) > 0:
            changed = True
            authenticate_nodes(module, nodes, pcs_user, pcs_password)
            for node in nodes:
                cmd = "pcs cluster node add --start %s" % node
                rc, out_node, err = module.run_command(cmd)
                if rc == 1:
                    module.fail_json(msg="Failed to add node to cluster.\nCommand: `%s`\nError: %s" % (cmd, err))

        # now that all nodes should be present, check their status
        online_nodes, offline_nodes = get_nodes_status(module)

        # check if properties already exist
        match_object = re.search(r'Cluster Properties:\n (.*?:.*?\n)*', out)
        existing_properties = re.findall(r'(\S*?): (\S*?)\n', match_object.group(0))
        for existing_property in existing_properties:
            if existing_property in properties:
                properties.remove(existing_property)

        if len(properties) > 0:
            changed = True
            cmd = "pcs property set %s" % " ".join(["%s=%s" % props for props in properties.items()])
            rc, out, err = module.run_command(cmd)
            if rc == 1:
                # if the cluster is up but still failed to get cluster config => error
                module.fail_json(msg="Failed to set cluster properties.\nCommand: `%s`\nError: %s" % (cmd, err))

        return changed


def clean_cluster(module, timeout):
    cmd = "pcs resource cleanup"
    rc, out, err = module.run_command(cmd)
    if rc == 1:
        module.fail_json(msg="Command execution failed.\nCommand: `%s`\nError: %s" % (cmd, err))


def main():
    argument_spec = dict(
        state=dict(type='str', choices=['online', 'offline', 'restart', 'cleanup', 'present', 'absent']),
        name=dict(type='str', required=True),
        pcs_user=dict(type='str', required=True),
        pcs_password=dict(type='str', required=True),
        timeout=dict(type='int', default=300),
        force=dict(type='bool', default=True),
        nodes=dict(type='list', elements='str'),
        properties=dict(type='dict', default={}),
    )

    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
    )
    changed = False
    state = module.params['state']
    pcs_user = module.params['pcs_user']
    pcs_password = module.params['pcs_password']
    force = module.params['force']
    timeout = module.params['timeout']
    nodes = module.params['nodes']
    properties = module.params['properties']
    name = module.params['name']

    if state in ['online', 'present']:
        changed = create_cluster(module, timeout, name, nodes, pcs_user, pcs_password, properties)

    if state in ['online', 'offline']:
        cluster_state = get_cluster_status(module)
        # if state is already offline, we can't really determine the status
        # of other nodes, but we will not error out and just assume all is well
        if not(state == 'offline' and state == cluster_state):
            if state == 'online':
                if cluster_state == 'offline':
                    changed = True
                    # start them all
                    set_nodes(module, state, nodes, timeout, force)
                else:
                    # make sure the cluster nodes are all up
                    online_nodes, offline_nodes = get_nodes_status(module)
                    if len(online_nodes) < len(nodes):
                        changed = True
                        set_nodes(module, state, nodes, timeout, force)
            elif state == 'offline':
                # cluster must still be online otherwise we wouldn't be here
                # so no need to check node status just stop all nodes
                changed = True
                set_nodes(module, state, nodes, timeout, force)

    if state in ['restart']:
        changed = True
        set_cluster(module, 'offline', timeout, force)
        cluster_state = get_cluster_status(module)
        if cluster_state == 'offline':
            set_cluster(module, 'online', timeout, force)
            cluster_state = get_cluster_status(module)
            if cluster_state != 'online':
                module.fail_json(msg="Failed during the restart of the cluster, the cluster can't be started")
        else:
            module.fail_json(msg="Failed during the restart of the cluster, the cluster can't be stopped")

    if state in ['cleanup']:
        changed = True
        clean_cluster(module, timeout)
        cluster_state = get_cluster_status(module)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
