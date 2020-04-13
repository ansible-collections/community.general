#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017-present Alibaba Group Holding Limited. He Guimin <heguimin36@163.com.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#
#  This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible. If not, see http://www.gnu.org/licenses/.


__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: ali_rds_database_info
version_added: "2.9"
short_description: Gather info on database of Alibaba Cloud RDS.
description:
     - Gather info on database of Alibaba Cloud RDS and Support use status, name_prefix
       to filter database.
options:
  db_instance_id:
    description:
      - The ID of the instance.
    aliases: ["instance_id"]
    required: True
    type: str
  db_status:
    description:
      - The status of the database.
    aliases: ["status"]
    type: str
  name_prefix:
    description:
      - Use a database name prefix to filter rds database.
    type: str
author:
    - "He Guimin (@xiaozhu36)"
requirements:
    - "python >= 3.6"
    - "footmark >= 1.16.0"
extends_documentation_fragment:
    - alicloud
'''

EXAMPLES = '''
- name: Get the existing database with name prefix
  ali_rds_database_info:
    name_prefix: ansible_
    db_instance_id: '{{ db_instance_id}}'

- name: Get the existing database with status
  ali_rds_database_info:
    db_status: creating
    db_instance_id: '{{ db_instance_id }}'

- name: Retrieving all database
  ali_rds_database_info:
    db_instance_id: '{{ db_instance_id }}'
'''

RETURN = '''
databases:
    description: Describe the info after operating database.
    returned: always
    type: complex
    contains:
        character_set_name:
            description: The character of database.
            returned: always
            type: string
            sample: utf8
        db_description:
            description: The description of database.
            returned: always
            type: string
            sample: test for ansible
        db_instance_id:
            description: The id of rds instance.
            returned: always
            type: string
            sample: rm-uf6wjk5xxxxxxx      
        db_name:
            description: The name of database.
            returned: always
            type: string
            sample: ansible_test
        db_status:
            description: The status of database.
            returned: always
            type: string
            sample: Creating
        description:
            description: alias of 'db_description'.
            returned: always
            type: string
            sample: test for ansible
        engine:
            description: The engine of database.
            returned: always
            type: string
            sample: MySQL
        name:
            description: alias of 'db_name'.
            returned: always
            type: string
            sample: ansible_test
        status:
            description: alias of 'db_status'.
            returned: always
            type: string
            sample: Creating
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.alicloud_ecs import ecs_argument_spec, rds_connect, vpc_connect

HAS_FOOTMARK = False

try:
    from footmark.exception import RDSResponseError
    HAS_FOOTMARK = True
except ImportError:
    HAS_FOOTMARK = False


def main():
    argument_spec = ecs_argument_spec()
    argument_spec.update(dict(
        db_instance_id=dict(type='str', aliases=['instance_id'], required=True),
        name_prefix=dict(type='str'),
        db_status=dict(type='str', aliases=['status'])
    ))
    module = AnsibleModule(argument_spec=argument_spec)
    rds = rds_connect(module)
    name_prefix = module.params['name_prefix']
    db_status = module.params['db_status']

    if HAS_FOOTMARK is False:
        module.fail_json(msg="Package 'footmark' required for this module.")

    result = []
    try:
        for db in rds.describe_databases(**module.params):
            if name_prefix and not db.dbname.startswith(name_prefix):
                continue
            if db_status and db.dbstatus.lower() != db_status.lower():
                continue
            result.append(db.read())
        module.exit_json(changed=False, databases=result)
    except Exception as e:
        module.fail_json(msg="Unable to describe rds database, and got an error: {0}.".format(e))


if __name__ == '__main__':
    main()
