#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2020, Tristan Le Guern <tleguern at bouledef.eu>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: proxmox_instance_actions
short_description: Perform actions on Qemu/KVM and LXC instances from Proxmox VE
version_added: 2.2.0
description:
  - Perform actions on an existing instance from Proxmox VE.
  - This module does not return data.
options:
  action:
    description:
      - Perform the given action.
      - C(reset) is only valid with Qemu/KVM instances.
    type: str
    choices: ['reboot', 'reset', 'resume', 'shutdown', 'start', 'stop', 'suspend']
    required: true
  force:
    description:
      - Force an instance to shutdown.
      - Only possible if I(action) is C(shutdown), otherwise, ignored.
    type: bool
    default: no
  name:
    description:
      - Specifies the instance name.
    type: str
  node:
    description:
      - Proxmox VE node on which to operate.
    type: str
    required: true
  timeout:
    description:
      - How long should the socket layer wait before timing out for API calls.
    type: int
    default: 30
  vmid:
    description:
      - Specifies the instance ID.
    type: int
author: Tristan Le Guern (@Aversiste)
extends_documentation_fragment: community.general.proxmox.documentation
notes:
  - Supports C(check_mode).
'''


EXAMPLES = '''
- name: Restart instance sabrewulf
  community.general.proxmox_instance_actions:
    api_host: helldorado
    api_user: root@pam
    api_password: "{{ password | default(omit) }}"
    api_token_id: "{{ token_id | default(omit) }}"
    api_token_secret: "{{ token_secret | default(omit) }}"
    node: sabrewulf
    name: spynal
    action: reboot

- name: Stop instance zavala
  community.general.proxmox_instance_actions:
    api_host: helldorado
    api_user: root@pam
    api_password: "{{ password | default(omit) }}"
    api_token_id: "{{ token_id | default(omit) }}"
    api_token_secret: "{{ token_secret | default(omit) }}"
    node: sabrewulf
    name: zavala
    action: stop
'''

RETURN = '''#'''

import time
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils._text import to_native
from ansible_collections.community.general.plugins.module_utils.proxmox import (
    proxmox_auth_argument_spec, ProxmoxAnsible, ansible_to_proxmox_bool, HAS_PROXMOXER,
    PROXMOXER_IMP_ERR)


class ProxmoxInstanceActionsAnsible(ProxmoxAnsible):
    def _get_instance_by_id(self, vmid):
        vms = self.proxmox_api.cluster.resources.get(type='vm')
        vm = [vm for vm in vms if vm['vmid'] == int(vmid)]
        if len(vm) == 0:
            self.module.fail_json(msg="No instance with ID '%d' exists in this cluster" % vmid)
        return vm[0]

    def _get_instance_by_name(self, name):
        vms = self.proxmox_api.cluster.resources.get(type='vm')
        vm = [vm for vm in vms if vm['name'] == name]
        if len(vm) == 0:
            self.module.fail_json(msg="No instance with name '%s' exists in this cluster" % name)
        return vm[0]

    def get_instance(self, vmid=None, name=None):
        if vmid:
            vm = self._get_instance_by_id(vmid)
        elif name:
            vm = self._get_instance_by_name(name)
        else:
            self.module.fail_json(msg="Implementation error")
        return ProxmoxInstance(self.proxmox_api, vm)

    def get_tasks(self, node=None):
        tasks = self.proxmox_api.nodes(node).tasks.get()
        return [ProxmoxTask(self.proxmox_api, node, task['upid']) for task in tasks]


class ProxmoxInstance:
    def __init__(self, proxmox_api, vm):
        self.vm = vm
        self.proxmox_api = proxmox_api

    def status(self):
        node = self.vm['node']
        vmid = self.vm['vmid']
        vztype = self.vm['type']
        return getattr(self.proxmox_api.nodes(node), vztype)(vmid).status.current.get()

    def reboot(self):
        node = self.vm['node']
        vmid = self.vm['vmid']
        vztype = self.vm['type']
        taskid = getattr(self.proxmox_api.nodes(node), vztype)(vmid).status.reboot.post()
        return ProxmoxTask(self.proxmox_api, node, taskid)

    def reset(self):
        node = self.vm['node']
        vmid = self.vm['vmid']
        vztype = self.vm['type']
        if vztype == 'lxc':
            raise Exception('The action "reset" is only valid for qemu virtual machines')
        taskid = self.proxmox_api.nodes(node).qemu(vmid).status.reset.post()
        return ProxmoxTask(self.proxmox_api, node, taskid)

    def resume(self):
        node = self.vm['node']
        vmid = self.vm['vmid']
        vztype = self.vm['type']
        taskid = getattr(self.proxmox_api.nodes(node), vztype)(vmid).status.resume.post()
        return ProxmoxTask(self.proxmox_api, node, taskid)

    def shutdown(self, force=False):
        node = self.vm['node']
        vmid = self.vm['vmid']
        vztype = self.vm['type']
        force = ansible_to_proxmox_bool(force)
        taskid = getattr(self.proxmox_api.nodes(node), vztype)(vmid).status.shutdown.post(forceStop=force)
        return ProxmoxTask(self.proxmox_api, node, taskid)

    def start(self):
        node = self.vm['node']
        vmid = self.vm['vmid']
        vztype = self.vm['type']
        taskid = getattr(self.proxmox_api.nodes(node), vztype)(vmid).status.start.post()
        return ProxmoxTask(self.proxmox_api, node, taskid)

    def stop(self):
        node = self.vm['node']
        vmid = self.vm['vmid']
        vztype = self.vm['type']
        taskid = getattr(self.proxmox_api.nodes(node), vztype)(vmid).status.stop.post()
        return ProxmoxTask(self.proxmox_api, node, taskid)

    def suspend(self):
        node = self.vm['node']
        vmid = self.vm['vmid']
        vztype = self.vm['type']
        taskid = getattr(self.proxmox_api.nodes(node), vztype)(vmid).status.suspend.post()
        return ProxmoxTask(self.proxmox_api, node, taskid)


