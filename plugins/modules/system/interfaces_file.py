#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2016, Roman Belyakovsky <ihryamzik () gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: interfaces_file
short_description: Tweak settings in /etc/network/interfaces files
extends_documentation_fragment: files
description:
     - Manage (add, remove, change) individual interface options in an interfaces-style file without having
       to manage the file as a whole with, say, M(ansible.builtin.template) or M(ansible.builtin.assemble). Interface has to be presented in a file.
     - Read information about interfaces from interfaces-styled files
options:
  dest:
    type: path
    description:
      - Path to the interfaces file
    default: /etc/network/interfaces
  iface:
    type: str
    description:
      - Name of the interface, required for value changes or option remove
  address_family:
    type: str
    description:
      - Address family of the interface, useful if same interface name is used for both inet and inet6
  option:
    type: str
    description:
      - Name of the option, required for value changes or option remove
  value:
    type: str
    description:
      - If I(option) is not presented for the I(interface) and I(state) is C(present) option will be added.
        If I(option) already exists and is not C(pre-up), C(up), C(post-up) or C(down), it's value will be updated.
        C(pre-up), C(up), C(post-up) and C(down) options can't be updated, only adding new options, removing existing
        ones or cleaning the whole option set are supported
  backup:
    description:
      - Create a backup file including the timestamp information so you can get
        the original file back if you somehow clobbered it incorrectly.
    type: bool
    default: 'no'
  state:
    type: str
    description:
      - If set to C(absent) the option or section will be removed if present instead of created.
    default: "present"
    choices: [ "present", "absent" ]

notes:
   - If option is defined multiple times last one will be updated but all will be deleted in case of an absent state
requirements: []
author: "Roman Belyakovsky (@hryamzik)"
'''

RETURN = '''
dest:
    description: destination file/path
    returned: success
    type: str
    sample: "/etc/network/interfaces"
ifaces:
    description: interfaces dictionary
    returned: success
    type: complex
    contains:
      ifaces:
        description: interface dictionary
        returned: success
        type: dict
        contains:
          eth0:
            description: Name of the interface
            returned: success
            type: dict
            contains:
              address_family:
                description: interface address family
                returned: success
                type: str
                sample: "inet"
              method:
                description: interface method
                returned: success
                type: str
                sample: "manual"
              mtu:
                description: other options, all values returned as strings
                returned: success
                type: str
                sample: "1500"
              pre-up:
                description: list of C(pre-up) scripts
                returned: success
                type: list
                sample:
                  - "route add -net 10.10.10.0/24 gw 10.10.10.1 dev eth1"
                  - "route add -net 10.10.11.0/24 gw 10.10.11.1 dev eth2"
              up:
                description: list of C(up) scripts
                returned: success
                type: list
                sample:
                  - "route add -net 10.10.10.0/24 gw 10.10.10.1 dev eth1"
                  - "route add -net 10.10.11.0/24 gw 10.10.11.1 dev eth2"
              post-up:
                description: list of C(post-up) scripts
                returned: success
                type: list
                sample:
                  - "route add -net 10.10.10.0/24 gw 10.10.10.1 dev eth1"
                  - "route add -net 10.10.11.0/24 gw 10.10.11.1 dev eth2"
              down:
                description: list of C(down) scripts
                returned: success
                type: list
                sample:
                  - "route del -net 10.10.10.0/24 gw 10.10.10.1 dev eth1"
                  - "route del -net 10.10.11.0/24 gw 10.10.11.1 dev eth2"
...
'''

EXAMPLES = '''
- name: Set eth1 mtu configuration value to 8000
  community.general.interfaces_file:
    dest: /etc/network/interfaces.d/eth1.cfg
    iface: eth1
    option: mtu
    value: 8000
    backup: yes
    state: present
  register: eth1_cfg
