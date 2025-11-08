#!/usr/bin/python
#
# Copyright (c) 2016, Roman Belyakovsky <ihryamzik () gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
module: interfaces_file
short_description: Tweak settings in C(/etc/network/interfaces) files
extends_documentation_fragment:
  - ansible.builtin.files
  - community.general.attributes
description:
  - Manage (add, remove, change) individual interface options in an interfaces-style file without having to manage the file
    as a whole with, say, M(ansible.builtin.template) or M(ansible.builtin.assemble). Interface has to be presented in a file.
  - Read information about interfaces from interfaces-styled files.
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  dest:
    type: path
    description:
      - Path to the interfaces file.
    default: /etc/network/interfaces
  iface:
    type: str
    description:
      - Name of the interface, required for value changes or option remove.
  address_family:
    type: str
    description:
      - Address family of the interface, useful if same interface name is used for both V(inet) and V(inet6).
  option:
    type: str
    description:
      - Name of the option, required for value changes or option remove.
  value:
    type: str
    description:
      - If O(option) is not presented for the O(iface) and O(state) is V(present), then O(option) is added. If O(option) already
        exists and is not V(pre-up), V(up), V(post-up) or V(down), its value is updated. V(pre-up), V(up), V(post-up) and
        V(down) options cannot be updated, only adding new options, removing existing ones or cleaning the whole option set
        are supported.
  backup:
    description:
      - Create a backup file including the timestamp information so you can get the original file back if you somehow clobbered
        it incorrectly.
    type: bool
    default: false
  state:
    type: str
    description:
      - If set to V(absent) the option or section is removed if present instead of created.
    default: "present"
    choices: ["present", "absent"]

notes:
  - If option is defined multiple times last one is updated but all others are deleted in case of an O(state=absent).
requirements: []
author: "Roman Belyakovsky (@hryamzik)"
"""

RETURN = r"""
dest:
  description: Destination file/path.
  returned: success
  type: str
  sample: "/etc/network/interfaces"
ifaces:
  description: Interfaces dictionary.
  returned: success
  type: dict
  contains:
    ifaces:
      description: Interface dictionary.
      returned: success
      type: dict
      contains:
        eth0:
          description: Name of the interface.
          returned: success
          type: dict
          contains:
            address_family:
              description: Interface address family.
              returned: success
              type: str
              sample: "inet"
            method:
              description: Interface method.
              returned: success
              type: str
              sample: "manual"
            mtu:
              description: Other options, all values returned as strings.
              returned: success
              type: str
              sample: "1500"
            pre-up:
              description: List of C(pre-up) scripts.
              returned: success
              type: list
              elements: str
              sample:
                - "route add -net 10.10.10.0/24 gw 10.10.10.1 dev eth1"
                - "route add -net 10.10.11.0/24 gw 10.10.11.1 dev eth2"
            up:
              description: List of C(up) scripts.
              returned: success
              type: list
              elements: str
              sample:
                - "route add -net 10.10.10.0/24 gw 10.10.10.1 dev eth1"
                - "route add -net 10.10.11.0/24 gw 10.10.11.1 dev eth2"
            post-up:
              description: List of C(post-up) scripts.
              returned: success
              type: list
              elements: str
              sample:
                - "route add -net 10.10.10.0/24 gw 10.10.10.1 dev eth1"
                - "route add -net 10.10.11.0/24 gw 10.10.11.1 dev eth2"
            down:
              description: List of C(down) scripts.
              returned: success
              type: list
              elements: str
              sample:
                - "route del -net 10.10.10.0/24 gw 10.10.10.1 dev eth1"
                - "route del -net 10.10.11.0/24 gw 10.10.11.1 dev eth2"
"""

EXAMPLES = r"""
- name: Set eth1 mtu configuration value to 8000
  community.general.interfaces_file:
    dest: /etc/network/interfaces.d/eth1.cfg
    iface: eth1
    option: mtu
    value: 8000
    backup: true
    state: present
  register: eth1_cfg
