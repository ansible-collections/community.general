#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2021, Andreas Botzner (@paginabianca) <andreas at botzner dot com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: proxmox_tasks_info
short_description: Retrieve information about one or more Proxmox VE tasks
version_added: 3.8.0
description:
  - Retrieve information about one or more Proxmox VE tasks.
author: 'Andreas Botzner (@paginabianca) <andreas at botzner dot com>'
options:
  node:
    description:
      - Node where to get tasks.
    required: true
    type: str
  task:
    description:
      - Return specific task.
    aliases: ['upid', 'name']
    type: str
extends_documentation_fragment:
    - community.general.proxmox.documentation
    - community.general.attributes
    - community.general.attributes.info_module
'''


EXAMPLES = '''
- name: List tasks on node01
  community.general.proxmox_task_info:
    api_host: proxmoxhost
    api_user: root@pam
    api_password: '{{ password | default(omit) }}'
    api_token_id: '{{ token_id | default(omit) }}'
    api_token_secret: '{{ token_secret | default(omit) }}'
    node: node01
  register: result

- name: Retrieve information about specific tasks on node01
  community.general.proxmox_task_info:
    api_host: proxmoxhost
    api_user: root@pam
    api_password: '{{ password | default(omit) }}'
    api_token_id: '{{ token_id | default(omit) }}'
    api_token_secret: '{{ token_secret | default(omit) }}'
    task: 'UPID:node01:00003263:16167ACE:621EE230:srvreload:networking:root@pam:'
    node: node01
  register: proxmox_tasks
'''


RETURN = '''
proxmox_tasks:
    description: List of tasks.
    returned: on success
    type: list
    elements: dict
    contains:
      id:
        description: ID of the task.
        returned: on success
        type: str
      node:
        description: Node name.
        returned: on success
        type: str
      pid:
        description: PID of the task.
        returned: on success
        type: int
      pstart:
        description: pastart of the task.
        returned: on success
        type: int
      starttime:
        description: Starting time of the task.
        returned: on success
        type: int
      type:
        description: Type of the task.
        returned: on success
        type: str
      upid:
        description: UPID of the task.
        returned: on success
        type: str
      user:
        description: User that owns the task.
        returned: on success
        type: str
      endtime:
        description: Endtime of the task.
        returned: on success, can be absent
        type: int
      status:
        description: Status of the task.
        returned: on success, can be absent
        type: str
      failed:
        description: If the task failed.
        returned: when status is defined
        type: bool
msg:
    description: Short message.
    returned: on failure
    type: str
    sample: 'Task: UPID:xyz:xyz does not exist on node: proxmoxnode'
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.proxmox import (
    proxmox_auth_argument_spec, ProxmoxAnsible)


class ProxmoxTaskInfoAnsible(ProxmoxAnsible):
    def get_task(self, upid, node):
        tasks = self.get_tasks(node)
        for task in tasks:
            if task.info['upid'] == upid:
                return [task]

    def get_tasks(self, node):
        tasks = self.proxmox_api.nodes(node).tasks.get()
        return [ProxmoxTask(task) for task in tasks]


class ProxmoxTask:
    def __init__(self, task):
        self.info = dict()
        for k, v in task.items():
            if k == 'status' and isinstance(v, str):
                self.info[k] = v
                if v != 'OK':
                    self.info['failed'] = True
            else:
                self.info[k] = v


def proxmox_task_info_argument_spec():
    return dict(
        task=dict(type='str', aliases=['upid', 'name'], required=False),
        node=dict(type='str', required=True),
    )


def main():
    module_args = proxmox_auth_argument_spec()
    task_info_args = proxmox_task_info_argument_spec()
    module_args.update(task_info_args)

    module = AnsibleModule(
        argument_spec=module_args,
        required_together=[('api_token_id', 'api_token_secret')],
        required_one_of=[('api_password', 'api_token_id')],
        supports_check_mode=True)
    result = dict(changed=False)

    proxmox = ProxmoxTaskInfoAnsible(module)
    upid = module.params['task']
    node = module.params['node']
    if upid:
        tasks = proxmox.get_task(upid=upid, node=node)
    else:
        tasks = proxmox.get_tasks(node=node)
    if tasks is not None:
        result['proxmox_tasks'] = [task.info for task in tasks]
        module.exit_json(**result)
    else:
        result['msg'] = 'Task: {0} does not exist on node: {1}.'.format(
            upid, node)
        module.fail_json(**result)


if __name__ == '__main__':
    main()
