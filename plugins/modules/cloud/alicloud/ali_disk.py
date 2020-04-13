#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017-present Alibaba Group Holding Limited. He Guimin <heguimin36@163.com.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#
# This file is part of Ansible
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
module: ali_disk
short_description: Create, Attach, Detach or Delete a disk in Alicloud ECS
description:
  - Creates and delete a ECS disk.starts, stops, restarts or terminates ecs instances.
  - Attach a disk to an ecs instance or detach a disk from it.
options:
  state:
    description:
      - The state of operating ecs disk.
    default: 'present'
    choices: ['present', 'absent']
    type: str
  alicloud_zone:
    description:
      - Aliyun availability zone ID which to launch the disk
    aliases: ['zone_id', 'zone']
    type: str
  disk_name:
    description:
      - The name of ECS disk, which is a string of 2 to 128 Chinese or English characters. It must begin with an
        uppercase/lowercase letter or a Chinese character and can contain numerals, ".", "_", or "-".
        It cannot begin with http:// or https://.
    aliases: ['name']
    type: str
  description:
    description:
      - The description of ECS disk, which is a string of 2 to 256 characters. It cannot begin with http:// or https://.
    aliases: ['disk_description']
    type: str
  resource_group_id:
    description:
      - The Id  of group which disk belongs to.
    aliases: ['group_id']
    type: str
  disk_category:
    description:
      - The category to apply to the disk.
    default: 'cloud'
    aliases: ['volume_type', 'disk_type']
    choices: ['cloud', 'cloud_efficiency', 'cloud_ssd', 'cloud_essd']
    type: str
  size:
    description:
      - Size of disk (in GB) to create.
        'cloud' valid value is 5~2000; 'cloud_efficiency', 'cloud_essd' or 'cloud_ssd' valid value is 20~32768.
    aliases: ['volume_size', 'disk_size']
    type: int
  snapshot_id:
    description:
      - Snapshot ID on which to base the data disk.
        If this parameter is specified, the value of 'size' will be ignored. The actual created disk size is the specified snapshot's size.
    aliases: ['snapshot']
    type: str
  disk_tags:
    description:
      - A hash/dictionaries of rds tags. C({"key":"value"})
    aliases: ['tags']
    type: dict
  instance_id:
    description:
      - Ecs instance ID is used to attach the disk. The specified instance and disk must be in the same zone.
        If it is null or not be specified, the attached disk will be detach from instance.
    aliases: ['instance']
    type: str
  disk_id:
    description:
      - Disk ID is used to attach an existing disk (required instance_id), detach or remove an existing disk.
    aliases: ['vol_id', 'id']
    type: str
  delete_with_instance:
    description:
      - When set to true, the disk will be released along with terminating ECS instance.
        When mark instance's attribution 'OperationLocks' as "LockReason":"security",
        its value will be ignored and disk will be released along with terminating ECS instance.
    aliases: ['delete_on_termination']
    default: False
    type: bool
notes:
    - At present, when attach disk, system allocates automatically disk device according to default order from /dev/xvdb to /dev/xvdz.
requirements:
    - "python >= 3.6"
    - "footmark >= 1.18.0"
extends_documentation_fragment:
    - community.general.alicloud
author:
    - "He Guimin (@xiaozhu36)"
'''

EXAMPLES = '''
# Advanced example with tagging and snapshot
- name: Create disk
  ali_disk:
    alicloud_zone: cn-beijing-h
    disk_name: Ansible-Disk
    description: Create From Ansible
    size: 20
    disk_category: 'cloud'


# Example to attach disk to an instance
- name: Attach disk to instance
  ali_disk:
    instance_id: xxxxxxxxxx
    disk_id: xxxxxxxxxx
    delete_with_instance: true

# Example to delete disk
- name: Delete disk
  ali_disk:
    id: xxxxxxxxxx
    state: absent


# Example to detach disk from instance
- name: Detach disk
  ali_disk:
    instance_id: xxxxxxxxxx
    disk_id: xxxxxxxxxx
    state: absent
'''

RETURN = '''
device:
    description: device name of attached disk
    returned: except on delete
    type: str
    sample: "/def/xdva"
disk_category:
    description: the category of disk
    returned: except on delete
    type: str
    sample: "cloud"
disk_id:
    description: the id of disk
    returned: when success
    type: str
    sample: "d-2zecn395ktwxxxxx"
disk_status:
    description: the current status of disk
    returned: except on delete
    type: str
    sample: "available"
disk:
    description: Details about the ecs disk that was created.
    returned: except on delete
    type: dict
    sample: {
        "category": "cloud_efficiency",
        "description": "travis-ansible-instance",
        "device": "",
        "disk_name": "travis-ansible-instance",
        "id": "d-2ze9yw0a1sw9neyx8t24",
        "instance_id": "",
        "launch_time": "2017-06-19T03:19:30Z",
        "region_id": "cn-beijing",
        "size": 40,
        "status": "available",
        "type": "data",
        "zone_id": "cn-beijing-a"
    }
instance_id:
    description: the instance id which attached disk
    returned: on attach
    type: str
    sample: "i-i2rnfnenfnds"
