#!/usr/bin/python

# Copyright (c) 2016, Adfinis SyGroup AG
# Tobias Rueetschi <tobias.ruetschi@adfinis-sygroup.ch>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
module: udm_dns_zone
author:
  - Tobias Rüetschi (@keachi)
short_description: Manage DNS zones on a univention corporate server
description:
  - This module allows to manage DNS zones on a univention corporate server (UCS). It uses the Python API of the UCS to create
    a new object or edit it.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: partial
options:
  state:
    type: str
    default: "present"
    choices: [present, absent]
    description:
      - Whether the DNS zone is present or not.
  type:
    type: str
    required: true
    description:
      - Define if the zone is a forward or reverse DNS zone.
      - 'The available choices are: V(forward_zone), V(reverse_zone).'
  zone:
    type: str
    required: true
    description:
      - DNS zone name, for example V(example.com).
    aliases: [name]
  nameserver:
    type: list
    elements: str
    default: []
    description:
      - List of appropriate name servers. Required if O(state=present).
  interfaces:
    type: list
    elements: str
    default: []
    description:
      - List of interface IP addresses, on which the server should response this zone. Required if O(state=present).
  refresh:
    type: int
    default: 3600
    description:
      - Interval before the zone should be refreshed.
  retry:
    type: int
    default: 1800
    description:
      - Interval that should elapse before a failed refresh should be retried.
  expire:
    type: int
    default: 604800
    description:
      - Specifies the upper limit on the time interval that can elapse before the zone is no longer authoritative.
  ttl:
    type: int
    default: 600
    description:
      - Minimum TTL field that should be exported with any RR from this zone.
  contact:
    type: str
    default: ''
    description:
      - Contact person in the SOA record.
  mx:
    type: list
    elements: str
    default: []
    description:
      - List of MX servers. (Must declared as A or AAAA records).
"""


EXAMPLES = r"""
- name: Create a DNS zone on a UCS
  community.general.udm_dns_zone:
    zone: example.com
    type: forward_zone
    nameserver:
      - ucs.example.com
    interfaces:
      - 192.0.2.1
"""


RETURN = """#"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.univention_umc import (
    umc_module_for_add,
    umc_module_for_edit,
    ldap_search,
    base_dn,
)


def convert_time(time):
    """Convert a time in seconds into the biggest unit"""
    units = [
        (24 * 60 * 60, "days"),
        (60 * 60, "hours"),
        (60, "minutes"),
        (1, "seconds"),
    ]

    if time == 0:
        return ("0", "seconds")
    for unit in units:
        if time >= unit[0]:
            return (f"{time // unit[0]}", unit[1])


def main():
    module = AnsibleModule(
        argument_spec=dict(
            type=dict(required=True, type="str"),
            zone=dict(required=True, aliases=["name"], type="str"),
            nameserver=dict(default=[], type="list", elements="str"),
            interfaces=dict(default=[], type="list", elements="str"),
            refresh=dict(default=3600, type="int"),
            retry=dict(default=1800, type="int"),
            expire=dict(default=604800, type="int"),
            ttl=dict(default=600, type="int"),
            contact=dict(default="", type="str"),
            mx=dict(default=[], type="list", elements="str"),
            state=dict(default="present", choices=["present", "absent"], type="str"),
        ),
        supports_check_mode=True,
        required_if=([("state", "present", ["nameserver", "interfaces"])]),
    )
    type = module.params["type"]
    zone = module.params["zone"]
    nameserver = module.params["nameserver"]
    interfaces = module.params["interfaces"]
    refresh = module.params["refresh"]
    retry = module.params["retry"]
    expire = module.params["expire"]
    ttl = module.params["ttl"]
    contact = module.params["contact"]
    mx = module.params["mx"]
    state = module.params["state"]
    changed = False
    diff = None

    obj = list(ldap_search(f"(&(objectClass=dNSZone)(zoneName={zone}))", attr=["dNSZone"]))

    exists = bool(len(obj))
    container = f"cn=dns,{base_dn()}"
    dn = f"zoneName={zone},{container}"
    if contact == "":
        contact = f"root@{zone}."

    if state == "present":
        try:
            if not exists:
                obj = umc_module_for_add(f"dns/{type}", container)
            else:
                obj = umc_module_for_edit(f"dns/{type}", dn)
            obj["zone"] = zone
            obj["nameserver"] = nameserver
            obj["a"] = interfaces
            obj["refresh"] = convert_time(refresh)
            obj["retry"] = convert_time(retry)
            obj["expire"] = convert_time(expire)
            obj["ttl"] = convert_time(ttl)
            obj["contact"] = contact
            obj["mx"] = mx
            diff = obj.diff()
            if exists:
                for k in obj.keys():
                    if obj.hasChanged(k):
                        changed = True
            else:
                changed = True
            if not module.check_mode:
                if not exists:
                    obj.create()
                elif changed:
                    obj.modify()
        except Exception as e:
            module.fail_json(msg=f"Creating/editing dns zone {zone} failed: {e}")

    if state == "absent" and exists:
        try:
            obj = umc_module_for_edit(f"dns/{type}", dn)
            if not module.check_mode:
                obj.remove()
            changed = True
        except Exception as e:
            module.fail_json(msg=f"Removing dns zone {zone} failed: {e}")

    module.exit_json(changed=changed, diff=diff, zone=zone)


if __name__ == "__main__":
    main()
