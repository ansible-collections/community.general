#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Andreas Botzner (@botzner_andreas) <andreas at botzner dot com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: proxmox_interfaces
short_description: Management network interfaces on a Proxmox node.
version_added: 3.6.0
description:
  - Allows you to create/update/delete network interfaces of a Proxmox node.
  - The module tries to understand what interface configurations get updated
    and applies that changes. Interfaces that already have the a the specified
    configuration, are not changed.
author: "Andreas Botzner (@paginabianca) <andreas at botzner dot com>"
options:
  config:
    description: Interface configuration.
    required: true
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
          - Network interface type.
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
          - Bonding mode of the interface.
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
          - Selects the transmit hash policy to use for slave selection in balance-xor and 802.3ad.
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
          - Enable bridge VLAN support.
        type: bool
      cidr:
        description:
          - IPv4 CIDR of the interface.
        type: str
      cidr6:
        description:
          - IPv6 CIDR of the interface.
        type: str
      comments:
        description:
          - Comments added to the int
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
          - The MTU.
          - Value should be C(1280 ≤ n ≤ 65520).
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
          - Specify a VLAN tag (used by OVSPort, OVSIntPort, OVSBond).
          - Value should be C(1 ≤ n ≤ 4094).
        type: int
      slaves:
        description:
          - Specify a VLAN tag (used by OVSPort, OVSIntPort, OVSBond).
        type: str
      vlan_id:
        description:
          - vlan-id for a custom named VLAN interface (ifupdown2 only).
        type: int
      vlan_raw_device:
        description:
          - Specify the raw interface for the VLAN interface.
        type: str
      state:
        description:
          - Indicates desired state of the NIC.
        type: str
        choices: ['present', 'absent']
        default: present
  node:
    description:
      - Name of the cluster node.
    type: str
    required: true
  state:
    description:
      - The state of the configuration after module completion.
    type: str
    default: present
    choices:
      - present
      - reloaded
  apply:
    description:
      - Reload interfaces and make configuration persistent after going
        though list of interfaces.
    type: bool
    default: true
  ignore_errors:
    description:
      - Ignore Errors when creating multiple interfaces.
    type: bool
    default: false
  revert_on_error:
    description:
      - Try to revert to previous configuration upon encountering errors.
    type: bool
    default: false
extends_documentation_fragment:
  - community.general.proxmox.documentation
'''

EXAMPLES = '''
- name: Change a list of interfaces
  community.general.proxmox_interfaces:
    api_user: root@pam
    api_password: secret
    api_host: proxmoxhost
    node: node01
    config:
      - name: vmrb135
        type: bridge
        cidr: 10.189.5.37/24
        mtu: 5555
      - name: vmrb56
        type: bridge
        cidr: 192.168.5.4/24
        comments: 'This is a new VM bridge with the host inside'
    state: present
    apply: true

- name: Delete a list of interfaces from node01 and try to revert on error
  community.general.proxmox_interfaces:
    api_user: root@pam
    api_password: secret
    api_host: proxmoxhost
    node: node01
    config:
      - name: vmbr34
        state: absent
      - name: vmbr48
        state: absent
    apply: true
    revert_on_error: true
'''

RETURN = '''
diff:
  description: List of changes that where applied to an individual interface.
  returned: always
  type: dict
  elements: dict
  sample:
    vmrb12:
      cidr:
        before: 10.0.0.1/24
        after: 192.168.0.1/24
      type:
        before: unknown
        after: bridge
    vmbr56:
      cidr:
        before:
        after: 10.0.0.1/254
      type:
        before:
        after: bridge

msg:
  description: A list of messages.
  returned: always
  type: list
  elements: string
  sample:
    - Successfully updated interface: vmbr8
    - Successfully updated interface: vmbr37
    - Successfully reloaded and applied interface changes on node node01

upid:
  description: UPID of the svreload:networking task
  returned: when changed and reload_interfaces is enabled
  type: str
  sample: 'UPID:node01:00003098:16036ACE:6216F174:srvreload:networking:root@pam:'
errors:
  description: Errors that occurred and where ignored
  returned: when failed
  type: list
  sample:
    - list of errors
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
    get_nics, delete_nic, create_nic, reload_interfaces, rollback_interfaces,
    update_nic, proxmox_map_interface_args, proxmox_interface_argument_spec, check_doublicates,
    get_config_diff)
from ansible.module_utils.basic import AnsibleModule


