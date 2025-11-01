#!/usr/bin/python

# Copyright (c) 2016, Adfinis SyGroup AG
# Tobias Rueetschi <tobias.ruetschi@adfinis-sygroup.ch>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
module: udm_dns_record
author:
  - Tobias Rüetschi (@keachi)
short_description: Manage DNS entries on a univention corporate server
description:
  - This module allows to manage DNS records on a univention corporate server (UCS). It uses the Python API of the UCS to
    create a new object or edit it.
requirements:
  - Univention
  - ipaddress (for O(type=ptr_record))
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
      - Whether the DNS record is present or not.
  name:
    type: str
    required: true
    description:
      - Name of the record, this is also the DNS record. For example V(www) for www.example.com.
      - For PTR records this has to be the IP address.
  zone:
    type: str
    required: true
    description:
      - Corresponding DNS zone for this record, for example V(example.com).
      - For PTR records this has to be the full reverse zone (for example V(1.1.192.in-addr.arpa)).
  type:
    type: str
    required: true
    description:
      - Define the record type. V(host_record) is a A or AAAA record, V(alias) is a CNAME, V(ptr_record) is a PTR record,
        V(srv_record) is a SRV record and V(txt_record) is a TXT record.
      - 'The available choices are: V(host_record), V(alias), V(ptr_record), V(srv_record), V(txt_record).'
  data:
    type: dict
    default: {}
    description:
      - "Additional data for this record, for example V({'a': '192.0.2.1'})."
      - Required if O(state=present).
"""


EXAMPLES = r"""
- name: Create a DNS record on a UCS
  community.general.udm_dns_record:
    name: www
    zone: example.com
    type: host_record
    data:
      a:
        - 192.0.2.1
        - 2001:0db8::42

- name: Create a DNS v4 PTR record on a UCS
  community.general.udm_dns_record:
    name: 192.0.2.1
    zone: 2.0.192.in-addr.arpa
    type: ptr_record
    data:
      ptr_record: "www.example.com."

- name: Create a DNS v6 PTR record on a UCS
  community.general.udm_dns_record:
    name: 2001:db8:0:0:0:ff00:42:8329
    zone: 2.4.0.0.0.0.f.f.0.0.0.0.0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa
    type: ptr_record
    data:
      ptr_record: "www.example.com."
"""


RETURN = """#"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils import deps
from ansible_collections.community.general.plugins.module_utils.univention_umc import (
    umc_module_for_add,
    umc_module_for_edit,
    ldap_search,
    base_dn,
    config,
    uldap,
)


with deps.declare("univention", msg="This module requires univention python bindings"):
    from univention.admin.handlers.dns import (
        forward_zone,
        reverse_zone,
    )

with deps.declare("ipaddress"):
    import ipaddress


def main():
    module = AnsibleModule(
        argument_spec=dict(
            type=dict(required=True, type="str"),
            zone=dict(required=True, type="str"),
            name=dict(required=True, type="str"),
            data=dict(default={}, type="dict"),
            state=dict(default="present", choices=["present", "absent"], type="str"),
        ),
        supports_check_mode=True,
        required_if=([("state", "present", ["data"])]),
    )

    deps.validate(module, "univention")

    type = module.params["type"]
    zone = module.params["zone"]
    name = module.params["name"]
    data = module.params["data"]
    state = module.params["state"]
    changed = False
    diff = None

    workname = name
    if type == "ptr_record":
        deps.validate(module, "ipaddress")

        try:
            if "arpa" not in zone:
                raise Exception("Zone must be reversed zone for ptr_record. (e.g. 1.1.192.in-addr.arpa)")
            ipaddr_rev = ipaddress.ip_address(name).reverse_pointer
            subnet_offset = ipaddr_rev.find(zone)
            if subnet_offset == -1:
                raise Exception(f"reversed IP address {ipaddr_rev} is not part of zone.")
            workname = ipaddr_rev[0 : subnet_offset - 1]
        except Exception as e:
            module.fail_json(msg=f"handling PTR record for {name} in zone {zone} failed: {e}")

    obj = list(
        ldap_search(f"(&(objectClass=dNSZone)(zoneName={zone})(relativeDomainName={workname}))", attr=["dNSZone"])
    )
    exists = bool(len(obj))
    container = f"zoneName={zone},cn=dns,{base_dn()}"
    dn = f"relativeDomainName={workname},{container}"

    if state == "present":
        try:
            if not exists:
                so = forward_zone.lookup(
                    config(),
                    uldap(),
                    f"(zone={zone})",
                    scope="domain",
                ) or reverse_zone.lookup(
                    config(),
                    uldap(),
                    f"(zoneName={zone})",
                    scope="domain",
                )
                if not so == 0:
                    raise Exception(f"Did not find zone '{zone}' in Univention")
                obj = umc_module_for_add(f"dns/{type}", container, superordinate=so[0])
            else:
                obj = umc_module_for_edit(f"dns/{type}", dn)

            if type == "ptr_record":
                obj["ip"] = name
                obj["address"] = workname
            else:
                obj["name"] = name

            obj.update(data)
            diff = obj.diff()
            changed = obj.diff() != []
            if not module.check_mode:
                if not exists:
                    obj.create()
                else:
                    obj.modify()
        except Exception as e:
            module.fail_json(msg=f"Creating/editing dns entry {name} in {container} failed: {e}")

    if state == "absent" and exists:
        try:
            obj = umc_module_for_edit(f"dns/{type}", dn)
            if not module.check_mode:
                obj.remove()
            changed = True
        except Exception as e:
            module.fail_json(msg=f"Removing dns entry {name} in {container} failed: {e}")

    module.exit_json(changed=changed, name=name, diff=diff, container=container)


if __name__ == "__main__":
    main()
