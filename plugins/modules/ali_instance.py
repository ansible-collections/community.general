#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017-present Alibaba Group Holding Limited. He Guimin <heguimin36@163.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
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

DOCUMENTATION = '''
---
module: ali_instance
short_description: Create, Start, Stop, Restart or Terminate an Instance in ECS. Add or Remove Instance to/from a Security Group.
description:
    - Create, start, stop, restart, modify or terminate ecs instances.
    - Add or remove ecs instances to/from security group.
options:
    state:
      description:
        - The state of the instance after operating.
      default: 'present'
      choices: ['present', 'running', 'stopped', 'restarted', 'absent']
      type: str
    availability_zone:
      description:
        - Aliyun availability zone ID in which to launch the instance.
          If it is not specified, it will be allocated by system automatically.
      aliases: ['alicloud_zone', 'zone_id']
      type: str
    image_id:
      description:
        - Image ID used to launch instances. Required when I(state=present) and creating new ECS instances.
      aliases: ['image']
      type: str
    instance_type:
      description:
        - Instance type used to launch instances. Required when I(state=present) and creating new ECS instances.
      aliases: ['type']
      type: str
    security_groups:
      description:
        - A list of security group IDs.
      aliases: ['group_ids']
      type: list
      elements: str
    vswitch_id:
      description:
        - The subnet ID in which to launch the instances (VPC).
      aliases: ['subnet_id']
      type: str
    instance_name:
      description:
        - The name of ECS instance, which is a string of 2 to 128 Chinese or English characters. It must begin with an
          uppercase/lowercase letter or a Chinese character and can contain numerals, ".", "_" or "-".
          It cannot begin with http:// or https://.
      aliases: ['name']
      type: str
    description:
      description:
        - The description of ECS instance, which is a string of 2 to 256 characters. It cannot begin with http:// or https://.
      type: str
    internet_charge_type:
      description:
        - Internet charge type of ECS instance.
      default: 'PayByBandwidth'
      choices: ['PayByBandwidth', 'PayByTraffic']
      type: str
    max_bandwidth_in:
      description:
        - Maximum incoming bandwidth from the public network, measured in Mbps (Megabits per second).
      default: 200
      type: int
    max_bandwidth_out:
      description:
        - Maximum outgoing bandwidth to the public network, measured in Mbps (Megabits per second).
          Required when I(allocate_public_ip=true). Ignored when I(allocate_public_ip=false).
      default: 0
      type: int
    host_name:
      description:
        - Instance host name. Ordered hostname is not supported.
      type: str
    unique_suffix:
      description:
        - Specifies whether to add sequential suffixes to the host_name.
          The sequential suffix ranges from 001 to 999.
      default: false
      type: bool
      version_added: '0.2.0'
    password:
      description:
        - The password to login instance. After rebooting instances, modified password will take effect.
      type: str
    system_disk_category:
      description:
        - Category of the system disk.
      default: 'cloud_efficiency'
      choices: ['cloud_efficiency', 'cloud_ssd']
      type: str
    system_disk_size:
      description:
        - Size of the system disk, in GB. The valid values are 40~500.
      default: 40
      type: int
    system_disk_name:
      description:
        - Name of the system disk.
      type: str
    system_disk_description:
      description:
        - Description of the system disk.
      type: str
    count:
      description:
        - The number of the new instance. An integer value which indicates how many instances that match I(count_tag)
          should be running. Instances are either created or terminated based on this value.
      default: 1
      type: int
    count_tag:
      description:
      - I(count) determines how many instances based on a specific tag criteria should be present.
        This can be expressed in multiple ways and is shown in the EXAMPLES section.
        The specified count_tag must already exist or be passed in as the I(tags) option.
        If it is not specified, it will be replaced by I(instance_name).
      type: str
    allocate_public_ip:
      description:
        - Whether allocate a public ip for the new instance.
      default: false
      aliases: [ 'assign_public_ip' ]
      type: bool
    instance_charge_type:
      description:
        - The charge type of the instance.
      choices: ['PrePaid', 'PostPaid']
      default: 'PostPaid'
      type: str
    period:
      description:
        - The charge duration of the instance, in months. Required when I(instance_charge_type=PrePaid).
        - The valid value are [1-9, 12, 24, 36].
      default: 1
      type: int
    auto_renew:
      description:
        - Whether automate renew the charge of the instance.
      type: bool
      default: false
    auto_renew_period:
      description:
        - The duration of the automatic renew the charge of the instance. Required when I(auto_renew=true).
      choices: [1, 2, 3, 6, 12]
      type: int
    instance_ids:
      description:
        - A list of instance ids. It is required when need to operate existing instances.
          If it is specified, I(count) will lose efficacy.
      type: list
      elements: str
    force:
      description:
        - Whether the current operation needs to be execute forcibly.
      default: false
      type: bool
    tags:
      description:
        - A hash/dictionaries of instance tags, to add to the new instance or for starting/stopping instance by tag. C({"key":"value"})
      aliases: ["instance_tags"]
      type: dict
      version_added: '0.2.0'
    purge_tags:
      description:
        - Delete any tags not specified in the task that are on the instance.
          If True, it means you have to specify all the desired tags on each task affecting an instance.
      default: false
      type: bool
      version_added: '0.2.0'
    key_name:
      description:
        - The name of key pair which is used to access ECS instance in SSH.
      required: false
      type: str
      aliases: ['keypair']
    user_data:
      description:
        - User-defined data to customize the startup behaviors of an ECS instance and to pass data into an ECS instance.
          It only will take effect when launching the new ECS instances.
      required: false
      type: str
    ram_role_name:
      description:
        - The name of the instance RAM role.
      type: str
      version_added: '0.2.0'
    spot_price_limit:
      description:
        - The maximum hourly price for the preemptible instance. This parameter supports a maximum of three decimal
          places and takes effect when the SpotStrategy parameter is set to SpotWithPriceLimit.
      type: float
      version_added: '0.2.0'
    spot_strategy:
      description:
        - The bidding mode of the pay-as-you-go instance. This parameter is valid when InstanceChargeType is set to PostPaid.
      choices: ['NoSpot', 'SpotWithPriceLimit', 'SpotAsPriceGo']
      default: 'NoSpot'
      type: str
      version_added: '0.2.0'
    period_unit:
      description:
        - The duration unit that you will buy the resource. It is valid when I(instance_charge_type=PrePaid).
      choices: ['Month', 'Week']
      default: 'Month'
      type: str
      version_added: '0.2.0'
    dry_run:
      description:
        - Specifies whether to send a dry-run request.
        - If I(dry_run=true), Only a dry-run request is sent and no instance is created. The system checks whether the
          required parameters are set, and validates the request format, service permissions, and available ECS instances.
          If the validation fails, the corresponding error code is returned. If the validation succeeds, the DryRunOperation error code is returned.
        - If I(dry_run=false), A request is sent. If the validation succeeds, the instance is created.
      default: false
      type: bool
      version_added: '0.2.0'
    include_data_disks:
      description:
        - Whether to change instance disks charge type when changing instance charge type.
      default: true
      type: bool
      version_added: '0.2.0'
author:
    - "He Guimin (@xiaozhu36)"
requirements:
    - "python >= 3.6"
    - "footmark >= 1.19.0"
extends_documentation_fragment:
    - community.general.alicloud
'''

