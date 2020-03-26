#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2016, Mathieu Bultel <mbultel@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: pacemaker_manage
short_description: Manage a pacemaker resource
extends_documentation_fragment: openstack
version_added: "2.9"
author: "Mathieu Bultel (matbu)"
description:
   - Manage a pacemaker resource from Ansible
options:
    state:
      description:
        - Indicate desired state of the cluster
      choices: ['manage', 'unmanage', 'enable', 'disable', 'restart',
                'show', 'delete', 'started', 'master', 'slave']
      required: true
    resource:
      description:
        - Specify which resource you want to handle
      required: false
      default: None
    timeout:
      description:
        - Timeout when the module should considered that the action has failed
      required: false
      default: 300
    check_mode:
        description:
          - Check only the status of the resource
        required: false
        default: false
    wait_for_resource:
        description:
          - Wait for resource to get the required state, will failed if the
            timeout is reach
        required: false
        default: false
requirements:
    - "python >= 2.6"
'''
EXAMPLES = '''
---
- name: Manage Pacemaker resources
  hosts: localhost
  gather_facts: no
  tasks:
    - name: enable haproxy
      pacemaker_resource: state=enable resource=haproxy
'''

RETURN = '''

'''

import time

from ansible.module_utils.basic import AnsibleModule


def check_resource_state(module, resource, state):
    # get resources
    cmd = "bash -c 'pcs status --full | grep -w \"%s[ \t]\"'" % resource
    rc, out, err = module.run_command(cmd)
    if state in out.lower():
        return True


def get_resource(module, resource):
    cmd = "pcs resource show %s" % resource
    return module.run_command(cmd)


def set_resource_state(module, resource, state, timeout):
    cmd = "pcs resource %s %s --wait=%s" % (state, resource, timeout)
    cmd_status = module.run_command(cmd)
    if cmd_status[0] == 0 and state == 'delete':
        # pcs delete operations are not atomic, the deletion might
        # fail if concurrent actions are happening on the resource
        # (e.g. cleanup). Double check that the deletion succeeded
        probe_status = get_resource(module, resource)
        if probe_status[0] == 0:
            return (1, 'Resource still present after deletion command', '')
    return cmd_status


def main():
    argument_spec = dict(
        state=dict(choices=['manage', 'unmanage', 'enable', 'disable',
                            'restart', 'show', 'delete', 'started',
                            'stopped', 'master', 'slave']),
        resource=dict(default=None),
        timeout=dict(default=300, type='int'),
        check_mode=dict(default=False, type='bool'),
        wait_for_resource=dict(default=False, type='bool'),
    )

    module = AnsibleModule(argument_spec, supports_check_mode=True)
    changed = False
    state = module.params['state']
    resource = module.params['resource']
    timeout = module.params['timeout']
    check_mode = module.params['check_mode']
    wait_for_resource = module.params['wait_for_resource']

    if check_mode:
        if check_resource_state(module, resource, state):
            module.exit_json(changed=changed,
                             out={'resource': resource, 'status': state})
        else:
            if wait_for_resource:
                t = time.time()
                status = False
                while time.time() < t + timeout:
                    if check_resource_state(module, resource, state):
                        status = True
                        break
                if status:
                    module.exit_json(changed=changed,
                                     out={'resource': resource,
                                          'status': state})
            module.fail_json(msg="Failed, the resource %s is not %s\n" %
                             (resource, state))

    resource_state = get_resource(module, resource)
    if resource_state == state:
        module.exit_json(changed=changed, out={'resource': resource,
                         'status': state})
    rc, out, err = set_resource_state(module, resource, state, timeout)
    if rc == 1:
        module.fail_json(msg="Failed, to set the resource %s to the state "
                         "%s" % (resource, state),
                         rc=rc,
                         output=out,
                         error=err)
    changed = True
    module.exit_json(changed=changed, out=out, rc=rc)


if __name__ == '__main__':
    main()
