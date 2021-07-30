#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Andreas Botzner (@andreas.botzner) <andreas@botzner.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: proxmox_interface
short_description: Management network interface on a Proxmox VE cluster.
version_added: 3.5.0
description:
  - Allows you to create/update/delete a network interface of a Proxmox VE node.
author: "Andreas Botzner (@botzner_andreas) <andreas@botzner.com>"
options:
  name:
    description:
      - Name of the network interface.
    type: str
    required: true
  type:
    description:
      - Network interface type
    type: str
    default: bridge
    choices:
    - bridge
    - bond
    - eth
    - alias
    - vlan
    - OVSBridge
    - OVSBond
    - OVSPort
    - OVSIntPort
    - unknown
  address:
    description:
      - IPv4 address of the interface
    type: str
  address6:
    description:
      - IPv6 address of the interface
    type: str
  autostart:
    description:
      - Automatically start interface on boot.
    type: bool
    default: true
  bond_primary:
    description:
      - Primary interface for active-backup bond.
    type: str
  bond_mode:
    description:
      - Bonding mode
    type: str
    choices:
      - balance-rr
      - active-backup
      - balance-xor
      - broadcast
      - 802.3ad
      - balance-tlb
      - balance-alb
      - balance-slb
      - lacp-balance-slb
      - lacp-balance-tcp
  bond_xmit_hash_policy:
    description:
      - Selects the transmit hash policy to use for slave selection in balance-xor and 802.3ad
    type: str
    choices:
      - layer2
      - layer2+3
      - layer3+4
  bridge_ports:
    description:
      - Specify the interfaces you want to add to your bridge.
    type: str
  bridge_vlan_ports:
    description:
      - Enable bridge vlan support.
    type: bool
  cidr:
    description:
      - IPv4 CIDR
    type: str
  cidr6:
    description:
      - IPv6 CIDR
    type: str
  comments:
    description:
      - Comments
    type: str
  comments6:
    description:
      - Comments
    type: str
  gateway:
    description:
      - Default gateway address.
    type: str
  gateway6:
    description:
      - Default IPv6 gateway address.
    type: str
  mtu:
    description:
      - MTU,
      - Value should be C(1280 ≤ n ≤ 65520).
    type: int
  netmask:
    description:
      - Network mask
    type: str
  netmask6:
    description:
      - Network mask for IPv6.
      - Value should be C(0 ≤ n ≤ 128).
    type: int
  ovs_bonds:
    description:
      - Specify the interfaces used by the bonding device.
    type: str
  ovs_bridge:
    description:
      - The OVS bridge associated with a OVS port.
      - This is required when you create an OVS port.
    type: str
  ovs_options:
    description:
      - OVS interface options.
    type: str
  ovs_ports:
    description:
      - Specify the interfaces you want to add to your bridge.
    type: str
  ovs_tag:
    description:
      - Specify a VLan tag (used by OVSPort, OVSIntPort, OVSBond)
      - Value should be C(1 ≤ n ≤ 4094).
    type: int
  slaves:
    description:
      - Specify a VLan tag (used by OVSPort, OVSIntPort, OVSBond)
    type: str
  vlan_id:
    description:
      - vlan-id for a custom named vlan interface (ifupdown2 only).
    type: int
  vlan_raw_device:
    description:
      - Specify the raw interface for the vlan interface.
    type: str
  node:
    description:
      - Name of the cluster node.
    type: str
    required: true
  state:
    description:
      - Indicates desired state of the NIC.
    type: str
    choices:
      - present
      - absent
    default: present
  apply:
    description:
      - Reload interfaces and make configuration persistent after going
      - though list of interfaces
    type: bool
    default: true
  ignore_errors:
    description:
      - Ignore Errors when changing an interface
    type: bool
    default: false
  revert_on_error:
    description:
      - Try to revert to previous configuration upon encountering errors
    type: bool
    default: true
extends_documentation_fragment:
  - community.general.proxmox.documentation
'''

EXAMPLES = '''
- name: Create new VM bridge on node01
  community.general.proxmox_interface:
    api_user: root@pam
    api_password: secret
    api_host: proxmoxhost
    node: node01
    type: bridge
    name: vmrb56
    address: 192.168.5.4
    netmask: 255.255.255.0
    comment: 'This is a new VM bridge with the host inside'
    state: present

- name: Create new OVS bridge on node02
  community.general.proxmox_interface:
    api_user: john.doe@pve
    api_password: supersecret
    api_host: proxmoxhost
    node: node02
    type: ovs_bridge
    name: vmbr23
    cidr: 10.34.43.22/23
    gateway: 10.34.43.1
    bridge_ports: eth1
    ovs_options: 'some OVS options'