EXAMPLES = '''
# basic provisioning example vpc network
- name: Basic provisioning example
  hosts: localhost
  vars:
    alicloud_access_key: <your-alicloud-access-key-id>
    alicloud_secret_key: <your-alicloud-access-secret-key>
    alicloud_region: cn-beijing
    image: ubuntu1404_64_40G_cloudinit_20160727.raw
    instance_type: ecs.n4.small
    vswitch_id: vsw-abcd1234
    assign_public_ip: true
    max_bandwidth_out: 10
    host_name: myhost
    password: mypassword
    system_disk_category: cloud_efficiency
    system_disk_size: 100
    internet_charge_type: PayByBandwidth
    security_groups: ["sg-f2rwnfh23r"]

    instance_ids: ["i-abcd12346", "i-abcd12345"]
    force: true

  tasks:
    - name: Launch ECS instance in VPC network
      community.general.ali_instance:
        alicloud_access_key: '{{ alicloud_access_key }}'
        alicloud_secret_key: '{{ alicloud_secret_key }}'
        alicloud_region: '{{ alicloud_region }}'
        image: '{{ image }}'
        system_disk_category: '{{ system_disk_category }}'
        system_disk_size: '{{ system_disk_size }}'
        instance_type: '{{ instance_type }}'
        vswitch_id: '{{ vswitch_id }}'
        assign_public_ip: '{{ assign_public_ip }}'
        internet_charge_type: '{{ internet_charge_type }}'
        max_bandwidth_out: '{{ max_bandwidth_out }}'
        tags:
            Name: created_one
        host_name: '{{ host_name }}'
        password: '{{ password }}'

    - name: With count and count_tag to create a number of instances
      community.general.ali_instance:
        alicloud_access_key: '{{ alicloud_access_key }}'
        alicloud_secret_key: '{{ alicloud_secret_key }}'
        alicloud_region: '{{ alicloud_region }}'
        image: '{{ image }}'
        system_disk_category: '{{ system_disk_category }}'
        system_disk_size: '{{ system_disk_size }}'
        instance_type: '{{ instance_type }}'
        assign_public_ip: '{{ assign_public_ip }}'
        security_groups: '{{ security_groups }}'
        internet_charge_type: '{{ internet_charge_type }}'
        max_bandwidth_out: '{{ max_bandwidth_out }}'
        tags:
            Name: created_one
            Version: 0.1
        count: 2
        count_tag:
            Name: created_one
        host_name: '{{ host_name }}'
        password: '{{ password }}'

    - name: Start instance
      community.general.ali_instance:
        alicloud_access_key: '{{ alicloud_access_key }}'
        alicloud_secret_key: '{{ alicloud_secret_key }}'
        alicloud_region: '{{ alicloud_region }}'
        instance_ids: '{{ instance_ids }}'
        state: 'running'

    - name: Reboot instance forcibly
      ecs:
        alicloud_access_key: '{{ alicloud_access_key }}'
        alicloud_secret_key: '{{ alicloud_secret_key }}'
        alicloud_region: '{{ alicloud_region }}'
        instance_ids: '{{ instance_ids }}'
        state: 'restarted'
        force: '{{ force }}'

    - name: Add instances to an security group
      ecs:
        alicloud_access_key: '{{ alicloud_access_key }}'
        alicloud_secret_key: '{{ alicloud_secret_key }}'
        alicloud_region: '{{ alicloud_region }}'
        instance_ids: '{{ instance_ids }}'
        security_groups: '{{ security_groups }}'
'''

