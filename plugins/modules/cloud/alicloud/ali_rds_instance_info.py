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
module: ali_rds_instance_info
short_description: Gather info on rds instance in Alibaba Cloud.
description:
     - Gather info on rds instance in Alibaba Cloud and Support use tags, name_prefix to
       filter rds.
options:
  name_prefix:
    description:
      - Use instance name prefix to filter rds.
    type: str
  tags:
    description:
      - A hash/dictionaries of rds tags. C({"key":"value"}).
    type: dict
author:
    - "He Guimin (@xiaozhu36)"
requirements:
    - "python >= 3.6"
    - "footmark >= 1.16.0"
extends_documentation_fragment:
    - community.general.alicloud
'''

EXAMPLES = '''
- name: Get the existing rds with name prefix
  ali_rds_instance_info:
    name_prefix: ansible_rds

- name: Retrieving all rds
  ali_rds_instance_info: 
'''

RETURN = '''
instances:
    description: Describe the info after operating rds instance.
    returned: always
    type: complex
    contains:
        db_instance_class:
            description: The type of the instance.
            returned: always
            type: string
            sample: rds.mysql.t1.small
        db_instance_description:
            description: The description of the instance.
            returned: always
            type: string
            sample: ansible_test_rds
        db_instance_id:
            description: The ID of the instance.
            returned: always
            type: string
            sample: rm-uf6wjk5xxxxxxxxxx
        db_instance_net_type:
            description: The network type of the instance.
            returned: always
            type: string
            sample: Internet
        db_instance_status:
            description: The status of the instance.
            returned: always
            type: string
            sample: Running
        db_instance_type:
            description: The type of the instance role.
            returned: always
            type: string
            sample: Primary
        engine:
            description: The type of the database.
            returned: always
            type: string
            sample: MySQL
        engine_version:
            description: The version of the database.
            returned: always
            type: string
            sample: 5.6
        id:
            description: alias of 'db_instance_id'.
            returned: always
            type: string
            sample: rm-uf6wjk5xxxxxxxxxx
        type:
            description: alias of 'db_instance_type'.
            returned: always
            type: string
            sample: Primary
        instance_network_type:
            description: The network type of the instance.
            returned: always
            type: string
            sample: VPC
        name:
            description: alias of 'db_instance_description'.
            returned: always
            type: string
            sample: ansible_test_rds
        pay_type:
            description: The billing method of the instance.
            returned: always
            type: string
            sample: Postpaid
        resource_group_id:
            description: The ID of the resource group.
            returned: always
            type: string
            sample: rg-acfmyxxxxxxx
        status:
            description: alias of 'db_instance_status'
            returned: always
            type: string
            sample: Running
        vpc_cloud_instance_id:
            description: The ID of the VPC instance
            returned: always
            type: string
            sample: rm-uf6wjk5xxxxxxx
        vpc_id:
            description: The ID of the VPC.
            returned: always
            type: string
            sample: vpc-uf6f7l4fg90xxxxxxx
        vswitch_id:
            description: The ID of the VSwitch.
            returned: always
            type: string
            sample: vsw-uf6adz52c2pxxxxxxx
        lock_mode:
            description: The lock mode of the instance.
            returned: always
            type: string
            sample: Unlock
        connection_mode:
            description: The access mode of the instance.
            returned: always
            type: string
            sample: Standard
        account_max_quantity:
            description: The maximum number of accounts that can be created in an instance.
            returned: always
            type: int
            sample: 50
        account_type:
            description: The type of the account.
            returned: always
            type: string
            sample: Mix
        auto_upgrade_minor_version:
            description: The method of upgrading an instance to a minor version.
            returned: always
            type: string
            sample: Auto
        availability_value:
            description: The availability of the instance.
            returned: always
            type: string
            sample: 100.0%
        category:
            description: The edition (series) of the instance.
            returned: always
            type: string
            sample: Basic
        connection_string:
            description: The private IP address of the instance.
            returned: always
            type: string
            sample: rm-uf6wjk5xxxxxxxxxx.mysql.rds.aliyuncs.com
        creation_time:
            description: The time when the instance is created
            returned: always
            type: string
            sample: 2011-05-30T12:11:04Z
        current_kernel_version:
            description: The current kernel version.
            returned: always
            type: string
            sample: rds_20181010
        db_instance_class_type:
            description: The instance type (specifications).
            returned: always
            type: string
            sample: rds.mys2.small
        db_instance_cpu:
            description: The count of the instance cpu.
            returned: always
            type: int
            sample: 2
        db_instance_memory:
            description: The memory of the instance.
            returned: always
            type: int
            sample: 4096
        db_instance_storage:
            description: The type of the instance.
            returned: always
            type: string
            sample: rds.mysql.t1.small
        db_instance_storage_type:
            description: The storage capacity of the instance.
            returned: always
            type: int
            sample: 10
        db_max_quantity:
            description: The maximum number of databases that can be created in an instance.
            returned: always
            type: int
            sample: 200
        dispense_mode:
            description: The allocation mode.
            returned: always
            type: string
            sample: ClassicDispenseMode
        expire_time:
            description: The expiration time.
            returned: always
            type: string
            sample: 2019-03-27T16:00:00Z
        maintain_time:
            description: The maintenance period of the instance.
            returned: always
            type: string
            sample: 00:00Z-02:00Z
        max_connections:
            description: The maximum number of concurrent connections.
            returned: always
            type: int
            sample: 60
        max_iops:
            description: The maximum number of I/O requests per second.
            returned: always
            type: int
            sample: 60
        origin_configuration:
            description: The type of the instance.
            returned: always
            type: string
            sample: rds.mysql.t1.small
        port:
            description: The private port of the instance.
            returned: always
            type: string
            sample: 3306
        read_only_dbinstance_ids:
            description: The IDs of read-only instances attached to the master instance.
            returned: always
            type: complex
            contains:
                read_only_dbinstance_id:
                    description: The ID of a read-only instance.
                    returned: always
                    type: list
                    sample: ['rr-bpxxxxxxxxx']
        security_ipmode:
            description: The IP whitelist mode.
            returned: always
            type: complex
            sample: normal

'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.alicloud_ecs import ecs_argument_spec, rds_connect

HAS_FOOTMARK = False

try:
    from footmark.exception import RDSResponseError
    HAS_FOOTMARK = True
except ImportError:
    HAS_FOOTMARK = False


def main():
    argument_spec = ecs_argument_spec()
    argument_spec.update(dict(
        name_prefix=dict(type='str'),
        tags=dict(type='dict')
    ))
    module = AnsibleModule(argument_spec=argument_spec)
    rds = rds_connect(module)
    name_prefix = module.params['name_prefix']

    if HAS_FOOTMARK is False:
        module.fail_json(msg="Package 'footmark' required for this module.")

    result = []
    try:
        for rds_instance in rds.describe_db_instances(**module.params):
            if name_prefix and not rds_instance.read()['name'].startswith(name_prefix):
                continue
            result.append(rds_instance.get().read())
        module.exit_json(changed=False, instances=result)
    except Exception as e:
        module.fail_json(msg="Unable to describe rds db instance, and got an error: {0}.".format(e))


if __name__ == '__main__':
    main()
