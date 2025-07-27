#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2025, Marco Noce <nce.marco@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: systemd_info
short_description: Gather C(systemd) unit info
description:
  - This module gathers info about systemd units (services, targets, sockets, mounts, timers).
  - Timer units are supported since community.general 10.5.0.
  - It runs C(systemctl list-units) (or processes selected units) and collects properties for each unit using C(systemctl
    show).
  - In case a unit has multiple properties with the same name, only the value of the first one is collected.
  - Even if a unit has a RV(units.loadstate) of V(not-found) or V(masked), it is returned, but only with the minimal properties
    (RV(units.name), RV(units.loadstate), RV(units.activestate), RV(units.substate)).
  - When O(unitname) and O(extra_properties) are used, the module first checks if the unit exists, then check if properties
    exist. If not, the module fails.
  - When O(unitname) is used with wildcard expressions, the module checks for units that match the indicated expressions,
    if units are not present for all the indicated expressions, the module fails.
version_added: "10.4.0"
options:
  unitname:
    description:
      - List of unit names to process.
      - It supports C(.service), C(.target), C(.socket), C(.mount) and C(.timer) units type.
      - C(.timer) units are supported since community.general 10.5.0.
      - Each name must correspond to the full name of the C(systemd) unit or to a wildcard expression like V('ssh*') and V('*.service').
      - Wildcard expressions in O(unitname) are supported since community.general 10.5.0.
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
"""

EXAMPLES = r"""
---
# Gather info for all systemd services, targets, sockets, mount and timer
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

# Gather info using wildcards/expression
- name: Gather info of units that start with 'systemd-'
  community.general.systemd_info:
    unitname:
      - 'systemd-*'
  register: results

# Gather info for systemd-tmpfiles-clean.timer with extra properties
- name: Gather info of systemd-tmpfiles-clean.timer and extra AccuracyUSec
  community.general.systemd_info:
    unitname:
      - systemd-tmpfiles-clean.timer
    extra_properties:
      - AccuracyUSec
  register: results
