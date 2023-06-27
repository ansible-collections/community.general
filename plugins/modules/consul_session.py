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
  - requests
author:
  - Steve Gargan (@sgargan)
  - Håkon Lerring (@Hakon)
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

from ansible.module_utils.basic import AnsibleModule

try:
    import requests
    from requests.exceptions import ConnectionError
    has_requests = True
except ImportError:
    has_requests = False


def execute(module):

    state = module.params.get('state')

    if state in ['info', 'list', 'node']:
        lookup_sessions(module)
    elif state == 'present':
        update_session(module)
    else:
        remove_session(module)


class RequestError(Exception):
    pass


def handle_consul_response_error(response):
    if 400 <= response.status_code < 600:
        raise RequestError('%d %s' % (response.status_code, response.content))


def get_consul_url(module):
    return '%s://%s:%s/v1' % (module.params.get('scheme'),
                              module.params.get('host'), module.params.get('port'))


def get_auth_headers(module):
    if 'token' in module.params and module.params.get('token') is not None:
        return {'X-Consul-Token': module.params.get('token')}
    else:
        return {}


def list_sessions(module, datacenter):
    url = '%s/session/list' % get_consul_url(module)
    headers = get_auth_headers(module)
    response = requests.get(
        url,
        headers=headers,
        params={
            'dc': datacenter},
        verify=module.params.get('validate_certs'))
    handle_consul_response_error(response)
    return response.json()


def list_sessions_for_node(module, node, datacenter):
    url = '%s/session/node/%s' % (get_consul_url(module), node)
    headers = get_auth_headers(module)
    response = requests.get(
        url,
        headers=headers,
        params={
            'dc': datacenter},
        verify=module.params.get('validate_certs'))
    handle_consul_response_error(response)
    return response.json()


def get_session_info(module, session_id, datacenter):
    url = '%s/session/info/%s' % (get_consul_url(module), session_id)
    headers = get_auth_headers(module)
    response = requests.get(
        url,
        headers=headers,
        params={
            'dc': datacenter},
        verify=module.params.get('validate_certs'))
    handle_consul_response_error(response)
    return response.json()


def lookup_sessions(module):

    datacenter = module.params.get('datacenter')

    state = module.params.get('state')
    try:
        if state == 'list':
            sessions_list = list_sessions(module, datacenter)
            # Ditch the index, this can be grabbed from the results
            if sessions_list and len(sessions_list) >= 2:
                sessions_list = sessions_list[1]
            module.exit_json(changed=True,
                             sessions=sessions_list)
        elif state == 'node':
            node = module.params.get('node')
            sessions = list_sessions_for_node(module, node, datacenter)
            module.exit_json(changed=True,
                             node=node,
                             sessions=sessions)
        elif state == 'info':
            session_id = module.params.get('id')

            session_by_id = get_session_info(module, session_id, datacenter)
            module.exit_json(changed=True,
                             session_id=session_id,
                             sessions=session_by_id)

    except Exception as e:
        module.fail_json(msg="Could not retrieve session info %s" % e)


def create_session(module, name, behavior, ttl, node,
                   lock_delay, datacenter, checks):
    url = '%s/session/create' % get_consul_url(module)
    headers = get_auth_headers(module)
    create_data = {
        "LockDelay": lock_delay,
        "Node": node,
        "Name": name,
        "Checks": checks,
        "Behavior": behavior,
    }
    if ttl is not None:
        create_data["TTL"] = "%ss" % str(ttl)  # TTL is in seconds
    response = requests.put(
        url,
        headers=headers,
        params={
            'dc': datacenter},
        json=create_data,
        verify=module.params.get('validate_certs'))
    handle_consul_response_error(response)
    create_session_response_dict = response.json()
    return create_session_response_dict["ID"]


def update_session(module):

    name = module.params.get('name')
    delay = module.params.get('delay')
    checks = module.params.get('checks')
    datacenter = module.params.get('datacenter')
    node = module.params.get('node')
    behavior = module.params.get('behavior')
    ttl = module.params.get('ttl')

    try:
        session = create_session(module,
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


def destroy_session(module, session_id):
    url = '%s/session/destroy/%s' % (get_consul_url(module), session_id)
    headers = get_auth_headers(module)
    response = requests.put(
        url,
        headers=headers,
        verify=module.params.get('validate_certs'))
    handle_consul_response_error(response)
    return response.content == "true"


def remove_session(module):
    session_id = module.params.get('id')

    try:
        destroy_session(module, session_id)

        module.exit_json(changed=True,
                         session_id=session_id)
    except Exception as e:
        module.fail_json(msg="Could not remove session with id '%s' %s" % (
                         session_id, e))


def test_dependencies(module):
    if not has_requests:
        raise ImportError(
            "requests required for this module. See https://pypi.org/project/requests/")


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
        host=dict(type='str', default='localhost'),
        port=dict(type='int', default=8500),
        scheme=dict(type='str', default='http'),
        validate_certs=dict(type='bool', default=True),
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
