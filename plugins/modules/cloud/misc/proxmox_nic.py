#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Lammert Hellinga (@Kogelvis) <lammert@hellinga.it>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: proxmox_nic
short_description: Management of a NIC of a Qemu(KVM) VM in a Proxmox VE cluster.
version_added: 3.1.0
description:
  - Allows you to create/update/delete a NIC on Qemu(KVM) Virtual Machines in a Proxmox VE cluster.
author: "Lammert Hellinga (@Kogelvis) <lammert@hellinga.it>"
options:
  bridge:
    description:
      - Add this interface to the specified bridge device. The Proxmox VE default bridge is called C(vmbr0).
    type: str
  firewall:
    description:
      - Whether this interface should be protected by the firewall.
    type: bool
    default: false
  interface:
    description:
      - Name of the interface, should be C(net[n]) where C(1 ≤ n ≤ 31).
    type: str
    required: true
  link_down:
    description:
      - Whether this interface should be disconnected (like pulling the plug).
    type: bool
    default: false
  mac:
    description:
      - C(XX:XX:XX:XX:XX:XX) should be a unique MAC address. This is automatically generated if not specified.
      - When not specified this module will keep the MAC address the same when changing an existing interface.
    type: str
  model:
    description:
      - The NIC emulator model.
    type: str
    choices: ['e1000', 'e1000-82540em', 'e1000-82544gc', 'e1000-82545em', 'i82551', 'i82557b', 'i82559er', 'ne2k_isa', 'ne2k_pci', 'pcnet',
              'rtl8139', 'virtio', 'vmxnet3']
    default: virtio
  mtu:
    description:
      - Force MTU, for C(virtio) model only, setting will be ignored otherwise.
      - Set to C(1) to use the bridge MTU.
      - Value should be C(1 ≤ n ≤ 65520).
    type: int
  name:
    description:
      - Specifies the VM name. Only used on the configuration web interface.
      - Required only for I(state=present).
    type: str
  queues:
    description:
      - Number of packet queues to be used on the device.
      - Value should be C(0 ≤ n ≤ 16).
    type: int
  rate:
    description:
      - Rate limit in MBps (MegaBytes per second) as floating point number.
    type: float
  state:
    description:
      - Indicates desired state of the NIC.
    type: str
    choices: ['present', 'absent']
    default: present
  tag:
    description:
      - VLAN tag to apply to packets on this interface.
      - Value should be C(1 ≤ n ≤ 4094).
    type: int
  trunks:
    description:
      - List of VLAN trunks to pass through this interface.
    type: list
    elements: int
  vmid:
    description:
      - Specifies the instance ID.
    type: int
extends_documentation_fragment:
  - community.general.proxmox.documentation
'''

EXAMPLES = '''
- name: Create NIC net0 targeting the vm by name
  community.general.proxmox_nic:
    api_user: root@pam
    api_password: secret
    api_host: proxmoxhost
    name: my_vm
    interface: net0
    bridge: vmbr0
    tag: 3

- name: Create NIC net0 targeting the vm by id
  community.general.proxmox_nic:
    api_user: root@pam
    api_password: secret
    api_host: proxmoxhost
    vmid: 103
    interface: net0
    bridge: vmbr0
    mac: "12:34:56:C0:FF:EE"
    firewall: true

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
vmid:
  description: The VM vmid.
  returned: success
  type: int
  sample: 115
msg:
  description: A short message
  returned: always
  type: str
  sample: "Nic net0 unchanged on VM with vmid 103"
