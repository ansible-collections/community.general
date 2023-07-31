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
      - Node where to get virtual machines info.
    required: true
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
    type: int
  name:
    description:
      - Restrict results to a specific virtual machine by using its name.
      - If multiple virtual machines have the same name then vmid must be used instead.
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
          "maxdisk": 34359738368,
          "maxmem": 4294967296,
          "mem": 35158379,
          "name": "pxe.home.arpa",
          "netin": 99715803,
          "netout": 14237835,
          "pid": 1947197,
          "status": "running",
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
          "maxdisk": 0,
          "maxmem": 536870912,
          "mem": 0,
          "name": "test1",
          "netin": 0,
          "netout": 0,
          "status": "stopped",
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
)


class ProxmoxVmInfoAnsible(ProxmoxAnsible):
    def get_qemu_vms(self, node, vmid=None):
        try:
            vms = self.proxmox_api.nodes(node).qemu().get()
            for vm in vms:
                vm["vmid"] = int(vm["vmid"])
                vm["type"] = "qemu"
            if vmid is None:
                return vms
            return [vm for vm in vms if vm["vmid"] == vmid]
        except Exception as e:
            self.module.fail_json(msg="Failed to retrieve QEMU VMs information: %s" % e)

    def get_lxc_vms(self, node, vmid=None):
        try:
            vms = self.proxmox_api.nodes(node).lxc().get()
            for vm in vms:
                vm["vmid"] = int(vm["vmid"])
            if vmid is None:
                return vms
            return [vm for vm in vms if vm["vmid"] == vmid]
        except Exception as e:
            self.module.fail_json(msg="Failed to retrieve LXC VMs information: %s" % e)


def main():
    module_args = proxmox_auth_argument_spec()
    vm_info_args = dict(
        node=dict(type="str", required=True),
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

    if proxmox.get_node(node) is None:
        module.fail_json(msg="Node %s doesn't exist in PVE cluster" % node)

    if not vmid and name:
        vmid = int(proxmox.get_vmid(name, ignore_missing=False))

    vms = None
    if type == "lxc":
        vms = proxmox.get_lxc_vms(node, vmid=vmid)
    elif type == "qemu":
        vms = proxmox.get_qemu_vms(node, vmid=vmid)
    else:
        vms = proxmox.get_qemu_vms(node, vmid=vmid) + proxmox.get_lxc_vms(
            node, vmid=vmid
        )

    if vms or vmid is None:
        result["proxmox_vms"] = vms
        module.exit_json(**result)
    else:
        result["msg"] = "VM with vmid %s doesn't exist on node %s" % (vmid, node)
        module.fail_json(**result)


if __name__ == "__main__":
    main()