"""

RETURN = r"""
units:
  description:
    - Dictionary of systemd unit info keyed by unit name.
    - Additional fields are returned depending on the value of O(extra_properties).
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
        - The most common values are V(running), V(dead), V(exited), V(failed), V(listening), V(active), and V(mounted), but
          other values are possible as well.
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
  sample:
    {
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
"""

import fnmatch
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.systemd import systemd_runner


def get_version(runner):
    with runner("version") as ctx:
        rc, stdout, stderr = ctx.run()
    return stdout.strip()


def list_units(runner, types_value):
    context = "list_units types all plain no_legend"
    with runner(context) as ctx:
        rc, stdout, stderr = ctx.run(types=types_value)
    return stdout.strip()


def show_unit_properties(runner, prop_list, unit):
    context = "show props dashdash unit"
    with runner(context) as ctx:
        rc, stdout, stderr = ctx.run(props=prop_list, unit=unit)
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


def get_unit_properties(runner, prop_list, unit):
    output = show_unit_properties(runner, prop_list, unit)
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
    elif unit.endswith('.timer'):
        return 'timer'
    else:
        return None


def extract_unit_properties(unit_data, prop_list):
    lowerprop = [x.lower() for x in prop_list]
    return {prop: unit_data[prop] for prop in lowerprop if prop in unit_data}


def unit_exists(unit, units_info):
    info = units_info.get(unit, {})
    loadstate = info.get("loadstate", "").lower()
    return loadstate not in ("not-found", "masked")


def get_category_base_props(category):
    base_props = {
        'service': ['FragmentPath', 'UnitFileState', 'UnitFilePreset', 'MainPID', 'ExecMainPID'],
        'target': ['FragmentPath', 'UnitFileState', 'UnitFilePreset'],
        'socket': ['FragmentPath', 'UnitFileState', 'UnitFilePreset'],
        'mount': ['Where', 'What', 'Options', 'Type'],
        'timer': ['FragmentPath', 'UnitFileState', 'UnitFilePreset'],
    }
    return base_props.get(category, [])


def validate_unit_and_properties(runner, unit, extra_properties, units_info, property_cache):
    if not unit_exists(unit, units_info):
        module.fail_json(msg="Unit '{0}' does not exist or is inaccessible.".format(unit))

    category = determine_category(unit)

    if not category:
        module.fail_json(msg="Could not determine the category for unit '{0}'.".format(unit))

    state_props = ['LoadState', 'ActiveState', 'SubState']
    props = get_category_base_props(category)
    full_props = set(props + state_props + extra_properties)

    if unit not in property_cache:
        unit_data = get_unit_properties(runner, full_props, unit)
        property_cache[unit] = unit_data
    else:
        unit_data = property_cache[unit]
    if extra_properties:
        missing_props = [prop for prop in extra_properties if prop.lower() not in unit_data]
        if missing_props:
            module.fail_json(msg="The following properties do not exist for unit '{0}': {1}".format(unit, ", ".join(missing_props)))

    return True


def process_wildcards(selected_units, all_units, module):
    resolved_units = {}
    non_matching_patterns = []

    for pattern in selected_units:
        matches = fnmatch.filter(all_units, pattern)
        if not matches:
            non_matching_patterns.append(pattern)
        else:
            for match in matches:
                resolved_units[match] = True

    if not resolved_units:
        module.fail_json(msg="No units match any of the provided patterns: {}".format(", ".join(non_matching_patterns)))

    return resolved_units, non_matching_patterns


def process_unit(runner, unit, extra_properties, units_info, property_cache, state_props):
    if not unit_exists(unit, units_info):
        return units_info.get(unit, {"name": unit, "loadstate": "not-found"})

    validate_unit_and_properties(runner, unit, extra_properties, units_info, property_cache)
    category = determine_category(unit)

    if not category:
        module.fail_json(msg="Could not determine the category for unit '{0}'.".format(unit))

    props = get_category_base_props(category)
    full_props = set(props + state_props + extra_properties)
    unit_data = property_cache[unit]
    fact = {"name": unit}
    minimal_keys = ["LoadState", "ActiveState", "SubState"]
    fact.update(extract_unit_properties(unit_data, minimal_keys))
    ls = unit_data.get("loadstate", "").lower()

    if ls not in ("not-found", "masked"):
        fact.update(extract_unit_properties(unit_data, full_props))

    return fact


def main():
    global module
    module_args = dict(
        unitname=dict(type='list', elements='str', default=[]),
        extra_properties=dict(type='list', elements='str', default=[])
    )
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
    systemctl_bin = module.get_bin_path('systemctl', required=True)

    base_runner = systemd_runner(module, systemctl_bin)

    get_version(base_runner)

    state_props = ['LoadState', 'ActiveState', 'SubState']
    results = {}

    unit_types = ["service", "target", "socket", "mount", "timer"]

    list_output = list_units(base_runner, unit_types)
    units_info = {}
    for line in list_output.splitlines():
        tokens = line.split()
        if len(tokens) < 4:
            continue
        unit_name = tokens[0]
        loadstate = tokens[1]
        activestate = tokens[2]
        substate = tokens[3]
        units_info[unit_name] = {
            "name": unit_name,
            "loadstate": loadstate,
            "activestate": activestate,
            "substate": substate,
        }

    property_cache = {}
    extra_properties = module.params['extra_properties']

    if module.params['unitname']:
        selected_units = module.params['unitname']
        all_units = list(units_info)
        resolved_units, non_matching = process_wildcards(selected_units, all_units, module)
        units_to_process = sorted(resolved_units)
    else:
        units_to_process = list(units_info)

    for unit in units_to_process:
        results[unit] = process_unit(base_runner, unit, extra_properties, units_info, property_cache, state_props)
    module.exit_json(changed=False, units=results)


if __name__ == '__main__':
    main()