RETURN = '''
instances:
    description: List of ECS instances
    returned: always
    type: complex
    contains:
        availability_zone:
            description: The availability zone of the instance is in.
            returned: always
            type: str
            sample: cn-beijing-a
        block_device_mappings:
            description: Any block device mapping entries for the instance.
            returned: always
            type: complex
            contains:
                device_name:
                    description: The device name exposed to the instance (for example, /dev/xvda).
                    returned: always
                    type: str
                    sample: /dev/xvda
                attach_time:
                    description: The time stamp when the attachment initiated.
                    returned: always
                    type: str
                    sample: "2018-06-25T04:08:26Z"
                delete_on_termination:
                    description: Indicates whether the volume is deleted on instance termination.
                    returned: always
                    type: bool
                    sample: true
                status:
                    description: The attachment state.
                    returned: always
                    type: str
                    sample: in_use
                volume_id:
                    description: The ID of the cloud disk.
                    returned: always
                    type: str
                    sample: d-2zei53pjsi117y6gf9t6
        cpu:
            description: The CPU core count of the instance.
            returned: always
            type: int
            sample: 4
        creation_time:
            description: The time the instance was created.
            returned: always
            type: str
            sample: "2018-06-25T04:08Z"
        description:
            description: The instance description.
            returned: always
            type: str
            sample: "my ansible instance"
        eip:
            description: The attribution of EIP associated with the instance.
            returned: always
            type: complex
            contains:
                allocation_id:
                    description: The ID of the EIP.
                    returned: always
                    type: str
                    sample: eip-12345
                internet_charge_type:
                    description: The internet charge type of the EIP.
                    returned: always
                    type: str
                    sample: "paybybandwidth"
                ip_address:
                    description: EIP address.
                    returned: always
                    type: str
                    sample: 42.10.2.2
        expired_time:
            description: The time the instance will expire.
            returned: always
            type: str
            sample: "2099-12-31T15:59Z"
        gpu:
            description: The attribution of instance GPU.
            returned: always
            type: complex
            contains:
                amount:
                    description: The count of the GPU.
                    returned: always
                    type: int
                    sample: 0
                spec:
                    description: The specification of the GPU.
                    returned: always
                    type: str
                    sample: ""
        host_name:
            description: The host name of the instance.
            returned: always
            type: str
            sample: iZ2zewaoZ
        id:
            description: Alias of instance_id.
            returned: always
            type: str
            sample: i-abc12345
        instance_id:
            description: ECS instance resource ID.
            returned: always
            type: str
            sample: i-abc12345
        image_id:
            description: The ID of the image used to launch the instance.
            returned: always
            type: str
            sample: m-0011223344
        inner_ip_address:
            description: The inner IPv4 address of the classic instance.
            returned: always
            type: str
            sample: 10.0.0.2
        instance_charge_type:
            description: The instance charge type.
            returned: always
            type: str
            sample: PostPaid
        instance_name:
            description: The name of the instance.
            returned: always
            type: str
            sample: my-ecs
        instance_type:
            description: The instance type of the running instance.
            returned: always
            type: str
            sample: ecs.sn1ne.xlarge
        instance_type_family:
            description: The instance type family of the instance belongs.
            returned: always
            type: str
            sample: ecs.sn1ne
        internet_charge_type:
            description: The billing method of the network bandwidth.
            returned: always
            type: str
            sample: PayByBandwidth
        internet_max_bandwidth_in:
            description: Maximum incoming bandwidth from the internet network.
            returned: always
            type: int
            sample: 200
        internet_max_bandwidth_out:
            description: Maximum incoming bandwidth from the internet network.
            returned: always
            type: int
            sample: 20
        io_optimized:
            description: Indicates whether the instance is optimized for EBS I/O.
            returned: always
            type: bool
            sample: false
        memory:
            description: Memory size of the instance.
            returned: always
            type: int
            sample: 8192
        network_interfaces:
            description: One or more network interfaces for the instance.
            returned: always
            type: complex
            contains:
                mac_address:
                    description: The MAC address.
                    returned: always
                    type: str
                    sample: "00:11:22:33:44:55"
                network_interface_id:
                    description: The ID of the network interface.
                    returned: always
                    type: str
                    sample: eni-01234567
                primary_ip_address:
                    description: The primary IPv4 address of the network interface within the vswitch.
                    returned: always
                    type: str
                    sample: 10.0.0.1
        osname:
            description: The operation system name of the instance owned.
            returned: always
            type: str
            sample: CentOS
        ostype:
            description: The operation system type of the instance owned.
            returned: always
            type: str
            sample: linux
        private_ip_address:
            description: The IPv4 address of the network interface within the subnet.
            returned: always
            type: str
            sample: 10.0.0.1
        public_ip_address:
            description: The public IPv4 address assigned to the instance or eip address
            returned: always
            type: str
            sample: 43.0.0.1
        resource_group_id:
            description: The id of the resource group to which the instance belongs.
            returned: always
            type: str
            sample: my-ecs-group
        security_groups:
            description: One or more security groups for the instance.
            returned: always
            type: list
            elements: dict
            contains:
                group_id:
                  description: The ID of the security group.
                  returned: always
                  type: str
                  sample: sg-0123456
                group_name:
                  description: The name of the security group.
                  returned: always
                  type: str
                  sample: my-security-group
        status:
            description: The current status of the instance.
            returned: always
            type: str
            sample: running
        tags:
            description: Any tags assigned to the instance.
            returned: always
            type: dict
            sample:
        user_data:
            description: User-defined data.
            returned: always
            type: dict
            sample:
        vswitch_id:
            description: The ID of the vswitch in which the instance is running.
            returned: always
            type: str
            sample: vsw-dew00abcdef
        vpc_id:
            description: The ID of the VPC the instance is in.
            returned: always
            type: str
            sample: vpc-0011223344
        spot_price_limit:
          description:
            - The maximum hourly price for the preemptible instance.
          returned: always
          type: float
          sample: 0.97
        spot_strategy:
          description:
             - The bidding mode of the pay-as-you-go instance.
          returned: always
          type: str
          sample: NoSpot
ids:
    description: List of ECS instance IDs
    returned: always
    type: list
    sample: [i-12345er, i-3245fs]
'''