'''

import time
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.alicloud_ecs import ecs_argument_spec, ecs_connect

HAS_FOOTMARK = False

try:
    from footmark.exception import ECSResponseError

    HAS_FOOTMARK = True
except ImportError:
    HAS_FOOTMARK = False


def get_disk_detail(disk):
    """
    Method call to attach disk

    :param module: Ansible module object
    :param disk_id:  ID of Disk to Describe
    :return: return id, status and object of disk
    """

    return {'id': disk.disk_id,
            'category': disk.category,
            'size': disk.size,
            'device': disk.device,
            'zone_id': disk.zone_id,
            'region_id': disk.region_id,
            'launch_time': disk.creation_time,
            'disk_name': disk.disk_name,
            'description': disk.description,
            'status': disk.status,
            'type': disk.type,
            'instance_id': disk.instance_id
            }


def main():
    argument_spec = ecs_argument_spec()
    argument_spec.update(dict(
        resource_group_id=dict(type='str', aliases=['group_id']),
        alicloud_zone=dict(type='str', aliases=['zone_id', 'zone']),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        disk_id=dict(type='str', aliases=['vol_id', 'id']),
        disk_name=dict(type='str', aliases=['name']),
        disk_category=dict(type='str', aliases=['disk_type', 'volume_type'], choices=['cloud', 'cloud_efficiency', 'cloud_ssd', 'cloud_essd'], default='cloud'),
        size=dict(type='int', aliases=['disk_size', 'volume_size']),
        disk_tags=dict(type='dict', aliases=['tags']),
        snapshot_id=dict(type='str', aliases=['snapshot']),
        description=dict(type='str', aliases=['disk_description']),
        instance_id=dict(type='str', aliases=['instance']),
        delete_with_instance=dict(type='bool', aliases=['delete_on_termination'], default=False)
    )
    )
    module = AnsibleModule(argument_spec=argument_spec)

    if not HAS_FOOTMARK:
        module.fail_json(msg="footmark required for the module ali_disk.")

    ecs = ecs_connect(module)
    state = module.params['state']

    instance_id = module.params['instance_id']
    disk_id = module.params['disk_id']
    zone_id = module.params['alicloud_zone']
    disk_name = module.params['disk_name']
    delete_with_instance = module.params['delete_with_instance']
    description = module.params['description']

    changed = False
    current_disk = None

    try:
        if disk_id:
            disks = ecs.get_all_volumes(zone_id=zone_id, volume_ids=[disk_id])
            if disks and len(disks) == 1:
                current_disk = disks[0]
        elif disk_name:
            disks = ecs.get_all_volumes(zone_id=zone_id, volume_name=disk_name)
            if disks:
                if len(disks) == 1:
                    current_disk = disks[0]
                else:
                    disk_ids = []
                    for d in disks:
                        disk_ids.append(d.id)
                    module.fail_json(msg="There is too many disks match name '{0}', "
                                         "please use disk_id or a new disk_name to specify a unique disk."
                                         "Matched disk ids are: {1}".format(disk_name, disk_ids))
    except ECSResponseError as e:
        module.fail_json(msg='Error in get_all_volumes: %s' % str(e))

    if state == 'absent':
        if not current_disk:
            module.fail_json(msg="Please use disk_id or disk_name to specify one disk for detaching or deleting.")
        if instance_id:
            try:
                changed = current_disk.detach(instance_id)
                module.exit_json(changed=changed, disk_id=current_disk.id, disk_category=current_disk.category,
                                 disk_status=current_disk.status, instance_id=instance_id,
                                 disk=get_disk_detail(current_disk))
            except Exception as e:
                module.fail_json(msg='Detaching disk {0} is failed, error: {1}'.format(current_disk.id, e))

        try:
            changed = current_disk.delete()
            module.exit_json(changed=changed)
        except Exception as e:
            module.fail_json(msg='Deleting disk {0} is failed, error: {1}'.format(current_disk.id, e))

    # state == present
    if not current_disk:
        disk_category = module.params['disk_category']
        size = module.params['size']
        disk_tags = module.params['disk_tags']
        snapshot_id = module.params['snapshot_id']
        client_token = "Ansible-Alicloud-%s-%s" % (hash(str(module.params)), str(time.time()))
        try:
            current_disk = ecs.create_disk(zone_id=zone_id, disk_name=disk_name,
                                           description=description, disk_category=disk_category, size=size,
                                           disk_tags=disk_tags, snapshot_id=snapshot_id, client_token=client_token)
            changed = True
        except Exception as e:
            module.fail_json(msg='Creating a new disk is failed, error: {0}'.format(e))

    else:
        try:
            if current_disk.name != disk_name \
                    or current_disk.description != description \
                    or current_disk.delete_with_instance != delete_with_instance:
                changed = current_disk.modify(disk_name=disk_name, description=description,
                                              delete_with_instance=delete_with_instance)
        except Exception as e:
            module.fail_json(msg='Updating disk {0} attribute is failed, error: {1}'.format(current_disk.id, e))

    if instance_id and current_disk and str(current_disk.status).lower() == "available":
        try:
            changed = current_disk.attach(instance_id=instance_id, delete_with_instance=delete_with_instance)
        except Exception as e:
            module.fail_json(
                msg='Attaching disk {0} to instance {1} is failed, error: {2}'.format(current_disk.id, instance_id, e))

    module.exit_json(changed=changed, disk_id=current_disk.id, disk_category=current_disk.category,
                     disk_status=current_disk.status, instance_id=instance_id, disk=get_disk_detail(current_disk))


if __name__ == '__main__':
    main()