'''

try:
    from proxmoxer import ProxmoxAPI
    HAS_PROXMOXER = True
except ImportError:
    HAS_PROXMOXER = False

from ansible.module_utils.basic import AnsibleModule, env_fallback
from ansible_collections.community.general.plugins.module_utils.proxmox import proxmox_auth_argument_spec


def get_vmid(module, proxmox, name):
    try:
        vms = [vm['vmid'] for vm in proxmox.cluster.resources.get(type='vm') if vm.get('name') == name]
    except Exception as e:
        module.fail_json(msg='Error: %s occurred while retrieving VM with name = %s' % (e, name))

    if not vms:
        module.fail_json(msg='No VM found with name: %s' % name)
    elif len(vms) > 1:
        module.fail_json(msg='Multiple VMs found with name: %s, provide vmid instead' % name)

    return vms[0]


def get_vm(proxmox, vmid):
    return [vm for vm in proxmox.cluster.resources.get(type='vm') if vm['vmid'] == int(vmid)]


def update_nic(module, proxmox, vmid, interface, model, **kwargs):
    vm = get_vm(proxmox, vmid)

    try:
        vminfo = proxmox.nodes(vm[0]['node']).qemu(vmid).config.get()
    except Exception as e:
        module.fail_json(msg='Getting information for VM with vmid = %s failed with exception: %s' % (vmid, e))

    if interface in vminfo:
        # Convert the current config to a dictionary
        config = vminfo[interface].split(',')
        config.sort()

        config_current = {}

        for i in config:
            kv = i.split('=')
            try:
                config_current[kv[0]] = kv[1]
            except IndexError:
                config_current[kv[0]] = ''

        # determine the current model nic and mac-address
        models = ['e1000', 'e1000-82540em', 'e1000-82544gc', 'e1000-82545em', 'i82551', 'i82557b',
                  'i82559er', 'ne2k_isa', 'ne2k_pci', 'pcnet', 'rtl8139', 'virtio', 'vmxnet3']
        current_model = set(models) & set(config_current.keys())
        current_model = current_model.pop()
        current_mac = config_current[current_model]

        # build nic config string
        config_provided = "{0}={1}".format(model, current_mac)
    else:
        config_provided = model

    if kwargs['mac']:
        config_provided = "{0}={1}".format(model, kwargs['mac'])

    if kwargs['bridge']:
        config_provided += ",bridge={0}".format(kwargs['bridge'])

    if kwargs['firewall']:
        config_provided += ",firewall=1"

    if kwargs['link_down']:
        config_provided += ',link_down=1'

    if kwargs['mtu']:
        config_provided += ",mtu={0}".format(kwargs['mtu'])
        if model != 'virtio':
            module.warn(
                'Ignoring MTU for nic {0} on VM with vmid {1}, '
                'model should be set to \'virtio\': '.format(interface, vmid))

    if kwargs['queues']:
        config_provided += ",queues={0}".format(kwargs['queues'])

    if kwargs['rate']:
        config_provided += ",rate={0}".format(kwargs['rate'])

    if kwargs['tag']:
        config_provided += ",tag={0}".format(kwargs['tag'])

    if kwargs['trunks']:
        config_provided += ",trunks={0}".format(';'.join(str(x) for x in kwargs['trunks']))

    net = {interface: config_provided}
    vm = get_vm(proxmox, vmid)

    if ((interface not in vminfo) or (vminfo[interface] != config_provided)):
        if not module.check_mode:
            proxmox.nodes(vm[0]['node']).qemu(vmid).config.set(**net)
        return True

    return False


def delete_nic(module, proxmox, vmid, interface):
    vm = get_vm(proxmox, vmid)
    vminfo = proxmox.nodes(vm[0]['node']).qemu(vmid).config.get()

    if interface in vminfo:
        if not module.check_mode:
            proxmox.nodes(vm[0]['node']).qemu(vmid).config.set(vmid=vmid, delete=interface)
        return True

    return False


def main():
    module_args = proxmox_auth_argument_spec()
    nic_args = dict(
        bridge=dict(type='str'),
        firewall=dict(type='bool', default=False),
        interface=dict(type='str', required=True),
        link_down=dict(type='bool', default=False),
        mac=dict(type='str'),
        model=dict(choices=['e1000', 'e1000-82540em', 'e1000-82544gc', 'e1000-82545em',
                            'i82551', 'i82557b', 'i82559er', 'ne2k_isa', 'ne2k_pci', 'pcnet',
                            'rtl8139', 'virtio', 'vmxnet3'], default='virtio'),
        mtu=dict(type='int'),
        name=dict(type='str'),
        queues=dict(type='int'),
        rate=dict(type='float'),
        state=dict(default='present', choices=['present', 'absent']),
        tag=dict(type='int'),
        trunks=dict(type='list', elements='int'),
        vmid=dict(type='int'),
    )
    module_args.update(nic_args)

    module = AnsibleModule(
        argument_spec=module_args,
        required_together=[('api_token_id', 'api_token_secret')],
        required_one_of=[('name', 'vmid'), ('api_password', 'api_token_id')],
        supports_check_mode=True,
    )

    if not HAS_PROXMOXER:
        module.fail_json(msg='proxmoxer required for this module')

    api_host = module.params['api_host']
    api_password = module.params['api_password']
    api_token_id = module.params['api_token_id']
    api_token_secret = module.params['api_token_secret']
    api_user = module.params['api_user']
    interface = module.params['interface']
    model = module.params['model']
    name = module.params['name']
    state = module.params['state']
    validate_certs = module.params['validate_certs']
    vmid = module.params['vmid']

    auth_args = {'user': api_user}
    if not (api_token_id and api_token_secret):
        auth_args['password'] = api_password
    else:
        auth_args['token_name'] = api_token_id
        auth_args['token_value'] = api_token_secret

    try:
        proxmox = ProxmoxAPI(api_host, verify_ssl=validate_certs, **auth_args)
    except Exception as e:
        module.fail_json(msg='authorization on proxmox cluster failed with exception: %s' % e)

    # If vmid is not defined then retrieve its value from the vm name,
    if not vmid:
        vmid = get_vmid(module, proxmox, name)

    # Ensure VM id exists
    if not get_vm(proxmox, vmid):
        module.fail_json(vmid=vmid, msg='VM with vmid = %s does not exist in cluster' % vmid)

    if state == 'present':
        try:
            if update_nic(module, proxmox, vmid, interface, model,
                          bridge=module.params['bridge'],
                          firewall=module.params['firewall'],
                          link_down=module.params['link_down'],
                          mac=module.params['mac'],
                          mtu=module.params['mtu'],
                          queues=module.params['queues'],
                          rate=module.params['rate'],
                          tag=module.params['tag'],
                          trunks=module.params['trunks']):
                module.exit_json(changed=True, vmid=vmid, msg="Nic {0} updated on VM with vmid {1}".format(interface, vmid))
            else:
                module.exit_json(vmid=vmid, msg="Nic {0} unchanged on VM with vmid {1}".format(interface, vmid))
        except Exception as e:
            module.fail_json(vmid=vmid, msg='Unable to change nic {0} on VM with vmid {1}: '.format(interface, vmid) + str(e))

    elif state == 'absent':
        try:
            if delete_nic(module, proxmox, vmid, interface):
                module.exit_json(changed=True, vmid=vmid, msg="Nic {0} deleted on VM with vmid {1}".format(interface, vmid))
            else:
                module.exit_json(vmid=vmid, msg="Nic {0} does not exist on VM with vmid {1}".format(interface, vmid))
        except Exception as e:
            module.fail_json(vmid=vmid, msg='Unable to delete nic {0} on VM with vmid {1}: '.format(interface, vmid) + str(e))


if __name__ == '__main__':
    main()
