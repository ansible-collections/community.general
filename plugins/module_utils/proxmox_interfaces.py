# -*- coding: utf-8 -*-
#
# Copyright: (c) 2020, Andreas Botzner <andreas at botzner.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.proxmox import ProxmoxAnsible
import traceback

PROXMOXER_IMP_ERR = None
try:
    from proxmoxer import ProxmoxAPI
    HAS_PROXMOXER = True
except ImportError:
    HAS_PROXMOXER = False
    PROXMOXER_IMP_ERR = traceback.format_exc()


def proxmox_interface_argument_spec():
    return dict(
        name=dict(type='str',
                  required=True
                  ),
        type=dict(type='str',
                  required=True,
                  choices=[
                      'bridge',
                      'bond',
                      'eth',
                      'alias',
                      'vlan',
                      'OVSBridge',
                      'OVSBond',
                      'OVSPort',
                      'OVSIntPort',
                      'unknown'
                  ],
                  default='bridge'
                  ),
        address=dict(type='str'),
        address6=dict(type='str'),
        autostart=dict(type='bool',
                       default=False
                       ),
        bond_mode=dict(type='str',
                       choices=[
                           'balance-rr',
                           'active-backup',
                           'balance-xor',
                           'broadcast',
                           '802.3ad',
                           'balance-tlb',
                           'balance-alb',
                           'balance-slb',
                           'lacp-balance-slb',
                           'lacp-balance-tcp'
                       ]
                       ),
        bond_xmit_hash_policy=dict(type='str',
                                   choices=[
                                       'layer2',
                                       'layer2+3',
                                       'layer3+4'
                                   ]
                                   ),
        bridge_vlan_ports=dict(type='bool'),
        cidr=dict(type='str'),
        cidr6=dict(type='str'),
        gateway=dict(type='str'),
        gateway6=dict(type='str'),
        mtu=dict(type='int'),
        netmask=dict(type='str'),
        netmask6=dict(type='int'),
        ovs_bonds=dict(type='str'),
        ovs_bridge=dict(type='str'),
        ovs_options=dict(type='str'),
        ovs_ports=dict(type='str'),
        ovs_tag=dict(type='int'),
        slaves=dict(type='str'),
        vlan_id=dict(type='int'),
        vlan_raw_device=dict(type='str'),
        state=dict(type='str',
                   choices=[
                       'absent',
                       'present'
                   ],
                   default='present'
                   )
    )


def proxmox_map_interface_args(module: AnsibleModule):
    ret = {}
    ret['iface'] = module.params['name']
    ret['type'] = module.params['type']
    ret['address'] = module.params['address']
    ret['address6'] = module.params['address6']
    ret['bond-primary'] = module.params['bond_mode']
    ret['bond_mode'] = module.params['bond_mode']
    ret['bond_xmit_hash_policy'] = module.params['bond_xmit_hash_policy']
    ret['bridge_ports'] = module.params['bridge_ports']
    ret['cidr'] = module.params['cidr']
    ret['cidr6'] = module.params['cidr6']
    ret['gateway'] = module.params['gateway']
    ret['comments'] = module.params['comments']
    ret['comments6'] = module.params['comments6']
    ret['gateway6'] = module.params['gateway6']
    ret['netmask'] = module.params['netmask']
    ret['ovs_bonds'] = module.params['ovs_bonds']
    ret['ovs_bridge'] = module.params['ovs_bridge']
    ret['ovs_options'] = module.params['ovs_options']
    ret['ovs_ports'] = module.params['ovs_ports']
    ret['slaves'] = module.params['slaves']
    ret['vlan-raw-device'] = module.params['vlan_raw_device']
    ret['autostart'] = 1 if module.params['autostart'] else 0
    ret['bridge_vlan_ports'] = 1 if module.params['bridge_vlan_ports'] else 0
    if module.params['mtu'] <= 65520 and module.params['mtu'] >= 1280:
        ret['mtu'] = module.params['mtu']
    else:
        module.fail_json(msg="MTU has to be between 1280 and 65520")
    if module.params['netmask6'] >= 0 and module.params['netmask6'] <= 128:
        ret['netmask6'] = module.params['netmask6']
    else:
        module.fail_json(msg='netmask6 has to be between 0 and 128')
    if module.params['ovs_tag'] >= 1 and module.params['ovs_tag'] <= 4094:
        ret['ovs_tag'] = module.params['ovs_tag']
    else:
        module.fail_json(msg='ovs_tag has to be between 1 and 4094')
    if module.params['vlan_id'] >= 1 and module.params['vlan_id'] <= 4094:
        ret['vlan-id'] = module.params['vlan_id']
    else:
        module.fail_json(msg='vlan_id has to be between 1 and 4094')
    return ret


def get_nics(proxmox: ProxmoxAnsible):
    """ Returns list of all interfaces on Proxmox node"""
    nics = []
    node = proxmox.module.params['node']
    try:
        nics = proxmox.proxmox_api.nodes(node).network.get()
    except Exception as e:
        proxmox.module.fail_json(
            msg='Getting information from Node {0} failed with exception: {1}'.format(node, str(e)))
    return nics


def get_nic(proxmox_api: ProxmoxAPI, node: str, name: str):
    ret = {}
    try:
        ret = proxmox_api.nodes(node).network.get(name)
    except Exception as e:
        raise e
    return ret


def create_nic(proxmox_api: ProxmoxAPI, node: str, config: dict):
    try:
        proxmox_api.nodes(node).network.post(config)
    except Exception as e:
        raise e


def delete_nic(proxmox_api: ProxmoxAPI, node: str, name: str):
    try:
        proxmox_api.nodes(node).network.delete(name)
    except Exception as e:
        raise e


def update_nic(proxmox_api: ProxmoxAPI, node: str, name: str, config: dict):
    try:
        proxmox_api.nodes(node).network(name).post(config)
    except Exception as e:
        raise e


def reload_interfaces(proxmox_api: ProxmoxAPI, node: str):
    try:
        proxmox_api.nodes(node).network.put()
    except Exception as e:
        raise e


def rollback_interfaces(proxmox_api: ProxmoxAPI, node: str):
    try:
        proxmox_api.nodes(node).network.delete()
    except Exception as e:
        raise e
