#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2024, Alexander Bakanovskii <skottttt228@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
---
module: one_vnet
short_description: Manages OpenNebula virtual networks
version_added: 9.4.0
author: "Alexander Bakanovskii (@abakanovskii)"
requirements:
  - pyone
description:
  - Manages virtual networks in OpenNebula.
attributes:
  check_mode:
    support: partial
    details:
      - Note that check mode always returns C(changed=true) for existing networks, even if the network would not actually change.
  diff_mode:
    support: none
options:
  id:
    description:
      - A O(id) of the network you would like to manage.
      - If not set then a new network will be created with the given O(name).
    type: int
  name:
    description:
      - A O(name) of the network you would like to manage.  If a network with
        the given name does not exist it will be created, otherwise it will be
        managed by this module.
    type: str
  template:
    description:
      - A string containing the network template contents.
    type: str
  state:
    description:
      - V(present) - state that is used to manage the network.
      - V(absent) - delete the network.
    choices: ["present", "absent"]
    default: present
    type: str

extends_documentation_fragment:
  - community.general.opennebula
  - community.general.attributes
'''

EXAMPLES = '''
- name: Make sure the network is present by ID
  community.general.one_vnet:
    id: 0
    state: present
  register: result

- name: Make sure the network is present by name
  community.general.one_vnet:
    name: opennebula-bridge
    state: present
  register: result

- name: Create a new or update an existing network
  community.general.one_vnet:
    name: bridge-network
    template: |
      VN_MAD  = "bridge"
      BRIDGE  = "br0"
      BRIDGE_TYPE  = "linux"
      AR=[
        TYPE  = "IP4",
        IP    = 192.0.2.50,
        SIZE  = "20"
      ]
      DNS     = 192.0.2.1
      GATEWAY = 192.0.2.1

- name: Delete the network by ID
  community.general.one_vnet:
    id: 0
    state: absent
'''

RETURN = '''
id:
    description: The network id.
    type: int
    returned: when O(state=present)
    sample: 153
name:
    description: The network name.
    type: str
    returned: when O(state=present)
    sample: app1
template:
    description: The parsed network template.
    type: dict
    returned: when O(state=present)
    sample:
      BRIDGE: onebr.1000
      BRIDGE_TYPE: linux
      DESCRIPTION: sampletext
      PHYDEV: eth0
      SECURITY_GROUPS: 0
      VLAN_ID: 1000
      VN_MAD: 802.1Q
user_id:
    description: The network's user name.
    type: int
    returned: when O(state=present)
    sample: 1
user_name:
    description: The network's user id.
    type: str
    returned: when O(state=present)
    sample: oneadmin
group_id:
    description: The network's group id.
    type: int
    returned: when O(state=present)
    sample: 1
group_name:
    description: The network's group name.
    type: str
    returned: when O(state=present)
    sample: one-users
owner_id:
    description: The network's owner id.
    type: int
    returned: when O(state=present)
    sample: 143
owner_name:
    description: The network's owner name.
    type: str
    returned: when O(state=present)
    sample: ansible-test
permissions:
    description: The network's permissions.
    type: dict
    returned: when O(state=present)
    contains:
      owner_u:
        description: The network's owner USAGE permissions.
        type: str
        sample: 1
      owner_m:
        description: The network's owner MANAGE permissions.
        type: str
        sample: 0
      owner_a:
        description: The network's owner ADMIN permissions.
        type: str
        sample: 0
      group_u:
        description: The network's group USAGE permissions.
        type: str
        sample: 0
      group_m:
        description: The network's group MANAGE permissions.
        type: str
        sample: 0
      group_a:
        description: The network's group ADMIN permissions.
        type: str
        sample: 0
      other_u:
        description: The network's other users USAGE permissions.
        type: str
        sample: 0
      other_m:
        description: The network's other users MANAGE permissions.
        type: str
        sample: 0
      other_a:
        description: The network's other users ADMIN permissions
        type: str
        sample: 0
    sample:
      owner_u: 1
      owner_m: 0
      owner_a: 0
      group_u: 0
      group_m: 0
      group_a: 0
      other_u: 0
      other_m: 0
      other_a: 0
clusters:
    description: The network's clusters.
    type: list
    returned: when O(state=present)
    sample: [0, 100]
bridge:
    description: The network's bridge interface.
    type: str
    returned: when O(state=present)
    sample: br0
bridge_type:
    description: The network's bridge type.
    type: str
    returned: when O(state=present)
    sample: linux
parent_network_id:
    description: The network's parent network id.
    type: int
    returned: when O(state=present)
    sample: 1
vm_mad:
    description: The network's VM_MAD.
    type: str
    returned: when O(state=present)
    sample: bridge
phydev:
    description: The network's physical device (NIC).
    type: str
    returned: when O(state=present)
    sample: eth0
vlan_id:
    description: The network's VLAN tag.
    type: int
    returned: when O(state=present)
    sample: 1000
outer_vlan_id:
    description: The network's outer VLAN tag.
    type: int
    returned: when O(state=present)
    sample: 1000
vrouters:
    description: The network's list of virtual routers IDs.
    type: list
    returned: when O(state=present)
    sample: [0, 1]
ar_pool:
    description: The network's list of ar_pool.
    type: list
    returned: when O(state=present)
    sample:
      - ar_id: 0
        ip: 192.0.2.1
        mac: 6c:1e:46:01:cd:d1
        size: 20
        type: IP4
      - ar_id: 1
        allocated: 0
        ip: 198.51.100.1
        mac: 5d:9b:c0:9e:f6:e5
        size: 20
        type: IP4
