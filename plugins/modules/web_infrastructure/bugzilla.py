#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Chuang Cao <chcao@redhat.com>
# Atlassian open-source approval reference OSR-76.
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = """
module: bugzilla
version_added: "1.2.0"
short_description: Manage bugs in a Bugzilla instance by xmlrpc
description:
  -  Fetch, comment or change status on bugs of a Bugzilla instance, this moudle is not the idempotent as
     the POST method is called in comment and change status operations.

options:
  uri:
    required: true
    description:
      - Base URI of the Bugzilla instance.
    type: str

  operation:
    required: true
    type: str
    choices: [ comment, transition, fetch ]
    aliases: [ command ]
    description:
      - The operation to perform.

  username:
    required: true
    type: str
    description:
      - The username to log-in with.

  password:
    required: true
    type: str
    description:
      - The password to log-in with.

  bug:
    required: false
    type: str
    description:
      - An existing bug id to operate on.

  comment:
    required: false
    type: str
    description:
      - The comment text to add.

  status:
    required: false
    type: str
    description:
      - The desired status; only relevant for the transition operation.

  timeout:
    required: false
    type: float
    description:
      - Set timeout, in seconds, on requests to Bugzilla API.
    default: 10

  validate_certs:
    required: false
    description:
      - Require valid SSL certificates (set to C(false) if you'd like to use self-signed certificates).
    default: true
    type: bool

notes:
  - Currently this only works with REST API.

author: "Chuang Cao (@xiangge)"
"""

EXAMPLES = """ # Add a comment to bug
- name: Add a comment on a bug
  community.general.bugzilla:
    uri: '{{ server }}'
    username: '{{ user }}'
    password: '{{ pass }}'
    bug: '{{ bug.id }}'
    operation: comment
    comment: A comment added by Ansible

# Retrieve metadata for an issue and use it to create an account
- name: Get bug metadata
  community.general.bugzilla:
    uri: '{{ server }}'
    username: '{{ user }}'
    password: '{{ pass }}'
    operation: fetch
    bug: 123456
  register: bug

# Change the bug to another status
- name: Change bug's status to ON_QA
  community.general.bugzilla:
    uri: '{{ server }}'
    username: '{{ user }}'
    password: '{{ pass }}'
    bug: '{{ bug.id }}'
    operation: transition
    status: ON_QA
"""

import base64
import json
import sys

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url
from ansible.module_utils._text import to_native


def handle_request(url, timeout, data=None, method='GET'):
    """Handle request by ansible lib"""
    data = json.dumps(data)
    response, info = fetch_url(module, url, data=data, method=method, timeout=timeout,
                               headers={'Content-Type': 'application/json'})
    if info['status'] not in (200, 201, 204):
        module.fail_json(msg=to_native(info['msg']))
    body = response.read()
    ret = {}
    if body:
        ret = json.loads(body)
    return ret


def comment(restbase, user, passwd, params):
    data = {
        'comment': params['comment'],
        'Bugzilla_login': user,
        'Bugzilla_password': passwd,
    }
    url = restbase + '/bug/' + params['bug'] + '/comment'
    ret = handle_request(url, params['timeout'], data, 'POST')
    return ret


def fetch(restbase, user, passwd, params):
    url = restbase + '/bug/' + params['bug'] + "?Bugzilla_login=" + user + "&Bugzilla_password=" + passwd
    ret = handle_request(url, params['timeout'])
    return ret


def transition(restbase, user, passwd, params):
    data = {
        'status': params['status'],
        'Bugzilla_login': user,
        'Bugzilla_password': passwd,
    }
    url = restbase + '/bug/' + params['bug']
    ret = handle_request(url, params['timeout'], data, 'PUT')
    return ret


def main():
    global module
    module = AnsibleModule(
        argument_spec=dict(
            uri=dict(type='str', required=True),
            operation=dict(type='str', choices=['comment', 'fetch', 'transition'],
                           aliases=['command'], required=True),
            username=dict(type='str', required=True),
            password=dict(type='str', required=True, no_log=True),
            comment=dict(type='str'),
            status=dict(type='str'),
            bug=dict(type='str'),
            timeout=dict(type='float', default=10),

            validate_certs=dict(type='bool', default=True),
        ),
        # Some parameters depends on others
        required_if=[
            ('operation', 'comment', ['bug', 'comment']),
            ('operation', 'fetch', ['bug']),
            ('operation', 'transition', ['bug', 'status'])
        ],
        supports_check_mode=True,
    )

    op = module.params['operation']
    uri = module.params['uri']
    user = module.params['username']
    passwd = module.params['password']

    if not uri.endswith('/'):
        uri = uri + '/'
    restbase = uri + 'rest'

    try:
        # Lookup the corresponding method for this operation.
        bugzilla_operations = {"fetch": fetch,
                               "transition": transition,
                               "comment": comment
                               }
        ret = bugzilla_operations[op](restbase, user, passwd, module.params)

    except Exception as e:
        return module.fail_json(msg=e.message)

    module.exit_json(changed=True, meta=ret)


if __name__ == '__main__':
    main()
