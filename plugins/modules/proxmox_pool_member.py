#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, Sergei Antipov (UnderGreen) <greendayonfire@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r"""
---
module: proxmox_pool_member
short_description: Add or delete members from Proxmox VE cluster pools
description:
  - Create or delete a pool member in Proxmox VE clusters.
version_added: 7.1.0
author: "Sergei Antipov (@UnderGreen) <greendayonfire@gmail.com>"
attributes:
  check_mode:
    support: full
  diff_mode:
    support: full
  action_group:
    version_added: 9.0.0
options:
  poolid:
    description:
      - The pool ID.
    type: str
    aliases: [ "name" ]
    required: true
  member:
    description:
      - Specify the member name.
      - For O(type=storage) it is a storage name.
      - For O(type=vm) either vmid or vm name could be used.
    type: str
    required: true
  type:
    description:
      - Member type to add/remove from the pool.
    choices: ["vm", "storage"]
    default: vm
    type: str
  state:
    description:
     - Indicate desired state of the pool member.
    choices: ['present', 'absent']
    default: present
    type: str

extends_documentation_fragment:
  - community.general.proxmox.actiongroup_proxmox
  - community.general.proxmox.documentation
  - community.general.attributes
"""

EXAMPLES = """
- name: Add new VM to Proxmox VE pool
  community.general.proxmox_pool_member:
    api_host: node1
    api_user: root@pam
    api_password: password
    poolid: test
    member: 101

- name: Add new storage to Proxmox VE pool
  community.general.proxmox_pool_member:
    api_host: node1
    api_user: root@pam
    api_password: password
    poolid: test
    member: zfs-data
    type: storage

- name: Remove VM from the Proxmox VE pool using VM name
  community.general.proxmox_pool_member:
    api_host: node1
    api_user: root@pam
    api_password: password
    poolid: test
    member: pxe.home.arpa
    state: absent

- name: Remove storage from the Proxmox VE pool
  community.general.proxmox_pool_member:
    api_host: node1
    api_user: root@pam
    api_password: password
    poolid: test
    member: zfs-storage
    type: storage
    state: absent
"""

RETURN = """
poolid:
  description: The pool ID.
  returned: success
  type: str
  sample: test
member:
  description: Member name.
  returned: success
  type: str
  sample: 101
msg:
  description: A short message on what the module did.
  returned: always
  type: str
  sample: "Member 101 deleted from the pool test"
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.proxmox import (proxmox_auth_argument_spec, ProxmoxAnsible)


class ProxmoxPoolMemberAnsible(ProxmoxAnsible):

    def pool_members(self, poolid):
        vms = []
        storage = []
        for member in self.get_pool(poolid)["members"]:
            if member["type"] == "storage":
                storage.append(member["storage"])
            else:
                vms.append(member["vmid"])

        return (vms, storage)

    def add_pool_member(self, poolid, member, member_type):
        current_vms_members, current_storage_members = self.pool_members(poolid)
        all_members_before = current_storage_members + current_vms_members
        all_members_after = all_members_before.copy()
        diff = {"before": {"members": all_members_before}, "after": {"members": all_members_after}}

        try:
            if member_type == "storage":
                storages = self.get_storages(type=None)
                if member not in [storage["storage"] for storage in storages]:
                    self.module.fail_json(msg="Storage {0} doesn't exist in the cluster".format(member))
                if member in current_storage_members:
                    self.module.exit_json(changed=False, poolid=poolid, member=member,
                                          diff=diff, msg="Member {0} is already part of the pool {1}".format(member, poolid))

                all_members_after.append(member)
                if self.module.check_mode:
                    return diff

                self.proxmox_api.pools(poolid).put(storage=[member])
                return diff
            else:
                try:
                    vmid = int(member)
                except ValueError:
                    vmid = self.get_vmid(member)

                if vmid in current_vms_members:
                    self.module.exit_json(changed=False, poolid=poolid, member=member,
                                          diff=diff, msg="VM {0} is already part of the pool {1}".format(member, poolid))

                all_members_after.append(member)

                if not self.module.check_mode:
                    self.proxmox_api.pools(poolid).put(vms=[vmid])
                return diff
        except Exception as e:
            self.module.fail_json(msg="Failed to add a new member ({0}) to the pool {1}: {2}".format(member, poolid, e))

    def delete_pool_member(self, poolid, member, member_type):
        current_vms_members, current_storage_members = self.pool_members(poolid)
        all_members_before = current_storage_members + current_vms_members
        all_members_after = all_members_before.copy()
        diff = {"before": {"members": all_members_before}, "after": {"members": all_members_after}}

        try:
            if member_type == "storage":
                if member not in current_storage_members:
                    self.module.exit_json(changed=False, poolid=poolid, member=member,
                                          diff=diff, msg="Member {0} is not part of the pool {1}".format(member, poolid))

                all_members_after.remove(member)
                if self.module.check_mode:
                    return diff

                self.proxmox_api.pools(poolid).put(storage=[member], delete=1)
                return diff
            else:
                try:
                    vmid = int(member)
                except ValueError:
                    vmid = self.get_vmid(member)

                if vmid not in current_vms_members:
                    self.module.exit_json(changed=False, poolid=poolid, member=member,
                                          diff=diff, msg="VM {0} is not part of the pool {1}".format(member, poolid))

                all_members_after.remove(vmid)

                if not self.module.check_mode:
                    self.proxmox_api.pools(poolid).put(vms=[vmid], delete=1)
                return diff
        except Exception as e:
            self.module.fail_json(msg="Failed to delete a member ({0}) from the pool {1}: {2}".format(member, poolid, e))


def main():
    module_args = proxmox_auth_argument_spec()
    pool_members_args = dict(
        poolid=dict(type="str", aliases=["name"], required=True),
        member=dict(type="str", required=True),
        type=dict(default="vm", choices=["vm", "storage"]),
        state=dict(default="present", choices=["present", "absent"]),
    )

    module_args.update(pool_members_args)

    module = AnsibleModule(
        argument_spec=module_args,
        required_together=[("api_token_id", "api_token_secret")],
        required_one_of=[("api_password", "api_token_id")],
        supports_check_mode=True
    )

    poolid = module.params["poolid"]
    member = module.params["member"]
    member_type = module.params["type"]
    state = module.params["state"]

    proxmox = ProxmoxPoolMemberAnsible(module)

    if state == "present":
        diff = proxmox.add_pool_member(poolid, member, member_type)
        module.exit_json(changed=True, poolid=poolid, member=member, diff=diff, msg="New member {0} added to the pool {1}".format(member, poolid))
    else:
        diff = proxmox.delete_pool_member(poolid, member, member_type)
        module.exit_json(changed=True, poolid=poolid, member=member, diff=diff, msg="Member {0} deleted from the pool {1}".format(member, poolid))


if __name__ == "__main__":
    main()
