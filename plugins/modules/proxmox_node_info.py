#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright John Berninger (@jberning) <john.berninger at gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: proxmox_node_info
short_description: Retrieve information about one or more Proxmox VE nodes
version_added: 8.0.3
description:
  - Retrieve information about one or more Proxmox VE nodes.
options:
  node:
    description:
      - Restrict results to a specific node.
    aliases: ['node', 'name']
    type: str
author: John Berninger (@jberning)
extends_documentation_fragment:
  - community.general.proxmox.documentation
  - community.general.attributes
  - community.general.attributes.info_module
'''


EXAMPLES = '''
- name: List existing nodes
  community.general.proxmox_node_info:
    api_host: proxmox1
    api_user: root@pam
    api_password: "{{ password | default(omit) }}"
    api_token_id: "{{ token_id | default(omit) }}"
    api_token_secret: "{{ token_secret | default(omit) }}"
  register: proxmox_nodes
'''


RETURN = '''
proxmox_nodes:
    description: List of Proxmox VE nodes.
    returned: always, but can be empty
    type: list
    elements: dict
    contains:
      cpu:
        description: Current CPU usage in fractional shares of this host's total available CPU
        returned: on success
        type: float
      disk:
        description: Current local disk usage of this host
        returned: on success
        type: int
      id:
        description: identity of the node
        return: on success
        type: string
      level:
        description: Support level. Can be blank if not under a paid support contract
        return: on success
        type: string
      maxcpu:
        description: Number of available CPUs
        return: on success
        type: int
      maxdisk:
        description: Size of local disk in bytes
        return: on success
        type: int
      maxmem:
        description: Memory size in bytes
        return: on success
        type: int
      mem:
        description: Used memory in bytes
        return: on success
        type: int
      node:
        description: Node name
        return: on success
        type: string
      ssl_fingerprint:
        description: SSL fingerprint of the node certificate
        return: on success
        type: string
      status:
        description: Node status
        return: on success
        type: string 
      type:
        description: Object type being returned
        return: on success
        type: string
      uptime:
        description: Node uptime in seconds
        return: on success
        type: int
'''


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.proxmox import (
    proxmox_auth_argument_spec, ProxmoxAnsible)


class ProxmoxNodeInfoAnsible(ProxmoxAnsible):
    def get_nodes(self):
        nodes = self.proxmox_api.nodes()
        return nodes


def proxmox_node_info_argument_spec():
    return dict(
    )


def main():
    module_args = proxmox_auth_argument_spec()
    node_info_args = proxmox_node_info_argument_spec()
    module_args.update(node_info_args)

    module = AnsibleModule(
        argument_spec=module_args,
        required_one_of=[('api_password', 'api_token_id')],
        required_together=[('api_token_id', 'api_token_secret')],
        supports_check_mode=True
    )
    result = dict(
        changed=False
    )

    proxmox = ProxmoxNodeInfoAnsible(module)

    nodes = proxmox.get_nodes()
    result['proxmox_nodes'] = nodes

    module.exit_json(**result)


if __name__ == '__main__':
    main()