class ProxmoxTask:
    def __init__(self, proxmox_api, node, taskid):
        self.proxmox_api = proxmox_api
        self.node = node
        self.taskid = taskid

    def status(self):
        return self.proxmox_api.nodes(self.node).tasks(self.taskid).status.get()

    def log(self, start=0, limit=50):
        logs = self.proxmox_api.nodes(self.node).tasks(self.taskid).log.get(start=start, limit=limit)
        newlogs = dict()
        for d in logs:
            newlogs[d['n']] = d['t']
        return(newlogs)

    def lastlog(self):
        logs = self.log()
        return logs[len(logs)]

    def wait(self, timeout):
        while timeout:
            status = self.status()
            if status['status'] == 'stopped':
                if status['exitstatus'] == 'OK':
                    time.sleep(1)
                    return True
                else:
                    raise Exception('Task exited in error -- %s' % status['exitstatus'])
            timeout = timeout - 1
            if timeout == 0:
                raise Exception('Reached timeout while waiting for task. Last line in the log: %s'
                                % self.lastlog())
            time.sleep(1)


def proxmox_instance_actions_argument_spec():
    return dict(
        action=dict(type='str',
                    required=True,
                    choices=['reboot', 'reset', 'resume', 'shutdown', 'start', 'stop', 'suspend']
                    ),
        force=dict(type='bool', default=False),
        name=dict(type='str'),
        node=dict(type='str', required=True),
        timeout=dict(type='int', default=30),
        vmid=dict(type='int'),
    )


def main():
    module_args = proxmox_auth_argument_spec()
    proxmox_instance_actions_args = proxmox_instance_actions_argument_spec()
    module_args.update(proxmox_instance_actions_args)

    module = AnsibleModule(
        argument_spec=module_args,
        required_one_of=[('api_password', 'api_token_id'), ('name', 'vmid')],
        required_together=[('api_token_id', 'api_token_secret')],
        supports_check_mode=True
    )
    result = dict(
        changed=False
    )

    if not HAS_PROXMOXER:
        module.fail_json(msg=missing_required_lib('proxmoxer'), exception=PROXMOXER_IMP_ERR)

    proxmox = ProxmoxInstanceActionsAnsible(module)
    action = module.params['action']
    force = module.params['force']
    timeout = module.params['timeout']
    if module.params['vmid']:
        vm = proxmox.get_instance(vmid=module.params['vmid'])
    else:
        vm = proxmox.get_instance(name=module.params['name'])

    # State and actions matrice:
    #            +---------+---------+---------+-----------+
    #            | running | paused  | stopped | prelaunch |
    # +----------+---------+---------+---------+-----------+
    # | reboot   |      OK |   Error |   Error |           |
    # | reset    |      OK |      OK |   Error |           |
    # | resume   |    Noop |      OK |   Error |           |
    # | shutdown |      OK |   Error |    Noop |           |
    # | start    |    Noop |   Error |      OK |           |
    # | stop     |      OK |      OK |    Noop |        OK |
    # | suspend  |      OK |    Noop |   Error |           |
    # +----------+---------+---------+---------+-----------+

    # Skip noop operations directly
    status = vm.status()
    if ((status['qmpstatus'] == 'paused' and action == 'suspend')
       or (status['qmpstatus'] == 'running' and (action == 'resume' or action == 'start'))
       or (status['qmpstatus'] == 'stopped' and (action == 'stop' or action == 'shutdown'))):
        module.exit_json(**result)

    if module.check_mode:
        result['changed'] = True
        module.exit_json(**result)

    try:
        if action == 'reboot':
            task = vm.reboot()
        elif action == 'reset':
            task = vm.reset()
        elif action == 'resume':
            task = vm.resume()
        elif action == 'shutdown':
            task = vm.shutdown(force=force)
        elif action == 'start':
            task = vm.start()
        elif action == 'stop':
            task = vm.stop()
        elif action == 'suspend':
            task = vm.suspend()
    except Exception as e:
        module.fail_json(msg="Error during %s call:  %s" % (action, to_native(e)))

    try:
        task.wait(timeout)
    except Exception as e:
        module.fail_json(msg="Error while waiting for task: %s" % to_native(e), taskid=task.taskid)
    result['changed'] = True
    module.exit_json(**result)


if __name__ == '__main__':
    main()
