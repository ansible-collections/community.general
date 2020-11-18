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
module: dell_me4_initiator
short_description: Manage initiators in a Dell EMC me4 series SAN
description:
  - This module is used to add, update, delete initiators in a Dell EMC ME4 SAN
requirements:
  - "python >= 3.6"
  - requests
author:
  - Andreas Calminder (@acalm)
notes:
  - Tested on Dell EMC ME4024
options:
  initiator:
    description:
      - id of the initiator. fc and sas id is wwpn, for iscsi use iqn
      - required
    type: str
  nickname:
    description:
      - initiator nickname
      - cannot exceed 32 bytes
      - cannot include any of " , . < \\
    type: str
  profile:
    description:
      - only profile available is standard
    default: standard
    type: str
  state:
    default: present
    choices:
      - absent
      - present
    description:
      - when C(state=absent) give initiator will be deleted
      - when C(state=present) create/update an initiator
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
---
- name: create initiator
  community.general.dell_me4_initiator:
    hostname: me4.fqdn
    username: manage
    password: "!manage"
    initiator: some.iqn
    nickname: initiator2
'''

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
import copy
import hashlib
import os

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


def get_initiators(session_key, module):
    url = 'https://{0}/api/show/initiators'.format(module.params['hostname'])
    headers = {'sessionKey': session_key}
    ret = make_request(url, headers, module)
    return ret.get('initiator', [])


def set_initiator(session_key, module):
    rv = {'changed': False, 'msg': ''}
    nickname = module.params['nickname']
    headers = {'sessionKey': session_key}
    cmd = os.path.join('set', 'initiator', 'id', module.params['initiator'], 'profile', module.params['profile'])
    illegal_chars = ['"', ',', '.', '<', '\\']

    if nickname:
        if any([c in nickname for c in illegal_chars]):
            module.fail_json(msg='nickname {0} contains illegal characters {1}'.format(nickname, illegal_chars))
        if len(nickname.encode('utf-8')) > 32:
            module.fail_json(msg='nickname {0} larger ({1}) than 32 bytes'.format(nickname, len(nickname.encode('utf-8'))))
        cmd = os.path.join(cmd, 'nickname', nickname)

    url = 'https://{0}/api/{1}'.format(module.params['hostname'], cmd)

    if not module.check_mode:
        ret = make_request(url, headers, module)
        rv['msg'] = ret['status'][0]['response']
    else:
        rv['msg'] = 'initiator updated (check mode)'
    rv['changed'] = True
    return rv


def delete_initiator(session_key, module):
    rv = {'changed': False, 'msg': ''}
    headers = {'sessionKey': session_key}
    cmd = os.path.join('delete', 'initiator-nickname', module.params['initiator'])
    url = 'https://{0}/api/{1}'.format(module.params['hostname'], cmd)

    if not module.check_mode:
        ret = make_request(url, headers, module)
        rv['msg'] = ret['status'][0]['response']
    else:
        rv['msg'] = 'removed initiator {0}'.format(module.params['initiator'])

    rv['changed'] = True
    return rv


def present(module):
    changed = False
    diff = {'before': {}, 'after': {}}
    msg = 'no change'

    session_key = get_session_key(module)
    if not session_key:
        module.json_fail(msg='login to {hostname} failed'.format(**module.params))

    existing_initiators = get_initiators(session_key, module)

    for initiator in existing_initiators:
        if initiator.get('id') == module.params['initiator']:
            if module.params['nickname']:
                if initiator.get('nickname') == module.params['nickname']:
                    return changed, diff, msg
            diff['before'] = initiator

    ret = set_initiator(session_key, module)
    msg = ret['msg']
    changed = ret['changed']

    if not module.check_mode:
        for new_initiator in get_initiators(session_key, module):
            if new_initiator.get('id') == module.params['initiator']:
                diff['after'] = new_initiator
    else:
        if diff['before']:
            diff['after'] = copy.deepcopy(diff['before'])
            diff['after']['nickname'] = module.params['nickname']
        else:
            diff['after'] = {'nickname': module.params['nickname'], 'id': module.params['initiator']}

    return changed, diff, msg


def absent(module):
    changed = False
    diff = {'before': {}, 'after': {}}
    msg = 'no change'
    session_key = get_session_key(module)
    existing_initiators = get_initiators(session_key, module)

    for initiator in existing_initiators:
        if initiator.get('id') == module.params['initiator']:
            ret = delete_initiator(session_key, module)
            diff['before'] = initiator
            changed = ret['changed']
            msg = ret['msg']
            break

    return changed, diff, msg


def main():
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(type='str', required=True),
            verify_cert=dict(type='bool', default=True),
            username=dict(type='str', default='manage'),
            password=dict(type='str', required=True, no_log=True),
            state=dict(type='str', choices=['absent', 'present'], default='present'),
            initiator=dict(type='str', required=True),
            nickname=dict(type='str'),
            profile=dict(type='str', default='standard')
        ),
        supports_check_mode=True
    )

    if not REQUESTS_FOUND:
        module.fail_json(msg=missing_required_lib('requests'))

    if module.params['state'] == 'present':
        changed, diff, msg = present(module)

    if module.params['state'] == 'absent':
        changed, diff, msg = absent(module)

    module.exit_json(changed=changed, diff=diff, msg=msg)


if __name__ == '__main__':
    main()