def main():
    nic_args = proxmox_interface_argument_spec()
    module_args = proxmox_auth_argument_spec()
    network_args = dict(
        config=dict(type='list', elements='dict',
                    required=True, options=nic_args),
        node=dict(type='str', required=True),
        ignore_errors=dict(type='bool', default=False),
        apply=dict(type='bool', default=True),
        revert_on_error=dict(type='bool', default=False),
        state=dict(type='str', choices=[
                   'present', 'reloaded'], default='present')
    )
    module_args.update(network_args)

    module = AnsibleModule(
        argument_spec=module_args,
        required_together=[('api_token_id', 'api_token_secret'),
                           ('api_user', 'api_password')],
        required_one_of=[('api_password', 'api_token_id')],
        required_if=[('state', 'present', ('config',))],
        supports_check_mode=True,
    )

    proxmox = ProxmoxAnsible(module)

    state = module.params['state']
    node = module.params['node']
    config = module.params['config']
    ignore_errors = module.params['ignore_errors']
    revert_on_error = module.params['revert_on_error']
    apply = module.params['apply']

    result = {'changed': False}
    msg = []
    errors = []
    nics = get_nics(proxmox)

    if state == 'reloaded':
        try:
            upid = reload_interfaces(proxmox.proxmox_api, node)
            result['upid'] = upid
            result['msg'] = 'Successfully reloaded and applied interface changes on node {0}'.format(
                node)
            module.exit_json(**result)
        except Exception as e:
            result['errors'] = 'Failed to reload interfaces on node: {0} with error {1}'.format(
                node, str(e))
            module.fail_json(**result)

    check_doublicates(module)
    present_nics = {nic['iface'] for nic in nics}
    diff = get_config_diff(nics, config)
    config = {nic['name']: nic for nic in config}

    if diff is None:
        result['msg'] = 'No configuration changes.'
        module.exit_json(**result)

    result['diff'] = diff
    if module.check_mode:
        module.exit_json(**result)

    for key in config:
        if key not in diff:
            msg.append('Interface {0} did not change'.format(key))
            continue
        nic = config[key]
        name = nic['name']
        try:
            interface_args = proxmox_map_interface_args(nic)
        except ValueError as e:
            module.fail_json(str(e))
        if name in present_nics:
            if nic['state'] == 'absent':
                try:
                    delete_nic(proxmox.proxmox_api, node, name)
                    msg.append(
                        'Successfully deleted interface: {0}'.format(name))
                    result['changed'] = True
                except Exception as e:
                    errors.append(
                        'Failed to delete interface: {0} with exception: {1}'.format(name, str(e)))
                    if not ignore_errors:
                        break
            else:
                try:
                    update_nic(proxmox.proxmox_api, node, name, interface_args)
                    msg.append(
                        'Successfully updated interface {0}'.format(name))
                    result['changed'] = True
                except Exception as e:
                    errors.append(
                        'Failed to update interface: {0} with exception: {1}'.format(name, str(e)))
                    if not ignore_errors:
                        break
        else:
            if nic['state'] == 'present':
                try:
                    create_nic(proxmox.proxmox_api, node, interface_args)
                    msg.append(
                        'Successfully created interface {0}'.format(name))
                    result['changed'] = True
                except Exception as e:
                    errors.append('Failed to create interface: {0} with exception: {1}'.format(
                        name, str(e)))
                    if not ignore_errors:
                        break
            else:
                msg.append('Interface {0} is not present'.format(name))
    result['errors'] = errors
    result['msg'] = msg
    if not errors or ignore_errors:
        if not apply:
            module.exit_json(**result)
        else:
            try:
                upid = reload_interfaces(proxmox.proxmox_api, node)
                result['upid'] = upid
                result['msg'].append(
                    'Successfully reloaded and applied interface changes on node {0}'.format(node))
                module.exit_json(**result)
            except Exception as e:
                result['errors'].append(
                    'Failed to reload interfaces on node: {0} with error {1}'.format(node, str(e)))

    elif revert_on_error:
        try:
            rollback_interfaces(proxmox.proxmox_api, node)
            result['msg'].append(
                'Successfully rolled back uncommitted changes on node {0}'.format(node))
            result['changed'] = False
        except Exception as e:
            result['errors'].append(
                'Failed to roll back configuration on node {0} with error: {1}'.format(node, str(e)))
        finally:
            module.fail_json(**result)
    else:
        module.fail_json(**result)


if __name__ == '__main__':
    main()
