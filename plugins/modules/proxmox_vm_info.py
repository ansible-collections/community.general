#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2023, Sergei Antipov <greendayonfire at gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: proxmox_vm_info
short_description: Retrieve information about one or more Proxmox VE virtual machines
version_added: 7.2.0
description:
  - Retrieve information about one or more Proxmox VE virtual machines.
author: 'Sergei Antipov (@UnderGreen) <greendayonfire at gmail dot com>'
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
extends_documentation_fragment:
    - community.general.proxmox.documentation
    - community.general.attributes
    - community.general.attributes.info_module
"""

EXAMPLES = """
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

- name: Retrieve information about specific VM by name
  community.general.proxmox_vm_info:
    api_host: proxmoxhost
    api_user: root@pam
    api_password: '{{ password | default(omit) }}'
    node: node01
    type: lxc
    name: lxc05.home.arpa
"""

RETURN = """
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

    def get_vms_from_nodes(self, vms_unfiltered, type, vmid=None, name=None, node=None):
        vms = []
        for vm in vms_unfiltered:
            if (
                type != vm["type"]
                or (node and vm["node"] != node)
                or (vmid and int(vm["vmid"]) != vmid)
                or (name is not None and vm["name"] != name)
            ):
                continue
            vms.append(vm)
        nodes = frozenset([vm["node"] for vm in vms])
        for node in nodes:
            if type == "qemu":
                vms_from_nodes = self.proxmox_api.nodes(node).qemu().get()
            else:
                vms_from_nodes = self.proxmox_api.nodes(node).lxc().get()
            for vmn in vms_from_nodes:
                for vm in vms:
                    if int(vm["vmid"]) == int(vmn["vmid"]):
                        vm.update(vmn)
                        vm["vmid"] = int(vm["vmid"])
                        vm["template"] = proxmox_to_ansible_bool(vm["template"])
                        break

        return vms

    def get_qemu_vms(self, vms_unfiltered, vmid=None, name=None, node=None):
        try:
            return self.get_vms_from_nodes(vms_unfiltered, "qemu", vmid, name, node)
        except Exception as e:
            self.module.fail_json(msg="Failed to retrieve QEMU VMs information: %s" % e)

    def get_lxc_vms(self, vms_unfiltered, vmid=None, name=None, node=None):
        try:
            return self.get_vms_from_nodes(vms_unfiltered, "lxc", vmid, name, node)
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

    result = dict(changed=False)

    if node and proxmox.get_node(node) is None:
        module.fail_json(msg="Node %s doesn't exist in PVE cluster" % node)

    vms_cluster_resources = proxmox.get_vms_from_cluster_resources()
    vms = []

    if type == "lxc":
        vms = proxmox.get_lxc_vms(vms_cluster_resources, vmid, name, node)
    elif type == "qemu":
        vms = proxmox.get_qemu_vms(vms_cluster_resources, vmid, name, node)
    else:
        vms = proxmox.get_qemu_vms(
            vms_cluster_resources,
            vmid,
            name,
            node,
        ) + proxmox.get_lxc_vms(vms_cluster_resources, vmid, name, node)

    result["proxmox_vms"] = vms
    module.exit_json(**result)


if __name__ == "__main__":
    main()