import re
import time
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible_collections.community.general.plugins.module_utils.alicloud_ecs import (
    ecs_argument_spec, ecs_connect, FOOTMARK_IMP_ERR, HAS_FOOTMARK
)


def get_instances_info(connection, ids):
    result = []
    instances = connection.describe_instances(instance_ids=ids)
    if len(instances) > 0:
        for inst in instances:
            volumes = connection.describe_disks(instance_id=inst.id)
            setattr(inst, 'block_device_mappings', volumes)
            setattr(inst, 'user_data', inst.describe_user_data())
            result.append(inst.read())
    return result


def run_instance(module, ecs, exact_count):
    if exact_count <= 0:
        return None
    zone_id = module.params['availability_zone']
    image_id = module.params['image_id']
    instance_type = module.params['instance_type']
    security_groups = module.params['security_groups']
    vswitch_id = module.params['vswitch_id']
    instance_name = module.params['instance_name']
    description = module.params['description']
    internet_charge_type = module.params['internet_charge_type']
    max_bandwidth_out = module.params['max_bandwidth_out']
    max_bandwidth_in = module.params['max_bandwidth_in']
    host_name = module.params['host_name']
    password = module.params['password']
    system_disk_category = module.params['system_disk_category']
    system_disk_size = module.params['system_disk_size']
    system_disk_name = module.params['system_disk_name']
    system_disk_description = module.params['system_disk_description']
    allocate_public_ip = module.params['allocate_public_ip']
    period = module.params['period']
    auto_renew = module.params['auto_renew']
    instance_charge_type = module.params['instance_charge_type']
    auto_renew_period = module.params['auto_renew_period']
    user_data = module.params['user_data']
    key_name = module.params['key_name']
    ram_role_name = module.params['ram_role_name']
    spot_price_limit = module.params['spot_price_limit']
    spot_strategy = module.params['spot_strategy']
    unique_suffix = module.params['unique_suffix']
    # check whether the required parameter passed or not
    if not image_id:
        module.fail_json(msg='image_id is required for new instance')
    if not instance_type:
        module.fail_json(msg='instance_type is required for new instance')
    if not isinstance(security_groups, list):
        module.fail_json(msg='The parameter security_groups should be a list, aborting')
    if len(security_groups) <= 0:
        module.fail_json(msg='Expected the parameter security_groups is non-empty when create new ECS instances, aborting')

    client_token = "Ansible-Alicloud-{0}-{1}".format(hash(str(module.params)), str(time.time()))

    try:
        # call to create_instance method from footmark
        instances = ecs.run_instances(image_id=image_id, instance_type=instance_type, security_group_id=security_groups[0],
                                      zone_id=zone_id, instance_name=instance_name, description=description,
                                      internet_charge_type=internet_charge_type, internet_max_bandwidth_out=max_bandwidth_out,
                                      internet_max_bandwidth_in=max_bandwidth_in, host_name=host_name, password=password,
                                      io_optimized='optimized', system_disk_category=system_disk_category,
                                      system_disk_size=system_disk_size, system_disk_disk_name=system_disk_name,
                                      system_disk_description=system_disk_description, vswitch_id=vswitch_id,
                                      amount=exact_count, instance_charge_type=instance_charge_type, period=period, period_unit="Month",
                                      auto_renew=auto_renew, auto_renew_period=auto_renew_period, key_pair_name=key_name,
                                      user_data=user_data, client_token=client_token, ram_role_name=ram_role_name,
                                      spot_price_limit=spot_price_limit, spot_strategy=spot_strategy, unique_suffix=unique_suffix)

    except Exception as e:
        module.fail_json(msg='Unable to create instance, error: {0}'.format(e))

    return instances


