# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Andreas Botzner (@botzner_andreas) <andreas at botzner dot com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible_collections.community.general.plugins.module_utils.proxmox import ProxmoxAnsible


def proxmox_interface_argument_spec():
    return dict(
        name=dict(type='str',
                  required=True
                  ),
        type=dict(type='str',
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
                       default=True
                       ),
        bond_primary=dict(type='str'),
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
        bridge_ports=dict(type='str'),
        bridge_vlan_ports=dict(type='bool'),
        cidr=dict(type='str'),
        cidr6=dict(type='str'),
        comments=dict(type='str'),
        comments6=dict(type='str'),
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


def proxmox_map_interface_args(params):
    ret = {}
    if params['name'] is not None:
        ret['iface'] = params['name']
    if params['type'] is not None:
        ret['type'] = params['type']
    if params['address'] is not None:
        ret['address'] = params['address']
    if params['address6'] is not None:
        ret['address6'] = params['address6']
    if params['autostart'] is not None:
        ret['autostart'] = '1' if params['autostart'] else '0'
    if params['bond_primary'] is not None:
        ret['bond-primary'] = params['bond_primary']
    if params['bond_mode'] is not None:
        ret['bond_mode'] = params['bond_mode']
    if params['bond_xmit_hash_policy'] is not None:
        ret['bond_xmit_hash_policy'] = params['bond_xmit_hash_policy']
    if params['bridge_ports'] is not None:
        ret['bridge_ports'] = params['bridge_ports']
    if params['bridge_vlan_ports'] is not None:
        ret['bridge_vlan_ports'] = 1 if params['bridge_vlan_ports'] else 0
    if params['cidr'] is not None:
        ret['cidr'] = params['cidr']
    if params['cidr6'] is not None:
        ret['cidr6'] = params['cidr6']
    if params['gateway'] is not None:
        ret['gateway'] = params['gateway']
    if params['gateway6'] is not None:
        ret['gateway6'] = params['gateway6']
    if params['comments'] is not None:
        ret['comments'] = params['comments']
    if params['comments6'] is not None:
        ret['comments6'] = params['comments6']
    if params['mtu'] is not None:
        if int(params['mtu']) <= 65520 and int(params['mtu']) >= 1280:
            ret['mtu'] = params['mtu']
        else:
            raise ValueError(
                'MTU has to be be between 1280 and 65520 but was {0}'.format(params['mtu']))
    if params['netmask'] is not None:
        ret['netmask'] = params['netmask']
    if params['netmask6'] is not None:
        if int(params['netmask6']) >= 0 and int(params['netmask6']) <= 128:
            ret['netmask6'] = params['netmask6']
        else:
            raise ValueError(
                'netmaks6 has to be between 0 and 128 but was {0}'.format(params['netmaks6']))
    if params['ovs_bonds'] is not None:
        ret['ovs_bonds'] = params['ovs_bonds']
    if params['ovs_options'] is not None:
        ret['ovs_options'] = params['ovs_options']
    if params['ovs_bridge'] is not None:
        ret['ovs_bridge'] = params['ovs_bridge']
    if params['ovs_ports'] is not None:
        ret['ovs_ports'] = params['ovs_ports']
    if params['ovs_tag'] is not None:
        if int(params['ovs_tag']) >= 1 and int(params['ovs_tag']) <= 4094:
            ret['ovs_tag'] = params['ovs_tag']
        else:
            raise ValueError(
                'ovs_tag has to be between 1 and 4094 but was {0}'.format(params['ovs_tag']))
    if params['slaves'] is not None:
        ret['slaves'] = params['slaves']
    if params['vlan_id'] is not None:
        if int(params['vlan_id']) >= 1 and int(params['vlan_id']) <= 4094:
            ret['vlan-id'] = params['vlan_id']
        else:
            raise Exception('vlan_id has to be between 1 and 4094 but was {0}'.format(
                params['vlan_id']))
    if params['vlan_raw_device'] is not None:
        ret['vlan-raw-device'] = params['vlan_raw_device']
    return ret


def get_nics(proxmox):
    """ Returns list of all interfaces on Proxmox node"""
    nics = []
    node = proxmox.module.params['node']
    try:
        nics = proxmox.proxmox_api.nodes(node).network.get()
    except Exception as e:
        proxmox.module.fail_json(
            msg='Getting information from Node {0} failed with exception: {1}'.format(node, str(e)))
    return nics


def get_nic(proxmox_api, node, name):
    ret = {}
    try:
        ret = proxmox_api.nodes(node).network.get(name)
    except Exception as e:
        raise e
    return ret


def create_nic(proxmox_api, node, config):
    try:
        proxmox_api.nodes(node).network.post(**config)
    except Exception as e:
        raise e


def delete_nic(proxmox_api, node, name):
    try:
        proxmox_api.nodes(node).network.delete(name)
    except Exception as e:
        raise e


"""
Updates an interface with specified configuration
"""


def update_nic(proxmox_api, node, name, config):
    try:
        proxmox_api.nodes(node).network(name).put(**config)
    except Exception as e:
        raise e


"""
Starts task to reload interfaces on node.
Returns UPID string if successful
"""


def reload_interfaces(proxmox_api, node):
    try:
        ret = proxmox_api.nodes(node).network.put()
        return ret
    except Exception as e:
        raise e


def rollback_interfaces(proxmox_api, node):
    try:
        proxmox_api.nodes(node).network.delete()
    except Exception as e:
        raise e


"""
Tries to get the status of task on a Proxmox node.
"""


def get_process_status(proxmox_api, node, upid):
    try:
        ret = proxmox_api.nodes(node).tasks(upid).status().get()
        return ret
    except Exception as e:
        raise e


def check_doublicates(module):
    config = module.params['config']
    ifaces = list(nic['name'] for nic in config)
    ifaces_set = set()
    for iface in ifaces:
        if iface in ifaces_set:
            module.fail_json(
                msg="Interface {0} can only be present once in list".format(iface))
        else:
            ifaces_set.add(iface)
