#!/usr/bin/python
#
# Copyright Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
module: lldp
requirements: [lldpctl]
short_description: Get details reported by LLDP
description:
  - Reads data out of C(lldpctl).
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options:
  multivalues:
    description: If lldpctl outputs an attribute multiple time represent all values as a list.
    type: bool
    default: false
author: "Andy Hill (@andyhky)"
notes:
  - Requires C(lldpd) running and LLDP enabled on switches.
"""

EXAMPLES = r"""
# Retrieve switch/port information
- name: Gather information from LLDP
  community.general.lldp:

- name: Print each switch/port
  ansible.builtin.debug:
    msg: "{{ lldp[item]['chassis']['name'] }} / {{ lldp[item]['port']['ifname'] }}"
  with_items: "{{ lldp.keys() }}"

# TASK: [Print each switch/port] ***********************************************************
# ok: [10.13.0.22] => (item=eth2) => {"item": "eth2", "msg": "switch1.example.com / Gi0/24"}
# ok: [10.13.0.22] => (item=eth1) => {"item": "eth1", "msg": "switch2.example.com / Gi0/3"}
# ok: [10.13.0.22] => (item=eth0) => {"item": "eth0", "msg": "switch3.example.com / Gi0/3"}
"""

from ansible.module_utils.basic import AnsibleModule


def gather_lldp(module):
    cmd = [module.get_bin_path("lldpctl"), "-f", "keyvalue"]
    rc, output, err = module.run_command(cmd)
    if output:
        output_dict = {}
        current_dict = {}
        lldp_entries = output.strip().split("\n")

        final = ""
        for entry in lldp_entries:
            if entry.startswith("lldp"):
                path, value = entry.strip().split("=", 1)
                path = path.split(".")
                path_components, final = path[:-1], path[-1]
            elif final in current_dict and isinstance(current_dict[final], str):
                current_dict[final] += f"\n{entry}"
                continue
            elif final in current_dict and isinstance(current_dict[final], list):
                current_dict[final][-1] += f"\n{entry}"
                continue
            else:
                continue

            current_dict = output_dict
            for path_component in path_components:
                current_dict[path_component] = current_dict.get(path_component, {})
                if not isinstance(current_dict[path_component], dict):
                    current_dict[path_component] = {"value": current_dict[path_component]}
                current_dict = current_dict[path_component]

            if final in current_dict and isinstance(current_dict[final], dict) and module.params["multivalues"]:
                current_dict = current_dict[final]
                final = "value"

            if final not in current_dict or not module.params["multivalues"]:
                current_dict[final] = value
            elif isinstance(current_dict[final], str):
                current_dict[final] = [current_dict[final], value]
            elif isinstance(current_dict[final], list):
                current_dict[final].append(value)

        return output_dict


def main():
    module_args = dict(multivalues=dict(type="bool", default=False))
    module = AnsibleModule(module_args)

    lldp_output = gather_lldp(module)
    try:
        data = {"lldp": lldp_output["lldp"]}
        module.exit_json(ansible_facts=data)
    except TypeError:
        module.fail_json(msg="lldpctl command failed. is lldpd running?")


if __name__ == "__main__":
    main()