'''

import os
import re
import tempfile

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_bytes


def line_dict(line):
    return {'line': line, 'line_type': 'unknown'}


def make_option_dict(line, iface, option, value, address_family):
    return {'line': line, 'iface': iface, 'option': option, 'value': value, 'line_type': 'option', 'address_family': address_family}


def get_option_value(line):
    patt = re.compile(r'^\s+(?P<option>\S+)\s+(?P<value>\S?.*\S)\s*$')
    match = patt.match(line)
    if not match:
        return None, None
    return match.group("option"), match.group("value")


def read_interfaces_file(module, filename):
    with open(filename, 'r') as f:
        return read_interfaces_lines(module, f)


def _is_line_processing_none(first_word):
    return first_word in ("source", "source-dir", "source-directory", "auto", "no-auto-down", "no-scripts") or first_word.startswith("auto-")


def read_interfaces_lines(module, line_strings):
    lines = []
    ifaces = {}
    iface_name = None
    address_family = None
    currif = {}
    currently_processing = None
    for i, line in enumerate(line_strings):
        words = line.split()
        if not words or words[0].startswith("#"):
            lines.append(line_dict(line))
            continue
        if words[0] == "mapping":
            lines.append(line_dict(line))
            currently_processing = "MAPPING"
        elif _is_line_processing_none(words[0]):
            lines.append(line_dict(line))
            currently_processing = "NONE"
        elif words[0] == "iface":
            currif = {
                "pre-up": [],
                "up": [],
                "down": [],
                "post-up": []
            }
            iface_name = words[1]
            try:
                currif['address_family'] = words[2]
            except IndexError:
                currif['address_family'] = None
            address_family = currif['address_family']
            try:
                currif['method'] = words[3]
            except IndexError:
                currif['method'] = None

            ifaces[iface_name] = currif
            lines.append({'line': line, 'iface': iface_name, 'line_type': 'iface', 'params': currif, 'address_family': address_family})
            currently_processing = "IFACE"
        else:
            if currently_processing == "IFACE":
                option_name, value = get_option_value(line)
                # TODO: if option_name in currif.options
                lines.append(make_option_dict(line, iface_name, option_name, value, address_family))
                if option_name in ["pre-up", "up", "down", "post-up"]:
                    currif[option_name].append(value)
                else:
                    currif[option_name] = value
            elif currently_processing == "MAPPING":
                lines.append(line_dict(line))
            elif currently_processing == "NONE":
                lines.append(line_dict(line))
            else:
                module.fail_json(msg="misplaced option %s in line %d" % (line, i + 1))

    return lines, ifaces


def set_interface_option(module, lines, iface, option, raw_value, state, address_family=None):
    value = str(raw_value)
    changed = False

    iface_lines = [item for item in lines if "iface" in item and item["iface"] == iface]
    if address_family is not None:
        iface_lines = [item for item in iface_lines
                       if "address_family" in item and item["address_family"] == address_family]

    if not iface_lines:
        # interface not found
        module.fail_json(msg="Error: interface %s not found" % iface)

    iface_options = [il for il in iface_lines if il['line_type'] == 'option']
    target_options = [io for io in iface_options if io['option'] == option]

    if state == "present":
        if not target_options:
            # add new option
            last_line_dict = iface_lines[-1]
            return add_option_after_line(option, value, iface, lines, last_line_dict, iface_options, address_family)

        if option in ["pre-up", "up", "down", "post-up"] and all(ito['value'] != value for ito in target_options):
            return add_option_after_line(option, value, iface, lines, target_options[-1], iface_options, address_family)

        # if more than one option found edit the last one
        if target_options[-1]['value'] != value:
            changed = True
            target_option = target_options[-1]
            old_line = target_option['line']
            old_value = target_option['value']
            address_family = target_option['address_family']
            prefix_start = old_line.find(option)
            option_len = len(option)
            old_value_position = re.search(r"\s+".join(map(re.escape, old_value.split())), old_line[prefix_start + option_len:])
            start = old_value_position.start() + prefix_start + option_len
            end = old_value_position.end() + prefix_start + option_len
            line = old_line[:start] + value + old_line[end:]
            index = len(lines) - lines[::-1].index(target_option) - 1
            lines[index] = make_option_dict(line, iface, option, value, address_family)
            return changed, lines

    if state == "absent":
        if target_options:
            if option in ["pre-up", "up", "down", "post-up"] and value is not None and value != "None":
                for target_option in [ito for ito in target_options if ito['value'] == value]:
                    changed = True
                    lines = [ln for ln in lines if ln != target_option]
            else:
                changed = True
                for target_option in target_options:
                    lines = [ln for ln in lines if ln != target_option]

    return changed, lines


def add_option_after_line(option, value, iface, lines, last_line_dict, iface_options, address_family):
    # Changing method of interface is not an addition
    if option == 'method':
        changed = False
        for ln in lines:
            if ln.get('line_type', '') == 'iface' and ln.get('iface', '') == iface and value != ln.get('params', {}).get('method', ''):
                changed = True
                ln['line'] = re.sub(ln.get('params', {}).get('method', '') + '$', value, ln.get('line'))
                ln['params']['method'] = value
        return changed, lines

    last_line = last_line_dict['line']
    prefix_start = last_line.find(last_line.split()[0])
    suffix_start = last_line.rfind(last_line.split()[-1]) + len(last_line.split()[-1])
    prefix = last_line[:prefix_start]

    if not iface_options:
        # interface has no options, ident
        prefix += "    "

    line = prefix + "%s %s" % (option, value) + last_line[suffix_start:]
    option_dict = make_option_dict(line, iface, option, value, address_family)
    index = len(lines) - lines[::-1].index(last_line_dict)
    lines.insert(index, option_dict)
    return True, lines


def write_changes(module, lines, dest):
    tmpfd, tmpfile = tempfile.mkstemp()
    with os.fdopen(tmpfd, 'wb') as f:
        f.write(to_bytes(''.join(lines), errors='surrogate_or_strict'))
    module.atomic_move(tmpfile, os.path.realpath(dest))


def main():
    module = AnsibleModule(
        argument_spec=dict(
            dest=dict(type='path', default='/etc/network/interfaces'),
            iface=dict(type='str'),
            address_family=dict(type='str'),
            option=dict(type='str'),
            value=dict(type='str'),
            backup=dict(type='bool', default=False),
            state=dict(type='str', default='present', choices=['absent', 'present']),
        ),
        add_file_common_args=True,
        supports_check_mode=True,
        required_by=dict(
            option=('iface',),
        ),
    )

    dest = module.params['dest']
    iface = module.params['iface']
    address_family = module.params['address_family']
    option = module.params['option']
    value = module.params['value']
    backup = module.params['backup']
    state = module.params['state']

    if option is not None and state == "present" and value is None:
        module.fail_json(msg="Value must be set if option is defined and state is 'present'")

    lines, ifaces = read_interfaces_file(module, dest)

    changed = False

    if option is not None:
        changed, lines = set_interface_option(module, lines, iface, option, value, state, address_family)

    if changed:
        dummy, ifaces = read_interfaces_lines(module, [d['line'] for d in lines if 'line' in d])

    if changed and not module.check_mode:
        if backup:
            module.backup_local(dest)
        write_changes(module, [d['line'] for d in lines if 'line' in d], dest)

    module.exit_json(dest=dest, changed=changed, ifaces=ifaces)


if __name__ == '__main__':
    main()
