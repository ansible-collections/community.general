#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Kamil Szczygiel <kamil.szczygiel () intel.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: influxdb_retention_policy
short_description: Manage InfluxDB retention policies
description:
    - Manage InfluxDB retention policies.
author: "Kamil Szczygiel (@kamsz)"
requirements:
    - "python >= 2.6"
    - "influxdb >= 0.9"
    - requests
options:
    database_name:
        description:
            - Name of the database.
        required: true
        type: str
    policy_name:
        description:
            - Name of the retention policy.
        required: true
        type: str
    state:
        description:
            - State of the retention policy.
        choices: [ absent, present ]
        default: present
        type: str
        version_added: 3.1.0
    duration:
        description:
            - Determines how long InfluxDB should keep the data. If specified, it
              should be C(INF) or at least one hour. If not specified, C(INF) is
              assumed. Supports complex duration expressions with multiple units.
            - Required only if I(state) is set to C(present).
        type: str
    replication:
        description:
            - Determines how many independent copies of each point are stored in the cluster.
            - Required only if I(state) is set to C(present).
        type: int
    default:
        description:
            - Sets the retention policy as default retention policy.
        type: bool
        default: false
    shard_group_duration:
        description:
            - Determines the time range covered by a shard group. If specified it
              must be at least one hour. If none, it's determined by InfluxDB by
              the rentention policy's duration. Supports complex duration expressions
              with multiple units.
        type: str
        version_added: '2.0.0'
extends_documentation_fragment:
- community.general.influxdb

'''

EXAMPLES = r'''
# Example influxdb_retention_policy command from Ansible Playbooks
- name: Create 1 hour retention policy
  community.general.influxdb_retention_policy:
      hostname: "{{ influxdb_ip_address }}"
      database_name: "{{ influxdb_database_name }}"
      policy_name: test
      duration: 1h
      replication: 1
      ssl: true
      validate_certs: true
      state: present

- name: Create 1 day retention policy with 1 hour shard group duration
  community.general.influxdb_retention_policy:
      hostname: "{{ influxdb_ip_address }}"
      database_name: "{{ influxdb_database_name }}"
      policy_name: test
      duration: 1d
      replication: 1
      shard_group_duration: 1h
      state: present

- name: Create 1 week retention policy with 1 day shard group duration
  community.general.influxdb_retention_policy:
      hostname: "{{ influxdb_ip_address }}"
      database_name: "{{ influxdb_database_name }}"
      policy_name: test
      duration: 1w
      replication: 1
      shard_group_duration: 1d
      state: present

- name: Create infinite retention policy with 1 week of shard group duration
  community.general.influxdb_retention_policy:
      hostname: "{{ influxdb_ip_address }}"
      database_name: "{{ influxdb_database_name }}"
      policy_name: test
      duration: INF
      replication: 1
      ssl: false
      validate_certs: false
      shard_group_duration: 1w
      state: present

- name: Create retention policy with complex durations
  community.general.influxdb_retention_policy:
      hostname: "{{ influxdb_ip_address }}"
      database_name: "{{ influxdb_database_name }}"
      policy_name: test
      duration: 5d1h30m
      replication: 1
      ssl: false
      validate_certs: false
      shard_group_duration: 1d10h30m
      state: present

- name: Drop retention policy
  community.general.influxdb_retention_policy:
      hostname: "{{ influxdb_ip_address }}"
      database_name: "{{ influxdb_database_name }}"
      policy_name: test
      state: absent
