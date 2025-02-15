#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2025, Marco Noce <nce.marco@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: systemd_facts
short_description: Gather C(systemd) unit facts.
description:
  - This module gathers facts about systemd units (services, targets, sockets).
  - It runs C(systemctl list-units) (or processes selected units) and collects properties
    for each unit using C(systemctl show).
  - Even if a unit has a loadstate of "not-found" or "masked", it is added to the fact,
    but only with the minimal properties ( name, loadstate, activestate, substate).
  - When O(select) is used, the module first checks if the unit exists. If not, the unit
    is recorded with minimal information.
  - The gathered information is added to ansible facts under the key systemd_units.
version_added: "10.4.0"
options:
  select:
    description:
      - When set to V(true), only the units specified in O(unitname) are processed.
    type: bool
    default: false
  unitname:
    description:
      - List of unit names to process when O(select) is V(true).
    type: list
    elements: str
    default: []
  properties:
    description:
      - Additional properties to retrieve (appended to the default ones).
    type: list
    elements: str
    default: []
author:
  - Marco Noce (@NomakCooper)
'''

EXAMPLES = r'''
# Gather facts for all systemd services, targets, and sockets
- name: Gather all systemd unit facts
  community.general.systemd_facts:

# Gather facts for selected units with extra properties.
- name: Gather facts for selected unit(s)
  community.general.systemd_facts:
    select: true
    unitname:
      - sshd.service
      - sshd-keygen.target
      - systemd-journald.socket
    properties:
      - Description
'''

RETURN = r'''
ansible_facts:
  description: Dictionary of systemd unit facts keyed by unit name.
  returned: always
  type: complex
  contains:
    systemd_units:
      description: Properties of systemd units
      returned: always
      type: list
      elements: dict
      contains:
        name:
          description: Unit name.
          returned: always
          type: str
          sample: sshd.service
        loadstate:
          description:
          - The state of the unit's configuration load
          - Either V(loaded), V(not-found), V(masked).
          returned: always
          type: str
          sample: running
        activestate:
          description:
          - The current active state of the unit.
          - Either V(active), V(inactive), V(failed).
          returned: always
          type: str
          sample: enabled
        substate:
          description:
          - The detailed state of the unit.
          - Either V(running), V(dead), V(exited), V(failed), V(listening), V(active).
          returned: always
          type: str
          sample: arp-ethers.service
        fragmentpath:
          description: The path to the unit file fragment.
          returned: always
          type: str
          sample: /usr/lib/systemd/system/sshd.service
        unitfilestate:
          description:
          - The state of the unit file
          - Either V(enabled), V(disabled).
          returned: always
          type: str
          sample: enabled
        unitfilepreset:
          description:
          - The preset configuration for the unit file.
          - Either V(enabled), V(disabled).
          returned: always
          type: str
          sample: disabled
        mainpid:
          description: The main process ID
          returned: Only for service units.
          type: str
          sample: 798
        execmainpid:
          description: The effective main process ID
          returned: Only for service units.
          type: str
          sample: 798
'''

import os
from ansible.module_utils.basic import AnsibleModule


def is_systemd():
    if os.path.exists("/run/systemd/system"):
        return True
    try:
        with open("/proc/1/comm", "r") as f:
            return f.read().strip() == "systemd"
    except Exception:
        return False


def run_command(module, cmd):
    rc, stdout, stderr = module.run_command(cmd, use_unsafe_shell=True)
    if rc != 0:
        module.fail_json(msg="Command '{0}' failed: {1}".format(" ".join(cmd), stderr.strip()))
    return stdout.strip()


def parse_show_output(output):
    result = {}
    for line in output.splitlines():
        if "=" in line:
            key, val = line.split("=", 1)
            result[key.lower()] = val
    return result


def get_unit_properties(module, systemctl_bin, unit, prop_list):
    cmd = [systemctl_bin, "show", unit, "-p", ",".join(prop_list)]
    output = run_command(module, cmd)
    return parse_show_output(output)


def determine_category(unit):
    if unit.endswith('.service'):
        return 'service'
    elif unit.endswith('.target'):
        return 'target'
    elif unit.endswith('.socket'):
        return 'socket'
    else:
        return None


def add_properties(fact, unit_data, prop_list):
    for prop in prop_list:
        key = prop.lower()
        if key in unit_data:
            fact[key] = unit_data[key]


def unit_exists(module, systemctl_bin, unit):
    rc, stdout, stderr = module.run_command([systemctl_bin, "show", unit, "-p", "LoadState"], use_unsafe_shell=True)
    return (rc == 0)


def main():
    module_args = dict(
        select=dict(type='bool', default=False),
        unitname=dict(type='list', elements='str', default=[]),
        properties=dict(type='list', elements='str', default=[])
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if not is_systemd():
        module.fail_json(msg="This module only runs on hosts using systemd as the init system.")

    systemctl_bin = module.get_bin_path('systemctl', required=True)

    base_properties = {
        'service': ['FragmentPath', 'UnitFileState', 'UnitFilePreset', 'MainPID', 'ExecMainPID'],
        'target': ['FragmentPath', 'UnitFileState', 'UnitFilePreset'],
        'socket': ['FragmentPath', 'UnitFileState', 'UnitFilePreset']
    }

    state_props = ['LoadState', 'ActiveState', 'SubState']

    systemd_units = {}

    if not module.params['select']:
        list_cmd = [
            systemctl_bin, "list-units",
            "--no-pager",
            "--type", "service,target,socket",
            "--all",
            "--plain",
            "--no-legend"
        ]
        list_output = run_command(module, list_cmd)
        for line in list_output.splitlines():
            tokens = line.split()

            if len(tokens) < 4:
                continue

            unit_name = tokens[0]
            loadstate = tokens[1]
            activestate = tokens[2]
            substate = tokens[3]

            fact = {
                "name": unit_name,
                "loadstate": loadstate,
                "activestate": activestate,
                "substate": substate
            }

            if loadstate in ("not-found", "masked"):
                systemd_units[unit_name] = fact
                continue

            category = determine_category(unit_name)
            if not category:
                systemd_units[unit_name] = fact
                continue

            props = base_properties.get(category, [])
            full_props = list(set(props + state_props))
            unit_data = get_unit_properties(module, systemctl_bin, unit_name, full_props)

            add_properties(fact, unit_data, full_props)
            systemd_units[unit_name] = fact

    else:
        selected_units = module.params['unitname']
        extra_properties = module.params['properties']
        if not selected_units:
            module.fail_json(msg="When select is true, provide at least one unit name in 'unitname'.")

        for unit in selected_units:
            if not unit_exists(module, systemctl_bin, unit):
                systemd_units[unit] = {"name": unit, "loadstate": "not-found", "activestate": "", "substate": ""}
                continue

            category = determine_category(unit)
            if not category:
                systemd_units[unit] = {"name": unit, "loadstate": "unknown", "activestate": "", "substate": ""}
                continue

            props = base_properties.get(category, [])
            full_props = list(set(props + state_props + extra_properties))
            unit_data = get_unit_properties(module, systemctl_bin, unit, full_props)

            fact = {"name": unit}
            minimal_keys = ["LoadState", "ActiveState", "SubState"]
            add_properties(fact, unit_data, minimal_keys)

            ls = unit_data.get("loadstate", "").lower()
            if ls not in ("not-found", "masked"):
                add_properties(fact, unit_data, full_props)
            systemd_units[unit] = fact

    module.exit_json(changed=False, ansible_facts={"systemd_units": systemd_units})


if __name__ == '__main__':
    main()
