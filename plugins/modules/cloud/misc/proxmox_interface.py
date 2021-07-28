#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Andreas Botzner (@andreas.botzner) <andreas@botzner.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from ansible_collections.community.general.plugins.module_utils.proxmox import ProxmoxAnsible
from ansible_collections.community.general.plugins.module_utils.proxmox_interfaces import delete_nic, update_nic, create_nic, reload_interfaces, get_nics, proxmox_map_interface_args, proxmox_interface_argument_spec
from ansible_collections.community.general.plugins.module_utils.proxmox import proxmox_auth_argument_spec
from ansible.module_utils.basic import AnsibleModule, env_fallback
__metaclass__ = type

DOCUMENTATION = r'''
---
module: proxmox_interface
short_description: Management network interface on a Proxmox VE cluster.
version_added: 3.5.0
description:
  - Allows you to create/update/delete a network interface of a Proxmox VE node.
author: "Andreas Botzner (@andreas.botzner) <andreas@botzner.com>"
options:
description: Interface configuration
type: list
elements: dict
suboptions:
  name:
    description:
      - Name of the network interface.
    type: str
    required: true
  type:
    description:
      - Network interface type
    type: str
    required: true
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
    type: str
  vlan_raw_device:
    description:
      - Specify the raw interface for the vlan interface.
    type: str
  apply:
    description:
      - Reload interfaces and make configuration persistent
    type: bool
    default: True
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
      - gathered
    default: present
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

- name: Delete interface vmbr123 from node01
  community.general.proxmox_interface:
    api_user: root@pam
    api_password: secret
    api_host: proxmoxhost
    name: vmbr123
    node: node01
    state: absent

- name: Gather info about interface eth1 from node01
  community.general.proxmox_interface
    api_user: root@pam
    api_password: secret
    api_host: proxmoxhost
    name: eth1
    node: node01
    state: gathered
'''

RETURN = '''

config:
  description: The configuration as structured data before module execution
  returned: always
  type: list
  sample:
   - [{'exists': 1, 'type': 'eth', 'families': ['inet', 'inet6'], 'method6': 'static', 'netmask6': '64', 'address': '10.0.0.12', 'priority': 4, 'active': 1,
   - 'cidr6': 'abcd:abcd:abcd::2/64', 'gateway6': 'fe80::1', 'autostart': 1, 'method': 'static', 'address6': 'abcd:abcd:ab:abcd::2', 'netmask': '26',
   - 'iface': 'ens32', 'gateway': '10.0.0.1', 'cidr': '10.0.0.10/24'}]

config_after:
  description: The configuration as structured data after module completion
  returned: when changed
  type: list
  sample: same as in config
'''


def reload_interfaces(proxmox: ProxmoxAnsible):
    if proxmox.module.params['apply']:
        try:
            proxmox.proxmox_api.nodes(
                proxmox.module.params['node']).network.put()
        except Exception as e:
            proxmox.module.fail_json(msg="Failed to reload and apply interfaces on node {0}"
                                     + " with exception: {1}".format(proxmox.module.params['node'], str(e)))


def main():
    interface_common_args = proxmox_interface_argument_spec()
    network_args = dict(
        apply=dict(type=bool, default=True),
        node=dict(type='str', requied=True)
    )
    module_args = proxmox_auth_argument_spec()
    module_args.update(network_args)
    module_args.updated(interface_common_args)

    module = AnsibleModule(
        argument_spec=module_args,
        required_together=[('api_token_id', 'api_token_secret'),
                           ('api_user', 'api_password'),
                           ('state', 'present', ('config'))],
        required_one_of=[('api_password', 'api_token_id')],
        required_if=[('state', 'present', ('config',))],
        supports_check_mode=True,
    )
    proxmox = ProxmoxAnsible(module)

    state = module.params['state']
    name = module.params['name']
    node = module.params['node']

    result = {'changed': False}
    nics = get_nics(module=module, proxmox=proxmox, node=node)
    result['config'] = nics

    if state is 'gathered':
        module.exit_json(**result)

    config = proxmox_map_interface_args(module)

    present_nics = set(nic['iface'] for nic in nics)

    if name in present_nics:
        if state is 'absent':
            try:
                delete_nic(proxmox.proxmox_api, node, name)
                result['changed'] = True
                result['msg'] = 'Successfully deleted interface {0}'.format(
                    name)
            except Exception as e:
                print(str(e))
                module.exit_json(
                    node=node,
                    msg='Failed to delete interface {-} from node {1} with error: {2}'.format(
                        name, node, str(e)))
        else:
            try:
                update_nic(proxmox.proxmox_api, node, name, config)
                result['changed'] = True
                result['msg'] = 'Successfully updated interface {0}'.format(
                    name)
            except Exception as e:
                module.exit_json(
                    node=node,
                    msg='Failed to update interface {0} from node {1} with error: {2}'.format(
                        name, node, str(e)))
    else:
        if state is 'present':
            create_nic(proxmox, node, config)
            result['changed'] = True
            result['msg'] = 'Successfully created interface {0}'.format(name)
        else:
            result['msg'] = 'Interface {0} not present'.format(name)

    if proxmox.module.params['reload_interfaces']:
        try:
            reload_interfaces(proxmox)
        except Exception as e:
            proxmox.module.fail_json(msg="Failed to reload and apply interfaces on node {0}"
                                     + " with exception: {1}".format(node, str(e)))
    if result['changed'] is True:
        result['after'] = get_nics(proxmox)
    module.exit_json(**result)


if __name__ == '__main__':
    main()
