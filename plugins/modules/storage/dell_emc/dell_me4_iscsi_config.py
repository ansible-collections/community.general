#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2020, Andreas Calminder <andreas.calminder@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '0.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: dell_me4_iscsi_config
short_description: Manage Dell EMC me4 series SAN iscsi configuration
description:
  - This module is used to configure Dell EMC ME4 SAN iscsi parameters
requirements:
  - "python >= 3.6"
  - requests
author:
  - Andreas Calminder (@acalm)
notes:
  - Tested on Dell EMC ME4024
options:
  chap:
    default: False
    description:
      - enable/disable chap (Challenge Handshake Authentication Protocol)
    type: bool
  ip_version:
    choices:
      - 4
      - 6
    default: 4
    description:
      - whether to use ipv4 or ipv6 for addressing iscsi ports
    type: int
  isns:
    default: 0.0.0.0
    description:
      - ip address to isns (Internet Storage Name Service) server
      - setting this to anything else than the default (0.0.0.0) enables isns
    type: str
  isns_alt:
    default: 0.0.0.0
    description:
      - ip address to alternate isns (Internet Storage Name Service) server
    type: str
  jumbo_frames:
    default: False
    description:
      - enable or disable jumbo frames
    type: bool
  speed:
    description: host port link speed
    choices:
      - 1gbps
      - auto
    default: auto
    type: str
  hostname:
    required: True
    description:
      - management endpoint
    type: str
  username:
    default: manage
    description:
      - username for logging in to san management
    type: str
  password:
    required: True
    description:
      - password for logging in to san management
    type: str
  verify_cert:
    default: True
    description:
      - verify certificate(s) when connecting to san management
    type: bool
'''

EXAMPLES = '''
- name: enable jumbo-frames
  dell_me4_iscsi_config:
    hostname: me4.fqdn
    username: manage
    password: "!manage"
    jumbo_frames: true
'''

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
import copy
import hashlib
import os
import time

try:
    import requests
except ImportError:
    REQUESTS_FOUND = False
else:
    REQUESTS_FOUND = True


def get_session_key(module):
    rv = False
    auth = hashlib.sha256('{username}_{password}'.format(**module.params).encode('utf-8')).hexdigest()
    url = 'https://{0}/api/login/{1}'.format(module.params['hostname'], auth)
    headers = {'datatype': 'json'}
    r = requests.get(url, headers=headers, verify=module.params['verify_cert'])
    if not r.ok:
        return rv

    rv = r.json()['status'][0]['response']
    return rv


def make_request(url, headers, module):
    default_headers = {'datatype': 'json'}
    headers.update(default_headers)
    r = requests.get(url=url, headers=headers, verify=module.params['verify_cert'])
    if not r.ok:
        module.fail_json(msg='{0} returned status code {1}: {2}'.format(url, r.status_code, r.reason))

    ret = r.json()

    status = ret.get('status', [])[0]
    if not status.get('return-code') == 0:
        module.fail_json(
            msg='{0} returned abnormal status, response: {1}, response type: {2}, return code: {3}'.format(
                url, status.get('response'), status.get('response-type'), status.get('return-code')
            )
        )

    return ret


def get_iscsi_parameters(session_key, module):
    url = 'https://{0}/api/show/iscsi-parameters'.format(module.params['hostname'])
    headers = {'sessionKey': session_key}
    ret = make_request(url, headers, module)
    return ret.get('iscsi-parameters', [])


def set_iscsi_parameters(module):
    changed = False
    diff = {'before': {}, 'after': {}}
    params_out = {}
    msg = 'no change'
    session_key = get_session_key(module)
    headers = {'sessionKey': session_key}
    base_url = 'https://{0}/api/set/iscsi-parameters'.format(module.params['hostname'])
    current_params = get_iscsi_parameters(session_key, module)[0]

    if not all(
        [
            current_params['chap-numeric'] == module.params['chap'],
            current_params['jumbo-frames-numeric'] == module.params['jumbo_frames'],
            current_params['isns-ip'] == module.params['isns'],
            current_params['isns-alt-ip'] == module.params['isns_alt'],
            current_params['iscsi-speed'] == module.params['speed'],
            current_params['iscsi-ip-version'] == module.params['ip_version'],
        ]
    ):
        chap = 'disabled'
        jumbo_frames = 'disabled'
        isns = 'disabled'

        if module.params['chap']:
            chap = 'enabled'
        if module.params['jumbo_frames']:
            jumbo_frames = 'enabled'
        if module.params['isns'] != '0.0.0.0':
            isns = 'enabled'

        cmd = os.path.join(
            'chap', chap,
            'jumbo-frame', jumbo_frames,
            'speed', module.params['speed'],
            'iscsi-ip-version', 'ipv{0}'.format(module.params['ip_version']),
            'isns', isns,
            'isns-ip', module.params['isns'],
            'isns-alt-ip', module.params['isns_alt']

        )
        diff['before'] = current_params
        if module.check_mode:
            changed = True
            diff['after'] = copy.deepcopy(current_params)
            diff['after'].update(
                {
                    'chap': chap.capitalize(),
                    'jumbo-frames': jumbo_frames.capitalize(),
                    'iscsi-speed': module.params['speed'],
                    'iscsi-ip-version': module.params['ip_version'],
                    'isns': isns.capitalize(),
                    'isns-ip': module.params['isns'],
                    'isns-alt-ip': module.params['isns_alt']

                }
            )
            params_out = copy.deepcopy(diff['after'])
            msg = 'iscsi parameters changed (check mode)'
        else:
            url = os.path.join(base_url, cmd)
            ret = make_request(url, headers, module)
            msg = ret['status'][0]['response']
            changed = True

            # me4 are slow on picking up changes, perform the infamous enterprise-sleep!
            time.sleep(1)
            diff['after'] = get_iscsi_parameters(session_key, module)[0]
            params_out = copy.deepcopy(diff['after'])

    return changed, diff, params_out, msg


def main():
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(type='str', required=True),
            verify_cert=dict(type='bool', default=True),
            username=dict(type='str', default='manage'),
            password=dict(type='str', required=True, no_log=True),
            jumbo_frames=dict(type='bool', default=False),
            chap=dict(type='bool', default=False),
            ip_version=dict(type='int', choices=[4, 6], default=4),
            speed=dict(type='str', choices=['1gbps', 'auto'], default='auto'),
            isns=dict(type='str', default='0.0.0.0'),
            isns_alt=dict(type='str', default='0.0.0.0'),

        ),
        supports_check_mode=True
    )

    if not REQUESTS_FOUND:
        module.fail_json(msg=missing_required_lib('requests'))

    changed, diff, iscsi_params, msg = set_iscsi_parameters(module)
    module.exit_json(changed=changed, diff=diff, iscsi_parameters=iscsi_params, msg=msg)


if __name__ == '__main__':
    main()