def modify_instance(module, instance):
    # According to state to modify instance's some special attribute
    state = module.params["state"]
    name = module.params['instance_name']
    unique_suffix = module.params['unique_suffix']
    if not name:
        name = instance.name

    description = module.params['description']
    if not description:
        description = instance.description

    host_name = module.params['host_name']
    if unique_suffix and host_name:
        suffix = instance.host_name[-3:]
        host_name = host_name + suffix

    if not host_name:
        host_name = instance.host_name

    # password can be modified only when restart instance
    password = ""
    if state == "restarted":
        password = module.params['password']

    # userdata can be modified only when instance is stopped
    setattr(instance, "user_data", instance.describe_user_data())
    user_data = instance.user_data
    if state == "stopped":
        user_data = module.params['user_data'].encode()

    try:
        return instance.modify(name=name, description=description, host_name=host_name, password=password, user_data=user_data)
    except Exception as e:
        module.fail_json(msg="Modify instance {0} attribute got an error: {1}".format(instance.id, e))


def wait_for_instance_modify_charge(ecs, instance_ids, charge_type, delay=10, timeout=300):
    """
    To verify instance charge type has become expected after modify instance charge type
    """
    try:
        while True:
            instances = ecs.describe_instances(instance_ids=instance_ids)
            flag = True
            for inst in instances:
                if inst and inst.instance_charge_type != charge_type:
                    flag = False
            if flag:
                return
            timeout -= delay
            time.sleep(delay)
            if timeout <= 0:
                raise Exception("Timeout Error: Waiting for instance to {0}. ".format(charge_type))
    except Exception as e:
        raise e


