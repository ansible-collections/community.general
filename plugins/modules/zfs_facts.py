#!/usr/bin/python

# Copyright (c) 2016, Adam Števko <adam.stevko@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
module: zfs_facts
short_description: Gather facts about ZFS datasets
description:
  - Gather facts from ZFS dataset properties.
author: Adam Števko (@xen0l)
extends_documentation_fragment:
  - community.general.attributes
  - community.general.attributes.facts
  - community.general.attributes.facts_module
options:
  name:
    description:
      - ZFS dataset name.
    required: true
    aliases: ["ds", "dataset"]
    type: str
  recurse:
    description:
      - Specifies if properties for any children should be recursively displayed.
    type: bool
    default: false
  parsable:
    description:
      - Specifies if property values should be displayed in machine friendly format.
    type: bool
    default: false
  properties:
    description:
      - Specifies which dataset properties should be queried in comma-separated format. For more information about dataset
        properties, check zfs(1M) man page.
    default: all
    type: str
  type:
    description:
      - Specifies which datasets types to display. Multiple values have to be provided as a list or in comma-separated form.
      - Value V(all) cannot be used together with other values.
    choices: ['all', 'filesystem', 'volume', 'snapshot', 'bookmark']
    default: [all]
    type: list
    elements: str
  depth:
    description:
      - Specifies recursion depth.
    type: int
    default: 0
"""

EXAMPLES = r"""
- name: Gather facts about ZFS dataset rpool/export/home
  community.general.zfs_facts:
    dataset: rpool/export/home

- name: Report space usage on ZFS filesystems under data/home
  community.general.zfs_facts:
    name: data/home
    recurse: true
    type: filesystem

- ansible.builtin.debug:
    msg: 'ZFS dataset {{ item.name }} consumes {{ item.used }} of disk space.'
  with_items: '{{ ansible_zfs_datasets }}'
"""

RETURN = r"""
name:
  description: ZFS dataset name.
  returned: always
  type: str
  sample: rpool/var/spool
parsable:
  description: If parsable output should be provided in machine friendly format.
  returned: if O(parsable=True)
  type: bool
  sample: true
recurse:
  description: If we should recurse over ZFS dataset.
  returned: if O(recurse=True)
  type: bool
  sample: true
zfs_datasets:
  description: ZFS dataset facts.
  returned: always
  type: str
  sample:
    "aclinherit": "restricted"
    "aclmode": "discard"
    "atime": "on"
    "available": "43.8G"
    "canmount": "on"
    "casesensitivity": "sensitive"
    "checksum": "on"
    "compression": "off"
    "compressratio": "1.00x"
    "copies": "1"
    "creation": "Thu Jun 16 11:37 2016"
    "dedup": "off"
    "devices": "on"
    "exec": "on"
    "filesystem_count": "none"
    "filesystem_limit": "none"
    "logbias": "latency"
    "logicalreferenced": "18.5K"
    "logicalused": "3.45G"
    "mlslabel": "none"
    "mounted": "yes"
    "mountpoint": "/rpool"
    "name": "rpool"
    "nbmand": "off"
    "normalization": "none"
    "org.openindiana.caiman:install": "ready"
    "primarycache": "all"
    "quota": "none"
    "readonly": "off"
    "recordsize": "128K"
    "redundant_metadata": "all"
    "refcompressratio": "1.00x"
    "referenced": "29.5K"
    "refquota": "none"
    "refreservation": "none"
    "reservation": "none"
    "secondarycache": "all"
    "setuid": "on"
    "sharenfs": "off"
    "sharesmb": "off"
    "snapdir": "hidden"
    "snapshot_count": "none"
    "snapshot_limit": "none"
    "sync": "standard"
    "type": "filesystem"
    "used": "4.41G"
    "usedbychildren": "4.41G"
    "usedbydataset": "29.5K"
    "usedbyrefreservation": "0"
    "usedbysnapshots": "0"
    "utf8only": "off"
    "version": "5"
    "vscan": "off"
    "written": "29.5K"
    "xattr": "on"
    "zoned": "off"
"""

from collections import defaultdict

from ansible.module_utils.basic import AnsibleModule


SUPPORTED_TYPES = ["all", "filesystem", "volume", "snapshot", "bookmark"]


class ZFSFacts:
    def __init__(self, module):
        self.module = module

        self.name = module.params["name"]
        self.recurse = module.params["recurse"]
        self.parsable = module.params["parsable"]
        self.properties = module.params["properties"]
        self.type = module.params["type"]
        self.depth = module.params["depth"]

        self._datasets = defaultdict(dict)
        self.facts = []

    def dataset_exists(self):
        cmd = [self.module.get_bin_path("zfs"), "list", self.name]

        (rc, out, err) = self.module.run_command(cmd)

        return rc == 0

    def get_facts(self):
        cmd = [self.module.get_bin_path("zfs"), "get", "-H"]
        if self.parsable:
            cmd.append("-p")
        if self.recurse:
            cmd.append("-r")
        if self.depth != 0:
            cmd.append("-d")
            cmd.append(f"{self.depth}")
        if self.type:
            cmd.append("-t")
            cmd.append(",".join(self.type))
        cmd.extend(["-o", "name,property,value", self.properties, self.name])

        (rc, out, err) = self.module.run_command(cmd, check_rc=True)

        for line in out.splitlines():
            dataset, property, value = line.split("\t")

            self._datasets[dataset].update({property: value})

        for k, v in self._datasets.items():
            v.update({"name": k})
            self.facts.append(v)

        return {"ansible_zfs_datasets": self.facts}


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True, aliases=["ds", "dataset"], type="str"),
            recurse=dict(default=False, type="bool"),
            parsable=dict(default=False, type="bool"),
            properties=dict(default="all", type="str"),
            type=dict(default="all", type="list", elements="str", choices=SUPPORTED_TYPES),
            depth=dict(default=0, type="int"),
        ),
        supports_check_mode=True,
    )

    if "all" in module.params["type"] and len(module.params["type"]) > 1:
        module.fail_json(msg="Value 'all' for parameter 'type' is mutually exclusive with other values")

    zfs_facts = ZFSFacts(module)

    result = {}
    result["changed"] = False
    result["name"] = zfs_facts.name

    if zfs_facts.parsable:
        result["parsable"] = zfs_facts.parsable

    if zfs_facts.recurse:
        result["recurse"] = zfs_facts.recurse

    if not zfs_facts.dataset_exists():
        module.fail_json(msg=f"ZFS dataset {zfs_facts.name} does not exist!")

    result["ansible_facts"] = zfs_facts.get_facts()

    module.exit_json(**result)


if __name__ == "__main__":
    main()
