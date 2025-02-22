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
  - Even if a unit has a RV(units.loadstate) of V(not-found) or V(masked), it is returned,
    but only with the minimal properties (RV(units.name), RV(units.loadstate), RV(units.activestate), RV(units.substate)).
  - When O(unitname) and O(extra_properties) are used, the module first checks if the unit exists,
    then check if properties exist. If not, the module fails.
version_added: "10.4.0"
options:
  unitname:
    description:
      - List of unit names to process.
      - It supports C(.service), C(.target), C(.socket), and C(.mount) units type.
      - Each name must correspond to the full name of the C(systemd) unit.
    type: list
    elements: str
    default: []
  extra_properties:
    description:
      - Additional properties to retrieve (appended to the default ones).
      - Note that all property names are converted to lower-case.
    type: list
    elements: str
    default: []
author:
  - Marco Noce (@NomakCooper)
extends_documentation_fragment:
  - community.general.attributes
  - community.general.attributes.info_module
'''

EXAMPLES = r'''
---
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
units:
  description:
    - Dictionary of systemd unit info keyed by unit name.
    - Additional fields will be returned depending on the value of O(extra_properties).
  returned: success
  type: dict
  elements: dict
  contains:
    name:
      description: Unit full name.
      returned: always
      type: str
      sample: systemd-journald.service
    loadstate:
      description:
        - The state of the unit's configuration load.
        - The most common values are V(loaded), V(not-found), and V(masked), but other values are possible as well.
      returned: always
      type: str
      sample: loaded
    activestate:
      description:
        - The current active state of the unit.
        - The most common values are V(active), V(inactive), and V(failed), but other values are possible as well.
      returned: always
      type: str
      sample: active
    substate:
      description:
        - The detailed sub state of the unit.
        - The most common values are V(running), V(dead), V(exited), V(failed), V(listening), V(active), and V(mounted), but other values are possible as well.
      returned: always
      type: str
      sample: running
    fragmentpath:
      description: Path to the unit's fragment file.
      returned: always except for C(.mount) units.
      type: str
      sample: /usr/lib/systemd/system/systemd-journald.service
    unitfilepreset:
      description:
        - The preset configuration state for the unit file.
        - The most common values are V(enabled), V(disabled), and V(static), but other values are possible as well.
      returned: always except for C(.mount) units.
      type: str
      sample: disabled
    unitfilestate:
      description:
        - The actual configuration state for the unit file.
        - The most common values are V(enabled), V(disabled), and V(static), but other values are possible as well.
      returned: always except for C(.mount) units.
      type: str
      sample: enabled
    mainpid:
      description: PID of the main process of the unit.
      returned: only for C(.service) units.
      type: str
      sample: 798
    execmainpid:
      description: PID of the ExecStart process of the unit.
      returned: only for C(.service) units.
      type: str
      sample: 799
    options:
      description: The mount options.
      returned: only for C(.mount) units.
      type: str
      sample: rw,relatime,noquota
    type:
      description: The filesystem type of the mounted device.
      returned: only for C(.mount) units.
      type: str
      sample: ext4
    what:
      description: The device that is mounted.
      returned: only for C(.mount) units.
      type: str
      sample: /dev/sda1
    where:
      description: The mount point where the device is mounted.
      returned: only for C(.mount) units.
      type: str
      sample: /
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

from ansible.module_utils.basic import AnsibleModule


def run_command(module, cmd):
    rc, stdout, stderr = module.run_command(cmd, check_rc=True)
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
    cmd = [systemctl_bin, "show", "-p", ",".join(prop_list), "--", unit]
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


def extract_unit_properties(unit_data, prop_list):
    lowerprop = [x.lower() for x in prop_list]
    extracted = {
        prop: unit_data[prop] for prop in lowerprop if prop in unit_data
    }
    return extracted


def unit_exists(module, systemctl_bin, unit):
    cmd = [systemctl_bin, "show", "-p", "LoadState", "--", unit]
    rc, stdout, stderr = module.run_command(cmd)
    return (rc == 0)


def validate_unit_and_properties(module, systemctl_bin, unit, extra_properties):
    cmd = [systemctl_bin, "show", "-p", "LoadState", "--", unit]

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

    systemctl_bin = module.get_bin_path('systemctl', required=True)

    run_command(module, [systemctl_bin, '--version'])

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
            full_props = set(props + state_props)
            unit_data = get_unit_properties(module, systemctl_bin, unit_name, full_props)

            fact.update(extract_unit_properties(unit_data, full_props))
            results[unit_name] = fact

    else:
        selected_units = module.params['unitname']
        extra_properties = module.params['extra_properties']

        for unit in selected_units:
            validate_unit_and_properties(module, systemctl_bin, unit, extra_properties)
            category = determine_category(unit)

            if not category:
                module.fail_json(msg="Could not determine the category for unit '{0}'.".format(unit))

            props = base_properties.get(category, [])
            full_props = set(props + state_props + extra_properties)
            unit_data = get_unit_properties(module, systemctl_bin, unit, full_props)
            fact = {"name": unit}
            minimal_keys = ["LoadState", "ActiveState", "SubState"]

            fact.update(extract_unit_properties(unit_data, minimal_keys))

            ls = unit_data.get("loadstate", "").lower()
            if ls not in ("not-found", "masked"):
                fact.update(extract_unit_properties(unit_data, full_props))

            results[unit] = fact

    module.exit_json(changed=False, units=results)


if __name__ == '__main__':
    main()
