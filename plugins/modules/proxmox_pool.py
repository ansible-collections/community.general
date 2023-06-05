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
module: proxmox_pool
short_description: Pool management for Proxmox VE cluster
description:
  - Create or delete a pool for Proxmox VE clusters.
  - For pool members management please consult M(community.general.proxmox_pool_member) module.
version_added: 7.1.0
author: "Sergei Antipov (@UnderGreen) <greendayonfire@gmail.com>"
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  poolid:
    description:
      - The pool ID.
    type: str
    aliases: [ "name" ]
    required: true
  state:
    description:
     - Indicate desired state of the pool.
     - The pool must be empty prior deleting it with O(state=absent).
    choices: ['present', 'absent']
    default: present
    type: str
  comment:
    description:
      - Specify the description for the pool.
      - Parameter is ignored when pool already exists or O(state=absent).
    type: str

extends_documentation_fragment:
    - community.general.proxmox.documentation
    - community.general.attributes
"""

EXAMPLES = """
- name: Create new Proxmox VE pool
  community.general.proxmox_pool:
    api_host: node1
    api_user: root@pam
    api_password: password
    poolid: test
    comment: 'New pool'

- name: Delete the Proxmox VE pool
  community.general.proxmox_pool:
    api_host: node1
    api_user: root@pam
    api_password: password
    poolid: test
    state: absent
"""

RETURN = """
poolid:
  description: The pool ID.
  returned: success
  type: str
  sample: test
msg:
  description: A short message on what the module did.
  returned: always
  type: str
  sample: "Pool test successfully created"
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.proxmox import (proxmox_auth_argument_spec, ProxmoxAnsible)


class ProxmoxPoolAnsible(ProxmoxAnsible):

    def is_pool_existing(self, poolid):
        """Check whether pool already exist

        :param poolid: str - name of the pool
        :return: bool - is pool exists?
        """
        try:
            pools = self.proxmox_api.pools.get()
            for pool in pools:
                if pool['poolid'] == poolid:
                    return True
            return False
        except Exception as e:
            self.module.fail_json(msg="Unable to retrieve pools: {0}".format(e))

    def is_pool_empty(self, poolid):
        """Check whether pool has members

        :param poolid: str - name of the pool
        :return: bool - is pool empty?
        """
        return True if not self.get_pool(poolid)['members'] else False

    def create_pool(self, poolid, comment=None):
        """Create Proxmox VE pool

        :param poolid: str - name of the pool
        :param comment: str, optional - Description of a pool
        :return: None
        """
        if self.is_pool_existing(poolid):
            self.module.exit_json(changed=False, poolid=poolid, msg="Pool {0} already exists".format(poolid))

        if self.module.check_mode:
            return

        try:
            self.proxmox_api.pools.post(poolid=poolid, comment=comment)
        except Exception as e:
            self.module.fail_json(msg="Failed to create pool with ID {0}: {1}".format(poolid, e))

    def delete_pool(self, poolid):
        """Delete Proxmox VE pool

        :param poolid: str - name of the pool
        :return: None
        """
        if not self.is_pool_existing(poolid):
            self.module.exit_json(changed=False, poolid=poolid, msg="Pool {0} doesn't exist".format(poolid))

        if self.is_pool_empty(poolid):
            if self.module.check_mode:
                return

            try:
                self.proxmox_api.pools(poolid).delete()
            except Exception as e:
                self.module.fail_json(msg="Failed to delete pool with ID {0}: {1}".format(poolid, e))
        else:
            self.module.fail_json(msg="Can't delete pool {0} with members. Please remove members from pool first.".format(poolid))


def main():
    module_args = proxmox_auth_argument_spec()
    pools_args = dict(
        poolid=dict(type="str", aliases=["name"], required=True),
        comment=dict(type="str"),
        state=dict(default="present", choices=["present", "absent"]),
    )

    module_args.update(pools_args)

    module = AnsibleModule(
        argument_spec=module_args,
        required_together=[("api_token_id", "api_token_secret")],
        required_one_of=[("api_password", "api_token_id")],
        supports_check_mode=True
    )

    poolid = module.params["poolid"]
    comment = module.params["comment"]
    state = module.params["state"]

    proxmox = ProxmoxPoolAnsible(module)

    if state == "present":
        proxmox.create_pool(poolid, comment)
        module.exit_json(changed=True, poolid=poolid, msg="Pool {0} successfully created".format(poolid))
    else:
        proxmox.delete_pool(poolid)
        module.exit_json(changed=True, poolid=poolid, msg="Pool {0} successfully deleted".format(poolid))


if __name__ == "__main__":
    main()
