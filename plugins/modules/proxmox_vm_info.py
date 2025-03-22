#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2023, Sergei Antipov <greendayonfire at gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: proxmox_vm_info
short_description: Retrieve information about one or more Proxmox VE virtual machines
version_added: 7.2.0
description:
  - Retrieve information about one or more Proxmox VE virtual machines.
author: 'Sergei Antipov (@UnderGreen) <greendayonfire at gmail dot com>'
attributes:
  action_group:
    version_added: 9.0.0
options:
  node:
    description:
      - Restrict results to a specific Proxmox VE node.
    type: str
  type:
    description:
      - Restrict results to a specific virtual machine(s) type.
    type: str
    choices:
      - all
      - qemu
      - lxc
    default: all
  vmid:
    description:
      - Restrict results to a specific virtual machine by using its ID.
      - If VM with the specified vmid does not exist in a cluster then resulting list will be empty.
    type: int
  name:
    description:
      - Restrict results to a specific virtual machine(s) by using their name.
      - If VM(s) with the specified name do not exist in a cluster then the resulting list will be empty.
    type: str
  config:
    description:
      - Whether to retrieve the VM configuration along with VM status.
      - If set to V(none) (default), no configuration will be returned.
      - If set to V(current), the current running configuration will be returned.
      - If set to V(pending), the configuration with pending changes applied will be returned.
    type: str
    choices:
      - none
      - current
      - pending
    default: none
    version_added: 8.1.0
  network:
    description:
      - Whether to retrieve the current network status.
      - Requires enabled/running qemu-guest-agent on qemu VMs.
    type: bool
    default: false
    version_added: 9.1.0
extends_documentation_fragment:
  - community.general.proxmox.actiongroup_proxmox
  - community.general.proxmox.documentation
  - community.general.attributes
  - community.general.attributes.info_module
"""

EXAMPLES = r"""
- name: List all existing virtual machines on node
  community.general.proxmox_vm_info:
    api_host: proxmoxhost
    api_user: root@pam
    api_token_id: '{{ token_id | default(omit) }}'
    api_token_secret: '{{ token_secret | default(omit) }}'
    node: node01

- name: List all QEMU virtual machines on node
  community.general.proxmox_vm_info:
    api_host: proxmoxhost
    api_user: root@pam
    api_password: '{{ password | default(omit) }}'
    node: node01
    type: qemu

- name: Retrieve information about specific VM by ID
  community.general.proxmox_vm_info:
    api_host: proxmoxhost
    api_user: root@pam
    api_password: '{{ password | default(omit) }}'
    node: node01
    type: qemu
    vmid: 101

- name: Retrieve information about specific VM by name and get current configuration
  community.general.proxmox_vm_info:
    api_host: proxmoxhost
    api_user: root@pam
    api_password: '{{ password | default(omit) }}'
    node: node01
    type: lxc
    name: lxc05.home.arpa
    config: current
"""

RETURN = r"""
proxmox_vms:
    description: List of virtual machines.
    returned: on success
    type: list
    elements: dict
    sample:
      [
        {
          "cpu": 0.258944410905281,
          "cpus": 1,
          "disk": 0,
          "diskread": 0,
          "diskwrite": 0,
          "id": "qemu/100",
          "maxcpu": 1,
          "maxdisk": 34359738368,
          "maxmem": 4294967296,
          "mem": 35158379,
          "name": "pxe.home.arpa",
          "netin": 99715803,
          "netout": 14237835,
          "node": "pve",
          "pid": 1947197,
          "status": "running",
          "template": False,
          "type": "qemu",
          "uptime": 135530,
          "vmid": 100
        },
        {
          "cpu": 0,
          "cpus": 1,
          "disk": 0,
          "diskread": 0,
          "diskwrite": 0,
          "id": "qemu/101",
          "maxcpu": 1,
          "maxdisk": 0,
          "maxmem": 536870912,
          "mem": 0,
          "name": "test1",
          "netin": 0,
          "netout": 0,
          "node": "pve",
          "status": "stopped",
          "template": False,
          "type": "qemu",
          "uptime": 0,
          "vmid": 101
        }
      ]
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.proxmox import (
    proxmox_auth_argument_spec,
    ProxmoxAnsible,
    proxmox_to_ansible_bool,
)


