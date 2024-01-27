#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2015, Steve Gargan <steve.gargan@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
module: consul_session
short_description: Manipulate consul sessions
description:
 - Allows the addition, modification and deletion of sessions in a consul
   cluster. These sessions can then be used in conjunction with key value pairs
   to implement distributed locks. In depth documentation for working with
   sessions can be found at http://www.consul.io/docs/internals/sessions.html
author:
  - Steve Gargan (@sgargan)
  - Håkon Lerring (@Hakon)
extends_documentation_fragment:
  - community.general.consul
  - community.general.consul.actiongroup_consul
  - community.general.consul.token
  - community.general.attributes
attributes:
    check_mode:
        support: none
    diff_mode:
        support: none
options:
    id:
        description:
          - ID of the session, required when O(state) is either V(info) or
            V(remove).
        type: str
    state:
        description:
          - Whether the session should be present i.e. created if it doesn't
            exist, or absent, removed if present. If created, the O(id) for the
            session is returned in the output. If V(absent), O(id) is
            required to remove the session. Info for a single session, all the
            sessions for a node or all available sessions can be retrieved by
            specifying V(info), V(node) or V(list) for the O(state); for V(node)
            or V(info), the node O(name) or session O(id) is required as parameter.
        choices: [ absent, info, list, node, present ]
        type: str
        default: present
    name:
        description:
          - The name that should be associated with the session. Required when
            O(state=node) is used.
        type: str
    delay:
        description:
          - The optional lock delay that can be attached to the session when it
            is created. Locks for invalidated sessions ar blocked from being
            acquired until this delay has expired. Durations are in seconds.
        type: int
        default: 15
    node:
        description:
          - The name of the node that with which the session will be associated.
            by default this is the name of the agent.
        type: str
    datacenter:
        description:
          - The name of the datacenter in which the session exists or should be
            created.
        type: str
    checks:
        description:
          - Checks that will be used to verify the session health. If
            all the checks fail, the session will be invalidated and any locks
            associated with the session will be release and can be acquired once
            the associated lock delay has expired.
        type: list
        elements: str
    behavior:
        description:
          - The optional behavior that can be attached to the session when it
            is created. This controls the behavior when a session is invalidated.
        choices: [ delete, release ]
        type: str
        default: release
    ttl:
        description:
          - Specifies the duration of a session in seconds (between 10 and 86400).
        type: int
        version_added: 5.4.0
    token:
        version_added: 5.6.0
'''

EXAMPLES = '''
- name: Register basic session with consul
  community.general.consul_session:
    name: session1

- name: Register a session with an existing check
  community.general.consul_session:
    name: session_with_check
    checks:
      - existing_check_name

- name: Register a session with lock_delay
  community.general.consul_session:
    name: session_with_delay
    delay: 20s

- name: Retrieve info about session by id
  community.general.consul_session:
    id: session_id
    state: info

- name: Retrieve active sessions
  community.general.consul_session:
    state: list

- name: Register session with a ttl
  community.general.consul_session:
    name: session-with-ttl
    ttl: 600  # sec
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.consul import (
    AUTH_ARGUMENTS_SPEC, _ConsulModule
)


def execute(module, consul_module):

    state = module.params.get('state')

    if state in ['info', 'list', 'node']:
        lookup_sessions(module, consul_module)
    elif state == 'present':
        update_session(module, consul_module)
    else:
        remove_session(module, consul_module)


def list_sessions(consul_module, datacenter):
    return consul_module.get(
        'session/list',
        params={'dc': datacenter})


def list_sessions_for_node(consul_module, node, datacenter):
    return consul_module.get(
        ('session', 'node', node),
        params={'dc': datacenter})


def get_session_info(consul_module, session_id, datacenter):
    return consul_module.get(
        ('session', 'info', session_id),
        params={'dc': datacenter})


def lookup_sessions(module, consul_module):

    datacenter = module.params.get('datacenter')

    state = module.params.get('state')
    try:
        if state == 'list':
            sessions_list = list_sessions(consul_module, datacenter)
            # Ditch the index, this can be grabbed from the results
            if sessions_list and len(sessions_list) >= 2:
                sessions_list = sessions_list[1]
            module.exit_json(changed=True,
                             sessions=sessions_list)
        elif state == 'node':
            node = module.params.get('node')
            sessions = list_sessions_for_node(consul_module, node, datacenter)
            module.exit_json(changed=True,
                             node=node,
                             sessions=sessions)
        elif state == 'info':
            session_id = module.params.get('id')

            session_by_id = get_session_info(consul_module, session_id, datacenter)
            module.exit_json(changed=True,
                             session_id=session_id,
                             sessions=session_by_id)

    except Exception as e:
        module.fail_json(msg="Could not retrieve session info %s" % e)


def create_session(consul_module, name, behavior, ttl, node,
                   lock_delay, datacenter, checks):
    create_data = {
        "LockDelay": lock_delay,
        "Node": node,
        "Name": name,
        "Checks": checks,
        "Behavior": behavior,
    }
    if ttl is not None:
        create_data["TTL"] = "%ss" % str(ttl)  # TTL is in seconds
    create_session_response_dict = consul_module.put(
        'session/create',
        params={
            'dc': datacenter},
        data=create_data)
    return create_session_response_dict["ID"]


def update_session(module, consul_module):

    name = module.params.get('name')
    delay = module.params.get('delay')
    checks = module.params.get('checks')
    datacenter = module.params.get('datacenter')
    node = module.params.get('node')
    behavior = module.params.get('behavior')
    ttl = module.params.get('ttl')

    try:
        session = create_session(consul_module,
                                 name=name,
                                 behavior=behavior,
                                 ttl=ttl,
                                 node=node,
                                 lock_delay=delay,
                                 datacenter=datacenter,
                                 checks=checks
                                 )
        module.exit_json(changed=True,
                         session_id=session,
                         name=name,
                         behavior=behavior,
                         ttl=ttl,
                         delay=delay,
                         checks=checks,
                         node=node)
    except Exception as e:
        module.fail_json(msg="Could not create/update session %s" % e)


def destroy_session(consul_module, session_id):
    return consul_module.put(('session', 'destroy', session_id))


def remove_session(module, consul_module):
    session_id = module.params.get('id')

    try:
        destroy_session(consul_module, session_id)

        module.exit_json(changed=True,
                         session_id=session_id)
    except Exception as e:
        module.fail_json(msg="Could not remove session with id '%s' %s" % (
                         session_id, e))


def main():
    argument_spec = dict(
        checks=dict(type='list', elements='str'),
        delay=dict(type='int', default='15'),
        behavior=dict(
            type='str',
            default='release',
            choices=[
                'release',
                'delete']),
        ttl=dict(type='int'),
        id=dict(type='str'),
        name=dict(type='str'),
        node=dict(type='str'),
        state=dict(
            type='str',
            default='present',
            choices=[
                'absent',
                'info',
                'list',
                'node',
                'present']),
        datacenter=dict(type='str'),
        **AUTH_ARGUMENTS_SPEC
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=[
            ('state', 'node', ['name']),
            ('state', 'info', ['id']),
            ('state', 'remove', ['id']),
        ],
        supports_check_mode=False
    )
    consul_module = _ConsulModule(module)

    try:
        execute(module, consul_module)
    except Exception as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
