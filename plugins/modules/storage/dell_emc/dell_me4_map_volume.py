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
module: dell_me4_map_volume
short_description: Manage volume mappings in Dell EMC me4 series SAN
description:
  - This module is used to add and remove volume mappings in a Dell EMC ME4 SAN
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
      - existing initiator id
      - fc and sas ids == wwpn,  iscsi id == iqn
      - required
    required: True
    type: str
  volume:
    description:
      - an existing volume name
    required: true
    type: str
  lun:
    description:
      - lun id to use
    type: int
  ports:
    description:
      - controller ports to use
      - must be of same type (fc, iscsi)
    type: list
  access:
    choices:
      - no-access
      - read-only
      - read-write
    default: read-write
    description:
      - mapping access permissions to use
      - volume cannot be mapped when C(no-access) is set
      - setting C(no-access) will mask specified volume from given initiator
    type: str
  state:
    default: present
    choices:
      - absent
      - present
    description:
      - C(state=absent) remove volume mapping
      - C(state=present) create/update volume mapping
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
- name: map volumes to initiator
  community.general.dell_me4_map_volume:
    hostname: me4.fqdn
    username: manage
    password: "!manage"
    initiator: initiator3
    volume: "{{ item }}"
    access: read-write
  loop:
    - volume1
    - volume2
    - volume3
'''

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
import copy
import hashlib
import os
import re

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


def get_maps(session_key, module):
    url = 'https://{0}/api/show/maps'.format(module.params['hostname'])
    headers = {'sessionKey': session_key}
    ret = make_request(url, headers, module)
    return ret.get('volume-view', [])


def get_initiators(session_key, module):
    url = 'https://{0}/api/show/initiators'.format(module.params['hostname'])
    headers = {'sessionKey': session_key}
    ret = make_request(url, headers, module)
    return ret.get('initiator', [])


def get_volumes(session_key, module):
    url = 'https://{0}/api/show/volumes'.format(module.params['hostname'])
    headers = {'sessionKey': session_key}
    ret = make_request(url, headers, module)
    return ret.get('volumes', [])


def get_host_groups(session_key, module):
    url = 'https://{0}/api/show/host-groups'.format(module.params['hostname'])
    headers = {'sessionKey': session_key}
    ret = make_request(url, headers, module)
    return ret.get('host-group', [])


def get_initiator_host_groups(session_key, initiator_id, module):
    rv = []
    host_groups = get_host_groups(session_key, module)

    for group in host_groups:
        for host in group.get('host', []):
            if host.get('initiator'):
                if initiator_id in [i.get('id') for i in host.get('initiator', [])]:
                    rv.append({'name': group['name'], 'serial': group['serial-number']})
    return rv


def get_volume_maps(session_key, module):
    rv = []
    maps = get_maps(session_key, module)
    volume = module.params['volume']

    for v in maps:
        if v.get('volume-name') == volume:
            for m in v.get('volume-view-mappings', []):
                rv.append(m['identifier'])
    return sorted(rv)


def guess_lun(session_key, module):
    volumes = get_volumes(session_key, module)
    for v in volumes:
        if v['volume-name'] == module.params['volume']:
            for m in v.get('volume-view-mappings', []):
                return int(m['lun'])
            lun_str = re.sub('[a-zA-Z]+', '', v['durable-id'])
            if lun_str.isdigit():
                return int(lun_str)
            else:
                module.fail_json(msg='failed to guess lun, spcify lun manually')
    return None


def map_initiator(session_key, module):
    headers = {'sessionKey': session_key}
    rv = {'changed': False, 'msg': ''}
    url = 'https://{0}/api/map/volume/{1}/initiator/{2}/access/{3}/'.format(
        module.params['hostname'], module.params['volume'], module.params['initiator'], module.params['access']
    )

    if module.params['lun']:
        url = os.path.join(url, 'lun', '{0}'.format(module.params['lun']))
    else:
        lun = guess_lun(session_key, module)
        if lun is None:
            module.fail_json(msg='failed to automatically select lun, please specify manually')
        url = os.path.join(url, 'lun', '{0}'.format(lun))

    if module.params['ports']:
        ports = ','.join(module.params['ports'])
        url = os.path.join(url, 'ports', ports)

    if module.check_mode:
        rv['changed'] = True
        rv['msg'] = 'volume mappings updated (check mode)'
    else:
        ret = make_request(url, headers, module)
        rv['msg'] = ret.get('status', [])[0]
        rv['changed'] = True
    return rv


def unmap_initiator(session_key, module):
    rv = {}
    headers = {'sessionKey': session_key}
    url = 'https://{0}/api/unmap/volume/initiator/{1}/{2}'.format(module.params['hostname'], module.params['initiator'], module.params['volume'])
    if module.check_mode:
        rv['changed'] = True
        rv['msg'] = 'unmapped {0} from {1} (check mode)'.format(module.params['initiator'], module.params['volume'])
    else:
        ret = make_request(url, headers, module)
        rv['msg'] = ret.get('status', [])[0]
        rv['changed'] = True
    return rv


def present(module):
    changed = False
    diff = {'before': {}, 'after': {}}
    msg = 'no change'
    volume_name = module.params['volume']
    session_key = get_session_key(module)
    current_maps = get_volume_maps(session_key, module)
    initiators = get_initiators(session_key, module)
    volumes = get_volumes(session_key, module)
    initiator_host_groups = get_initiator_host_groups(session_key, module.params['initiator'], module)

    # validate
    if module.params['volume'] not in [v.get('volume-name') for v in volumes]:
        module.fail_json(msg='volume {0} does not exist'.format(module.params['volume']))

    if module.params['initiator'] not in [i.get('id') for i in initiators]:
        module.fail_json(msg='initiator id {0} does not exist'.format(module.params['initiator']))

    for host_group in initiator_host_groups:
        if host_group['serial'] in current_maps:
            return changed, diff, 'no change, initiator {0} already mapped via host group {1}, serial: {2}'.format(
                module.params['initiator'], host_group['name'], host_group['serial']
            )

    if module.params['initiator'] not in current_maps:
        diff['before'][volume_name] = copy.deepcopy(current_maps)
        ret = map_initiator(session_key, module)
        if module.check_mode:
            diff['after'][volume_name] = copy.deepcopy(current_maps)
            diff['after'][volume_name].append(module.params['initiator'])
        else:
            diff['after'][volume_name] = get_volume_maps(session_key, module)
        changed = ret['changed']
        msg = ret['msg']

    return changed, diff, msg


def absent(module):
    changed = False
    diff = {'before': {}, 'after': {}}
    msg = 'no change'
    volume_name = module.params['volume']
    session_key = get_session_key(module)
    current_maps = get_volume_maps(session_key, module)

    if module.params['initiator'] in current_maps:
        diff['before'][volume_name] = copy.deepcopy(current_maps)
        ret = unmap_initiator(session_key, module)
        msg = ret['msg']
        changed = ret['changed']
        if module.check_mode:
            diff['after'][volume_name] = [i for i in current_maps if i != module.params['initiator']]
        else:
            diff['after'][volume_name] = get_volume_maps(session_key, module)

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
            volume=dict(type='str', required=True),
            access=dict(type='str', choices=['no-access', 'read-only', 'read-write'], default='read-write'),
            lun=dict(type='int'),
            ports=dict(type='list', default=[]),
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