class ProxmoxVmInfoAnsible(ProxmoxAnsible):
    def get_vms_from_cluster_resources(self):
        try:
            return self.proxmox_api.cluster().resources().get(type="vm")
        except Exception as e:
            self.module.fail_json(
                msg="Failed to retrieve VMs information from cluster resources: %s" % e
            )

    def get_vms_from_nodes(self, cluster_machines, type, vmid=None, name=None, node=None, config=None, network=False):
        # Leave in dict only machines that user wants to know about
        filtered_vms = {
            vm: info for vm, info in cluster_machines.items() if not (
                type != info["type"]
                or (node and info["node"] != node)
                or (vmid and int(info["vmid"]) != vmid)
                or (name is not None and info["name"] != name)
            )
        }
        # Get list of unique node names and loop through it to get info about machines.
        nodes = frozenset([info["node"] for vm, info in filtered_vms.items()])
        for this_node in nodes:
            # "type" is mandatory and can have only values of "qemu" or "lxc". Seems that use of reflection is safe.
            call_vm_getter = getattr(self.proxmox_api.nodes(this_node), type)
            vms_from_this_node = call_vm_getter().get()
            for detected_vm in vms_from_this_node:
                this_vm_id = int(detected_vm["vmid"])
                desired_vm = filtered_vms.get(this_vm_id, None)
                if desired_vm:
                    desired_vm.update(detected_vm)
                    desired_vm["vmid"] = this_vm_id
                    desired_vm["template"] = proxmox_to_ansible_bool(desired_vm.get("template", 0))
                    # When user wants to retrieve the VM configuration
                    if config != "none":
                        # pending = 0, current = 1
                        config_type = 0 if config == "pending" else 1
                        # GET /nodes/{node}/qemu/{vmid}/config current=[0/1]
                        desired_vm["config"] = call_vm_getter(this_vm_id).config().get(current=config_type)
                    if network:
                        if type == "qemu":
                            desired_vm["network"] = call_vm_getter(this_vm_id).agent("network-get-interfaces").get()['result']
                        elif type == "lxc":
                            desired_vm["network"] = call_vm_getter(this_vm_id).interfaces.get()

        return filtered_vms

    def get_qemu_vms(self, cluster_machines, vmid=None, name=None, node=None, config=None, network=False):
        try:
            return self.get_vms_from_nodes(cluster_machines, "qemu", vmid, name, node, config, network)
        except Exception as e:
            self.module.fail_json(msg="Failed to retrieve QEMU VMs information: %s" % e)

    def get_lxc_vms(self, cluster_machines, vmid=None, name=None, node=None, config=None, network=False):
        try:
            return self.get_vms_from_nodes(cluster_machines, "lxc", vmid, name, node, config, network)
        except Exception as e:
            self.module.fail_json(msg="Failed to retrieve LXC VMs information: %s" % e)


def main():
    module_args = proxmox_auth_argument_spec()
    vm_info_args = dict(
        node=dict(type="str", required=False),
        type=dict(
            type="str", choices=["lxc", "qemu", "all"], default="all", required=False
        ),
        vmid=dict(type="int", required=False),
        name=dict(type="str", required=False),
        config=dict(
            type="str", choices=["none", "current", "pending"],
            default="none", required=False
        ),
        network=dict(type="bool", default=False, required=False),
    )
    module_args.update(vm_info_args)

    module = AnsibleModule(
        argument_spec=module_args,
        required_together=[("api_token_id", "api_token_secret")],
        required_one_of=[("api_password", "api_token_id")],
        supports_check_mode=True,
    )

    proxmox = ProxmoxVmInfoAnsible(module)
    node = module.params["node"]
    type = module.params["type"]
    vmid = module.params["vmid"]
    name = module.params["name"]
    config = module.params["config"]
    network = module.params["network"]

    result = dict(changed=False)

    if node and proxmox.get_node(node) is None:
        module.fail_json(msg="Node %s doesn't exist in PVE cluster" % node)

    vms_cluster_resources = proxmox.get_vms_from_cluster_resources()
    cluster_machines = {int(machine["vmid"]): machine for machine in vms_cluster_resources}
    vms = {}

    if type == "lxc":
        vms = proxmox.get_lxc_vms(cluster_machines, vmid, name, node, config, network)
    elif type == "qemu":
        vms = proxmox.get_qemu_vms(cluster_machines, vmid, name, node, config, network)
    else:
        vms = proxmox.get_qemu_vms(cluster_machines, vmid, name, node, config, network)
        vms.update(proxmox.get_lxc_vms(cluster_machines, vmid, name, node, config, network))

    result["proxmox_vms"] = [info for vm, info in sorted(vms.items())]
    module.exit_json(**result)


if __name__ == "__main__":
    main()
