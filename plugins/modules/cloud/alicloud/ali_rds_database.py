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

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: ali_rds_database
short_description: Create, delete or copy an database in Alibaba Cloud RDS.
description:
    - Create, delete, copy or modify description for database in RDS.
    - An unique ali_rds_database module is co-determined by parameters db_instance_id and db_name.
options:
  state:
    description:
      - If I(state=present), database will be created.
      - If I(state=present) and db_description exists, it will modify description.
      - If I(state=present) and target_db_instance_id,target_db_name exists, it will copy database between instances.
      - If I(state=absent), database will be removed.
    default: 'present'
    choices: ['present', 'absent']
    type: str
  db_instance_id:
    description:
      - rds instance id.
      - This is used in combination with C(db_name) to determine if the database already exists.
    aliases: ['instance_id']
    required: True
    type: str
  db_name:
    description:
      - database name. It must be 2 to 64 characters in length.It must start with a lowercase letter and end with a
        lowercase letter or digit. It can contain lowercase letters, digits, underscores (_), and hyphens (-).
        this will specify unique database in one instance.
        For more information about invalid characters, see Forbidden keywords table U(https://www.alibabacloud.com/help/doc-detail/26317.htm).
      - This is used in combination with C(db_instance_id) to determine if the database already exists.
    aliases: ['name']
    required: True
    type: str
  character_set_name:
    description:
      - database character name. MySQL or MariaDB (utf8 | gbk | latin1 | utf8mb4).
        SQL Server (Chinese_PRC_CI_AS | Chinese_PRC_CS_AS | SQL_Latin1_General_CP1_CI_AS | SQL_Latin1_General_CP1_CS_AS | Chinese_PRC_BIN).
        see more U(https://www.alibabacloud.com/help/doc-detail/26258.htm).
        Required when C(state=present).
    aliases: ['character']
    type: str
  db_description:
    description:
      - The description of the database. It must be 2 to 256 characters in length.
        It can contain letters, digits, underscores (_), and hyphens (-), and must start with a letter.
    aliases: ['description']
    type: str
  target_db_instance_id:
    description:
      - The ID of the destination instance, which must differ from the ID of the source instance.
    aliases: ['target_instance_id']
    type: str
  target_db_name:
    description:
      - Target instance database name.
    type: str
  backup_id:
    description:
      - The ID of the backup set on the source instance. When you copy databases based on the backup set.
    type: str
  restore_time:
    description:
      - The time when the system copies the database. You can select any time within the backup retention period.
    type: str
  sync_user_privilege:
    description:
      - Indicates whether to copy users and permissions.
    type: bool
    default: False
author:
    - "He Guimin (@xiaozhu36)"
    - "Li Xue (@lixue323)"
requirements:
    - "python >= 3.6"
    - "footmark >= 1.16.0"
extends_documentation_fragment:
    - alicloud
'''

EXAMPLES = '''
# Note: These examples do not set authentication details, see the Alibaba Cloud Guide for details.
- name: Create Database
  ali_rds_database:
    db_instance_id: '{{ db_instance_id }}'
    db_name: ansible
    character_set_name: utf8
    db_description: create for ansible
    state: present

- name: Changed. Modify db description.
  ali_rds_database:
    db_instance_id: '{{ db_instance_id }}'
    db_name: ansible
    db_description: modify db description

- name: Changed. Copy Database Between Instances
  ali_rds_database:
    db_instance_id: '{{ db_instance_id }}'
    db_name: '{{ db_name }}'
    target_db_instance_id: '{{ target_db_instance_id }}'
    target_db_name: '{{ target_db_name }}'

- name: Changed. Deleting database
  ali_rds_database:
    state: absent
    db_instance_id: '{{ db_instance_id }}'
    db_name: ansible
'''

RETURN = '''
database:
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
            sample: create for ansible
        db_instance_id:
            description: The id of rds instance.
            returned: always
            type: string
            sample: rm-uf6wjk5xxxxxxx  
        db_name:
            description: The name of database.
            returned: always
            type: string
            sample: ansible
        db_status:
            description: The status of database.
            returned: always
            type: string
            sample: Creating
        description:
            description: alias of 'db_description'.
            returned: always
            type: string
            sample: create for ansible
        engine:
            description: The engine of database.
            returned: always
            type: string
            sample: MySQL
        name:
            description: alias of 'db_name'.
            returned: always
            type: string
            sample: ansible
        status:
            description: alias of 'db_status'.
            returned: always
            type: string
            sample: Creating
'''

import time
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.alicloud_ecs import ecs_argument_spec, rds_connect, vpc_connect

HAS_FOOTMARK = False

try:
    from footmark.exception import ECSResponseError
    HAS_FOOTMARK = True
except ImportError:
    HAS_FOOTMARK = False


def database_exists(modules, rds):
    name = modules.params['db_name']
    match = ''
    for db in rds.describe_databases(db_instance_id=modules.params['db_instance_id']):
        if db.name == name:
            match = db
    return match


def main():
    argument_spec = ecs_argument_spec()
    argument_spec.update(dict(
        state=dict(default="present", choices=["present", "absent"]),
        db_instance_id=dict(type='str', aliases=['instance_id'], required=True),
        db_name=dict(type='str', aliases=['name'], required=True),
        character_set_name=dict(type='str', aliases=['character']),
        db_description=dict(type='str', aliases=['description']),
        target_db_instance_id=dict(type='str', aliases=['target_instance_id']),
        target_db_name=dict(type='str'),
        backup_id=dict(type='str'),
        restore_time=dict(type='str'),
        sync_user_privilege=dict(type='bool', default=False)
    ))
    modules = AnsibleModule(argument_spec=argument_spec)

    if HAS_FOOTMARK is False:
        modules.fail_json(msg="Package 'footmark' required for this module")

    rds = rds_connect(modules)
    state = modules.params['state']
    db_description = modules.params['db_description']
    target_db_instance_id = modules.params['target_db_instance_id']
    target_db_name = modules.params['target_db_name']
    db_name = modules.params['db_name']
    sync_user_privilege = modules.params['sync_user_privilege']
    modules.params['sync_user_privilege'] = 'NO'
    if sync_user_privilege:
        modules.params['sync_user_privilege'] = 'YES'
    db = ''
    try:
        db = database_exists(modules, rds)
    except Exception as e:
        modules.fail_json(msg=str("Unable to describe database, error:{0}".format(e)))

    if state == 'absent':
        if not db:
            modules.exit_json(changed=False, database={})
        try:
            db.delete()
            modules.exit_json(changed=True, database={})
        except Exception as e:
            modules.fail_json(msg=str("Unable to delete database error: {0}".format(e)))

    if not db:
        try:
            modules.params['client_token'] = "Ansible-Alicloud-%s-%s" % (hash(str(modules.params)), str(time.time()))
            db = rds.create_database(**modules.params)
            modules.exit_json(changed=True, database=db.read())
        except Exception as e:
            modules.fail_json(msg=str("Unable to create database error: {0}".format(e)))

    if db_description:
        try:
            res = db.modify_db_description(description=db_description)
            modules.exit_json(changed=res, database=db.read())
        except Exception as e:
            modules.fail_json(msg=str("Unable to modify db description error: {0}".format(e)))

    if target_db_instance_id and target_db_name:
        try:
            modules.params['db_names'] = str({db_name: target_db_name})
            res = db.copy_database_between_instances(**modules.params)
            modules.exit_json(changed=res, database=db.read())
        except Exception as e:
            modules.fail_json(msg=str("Unable to copy db instance id error: {0}".format(e)))


if __name__ == '__main__':
    main()