'''

RETURN = r'''
# only defaults
'''

import re

try:
    import requests.exceptions
    from influxdb import exceptions
except ImportError:
    pass

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.influxdb import InfluxDb
from ansible.module_utils.common.text.converters import to_native


VALID_DURATION_REGEX = re.compile(r'^(INF|(\d+(ns|u|µ|ms|s|m|h|d|w)))+$')

DURATION_REGEX = re.compile(r'(\d+)(ns|u|µ|ms|s|m|h|d|w)')
EXTENDED_DURATION_REGEX = re.compile(r'(?:(\d+)(ns|u|µ|ms|m|h|d|w)|(\d+(?:\.\d+)?)(s))')

DURATION_UNIT_NANOSECS = {
    'ns': 1,
    'u': 1000,
    'µ': 1000,
    'ms': 1000 * 1000,
    's': 1000 * 1000 * 1000,
    'm': 1000 * 1000 * 1000 * 60,
    'h': 1000 * 1000 * 1000 * 60 * 60,
    'd': 1000 * 1000 * 1000 * 60 * 60 * 24,
    'w': 1000 * 1000 * 1000 * 60 * 60 * 24 * 7,
}

MINIMUM_VALID_DURATION = 1 * DURATION_UNIT_NANOSECS['h']
MINIMUM_VALID_SHARD_GROUP_DURATION = 1 * DURATION_UNIT_NANOSECS['h']


def check_duration_literal(value):
    return VALID_DURATION_REGEX.search(value) is not None


def parse_duration_literal(value, extended=False):
    duration = 0.0

    if value == "INF":
        return duration

    lookup = (EXTENDED_DURATION_REGEX if extended else DURATION_REGEX).findall(value)

    for duration_literal in lookup:
        filtered_literal = list(filter(None, duration_literal))
        duration_val = float(filtered_literal[0])
        duration += duration_val * DURATION_UNIT_NANOSECS[filtered_literal[1]]

    return duration


def find_retention_policy(module, client):
    database_name = module.params['database_name']
    policy_name = module.params['policy_name']
    hostname = module.params['hostname']
    retention_policy = None

    try:
        retention_policies = client.get_list_retention_policies(database=database_name)
        for policy in retention_policies:
            if policy['name'] == policy_name:
                retention_policy = policy
                break
    except requests.exceptions.ConnectionError as e:
        module.fail_json(msg="Cannot connect to database %s on %s : %s" % (database_name, hostname, to_native(e)))

    if retention_policy is not None:
        retention_policy["duration"] = parse_duration_literal(retention_policy["duration"], extended=True)
        retention_policy["shardGroupDuration"] = parse_duration_literal(retention_policy["shardGroupDuration"], extended=True)

    return retention_policy


def create_retention_policy(module, client):
    database_name = module.params['database_name']
    policy_name = module.params['policy_name']
    duration = module.params['duration']
    replication = module.params['replication']
    default = module.params['default']
    shard_group_duration = module.params['shard_group_duration']

    if not check_duration_literal(duration):
        module.fail_json(msg="Failed to parse value of duration")

    influxdb_duration_format = parse_duration_literal(duration)
    if influxdb_duration_format != 0 and influxdb_duration_format < MINIMUM_VALID_DURATION:
        module.fail_json(msg="duration value must be at least 1h")

    if shard_group_duration is not None:
        if not check_duration_literal(shard_group_duration):
            module.fail_json(msg="Failed to parse value of shard_group_duration")

        influxdb_shard_group_duration_format = parse_duration_literal(shard_group_duration)
        if influxdb_shard_group_duration_format < MINIMUM_VALID_SHARD_GROUP_DURATION:
            module.fail_json(msg="shard_group_duration value must be finite and at least 1h")

    if not module.check_mode:
        try:
            if shard_group_duration:
                client.create_retention_policy(policy_name, duration, replication, database_name, default,
                                               shard_group_duration)
            else:
                client.create_retention_policy(policy_name, duration, replication, database_name, default)
        except exceptions.InfluxDBClientError as e:
            module.fail_json(msg=e.content)
    module.exit_json(changed=True)


def alter_retention_policy(module, client, retention_policy):
    database_name = module.params['database_name']
    policy_name = module.params['policy_name']
    duration = module.params['duration']
    replication = module.params['replication']
    default = module.params['default']
    shard_group_duration = module.params['shard_group_duration']

    changed = False

    if not check_duration_literal(duration):
        module.fail_json(msg="Failed to parse value of duration")

    influxdb_duration_format = parse_duration_literal(duration)
    if influxdb_duration_format != 0 and influxdb_duration_format < MINIMUM_VALID_DURATION:
        module.fail_json(msg="duration value must be at least 1h")

    if shard_group_duration is None:
        influxdb_shard_group_duration_format = retention_policy["shardGroupDuration"]
    else:
        if not check_duration_literal(shard_group_duration):
            module.fail_json(msg="Failed to parse value of shard_group_duration")

        influxdb_shard_group_duration_format = parse_duration_literal(shard_group_duration)
        if influxdb_shard_group_duration_format < MINIMUM_VALID_SHARD_GROUP_DURATION:
            module.fail_json(msg="shard_group_duration value must be finite and at least 1h")

    if (retention_policy['duration'] != influxdb_duration_format or
            retention_policy['shardGroupDuration'] != influxdb_shard_group_duration_format or
            retention_policy['replicaN'] != int(replication) or
            retention_policy['default'] != default):
        if not module.check_mode:
            try:
                client.alter_retention_policy(policy_name, database_name, duration, replication, default,
                                              shard_group_duration)
            except exceptions.InfluxDBClientError as e:
                module.fail_json(msg=e.content)
        changed = True
    module.exit_json(changed=changed)


def drop_retention_policy(module, client):
    database_name = module.params['database_name']
    policy_name = module.params['policy_name']

    if not module.check_mode:
        try:
            client.drop_retention_policy(policy_name, database_name)
        except exceptions.InfluxDBClientError as e:
            module.fail_json(msg=e.content)
    module.exit_json(changed=True)


def main():
    argument_spec = InfluxDb.influxdb_argument_spec()
    argument_spec.update(
        state=dict(default='present', type='str', choices=['present', 'absent']),
        database_name=dict(required=True, type='str'),
        policy_name=dict(required=True, type='str'),
        duration=dict(type='str'),
        replication=dict(type='int'),
        default=dict(default=False, type='bool'),
        shard_group_duration=dict(type='str'),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=(
            ('state', 'present', ['duration', 'replication']),
        ),
    )

    state = module.params['state']

    influxdb = InfluxDb(module)
    client = influxdb.connect_to_influxdb()

    retention_policy = find_retention_policy(module, client)

    if state == 'present':
        if retention_policy:
            alter_retention_policy(module, client, retention_policy)
        else:
            create_retention_policy(module, client)

    if state == 'absent':
        if retention_policy:
            drop_retention_policy(module, client)
        else:
            module.exit_json(changed=False)


if __name__ == '__main__':
    main()