def main():
    argument_spec = ecs_argument_spec()
    argument_spec.update(dict(
        security_groups=dict(type='list', elements='str', aliases=['group_ids']),
        availability_zone=dict(type='str', aliases=['alicloud_zone', 'zone_id']),
        instance_type=dict(type='str', aliases=['type']),
        image_id=dict(type='str', aliases=['image']),
        count=dict(type='int', default=1),
        count_tag=dict(type='str'),
        vswitch_id=dict(type='str', aliases=['subnet_id']),
        instance_name=dict(type='str', aliases=['name']),
        host_name=dict(type='str'),
        password=dict(type='str', no_log=True),
        internet_charge_type=dict(type='str', default='PayByBandwidth', choices=['PayByBandwidth', 'PayByTraffic']),
        max_bandwidth_in=dict(type='int', default=200),
        max_bandwidth_out=dict(type='int', default=0),
        system_disk_category=dict(type='str', default='cloud_efficiency', choices=['cloud_efficiency', 'cloud_ssd']),
        system_disk_size=dict(type='int', default=40),
        system_disk_name=dict(type='str'),
        system_disk_description=dict(type='str'),
        force=dict(type='bool', default=False),
        tags=dict(type='dict', aliases=['instance_tags']),
        purge_tags=dict(type='bool', default=False),
        state=dict(default='present', choices=['present', 'running', 'stopped', 'restarted', 'absent']),
        description=dict(type='str'),
        allocate_public_ip=dict(type='bool', aliases=['assign_public_ip'], default=False),
        instance_charge_type=dict(type='str', default='PostPaid', choices=['PrePaid', 'PostPaid']),
        period=dict(type='int', default=1),
        auto_renew=dict(type='bool', default=False),
        instance_ids=dict(type='list', elements='str'),
        auto_renew_period=dict(type='int', choices=[1, 2, 3, 6, 12]),
        key_name=dict(type='str', aliases=['keypair']),
        user_data=dict(type='str'),
        ram_role_name=dict(type='str'),
        spot_price_limit=dict(type='float'),
        spot_strategy=dict(type='str', default='NoSpot', choices=['NoSpot', 'SpotWithPriceLimit', 'SpotAsPriceGo']),
        unique_suffix=dict(type='bool', default=False),
        period_unit=dict(type='str', default='Month', choices=['Month', 'Week']),
        dry_run=dict(type='bool', default=False),
        include_data_disks=dict(type='bool', default=True)
    )
    )
    module = AnsibleModule(argument_spec=argument_spec)

    if HAS_FOOTMARK is False:
        module.fail_json(msg=missing_required_lib('footmark'), exception=FOOTMARK_IMP_ERR)

    ecs = ecs_connect(module)
    host_name = module.params['host_name']
    state = module.params['state']
    instance_ids = module.params['instance_ids']
    count_tag = module.params['count_tag']
    count = module.params['count']
    instance_name = module.params['instance_name']
    force = module.params['force']
    zone_id = module.params['availability_zone']
    key_name = module.params['key_name']
    tags = module.params['tags']
    max_bandwidth_out = module.params['max_bandwidth_out']
    instance_charge_type = module.params['instance_charge_type']
    if instance_charge_type == "PrePaid":
        module.params['spot_strategy'] = ''
    changed = False

    instances = []
    if instance_ids:
        if not isinstance(instance_ids, list):
            module.fail_json(msg='The parameter instance_ids should be a list, aborting')
        instances = ecs.describe_instances(zone_id=zone_id, instance_ids=instance_ids)
        if not instances:
            module.fail_json(msg="There are no instances in our record based on instance_ids {0}. "
                                 "Please check it and try again.".format(instance_ids))
    elif count_tag:
        instances = ecs.describe_instances(zone_id=zone_id, tags=eval(count_tag))
    elif instance_name:
        instances = ecs.describe_instances(zone_id=zone_id, instance_name=instance_name)

    ids = []
    if state == 'absent':
        if len(instances) < 1:
            module.fail_json(msg='Please specify ECS instances that you want to operate by using '
                                 'parameters instance_ids, tags or instance_name, aborting')
        try:
            targets = []
            for inst in instances:
                if inst.status != 'stopped' and not force:
                    module.fail_json(msg="Instance is running, and please stop it or set 'force' as True.")
                targets.append(inst.id)
            if ecs.delete_instances(instance_ids=targets, force=force):
                changed = True
                ids.extend(targets)

            module.exit_json(changed=changed, ids=ids, instances=[])
        except Exception as e:
            module.fail_json(msg='Delete instance got an error: {0}'.format(e))

    if module.params['allocate_public_ip'] and max_bandwidth_out < 0:
        module.fail_json(msg="'max_bandwidth_out' should be greater than 0 when 'allocate_public_ip' is True.")
    if not module.params['allocate_public_ip']:
        module.params['max_bandwidth_out'] = 0

    if state == 'present':
        if not instance_ids:
            if len(instances) > count:
                for i in range(0, len(instances) - count):
                    inst = instances[len(instances) - 1]
                    if inst.status != 'stopped' and not force:
                        module.fail_json(msg="That to delete instance {0} is failed results from it is running, "
                                             "and please stop it or set 'force' as True.".format(inst.id))
                    try:
                        if inst.terminate(force=force):
                            changed = True
                    except Exception as e:
                        module.fail_json(msg="Delete instance {0} got an error: {1}".format(inst.id, e))
                    instances.pop(len(instances) - 1)
            else:
                try:
                    if re.search(r"-\[\d+,\d+\]-", host_name):
                        module.fail_json(msg='Ordered hostname is not supported, If you want to add an ordered '
                                             'suffix to the hostname, you can set unique_suffix to True')
                    new_instances = run_instance(module, ecs, count - len(instances))
                    if new_instances:
                        changed = True
                        instances.extend(new_instances)
                except Exception as e:
                    module.fail_json(msg="Create new instances got an error: {0}".format(e))

        # Security Group join/leave begin
        security_groups = module.params['security_groups']
        if security_groups:
            if not isinstance(security_groups, list):
                module.fail_json(msg='The parameter security_groups should be a list, aborting')
            for inst in instances:
                existing = inst.security_group_ids['security_group_id']
                remove = list(set(existing).difference(set(security_groups)))
                add = list(set(security_groups).difference(set(existing)))
                for sg in remove:
                    if inst.leave_security_group(sg):
                        changed = True
                for sg in add:
                    if inst.join_security_group(sg):
                        changed = True
        # Security Group join/leave ends here

        # Attach/Detach key pair
        inst_ids = []
        for inst in instances:
            if key_name is not None and key_name != inst.key_name:
                if key_name == "":
                    if inst.detach_key_pair():
                        changed = True
                else:
                    inst_ids.append(inst.id)
        if inst_ids:
            changed = ecs.attach_key_pair(instance_ids=inst_ids, key_pair_name=key_name)

        # Modify instance attribute
        for inst in instances:
            if modify_instance(module, inst):
                changed = True
            if inst.id not in ids:
                ids.append(inst.id)

        # Modify instance charge type
        ids = []
        for inst in instances:
            if inst.instance_charge_type != instance_charge_type:
                ids.append(inst.id)
        if ids:
            params = {"instance_ids": ids, "instance_charge_type": instance_charge_type,
                      "include_data_disks": module.params['include_data_disks'], "dry_run": module.params['dry_run'],
                      "auto_pay": True}
            if instance_charge_type == 'PrePaid':
                params['period'] = module.params['period']
                params['period_unit'] = module.params['period_unit']

            if ecs.modify_instance_charge_type(**params):
                changed = True
                wait_for_instance_modify_charge(ecs, ids, instance_charge_type)

    else:
        if len(instances) < 1:
            module.fail_json(msg='Please specify ECS instances that you want to operate by using '
                                 'parameters instance_ids, tags or instance_name, aborting')
        if state == 'running':
            try:
                targets = []
                for inst in instances:
                    if modify_instance(module, inst):
                        changed = True
                    if inst.status != "running":
                        targets.append(inst.id)
                    ids.append(inst.id)
                if targets and ecs.start_instances(instance_ids=targets):
                    changed = True
                    ids.extend(targets)
            except Exception as e:
                module.fail_json(msg='Start instances got an error: {0}'.format(e))
        elif state == 'stopped':
            try:
                targets = []
                for inst in instances:
                    if inst.status != "stopped":
                        targets.append(inst.id)
                if targets and ecs.stop_instances(instance_ids=targets, force_stop=force):
                    changed = True
                    ids.extend(targets)
                for inst in instances:
                    if modify_instance(module, inst):
                        changed = True
            except Exception as e:
                module.fail_json(msg='Stop instances got an error: {0}'.format(e))
        elif state == 'restarted':
            try:
                targets = []
                for inst in instances:
                    if modify_instance(module, inst):
                        changed = True
                        targets.append(inst.id)
                if ecs.reboot_instances(instance_ids=targets, force_stop=module.params['force']):
                    changed = True
                    ids.extend(targets)
            except Exception as e:
                module.fail_json(msg='Reboot instances got an error: {0}'.format(e))

    tags = module.params['tags']
    if module.params['purge_tags']:
        for inst in instances:
            if not tags:
                tags = inst.tags
            try:
                if inst.remove_tags(tags):
                    changed = True
            except Exception as e:
                module.fail_json(msg="{0}".format(e))
        module.exit_json(changed=changed, instances=get_instances_info(ecs, ids))

    if tags:
        for inst in instances:
            try:
                if inst.add_tags(tags):
                    changed = True
            except Exception as e:
                module.fail_json(msg="{0}".format(e))
    module.exit_json(changed=changed, instances=get_instances_info(ecs, ids))


if __name__ == '__main__':
    main()
