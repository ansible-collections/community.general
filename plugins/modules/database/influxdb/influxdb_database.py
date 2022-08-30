#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Kamil Szczygiel <kamil.szczygiel () intel.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: influxdb_database
short_description: Manage InfluxDB databases
description:
    - Manage InfluxDB databases.
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
    state:
        description:
            - Determines if the database should be created or destroyed.
        choices: [ absent, present ]
        default: present
        type: str
extends_documentation_fragment:
- community.general.influxdb

'''

EXAMPLES = r'''
# Example influxdb_database command from Ansible Playbooks
- name: Create database
  community.general.influxdb_database:
      hostname: "{{influxdb_ip_address}}"
      database_name: "{{influxdb_database_name}}"

- name: Destroy database
  community.general.influxdb_database:
      hostname: "{{influxdb_ip_address}}"
      database_name: "{{influxdb_database_name}}"
      state: absent

- name: Create database using custom credentials
  community.general.influxdb_database:
      hostname: "{{influxdb_ip_address}}"
      username: "{{influxdb_username}}"
      password: "{{influxdb_password}}"
      database_name: "{{influxdb_database_name}}"
      ssl: true
      validate_certs: true
'''

RETURN = r'''
# only defaults
'''

try:
    import requests.exceptions
    from influxdb import exceptions
except ImportError:
    pass

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.influxdb import InfluxDb


def find_database(module, client, database_name):
    database = None

    try:
        databases = client.get_list_database()
        for db in databases:
            if db['name'] == database_name:
                database = db
                break
    except requests.exceptions.ConnectionError as e:
        module.fail_json(msg=str(e))
    return database


def create_database(module, client, database_name):
    if not module.check_mode:
        try:
            client.create_database(database_name)
        except requests.exceptions.ConnectionError as e:
            module.fail_json(msg=str(e))

    module.exit_json(changed=True)


def drop_database(module, client, database_name):
    if not module.check_mode:
        try:
            client.drop_database(database_name)
        except exceptions.InfluxDBClientError as e:
            module.fail_json(msg=e.content)

    module.exit_json(changed=True)


def main():
    argument_spec = InfluxDb.influxdb_argument_spec()
    argument_spec.update(
        database_name=dict(required=True, type='str'),
        state=dict(default='present', type='str', choices=['present', 'absent'])
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    state = module.params['state']

    influxdb = InfluxDb(module)
    client = influxdb.connect_to_influxdb()
    database_name = influxdb.database_name
    database = find_database(module, client, database_name)

    if state == 'present':
        if database:
            module.exit_json(changed=False)
        else:
            create_database(module, client, database_name)

    if state == 'absent':
        if database:
            drop_database(module, client, database_name)
        else:
            module.exit_json(changed=False)


if __name__ == '__main__':
    main()
