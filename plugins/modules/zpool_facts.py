#!/usr/bin/python

# Copyright (c) 2016, Adam Števko <adam.stevko@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
module: zpool_facts
short_description: Gather facts about ZFS pools
description:
  - Gather facts from ZFS pool properties.
author: Adam Števko (@xen0l)
extends_documentation_fragment:
  - community.general.attributes
  - community.general.attributes.facts
  - community.general.attributes.facts_module
options:
  name:
    description:
      - ZFS pool name.
    type: str
    aliases: ["pool", "zpool"]
  parsable:
    description:
      - Specifies if property values should be displayed in machine friendly format.
    type: bool
    default: false
  properties:
    description:
      - Specifies which dataset properties should be queried in comma-separated format. For more information about dataset
        properties, check zpool(1M) man page.
    type: str
    default: all
"""

EXAMPLES = r"""
- name: Gather facts about ZFS pool rpool
  community.general.zpool_facts: pool=rpool

- name: Gather space usage about all imported ZFS pools
  community.general.zpool_facts: properties='free,size'

- name: Print gathered information
  ansible.builtin.debug:
    msg: 'ZFS pool {{ item.name }} has {{ item.free }} free space out of {{ item.size }}.'
  with_items: '{{ ansible_zfs_pools }}'
"""

RETURN = r"""
ansible_facts:
  description: Dictionary containing all the detailed information about the ZFS pool facts.
  returned: always
  type: complex
  contains:
    ansible_zfs_pools:
      description: ZFS pool facts.
      returned: always
      type: str
      sample:
        "allocated": "3.46G"
        "altroot": "-"
        "autoexpand": "off"
        "autoreplace": "off"
        "bootfs": "rpool/ROOT/openindiana"
        "cachefile": "-"
        "capacity": "6%"
        "comment": "-"
        "dedupditto": "0"
        "dedupratio": "1.00x"
        "delegation": "on"
        "expandsize": "-"
        "failmode": "wait"
        "feature@async_destroy": "enabled"
        "feature@bookmarks": "enabled"
        "feature@edonr": "enabled"
        "feature@embedded_data": "active"
        "feature@empty_bpobj": "active"
        "feature@enabled_txg": "active"
        "feature@extensible_dataset": "enabled"
        "feature@filesystem_limits": "enabled"
        "feature@hole_birth": "active"
        "feature@large_blocks": "enabled"
        "feature@lz4_compress": "active"
        "feature@multi_vdev_crash_dump": "enabled"
        "feature@sha512": "enabled"
        "feature@skein": "enabled"
        "feature@spacemap_histogram": "active"
        "fragmentation": "3%"
        "free": "46.3G"
        "freeing": "0"
        "guid": "15729052870819522408"
        "health": "ONLINE"
        "leaked": "0"
        "listsnapshots": "off"
        "name": "rpool"
        "readonly": "off"
        "size": "49.8G"
        "version": "-"
name:
  description: ZFS pool name.
  returned: always
  type: str
  sample: rpool
parsable:
  description: If parsable output should be provided in machine friendly format.
  returned: if O(parsable=true)
  type: bool
  sample: true
"""

from collections import defaultdict

from ansible.module_utils.basic import AnsibleModule


class ZPoolFacts:
    def __init__(self, module):
        self.module = module
        self.name = module.params["name"]
        self.parsable = module.params["parsable"]
        self.properties = module.params["properties"]
        self._pools = defaultdict(dict)
        self.facts = []

    def pool_exists(self):
        cmd = [self.module.get_bin_path("zpool"), "list", self.name]
        rc, dummy, dummy = self.module.run_command(cmd)
        return rc == 0

    def get_facts(self):
        cmd = [self.module.get_bin_path("zpool"), "get", "-H"]
        if self.parsable:
            cmd.append("-p")
        cmd.append("-o")
        cmd.append("name,property,value")
        cmd.append(self.properties)
        if self.name:
            cmd.append(self.name)

        rc, out, err = self.module.run_command(cmd, check_rc=True)

        for line in out.splitlines():
            pool, prop, value = line.split("\t")

            self._pools[pool].update({prop: value})

        for k, v in self._pools.items():
            v.update({"name": k})
            self.facts.append(v)

        return {"ansible_zfs_pools": self.facts}


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(aliases=["pool", "zpool"], type="str"),
            parsable=dict(default=False, type="bool"),
            properties=dict(default="all", type="str"),
        ),
        supports_check_mode=True,
    )

    zpool_facts = ZPoolFacts(module)

    result = {
        "changed": False,
        "name": zpool_facts.name,
    }
    if zpool_facts.parsable:
        result["parsable"] = zpool_facts.parsable

    if zpool_facts.name is not None:
        if zpool_facts.pool_exists():
            result["ansible_facts"] = zpool_facts.get_facts()
        else:
            module.fail_json(msg=f"ZFS pool {zpool_facts.name} does not exist!")
    else:
        result["ansible_facts"] = zpool_facts.get_facts()

    module.exit_json(**result)


if __name__ == "__main__":
    main()
