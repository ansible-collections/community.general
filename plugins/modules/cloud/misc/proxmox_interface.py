#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Andreas Botzner (@andreas.botzner) <andreas@botzer.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
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
  ovs_tags:
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
  state:
    description:
      - Indicates desired state of the NIC.
    type: str
    choices:
      - present
      - absent
    default: present
  node:
    description:
      - Name of the cluster node.
    type: str
    required: true
  state:
    description:
      - The state of the configuration after module completion
extends_documentation_fragment:
  - community.general.proxmox.documentation
'''

EXAMPLES = '''
- name: Create new VM bridge on node01
  community.general.proxmox_networks:
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

- name: Delete NIC net0 targeting the vm by name
  community.general.proxmox_nic:
    api_user: root@pam
    api_password: secret
    api_host: proxmoxhost
    name: my_vm
    interface: net0
    state: absent
'''

RETURN = '''

before:
  description: The configuration as structured data before module execution
  returned: always
  type: dict
  sample:
    - {some example JSON here}
after:
  description: The configuration as structured data after module completion
  returned: when changed
  type: dict
  sample:
    - {some different JSON data here}

'''

try:
    from proxmoxer import ProxmoxAPI
    HAS_PROXMOXER = True
except ImportError:
    HAS_PROXMOXER = False


def get_nics(module, proxmox, node) -> list:
    try:
        nics = proxmox.nodes(node).network.get()
    except Exception as e:
        module.fail_json(
            msg='Getting information from Node = %s failed with exception: %s' % (node, e))
    return nics


def create_nic(module, proxmox, config):
    return None


def update_nic(module, proxmox, config):
    return None


def delete_nic(module, proxmox, nic):
    return None


def update_nic(module, proxmox, nic):
    return None

def main():
    network_args = dict(
        name=dict(type='str', required=True),
        type=dict(type='str', required=True, choices=[
                  'bridge', 'bond', 'eth', 'alias', 'vlan', 'OVSBridge', 'OVSBond', 'OVSPort', 'OVSIntPort', 'unknown'], default='bridge'),
        address=dict(type='str'),
        address6=dict(type='str'),
        autostart=dict(type='bool', default=False),
        bond_mode=dict(type='str', choices=['balance-rr', 'active-backup', 'balance-xor', 'broadcast',
                       '802.3ad', 'balance-tlb', 'balance-alb', 'balance-slb', 'lacp-balance-slb', 'lacp-balance-tcp']),
        bond_xmit_hash_policy=dict(
            type='str', choices=['layer2', 'layer2+3', 'layer3+4']),
        bridge_vlan_ports=dict(type='bool'),
        cidr=dict(type='str'),
        cidr6=dict(type='str'),
        gateway=dict(type='str'),
        gateway6=dict(type='str'),
        mtu=dict(type='int'),
        netmask=dict(type='str'),
        netmask6=dict(type='int'),
        ovs_bonds=dict(type='str'),
        ovs_options=dict(type='str'),
        ovs_ports=dict(type='str'),
        ovs_tags=dict(type='int'),
        slaves=dict(type='str'),
        vlan_id=dict(type='int'),
        vlan_raw_device=dict(type='str'),
        state=dict(choices=['absent', 'present'], default='present'),
        node=dict(type='str', requied=True)
    )
    module_args = proxmox_auth_argument_spec()
    module_args.update(network_args)

    module = AnsibleModule(
        argument_spec=module_args,
        required_together=[('api_token_id', 'api_token_secret'),
                           ('api_user', 'api_password'),
                           ('state', 'present', ('config'))],
        required_one_of=[('api_password', 'api_token_id')],
        required_if=[('state', 'present', ('config',))],
        supports_check_mode=True,
    )

    if not HAS_PROXMOXER:
        module.fail_json(msg='proxmoxer required for this module')

    api_host = module.params['api_host']
    api_password = module.params['api_password']
    api_token_id = module.params['api_token_id']
    api_token_secret = module.params['api_token_secret']
    api_user = module.params['api_user']
    node = module.params['node']
    state = module.params['state']
    validate_certs = module.params['validate_certs']
    name = module.params['name']


    auth_args = {'user': api_user}
    if not (api_token_id and api_token_secret):
        auth_args['password'] = api_password
    else:
        auth_args['token_name'] = api_token_id
        auth_args['token_value'] = api_token_secret
    try:
        proxmox = ProxmoxAPI(api_host, verify_ssl=validate_certs, **auth_args)
    except Exception as e:
        module.fail_json(
            msg='authorization on proxmox cluster failed with exception: %s' % e)

    nics = get_nics(module=module, proxmox=proxmox, node=node)
    if state is 'gathered':
        module.exit_json()

    present_nics = set(nic['iface'] for nic in nics)

    # TODO implement reloading networks to make changes persistent
    if name in present_nics:
        if state is 'absent':
            try:
                delete_nic(module, proxmox, name)
                moduel.exit_json(
                    name=name, msg="Deleted interface {0} from node {1}".format(name,node))
            except Exception as e:
                module.fail_json(
                    name=name, msg="Failed to remove NIC {0} from node {1}: ".format(name, node)
                    + str(e))
        else:
            try:
                update_nic(module, proxmox, nic)
            except Exception as e:
                module.fail_json(
                    msg="Failed to update NIC {0} from node {1}: ".format(name, node)
                    + str(e))
    else:
        if state is 'present':
            try:
                create_nic(module, proxmox, config)
                module.exit_json(name=name, msg="Successfully created NIC {0} on node {1}".format(name,node))
            except Exception as e:
                module.fail_json(
                    msg="Failed to change NIC {0} from node {1}: ".format(name, node)
                    + str(e))
        else:
            module.exit_json(name=name, msg="NIC {0} is not present on node {1}.".format(name,node))

if __name__ == '__main__':
    main()
