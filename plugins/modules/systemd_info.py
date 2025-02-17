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
module: systemd_info
short_description: Gather C(systemd) unit info
description:
  - This module gathers info about systemd units (services, targets, sockets, mount).
  - It runs C(systemctl list-units) (or processes selected units) and collects properties
    for each unit using C(systemctl show).
  - Even if a unit has a loadstate of "not-found" or "masked", it is returned,
    but only with the minimal properties ( name, loadstate, activestate, substate).
  - When O(unitname) and O(extra_properties) are used, the module first checks if the unit exists,
    then check if properties exist. If not, module fail.
version_added: "10.4.0"
options:
  unitname:
    description:
      - List of unit names to process.
    type: list
    elements: str
    default: []
  extra_properties:
    description:
      - Additional properties to retrieve (appended to the default ones).
    type: list
    elements: str
    default: []
author:
  - Marco Noce (@NomakCooper)
'''

EXAMPLES = r'''
# Gather info for all systemd services, targets, sockets and mount
- name: Gather all systemd unit info
  community.general.systemd_info:
  register: results

# Gather info for selected units with extra properties.
- name: Gather info for selected unit(s)
  community.general.systemd_info:
    unitname:
      - systemd-journald.service
      - systemd-journald.socket
      - sshd-keygen.target
      - -.mount
    extra_properties:
        - Description
    register: results
'''

RETURN = r'''
resutls:
  description: Dictionary of systemd unit info keyed by unit name.
  returned: success
  type: dict
  sample: {
    "-.mount": {
        "activestate": "active",
        "description": "Root Mount",
        "loadstate": "loaded",
        "name": "-.mount",
        "options": "rw,relatime,seclabel,attr2,inode64,logbufs=8,logbsize=32k,noquota",
        "substate": "mounted",
        "type": "xfs",
        "what": "/dev/mapper/cs-root",
        "where": "/"
    },
    "sshd-keygen.target": {
        "activestate": "active",
        "description": "sshd-keygen.target",
        "fragmentpath": "/usr/lib/systemd/system/sshd-keygen.target",
        "loadstate": "loaded",
        "name": "sshd-keygen.target",
        "substate": "active",
        "unitfilepreset": "disabled",
        "unitfilestate": "static"
    },
    "systemd-journald.service": {
        "activestate": "active",
        "description": "Journal Service",
        "execmainpid": "613",
        "fragmentpath": "/usr/lib/systemd/system/systemd-journald.service",
        "loadstate": "loaded",
        "mainpid": "613",
        "name": "systemd-journald.service",
        "substate": "running",
        "unitfilepreset": "disabled",
        "unitfilestate": "static"
    },
    "systemd-journald.socket": {
        "activestate": "active",
        "description": "Journal Socket",
        "fragmentpath": "/usr/lib/systemd/system/systemd-journald.socket",
        "loadstate": "loaded",
        "name": "systemd-journald.socket",
        "substate": "running",
        "unitfilepreset": "disabled",
        "unitfilestate": "static"
    }
  }
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
            key = key.lower()
            if key not in result:
                result[key] = val
    return result


def get_unit_properties(module, systemctl_bin, unit, prop_list):
    if unit.startswith("-"):
        cmd = [systemctl_bin, "show", "-p", ",".join(prop_list), "--", unit]
    else:
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
    elif unit.endswith('.mount'):
        return 'mount'
    else:
        return None


def add_properties(fact, unit_data, prop_list):
    for prop in prop_list:
        key = prop.lower()
        if key in unit_data:
            fact[key] = unit_data[key]


def unit_exists(module, systemctl_bin, unit):
    if unit.startswith("-"):
        cmd = [systemctl_bin, "show", "-p", "LoadState", "--", unit]
    else:
        cmd = [systemctl_bin, "show", unit, "-p", "LoadState"]
    rc, stdout, stderr = module.run_command(cmd, use_unsafe_shell=True)
    return (rc == 0)


def validate_unit_and_properties(module, systemctl_bin, unit, extra_properties):
    if unit.startswith("-"):
        cmd = [systemctl_bin, "show", "-p", "LoadState", "--", unit]
    else:
        cmd = [systemctl_bin, "show", unit, "-p", "LoadState"]

    output = run_command(module, cmd)
    if "loadstate=not-found" in output.lower():
        module.fail_json(msg="Unit '{0}' does not exist or is inaccessible.".format(unit))

    if extra_properties:
        unit_data = get_unit_properties(module, systemctl_bin, unit, extra_properties)
        missing_props = [prop for prop in extra_properties if prop.lower() not in unit_data]
        if missing_props:
            module.fail_json(msg="The following properties do not exist for unit '{0}': {1}".format(unit, ", ".join(missing_props)))


def main():
    module_args = dict(
        unitname=dict(type='list', elements='str', default=[]),
        extra_properties=dict(type='list', elements='str', default=[])
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
        'socket': ['FragmentPath', 'UnitFileState', 'UnitFilePreset'],
        'mount': ['Where', 'What', 'Options', 'Type']
    }
    state_props = ['LoadState', 'ActiveState', 'SubState']

    results = {}

    if not module.params['unitname']:
        list_cmd = [
            systemctl_bin, "list-units",
            "--no-pager",
            "--type", "service,target,socket,mount",
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
                results[unit_name] = fact
                continue

            category = determine_category(unit_name)
            if not category:
                results[unit_name] = fact
                continue

            props = base_properties.get(category, [])
            full_props = list(set(props + state_props))
            unit_data = get_unit_properties(module, systemctl_bin, unit_name, full_props)
            add_properties(fact, unit_data, full_props)
            results[unit_name] = fact

    else:
        selected_units = module.params['unitname']
        extra_properties = module.params['extra_properties']
        if not selected_units:
            module.fail_json(msg="Provide at least one unit name in 'unitname'.")

        for unit in selected_units:
            validate_unit_and_properties(module, systemctl_bin, unit, extra_properties)
            category = determine_category(unit)
            if not category:
                module.fail_json(msg="Could not determine the category for unit '{0}'.".format(unit))
            props = base_properties.get(category, [])
            full_props = list(set(props + state_props + extra_properties))
            unit_data = get_unit_properties(module, systemctl_bin, unit, full_props)
            fact = {"name": unit}
            minimal_keys = ["LoadState", "ActiveState", "SubState"]
            add_properties(fact, unit_data, minimal_keys)
            ls = unit_data.get("loadstate", "").lower()
            if ls not in ("not-found", "masked"):
                add_properties(fact, unit_data, full_props)
            results[unit] = fact

    module.exit_json(changed=False, **results)


if __name__ == '__main__':
    main()
