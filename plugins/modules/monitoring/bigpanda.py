#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: bigpanda
author: "Hagai Kariti (@hkariti)"
short_description: Notify BigPanda about deployments
description:
   - Notify BigPanda when deployments start and end (successfully or not). Returns a deployment object containing all the parameters for future module calls.
options:
  component:
    type: str
    description:
      - "The name of the component being deployed. Ex: billing"
    required: true
    aliases: ['name']
  version:
    type: str
    description:
      - The deployment version.
    required: true
  token:
    type: str
    description:
      - API token.
    required: true
  state:
    type: str
    description:
      - State of the deployment.
    required: true
    choices: ['started', 'finished', 'failed']
  hosts:
    type: str
    description:
      - Name of affected host name. Can be a list.
      - If not specified, it defaults to the remote system's hostname.
    required: false
    aliases: ['host']
  env:
    type: str
    description:
      - The environment name, typically 'production', 'staging', etc.
    required: false
  owner:
    type: str
    description:
      - The person responsible for the deployment.
    required: false
  description:
    type: str
    description:
      - Free text description of the deployment.
    required: false
  url:
    type: str
    description:
      - Base URL of the API server.
    required: false
    default: https://api.bigpanda.io
  validate_certs:
    description:
      - If C(false), SSL certificates for the target url will not be validated. This should only be used
        on personally controlled sites using self-signed certificates.
    required: false
    default: true
    type: bool
  deployment_message:
    type: str
    description:
    - Message about the deployment.
    version_added: '0.2.0'
  source_system:
    type: str
    description:
    - Source system used in the requests to the API
    default: ansible

# informational: requirements for nodes
requirements: [ ]
'''

EXAMPLES = '''
- name: Notify BigPanda about a deployment
  community.general.bigpanda:
    component: myapp
    version: '1.3'
    token: '{{ bigpanda_token }}'
    state: started

- name: Notify BigPanda about a deployment
  community.general.bigpanda:
    component: myapp
    version: '1.3'
    token: '{{ bigpanda_token }}'
    state: finished

# If outside servers aren't reachable from your machine, use delegate_to and override hosts:
- name: Notify BigPanda about a deployment
  community.general.bigpanda:
    component: myapp
    version: '1.3'
    token: '{{ bigpanda_token }}'
    hosts: '{{ ansible_hostname }}'
    state: started
  delegate_to: localhost
  register: deployment

- name: Notify BigPanda about a deployment
  community.general.bigpanda:
    component: '{{ deployment.component }}'
    version: '{{ deployment.version }}'
    token: '{{ deployment.token }}'
    state: finished
  delegate_to: localhost
'''

# ===========================================
# Module execution.
#
import json
import socket
import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native
from ansible.module_utils.urls import fetch_url


def main():

    module = AnsibleModule(
        argument_spec=dict(
            component=dict(required=True, aliases=['name']),
            version=dict(required=True),
            token=dict(required=True, no_log=True),
            state=dict(required=True, choices=['started', 'finished', 'failed']),
            hosts=dict(required=False, aliases=['host']),
            env=dict(required=False),
            owner=dict(required=False),
            description=dict(required=False),
            deployment_message=dict(required=False),
            source_system=dict(required=False, default='ansible'),
            validate_certs=dict(default=True, type='bool'),
            url=dict(required=False, default='https://api.bigpanda.io'),
        ),
        supports_check_mode=True,
    )

    token = module.params['token']
    state = module.params['state']
    url = module.params['url']

    # Build the common request body
    body = dict()
    for k in ('component', 'version', 'hosts'):
        v = module.params[k]
        if v is not None:
            body[k] = v
    if body.get('hosts') is None:
        body['hosts'] = [socket.gethostname()]

    if not isinstance(body['hosts'], list):
        body['hosts'] = [body['hosts']]

    # Insert state-specific attributes to body
    if state == 'started':
        for k in ('source_system', 'env', 'owner', 'description'):
            v = module.params[k]
            if v is not None:
                body[k] = v

        request_url = url + '/data/events/deployments/start'
    else:
        message = module.params['deployment_message']
        if message is not None:
            body['errorMessage'] = message

        if state == 'finished':
            body['status'] = 'success'
        else:
            body['status'] = 'failure'

        request_url = url + '/data/events/deployments/end'

    # Build the deployment object we return
    deployment = dict(token=token, url=url)
    deployment.update(body)
    if 'errorMessage' in deployment:
        message = deployment.pop('errorMessage')
        deployment['message'] = message

    # If we're in check mode, just exit pretending like we succeeded
    if module.check_mode:
        module.exit_json(changed=True, **deployment)

    # Send the data to bigpanda
    data = json.dumps(body)
    headers = {'Authorization': 'Bearer %s' % token, 'Content-Type': 'application/json'}
    try:
        response, info = fetch_url(module, request_url, data=data, headers=headers)
        if info['status'] == 200:
            module.exit_json(changed=True, **deployment)
        else:
            module.fail_json(msg=json.dumps(info))
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=traceback.format_exc())


if __name__ == '__main__':
    main()