"""

import os
import re
import tempfile

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_bytes


def lineDict(line):
    return {"line": line, "line_type": "unknown"}


def optionDict(line, iface, option, value, address_family):
    return {
        "line": line,
        "iface": iface,
        "option": option,
        "value": value,
        "line_type": "option",
        "address_family": address_family,
    }


def getValueFromLine(s):
    option = s.split()[0]
    optionStart = s.find(option)
    optionLen = len(option)
    return s[optionLen + optionStart :].strip()


def read_interfaces_file(module, filename):
    with open(filename, "r") as f:
        return read_interfaces_lines(module, f)


def read_interfaces_lines(module, line_strings):
    lines = []
    ifaces = {}
    currently_processing = None
    i = 0
    for line in line_strings:
        i += 1
        words = line.split()
        if len(words) < 1:
            lines.append(lineDict(line))
            continue
        if words[0][0] == "#":
            lines.append(lineDict(line))
            continue
        if words[0] == "mapping":
            # currmap = calloc(1, sizeof *currmap);
            lines.append(lineDict(line))
            currently_processing = "MAPPING"
        elif words[0] == "source":
            lines.append(lineDict(line))
            currently_processing = "NONE"
        elif words[0] == "source-dir":
            lines.append(lineDict(line))
            currently_processing = "NONE"
        elif words[0] == "source-directory":
            lines.append(lineDict(line))
            currently_processing = "NONE"
        elif words[0] == "iface":
            currif = {"pre-up": [], "up": [], "down": [], "post-up": []}
            iface_name = words[1]
            try:
                currif["address_family"] = words[2]
            except IndexError:
                currif["address_family"] = None
            address_family = currif["address_family"]
            try:
                currif["method"] = words[3]
            except IndexError:
                currif["method"] = None

            ifaces[iface_name] = currif
            lines.append(
                {
                    "line": line,
                    "iface": iface_name,
                    "line_type": "iface",
                    "params": currif,
                    "address_family": address_family,
                }
            )
            currently_processing = "IFACE"
        elif words[0] == "auto":
            lines.append(lineDict(line))
            currently_processing = "NONE"
        elif words[0].startswith("allow-"):
            lines.append(lineDict(line))
            currently_processing = "NONE"
        elif words[0] == "no-auto-down":
            lines.append(lineDict(line))
            currently_processing = "NONE"
        elif words[0] == "no-scripts":
            lines.append(lineDict(line))
            currently_processing = "NONE"
        else:
            if currently_processing == "IFACE":
                option_name = words[0]
                value = getValueFromLine(line)
                lines.append(optionDict(line, iface_name, option_name, value, address_family))
                if option_name in ["pre-up", "up", "down", "post-up"]:
                    currif[option_name].append(value)
                else:
                    currif[option_name] = value
            elif currently_processing == "MAPPING":
                lines.append(lineDict(line))
            elif currently_processing == "NONE":
                lines.append(lineDict(line))
            else:
                module.fail_json(msg=f"misplaced option {line} in line {i}")
                return None, None
    return lines, ifaces


def get_interface_options(iface_lines):
    return [i for i in iface_lines if i["line_type"] == "option"]


def get_target_options(iface_options, option):
    return [i for i in iface_options if i["option"] == option]


def update_existing_option_line(target_option, value):
    old_line = target_option["line"]
    old_value = target_option["value"]
    prefix_start = old_line.find(target_option["option"])
    optionLen = len(target_option["option"])
    old_value_position = re.search(r"\s+".join(map(re.escape, old_value.split())), old_line[prefix_start + optionLen :])
    start = old_value_position.start() + prefix_start + optionLen
    end = old_value_position.end() + prefix_start + optionLen
    line = old_line[:start] + value + old_line[end:]
    return line


def set_interface_option(module, lines, iface, option, raw_value, state, address_family=None):
    value = str(raw_value)
    changed = False

    iface_lines = [item for item in lines if "iface" in item and item["iface"] == iface]
    if address_family is not None:
        iface_lines = [
            item for item in iface_lines if "address_family" in item and item["address_family"] == address_family
        ]

    if len(iface_lines) < 1:
        # interface not found
        module.fail_json(msg=f"Error: interface {iface} not found")
        return changed, None

    iface_options = get_interface_options(iface_lines)
    target_options = get_target_options(iface_options, option)

    if state == "present":
        if len(target_options) < 1:
            changed = True
            # add new option
            last_line_dict = iface_lines[-1]
            changed, lines = addOptionAfterLine(
                option, value, iface, lines, last_line_dict, iface_options, address_family
            )
        else:
            if option in ["pre-up", "up", "down", "post-up"]:
                if len([i for i in target_options if i["value"] == value]) < 1:
                    changed, lines = addOptionAfterLine(
                        option, value, iface, lines, target_options[-1], iface_options, address_family
                    )
            else:
                # if more than one option found edit the last one
                if target_options[-1]["value"] != value:
                    changed = True
                    target_option = target_options[-1]
                    line = update_existing_option_line(target_option, value)
                    address_family = target_option["address_family"]
                    index = len(lines) - lines[::-1].index(target_option) - 1
                    lines[index] = optionDict(line, iface, option, value, address_family)
    elif state == "absent":
        if len(target_options) >= 1:
            if option in ["pre-up", "up", "down", "post-up"] and value is not None and value != "None":
                for target_option in [ito for ito in target_options if ito["value"] == value]:
                    changed = True
                    lines = [ln for ln in lines if ln != target_option]
            else:
                changed = True
                for target_option in target_options:
                    lines = [ln for ln in lines if ln != target_option]
    else:
        module.fail_json(msg=f"Error: unsupported state {state}, has to be either present or absent")

    return changed, lines


def addOptionAfterLine(option, value, iface, lines, last_line_dict, iface_options, address_family):
    # Changing method of interface is not an addition
    if option == "method":
        changed = False
        for ln in lines:
            if (
                ln.get("line_type", "") == "iface"
                and ln.get("iface", "") == iface
                and value != ln.get("params", {}).get("method", "")
            ):
                if address_family is not None and ln.get("address_family") != address_family:
                    continue
                changed = True
                ln["line"] = re.sub(f"{ln.get('params', {}).get('method', '')}$", value, ln.get("line"))
                ln["params"]["method"] = value
        return changed, lines

    last_line = last_line_dict["line"]
    prefix_start = last_line.find(last_line.split()[0])
    suffix_start = last_line.rfind(last_line.split()[-1]) + len(last_line.split()[-1])
    prefix = last_line[:prefix_start]

    if len(iface_options) < 1:
        # interface has no options, ident
        prefix += "    "

    line = f"{prefix}{option} {value}{last_line[suffix_start:]}"
    option_dict = optionDict(line, iface, option, value, address_family)
    index = len(lines) - lines[::-1].index(last_line_dict)
    lines.insert(index, option_dict)
    return True, lines


def write_changes(module, lines, dest):
    tmpfd, tmpfile = tempfile.mkstemp()
    with os.fdopen(tmpfd, "wb") as f:
        f.write(to_bytes("".join(lines), errors="surrogate_or_strict"))
    module.atomic_move(tmpfile, os.path.realpath(dest))


def main():
    module = AnsibleModule(
        argument_spec=dict(
            dest=dict(type="path", default="/etc/network/interfaces"),
            iface=dict(type="str"),
            address_family=dict(type="str"),
            option=dict(type="str"),
            value=dict(type="str"),
            backup=dict(type="bool", default=False),
            state=dict(type="str", default="present", choices=["absent", "present"]),
        ),
        add_file_common_args=True,
        supports_check_mode=True,
        required_by=dict(
            option=("iface",),
        ),
    )

    dest = module.params["dest"]
    iface = module.params["iface"]
    address_family = module.params["address_family"]
    option = module.params["option"]
    value = module.params["value"]
    backup = module.params["backup"]
    state = module.params["state"]

    if option is not None and state == "present" and value is None:
        module.fail_json(msg="Value must be set if option is defined and state is 'present'")

    lines, ifaces = read_interfaces_file(module, dest)

    changed = False

    if option is not None:
        changed, lines = set_interface_option(module, lines, iface, option, value, state, address_family)

    if changed:
        dummy, ifaces = read_interfaces_lines(module, [d["line"] for d in lines if "line" in d])

    if changed and not module.check_mode:
        if backup:
            module.backup_local(dest)
        write_changes(module, [d["line"] for d in lines if "line" in d], dest)

    module.exit_json(dest=dest, changed=changed, ifaces=ifaces)


if __name__ == "__main__":
    main()
