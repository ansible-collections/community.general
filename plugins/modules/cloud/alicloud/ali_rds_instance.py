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
module: ali_rds_instance
short_description: Create, Restart or Delete an RDS Instance in Alibaba Cloud.
description:
    - Create, Restart, Delete and Modify connection_string, spec for RDS Instance.
    - An unique ali_rds_instance module is determined by parameters db_instance_name.
options:
  state:
    description:
      - If I(state=present), instance will be created.
      - If I(state=present) and instance exists, it will be updated.
      - If I(state=absent), instance will be removed.
      - If I(state=restart), instance will be restarted.
    choices: ['present', 'restart', 'absent']
    default: 'present'
    type: str
  zone_id:
    description:
      - Aliyun availability zone ID in which to launch the instance.
        If it is not specified, it will be allocated by system automatically.
    aliases: ['alicloud_zone']
    type: str
  engine:
    description:
      - The engine type of the database. Required when C(state=present).
    choices: ['MySQL', 'SQLServer', 'PostgreSQL', 'PPAS', 'MariaDB']
    type: str
  engine_version:
    description:
      - The version of the database. Required when C(state=present).
      - MySQL (5.5 | 5.6 | 5.7 | 8.0).
      - SQL Server (2008r2 | 2012 | 2012_ent_ha | 2012_std_ha | 2012_web | 2016_ent_ha | 2016_std_ha | 2016_web | 2017_ent).
      - PostgreSQL (9.4 | 10.0).
      - PPAS (9.3 | 10.0).
      - MariaDB (10.3).
      - see more (https://www.alibabacloud.com/help/doc-detail/26228.htm).
    type: str
  db_instance_class:
    description:
      - The instance type (specifications). For more information, see(https://www.alibabacloud.com/help/doc-detail/26312.htm).
        Required when C(state=present).
    aliases: ['instance_class']
    type: str
  db_instance_storage:
    description:
      - The storage capacity of the instance. Unit(GB). This value must be a multiple of 5. For more information 
        see(https://www.alibabacloud.com/help/doc-detail/26312.htm).
      - Required when C(state=present).
    aliases: ['instance_storage']
    type: int
  db_instance_net_type:
    description:
      - Instance of the network connection type (Internet on behalf of the public network, Intranet on behalf of the private network）
        Required when C(state=present).
    aliases: ['instance_net_type']
    choices: ["Internet", "Intranet"]
    type: str
  db_instance_name:
    description:
      - The instance name. the unique identifier of the instance. It starts with a letter and contains 2 to 255 characters,
        including letters, digits, underscores (_), and hyphens (-). It cannot start with http:// or https://.
      - This is used to determine if the rds instance already exists.
    aliases: ['description', 'name']
    type: str
    required: True
  security_ip_list:
    description:
      - The IP address whitelist of the instance. Separate multiple IP addresses with commas (,).
        It can include up to 1,000 IP addresses. The IP addresses support two formats.
        IP address format. For example, 10.23.12.24. Classless Inter-Domain Routing (CIDR) format.
        For example, 10.23.12.24/24 (where /24 indicates the number of bits for the prefix of the IP address, in the range of 1 to 32).
        Required when C(state=present).
    aliases: ['security_ips']
    type: str
  pay_type:
    description:
      - The billing method of the instance. Required when C(state=present).
    choices: ["PostPaid", "PrePaid"]
    type: str
  period:
    description:
      - The duration of the instance. Required when C(pay_type=PrePaid).
    choices: [1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 24, 36]
    default: 1
    type: int
  connection_mode:
    description:
      - The access mode of the instance.
    choices: ["Standard", "Safe"]
    type: str
  vswitch_id:
    description:
      - The ID of the VSwitch.
        Required when C(engine=MariaDB)
    type: str
  private_ip_address:
    description:
      - The intranet IP address of the instance. It must be within the IP address range provided by the switch.
        By default, the system automatically assigns an IP address based on the VPCId and VSwitchId.
    type: str
  auto_renew:
    description:
      - Indicates whether the instance is automatically renewed
    type: bool
    default: False
    aliases: ['auto_renew']
  port:
    description:
      - The target port.
    type: str
  auto_pay:
    description:
      - Auto renew or not.
    type: bool
    default: False
  current_connection_string:
    description:
      - The current connection address of an instance. It can be an internal network address, a public network address,
        or a classic network address in the hybrid access mode.
    type: str
  connection_string_prefix:
    description:
      - The prefix of the target connection address. Only the prefix of CurrentConnectionString can be modified.
    type: str
  tags:
    description:
      - A hash/dictionaries of rds tags. C({"key":"value"})
    type: dict
  purge_tags:
    description:
      - Delete existing tags on the rds that are not specified in the task.
        If True, it means you have to specify all the desired tags on each task affecting a rds.
    default: False
    type: bool
author:
    - "He Guimin (@xiaozhu36)"
    - "Li Xue (@lixue323)"
requirements:
    - "python >= 3.6"
    - "footmark >= 1.16.0"
extends_documentation_fragment:
    - community.general.alicloud
'''

EXAMPLES = '''
- name: Changed. Add Tags.
  ali_rds_instance:
    db_instance_description: '{{ name }}'
    tags:
      TAG: "add1"
      TAG2: "add2"

- name: Changed. Removing tags.
  ali_rds_instance:
    db_instance_description: '{{ name }}'
    purge_tags: True
    tags:
      TAG: "add1"

- name: Changed. allocate instance public connection string
  ali_rds_instance:
    db_instance_description: '{{ name }}'
    connection_string_prefix: publicave-89asd
    port: 3165

- name: release instance public connection string
  ali_rds_instance:
    state: absent
    db_instance_description: '{{ name }}'
    current_connection_string: publicave-89asd.mysql.rds.aliyuncs.com

- name: restart rds instance
  ali_rds_instance:
    db_instance_description: '{{ name }}'
    state: restart

- name: Changed. modify instance spec
  ali_rds_instance:
    db_instance_description: '{{ name }}'
    db_instance_class: rds.mysql.c2.xlarge
    db_instance_storage: 40

- name: Changed. modify instance current connection string
  ali_rds_instance:
    current_connection_string: '{{ rds.instances.0.id }}.mysql.rds.aliyuncs.com'
    db_instance_description: '{{ name }}'
    connection_string_prefix: private-ansible
    port: 3307

- name: Changed. Deleting rds
  ali_rds_instance:
    state: absent
    db_instance_description: '{{ name }}'
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

import time
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.alicloud_ecs import ecs_argument_spec, rds_connect, vpc_connect

HAS_FOOTMARK = False

try:
    from footmark.exception import ECSResponseError
    HAS_FOOTMARK = True
except ImportError:
    HAS_FOOTMARK = False


def get_instance(name, modules, rds):
    try:
        instances = rds.describe_db_instances()
        res = None
        for ins in instances:
            if ins.name == name:
                res = ins
        return res
    except Exception as e:
        modules.fail_json(msg="Failed to describe rds: {0}".format(e))


def main():
    argument_spec = ecs_argument_spec()
    argument_spec.update(dict(
        state=dict(default="present", choices=["present", "absent", "restart"]),
        zone_id=dict(type='str', aliases=['alicloud_zone']),
        engine=dict(type='str', choices=['MySQL', 'SQLServer', 'PostgreSQL', 'PPAS', 'MariaDB']),
        engine_version=dict(type='str'),
        db_instance_net_type=dict(type='str', choices=["Internet", "Intranet"], aliases=['instance_net_type']),
        db_instance_name=dict(type='str', aliases=['description', 'name'], required=True),
        security_ip_list=dict(type='str', aliases=['security_ips']),
        pay_type=dict(type='str', choices=["PostPaid", "PrePaid"]),
        period=dict(type='int', choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 24, 36], default=1),
        connection_mode=dict(type='str', choices=["Standard", "Safe"]),
        vswitch_id=dict(type='str'),
        private_ip_address=dict(type='str'),
        tags=dict(type='dict'),
        purge_tags=dict(type='bool', default=False),
        auto_pay=dict(type='bool', aliases=['auto_renew']),
        connection_string_prefix=dict(type='str'),
        port=dict(type='str'),
        current_connection_string=dict(type='str'),
        db_instance_class=dict(type='str', aliases=['instance_class']),
        db_instance_storage=dict(type='int', aliases=['instance_storage'])
    ))
    modules = AnsibleModule(argument_spec=argument_spec)

    if HAS_FOOTMARK is False:
        modules.fail_json(msg="Package 'footmark' required for the module ali_rds_instance.")

    rds = rds_connect(modules)
    vpc = vpc_connect(modules)

    state = modules.params['state']
    vswitch_id = modules.params['vswitch_id']
    connection_string_prefix = modules.params['connection_string_prefix']
    port = modules.params['port']
    tags = modules.params['tags']
    current_connection_string = modules.params['current_connection_string']
    db_instance_description = modules.params['db_instance_name']
    modules.params['db_instance_description'] = db_instance_description
    db_instance_class = modules.params['db_instance_class']
    db_instance_storage = modules.params['db_instance_storage']
    pay_type = modules.params['pay_type']
    used_time = modules.params['period']
    modules.params['period'] = 'Month'
    modules.params['used_time'] = str(used_time)

    if used_time > 9:
        modules.params['period'] = 'Year'
        if used_time == 12:
            modules.params['used_time'] = '1'
        elif used_time == 24:
            modules.params['used_time'] = '2'
        else:
            modules.params['used_time'] = '3'
    if pay_type:
        modules.params['pay_type'] = pay_type.capitalize()

    current_instance = None
    changed = False

    if vswitch_id:
        modules.params['instance_network_type'] = 'VPC'
        try:
            vswitch_obj = vpc.describe_vswitch_attributes(vswitch_id=vswitch_id)
            if vswitch_obj:
                modules.params['vpc_id'] = vswitch_obj.vpc_id
        except Exception as e:
            modules.fail_json(msg=str("Unable to get vswitch, error:{0}".format(e)))

    try:
        current_instance = get_instance(db_instance_description, modules, rds)
    except Exception as e:
        modules.fail_json(msg=str("Unable to describe instance, error:{0}".format(e)))

    if state == 'absent':
        if current_instance:
            if current_connection_string:
                try:
                    changed = rds.release_instance_public_connection(current_connection_string=current_connection_string, db_instance_id=current_instance.id)
                    modules.exit_json(changed=changed, instances=current_instance.get().read())
                except Exception as e:
                    modules.fail_json(msg=str("Unable to release public connection string error: {0}".format(e)))
            try:
                current_instance.delete()
                modules.exit_json(changed=True, instances={})
            except Exception as e:
                modules.fail_json(msg=str("Unable to release instance error: {0}".format(e)))
        modules.fail_json(msg=str("Unable to operate your instance, please check your instance_id and try again!"))

    if state == 'restart':
        if current_instance:
            try:
                changed = current_instance.restart()
                modules.exit_json(changed=changed, instances=current_instance.get().read())
            except Exception as e:
                modules.fail_json(msg=str("Unable to restart instance error: {0}".format(e)))
        modules.fail_json(msg=str("Unable to restart your instance, please check your instance_id and try again!"))

    if not current_instance:
        try:
            modules.params['client_token'] = "Ansible-Alicloud-%s-%s" % (hash(str(modules.params)), str(time.time()))
            current_instance = rds.create_db_instance(**modules.params)
            modules.exit_json(changed=True, instances=current_instance.get().read())
        except Exception as e:
            modules.fail_json(msg=str("Unable to create rds instance error: {0}".format(e)))

    if connection_string_prefix and port:
        if current_connection_string:
            try:
                changed = current_instance.modify_db_instance_connection_string(current_connection_string=current_connection_string,
                                                                                connection_string_prefix=connection_string_prefix, port=port)
                modules.exit_json(changed=changed, instances=current_instance.get().read())
            except Exception as e:
                modules.fail_json(msg=str("Unable to modify current string error: {0}".format(e)))
        else:
            try:
                changed = current_instance.allocate_public_connection_string(connection_string_prefix=connection_string_prefix, port=port)
                modules.exit_json(changed=changed, instances=current_instance.get().read())
            except Exception as e:
                modules.fail_json(msg=str("Unable to allocate public connection error: {0}".format(e)))

    if db_instance_class or db_instance_storage:
        try:
            changed = current_instance.modify_instance_spec(db_instance_class=db_instance_class, db_instance_storage=db_instance_storage)
        except Exception as e:
            modules.fail_json(msg=str("Unable to modify instance spec: {0}".format(e)))

    if modules.params['purge_tags']:
        if not tags:
            tags = current_instance.tags
        try:
            if current_instance.remove_tags(tags):
                changed = True
            modules.exit_json(changed=changed, instances=current_instance.get().read())
        except Exception as e:
            modules.fail_json(msg="{0}".format(e))

    if tags:
        try:
            if current_instance.add_tags(tags):
                changed = True
        except Exception as e:
            modules.fail_json(msg="{0}".format(e))

    modules.exit_json(changed=changed, instances=current_instance.get().read())


if __name__ == '__main__':
    main()
