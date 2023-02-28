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
requirements:
  - python-consul
  - requests
author:
  - Steve Gargan (@sgargan)
extends_documentation_fragment:
  - community.general.attributes
attributes:
    check_mode:
        support: none
    diff_mode:
        support: none
options:
    id:
        description:
          - ID of the session, required when I(state) is either C(info) or
            C(remove).
        type: str
    state:
        description:
          - Whether the session should be present i.e. created if it doesn't
            exist, or absent, removed if present. If created, the I(id) for the
            session is returned in the output. If C(absent), I(id) is
            required to remove the session. Info for a single session, all the
            sessions for a node or all available sessions can be retrieved by
            specifying C(info), C(node) or C(list) for the I(state); for C(node)
            or C(info), the node I(name) or session I(id) is required as parameter.
        choices: [ absent, info, list, node, present ]
        type: str
        default: present
    name:
        description:
          - The name that should be associated with the session. Required when
            I(state=node) is used.
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
    host:
        description:
          - The host of the consul agent defaults to localhost.
        type: str
        default: localhost
    port:
        description:
          - The port on which the consul agent is running.
        type: int
        default: 8500
    scheme:
        description:
          - The protocol scheme on which the consul agent is running.
        type: str
        default: http
    validate_certs:
        description:
          - Whether to verify the TLS certificate of the consul agent.
        type: bool
        default: true
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
        description:
          - The token key identifying an ACL rule set that controls access to
            the key value pair.
        type: str
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

try:
    import consul
    from requests.exceptions import ConnectionError
    python_consul_installed = True
except ImportError:
    python_consul_installed = False

from ansible.module_utils.basic import AnsibleModule


def execute(module):

    state = module.params.get('state')

    if state in ['info', 'list', 'node']:
        lookup_sessions(module)
    elif state == 'present':
        update_session(module)
    else:
        remove_session(module)


def lookup_sessions(module):

    datacenter = module.params.get('datacenter')

    state = module.params.get('state')
    consul_client = get_consul_api(module)
    try:
        if state == 'list':
            sessions_list = consul_client.session.list(dc=datacenter)
            # Ditch the index, this can be grabbed from the results
            if sessions_list and len(sessions_list) >= 2:
                sessions_list = sessions_list[1]
            module.exit_json(changed=True,
                             sessions=sessions_list)
        elif state == 'node':
            node = module.params.get('node')
            sessions = consul_client.session.node(node, dc=datacenter)
            module.exit_json(changed=True,
                             node=node,
                             sessions=sessions)
        elif state == 'info':
            session_id = module.params.get('id')

            session_by_id = consul_client.session.info(session_id, dc=datacenter)
            module.exit_json(changed=True,
                             session_id=session_id,
                             sessions=session_by_id)

    except Exception as e:
        module.fail_json(msg="Could not retrieve session info %s" % e)


def update_session(module):

    name = module.params.get('name')
    delay = module.params.get('delay')
    checks = module.params.get('checks')
    datacenter = module.params.get('datacenter')
    node = module.params.get('node')
    behavior = module.params.get('behavior')
    ttl = module.params.get('ttl')

    consul_client = get_consul_api(module)

    try:
        session = consul_client.session.create(
            name=name,
            behavior=behavior,
            ttl=ttl,
            node=node,
            lock_delay=delay,
            dc=datacenter,
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


def remove_session(module):
    session_id = module.params.get('id')

    consul_client = get_consul_api(module)

    try:
        consul_client.session.destroy(session_id)

        module.exit_json(changed=True,
                         session_id=session_id)
    except Exception as e:
        module.fail_json(msg="Could not remove session with id '%s' %s" % (
                         session_id, e))


def get_consul_api(module):
    return consul.Consul(host=module.params.get('host'),
                         port=module.params.get('port'),
                         scheme=module.params.get('scheme'),
                         verify=module.params.get('validate_certs'),
                         token=module.params.get('token'))


def test_dependencies(module):
    if not python_consul_installed:
        module.fail_json(msg="python-consul required for this module. "
                             "see https://python-consul.readthedocs.io/en/latest/#installation")


def main():
    argument_spec = dict(
        checks=dict(type='list', elements='str'),
        delay=dict(type='int', default='15'),
        behavior=dict(type='str', default='release', choices=['release', 'delete']),
        ttl=dict(type='int'),
        host=dict(type='str', default='localhost'),
        port=dict(type='int', default=8500),
        scheme=dict(type='str', default='http'),
        validate_certs=dict(type='bool', default=True),
        id=dict(type='str'),
        name=dict(type='str'),
        node=dict(type='str'),
        state=dict(type='str', default='present', choices=['absent', 'info', 'list', 'node', 'present']),
        datacenter=dict(type='str'),
        token=dict(type='str', no_log=True),
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

    test_dependencies(module)

    try:
        execute(module)
    except ConnectionError as e:
        module.fail_json(msg='Could not connect to consul agent at %s:%s, error was %s' % (
            module.params.get('host'), module.params.get('port'), e))
    except Exception as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
