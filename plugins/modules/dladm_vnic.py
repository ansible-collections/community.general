#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2015, Adam Števko <adam.stevko@gmail.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: dladm_vnic
short_description: Manage VNICs on Solaris/illumos systems.
description:
    - Create or delete VNICs on Solaris/illumos systems.
author: Adam Števko (@xen0l)
options:
    name:
        description:
            - VNIC name.
        required: true
    link:
        description:
            - VNIC underlying link name.
        required: true
    temporary:
        description:
            - Specifies that the VNIC is temporary. Temporary VNICs
              do not persist across reboots.
        required: false
        default: false
        type: bool
    mac:
        description:
            - Sets the VNIC's MAC address. Must be valid unicast MAC address.
        required: false
        default: false
        aliases: [ "macaddr" ]
    vlan:
        description:
            - Enable VLAN tagging for this VNIC. The VLAN tag will have id
              I(vlan).
        required: false
        default: false
        aliases: [ "vlan_id" ]
    state:
        description:
            - Create or delete Solaris/illumos VNIC.
        required: false
        default: "present"
        choices: [ "present", "absent" ]
'''

EXAMPLES = '''
# Create 'vnic0' VNIC over 'bnx0' link
- dladm_vnic:
    name: vnic0
    link: bnx0
    state: present

# Create VNIC with specified MAC and VLAN tag over 'aggr0'
- dladm_vnic:
    name: vnic1
    link: aggr0
    mac: '00:00:5E:00:53:23'
    vlan: 4

# Remove 'vnic0' VNIC
- dladm_vnic:
    name: vnic0
    link: bnx0
    state: absent
'''

RETURN = '''
name:
    description: VNIC name
    returned: always
    type: str
    sample: "vnic0"
link:
    description: VNIC underlying link name
    returned: always
    type: str
    sample: "igb0"
state:
    description: state of the target
    returned: always
    type: str
    sample: "present"
temporary:
    description: VNIC's persistence
    returned: always
    type: bool
    sample: "True"
mac:
    description: MAC address to use for VNIC
    returned: if mac is specified
    type: str
    sample: "00:00:5E:00:53:42"
vlan:
    description: VLAN to use for VNIC
    returned: success
    type: int
    sample: 42
'''

import re

from ansible.module_utils.basic import AnsibleModule


class VNIC(object):

    UNICAST_MAC_REGEX = r'^[a-f0-9][2-9a-f0]:([a-f0-9]{2}:){4}[a-f0-9]{2}$'

    def __init__(self, module):
        self.module = module

        self.name = module.params['name']
        self.link = module.params['link']
        self.mac = module.params['mac']
        self.vlan = module.params['vlan']
        self.temporary = module.params['temporary']
        self.state = module.params['state']

    def vnic_exists(self):
        cmd = [self.module.get_bin_path('dladm', True)]

        cmd.append('show-vnic')
        cmd.append(self.name)

        (rc, _, _) = self.module.run_command(cmd)

        if rc == 0:
            return True
        else:
            return False

    def create_vnic(self):
        cmd = [self.module.get_bin_path('dladm', True)]

        cmd.append('create-vnic')

        if self.temporary:
            cmd.append('-t')

        if self.mac:
            cmd.append('-m')
            cmd.append(self.mac)

        if self.vlan:
            cmd.append('-v')
            cmd.append(self.vlan)

        cmd.append('-l')
        cmd.append(self.link)
        cmd.append(self.name)

        return self.module.run_command(cmd)

    def delete_vnic(self):
        cmd = [self.module.get_bin_path('dladm', True)]

        cmd.append('delete-vnic')

        if self.temporary:
            cmd.append('-t')
        cmd.append(self.name)

        return self.module.run_command(cmd)

    def is_valid_unicast_mac(self):

        mac_re = re.match(self.UNICAST_MAC_REGEX, self.mac)

        return mac_re is None

    def is_valid_vlan_id(self):

        return 0 <= self.vlan <= 4095


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            link=dict(required=True),
            mac=dict(default=None, aliases=['macaddr']),
            vlan=dict(default=None, aliases=['vlan_id']),
            temporary=dict(default=False, type='bool'),
            state=dict(default='present', choices=['absent', 'present']),
        ),
        supports_check_mode=True
    )

    vnic = VNIC(module)

    rc = None
    out = ''
    err = ''
    result = {}
    result['name'] = vnic.name
    result['link'] = vnic.link
    result['state'] = vnic.state
    result['temporary'] = vnic.temporary

    if vnic.mac is not None:
        if vnic.is_valid_unicast_mac():
            module.fail_json(msg='Invalid unicast MAC address',
                             mac=vnic.mac,
                             name=vnic.name,
                             state=vnic.state,
                             link=vnic.link,
                             vlan=vnic.vlan)
        result['mac'] = vnic.mac

    if vnic.vlan is not None:
        if vnic.is_valid_vlan_id():
            module.fail_json(msg='Invalid VLAN tag',
                             mac=vnic.mac,
                             name=vnic.name,
                             state=vnic.state,
                             link=vnic.link,
                             vlan=vnic.vlan)
        result['vlan'] = vnic.vlan

    if vnic.state == 'absent':
        if vnic.vnic_exists():
            if module.check_mode:
                module.exit_json(changed=True)
            (rc, out, err) = vnic.delete_vnic()
            if rc != 0:
                module.fail_json(name=vnic.name, msg=err, rc=rc)
    elif vnic.state == 'present':
        if not vnic.vnic_exists():
            if module.check_mode:
                module.exit_json(changed=True)
            (rc, out, err) = vnic.create_vnic()

        if rc is not None and rc != 0:
            module.fail_json(name=vnic.name, msg=err, rc=rc)

    if rc is None:
        result['changed'] = False
    else:
        result['changed'] = True

    if out:
        result['stdout'] = out
    if err:
        result['stderr'] = err

    module.exit_json(**result)


if __name__ == '__main__':
    main()