- name: Delete interface vmbr123 from node01
  community.general.proxmox_interface:
    api_user: root@pam
    api_password: secret
    api_host: proxmoxhost
    name: vmbr123
    node: node01
    state: absent

- name: Delete interface vmbr321 from node01 but don't apply changes
  community.general.proxmox_interface:
    api_user: root@pam
    api_password: secret
    api_host: proxmoxhost
    name: eth1
    node: node01
    apply: false
'''

RETURN = '''
config:
  description: The configuration as structured data before module execution
  returned: always
  type: list
  sample:

config_after:
  description: The configuration as structured data after module completion
  returned: when changed
  type: list
  sample: same as in config
'''

import traceback

PROXMOXER_IMP_ERR = None
try:
    from proxmoxer import ProxmoxAPI
    HAS_PROXMOXER = True
except ImportError:
    HAS_PROXMOXER = False
    PROXMOXER_IMP_ERR = traceback.format_exc()

from ansible_collections.community.general.plugins.module_utils.proxmox import (
    ProxmoxAnsible, proxmox_auth_argument_spec)
from ansible_collections.community.general.plugins.module_utils.proxmox_interfaces import (
    get_nics, delete_nic, create_nic, reload_interfaces, rollback_interfaces, update_nic, proxmox_map_interface_args, proxmox_interface_argument_spec)
from ansible.module_utils.basic import AnsibleModule


def main():
    interface_common_args = proxmox_interface_argument_spec()
    network_args = dict(
        apply=dict(type='bool', default=True),
        ignore_errors=dict(type='bool', default=False),
        revert_on_error=dict(type='bool', default=True),
        node=dict(type='str', required=True),
    )
    module_args = proxmox_auth_argument_spec()
    module_args.update(interface_common_args)
    module_args.update(network_args)

    module = AnsibleModule(
        argument_spec=module_args,
        required_together=[('api_token_id', 'api_token_secret'),
                           ('api_user', 'api_password')],
        required_one_of=[('api_password', 'api_token_id')],
        required_if=[('state', 'present', ('name',))],
        supports_check_mode=False,
    )
    proxmox = ProxmoxAnsible(module)

    state = module.params['state']
    name = module.params['name']
    node = module.params['node']
    ignore_errors = module.params['ignore_errors']
    revert_on_error = module.params['revert_on_error']
    apply = module.params['apply']

    result = {'changed': False}
    msg = []
    errors = []
    nics = dict(get_nics(proxmox))
    result['config'] = nics

    interface_args = proxmox_map_interface_args(module)

    present_nics = set(nic['iface'] for nic in nics)

    if name in present_nics:
        if state == 'absent':
            try:
                delete_nic(proxmox.proxmox_api, node, name)
                result['changed'] = True
                msg.append('Successfully deleted interface {0}'.format(name))
            except Exception as e:
                errors.append('Failed to delete interface {0} from node {1} with error: {2}'.format(
                    name, node, str(e)))
        else:
            try:
                update_nic(proxmox.proxmox_api, node, name, interface_args)
                result['changed'] = True
                msg.append('Successfully updated interface {0}'.format(name))
            except Exception as e:
                errors.append('Failed to update interface {0} from node {1} with error: {2}'.format(
                    name, node, str(e)))
    else:
        if state == 'present':
            create_nic(proxmox, node, interface_args)
            result['changed'] = True
            msg.append('Successfully created interface {0}'.format(name))
        else:
            msg.append('Interface {0} not present'.format(name))

    result['errors'] = errors
    result['msg'] = msg
    if not errors or ignore_errors:
        if not apply:
            module.exit_json(**result)
        else:
            try:
                reload_interfaces(proxmox.proxmox_api, node)
                result['msg'].append(
                    'Successfully reloaded and applied interface changes on node {0}'.format(node))
                module.exit_json(**result)
            except Exception as e:
                result['errors'].append(
                    'Failed to reload interfaces on node: {0} with error: {1}'.format(node, str(e)))
    elif revert_on_error:
        try:
            rollback_interfaces(proxmox.proxmox_api, node)
            result['msg'].append(
                'Successfully rolled back uncommitted changes on node {0}'.format(node))
            result['changed'] = False
            module.exit_json(**result)
        except Exception as e:
            result['errors'].append(
                "Failed to revert interfaces on node: {0} with error {1}".format(node, str(e)))
            module.fail_json(**result)
    else:
        module.fail_json(**result)


if __name__ == '__main__':
    main()
