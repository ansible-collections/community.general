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
module: ali_disk_info
short_description: Gather facts on disks of Alibaba Cloud ECS.
description:
     - This module fetches data from the Open API in Alicloud.
       The module must be called from within the ECS disk itself.
options:
  name_prefix:
    description:
      - Use a disk name prefix to filter disks.
    type: str
  filters:
    description:
      - A dict of filters to apply. Each dict item consists of a filter key and a filter value. The filter keys can be
        all of request parameters. See U(https://www.alibabacloud.com/help/zh/doc-detail/25514.htm) for parameter details.
        Filter keys can be same as request parameter name or be lower case and use underscore ("_") or dash ("-") to
        connect different words in one parameter.
    type: dict
  tags:
    description:
      - A hash/dictionaries of disk tags. C({"key":"value"})
    type: dict
author:
    - "He Guimin (@xiaozhu36)"
requirements:
    - "python >= 3.6"
    - "footmark >= 1.19.0"
extends_documentation_fragment:
    - community.general.alicloud
'''

EXAMPLES = '''
# Fetch disk details according to setting different filters
- name: Filter disk using filters
  ali_disk_info:
    filters:
      disk_ids: ['d-2ze3carakr2qxxxxxx', 'd-2zej6cuwzmummxxxxxx']
      zone_id: 'cn-beijing-c'
      instance_id: 'i-2zeii6c3xxxxxxx'

- name: Filter disk using name_prefix
  ali_disk_info:
    name_prefix: 'YourDiskNamePrefix'

- name: Filter all disks
  ali_disk_info:
'''

RETURN = '''
disk_ids:
    description: List all disk's id after operating ecs disk.
    returned: when success
    type: list
    elements: str
    sample: ["d-2ze8ohezcyvm4omrabud","d-2zeakwizkdjdu4q4lfco"]
disks:
    description: Details about the ecs disks that were created.
    returned: when success
    type: list
    elements: dict
    sample: [
    {
        "attached_time": "2017-08-15T06:47:55Z",
        "category": "cloud_efficiency",
        "creation_time": "2017-08-15T06:47:45Z",
        "delete_auto_snapshot": false,
        "delete_with_instance": true,
        "description": "helloworld",
        "detached_time": "",
        "device": "/dev/xvda",
        "disk_charge_type": "PostPaid",
        "enable_auto_snapshot": true,
        "encrypted": false,
        "id": "d-2ze8ohezcyvm4omrabud",
        "image_id": "ubuntu_140405_32_40G_cloudinit_20161115.vhd",
        "instance_id": "i-2zegc3s8ihxq2pcysekk",
        "name": "test1",
        "operation_locks": {
            "operation_lock": []
        },
        "portable": false,
        "product_code": "",
        "region_id": "cn-beijing",
        "size": 40,
        "snapshop_id": "",
        "status": "in_use",
        "type": "system",
        "zone_id": "cn-beijing-a"
    },
    {
        "attached_time": "2017-08-13T06:57:37Z",
        "category": "cloud_efficiency",
        "creation_time": "2017-08-13T06:57:30Z",
        "delete_auto_snapshot": false,
        "delete_with_instance": true,
        "description": "",
        "detached_time": "",
        "device": "/dev/xvda",
        "disk_charge_type": "PostPaid",
        "enable_auto_snapshot": true,
        "encrypted": false,
        "id": "d-2zeakwizkdjdu4q4lfco",
        "image_id": "ubuntu_140405_64_40G_cloudinit_20161115.vhd",
        "instance_id": "i-2zeenj8meljkoi85lz3c",
        "name": "test2",
        "operation_locks": {
            "operation_lock": []
        },
        "portable": false,
        "product_code": "",
        "region_id": "cn-beijing",
        "size": 40,
        "snapshop_id": "",
        "status": "in_use",
        "type": "system",
        "zone_id": "cn-beijing-a"
    }
]
total:
    description: The number of all disks after operating ecs disk.
    returned: when success
    type: int
    sample: 2
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.alicloud_ecs import ecs_argument_spec, ecs_connect

HAS_FOOTMARK = False

try:
    from footmark.exception import ECSResponseError
    HAS_FOOTMARK = True
except ImportError:
    HAS_FOOTMARK = False


def main():
    argument_spec = ecs_argument_spec()
    argument_spec.update(dict(
        filters=dict(type='dict'),
        name_prefix=dict(type='str'),
        tags=dict(type='dict')
    )
    )
    module = AnsibleModule(argument_spec=argument_spec)
    if HAS_FOOTMARK is False:
        module.fail_json(msg='footmark required for this module')

    ecs = ecs_connect(module)

    disks = []
    disk_ids = []

    filters = module.params['filters']
    if not filters:
        filters = {}

    name_prefix = module.params['name_prefix']
    tags = module.params['tags']

    for disk in ecs.describe_disks(**filters):
        if name_prefix and not str(disk.name).startswith(name_prefix):
            continue
        if tags:
            flag = False
            for key, value in list(tags.items()):
                if key in list(disk.tags.keys()) and value == disk.tags[key]:
                    flag = True
            if not flag:
                continue
        disks.append(disk.read())
        disk_ids.append(disk.id)

    module.exit_json(changed=False, disk_ids=disk_ids, disks=disks, total=len(disks))


if __name__ == '__main__':
    main()