'''


from ansible_collections.community.general.plugins.module_utils.opennebula import OpenNebulaModule


class NetworksModule(OpenNebulaModule):

    def __init__(self):
        argument_spec = dict(
            id=dict(type='int', required=False),
            name=dict(type='str', required=False),
            state=dict(type='str', choices=['present', 'absent'], default='present'),
            template=dict(type='str', required=False),
        )

        mutually_exclusive = [
            ['id', 'name']
        ]

        required_one_of = [('id', 'name')]

        required_if = [
            ['state', 'present', ['template']]
        ]

        OpenNebulaModule.__init__(self,
                                  argument_spec,
                                  supports_check_mode=True,
                                  mutually_exclusive=mutually_exclusive,
                                  required_one_of=required_one_of,
                                  required_if=required_if)

    def run(self, one, module, result):
        params = module.params
        id = params.get('id')
        name = params.get('name')
        desired_state = params.get('state')
        template_data = params.get('template')

        self.result = {}

        template = self.get_template_instance(id, name)
        needs_creation = False
        if not template and desired_state != 'absent':
            if id:
                module.fail_json(msg="There is no template with id=" + str(id))
            else:
                needs_creation = True

        if desired_state == 'absent':
            self.result = self.delete_template(template)
        else:
            if needs_creation:
                self.result = self.create_template(name, template_data)
            else:
                self.result = self.update_template(template, template_data)

        self.exit()

    def get_template(self, predicate):
        # -2 means "Resources belonging to all users"
        # the other two parameters are used for pagination, -1 for both essentially means "return all"
        pool = self.one.vnpool.info(-2, -1, -1)

        for template in pool.VMTEMPLATE:
            if predicate(template):
                return template

        return None

    def get_template_by_id(self, template_id):
        return self.get_template(lambda template: (template.ID == template_id))

    def get_template_by_name(self, name):
        return self.get_template(lambda template: (template.NAME == name))

    def get_template_instance(self, requested_id, requested_name):
        if requested_id:
            return self.get_template_by_id(requested_id)
        else:
            return self.get_template_by_name(requested_name)

    def get_networks_ar_pool(self, template):
        ar_pool = []
        for ar in template.AR_POOL:
            ar_pool.append({
                # These params will always be present
                'ar_id': ar['AR_ID'],
                'mac': ar['MAC'],
                'size': ar['SIZE'],
                'type': ar['TYPE'],
                # These are optional so firstly check for presence
                # and if not present set value to Null
                'allocated': getattr(ar, 'ALLOCATED', 'Null'),
                'ip': getattr(ar, 'IP', 'Null'),
                'global_prefix': getattr(ar, 'GLOBAL_PREFIX', 'Null'),
                'parent_network_ar_id': getattr(ar, 'PARENT_NETWORK_AR_ID', 'Null'),
                'ula_prefix': getattr(ar, 'ULA_PREFIX', 'Null'),
                'vn_mad': getattr(ar, 'VN_MAD', 'Null'),
            })
        return ar_pool

    def get_template_info(self, template):
        info = {
            'id': template.ID,
            'name': template.NAME,
            'template': template.TEMPLATE,
            'user_name': template.UNAME,
            'user_id': template.UID,
            'group_name': template.GNAME,
            'group_id': template.GID,
            'permissions': {
                'owner_u': template.PERMISSIONS.OWNER_U,
                'owner_m': template.PERMISSIONS.OWNER_M,
                'owner_a': template.PERMISSIONS.OWNER_A,
                'group_u': template.PERMISSIONS.GROUP_U,
                'group_m': template.PERMISSIONS.GROUP_M,
                'group_a': template.PERMISSIONS.GROUP_A,
                'other_u': template.PERMISSIONS.OTHER_U,
                'other_m': template.PERMISSIONS.OTHER_M,
                'other_a': template.PERMISSIONS.OTHER_A
            },
            'clusters': template.CLUSTERS.ID,
            'bridge': template.BRIDGE,
            'bride_type': template.BRIDGE_TYPE,
            'parent_network_id': template.PARENT_NETWORK_ID,
            'vm_mad': template.VM_MAD,
            'phydev': template.PHYDEV,
            'vlan_id': template.VLAN_ID,
            'outer_vlan_id': template.OUTER_VLAN_ID,
            'used_leases': template.USED_LEASES,
            'vrouters': template.VROUTERS.ID,
            'ar_pool': self.get_networks_ar_pool(template)
        }

        return info

    def create_template(self, name, template_data):
        if not self.module.check_mode:
            self.one.vn.allocate("NAME = \"" + name + "\"\n" + template_data)

        result = self.get_template_info(self.get_template_by_name(name))
        result['changed'] = True

        return result

    def update_template(self, template, template_data):
        if not self.module.check_mode:
            # 0 = replace the whole template
            self.one.vn.update(template.ID, template_data, 0)

        result = self.get_template_info(self.get_template_by_id(template.ID))
        if self.module.check_mode:
            # Unfortunately it is not easy to detect if the template would have changed, therefore always report a change here.
            result['changed'] = True
        else:
            # if the previous parsed template data is not equal to the updated one, this has changed
            result['changed'] = template.TEMPLATE != result['template']

        return result

    def delete_template(self, template):
        if not template:
            return {'changed': False}

        if not self.module.check_mode:
            self.one.vn.delete(template.ID)

        return {'changed': True}


def main():
    NetworksModule().run_module()


if __name__ == '__main__':
    main()
