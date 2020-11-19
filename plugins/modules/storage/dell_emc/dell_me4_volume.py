#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2020, Andreas Calminder <andreas.calminder@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
---
module: dell_me4_volume
short_description: manage volumes in Dell EMC me4 series SAN
description:
  - add, remove, expand volumes in a Dell EMC ME4 SAN
requirements:
  - python >= 2.7
  - requests
author:
  - Andreas Calminder (@acalm)
notes:
  - Tested on Dell EMC ME4024
options:
  access:
    choices:
      - no-access
      - read-only
      - read-write
    default: read-write
    description:
      - mapping access permissions to use
      - volume cannot be mapped when C(no-access) is set
      - access permissions set here will affect all access,
      - default sets C(read-write); access is for all initiators, use dell_me4_map_volume for initiator specific access
    type: str
  name:
    description:
      - volume name
    required: True
    type: str
  size:
    description:
      - volume size with suffix, for example C(300gib)
      - suffixes can be any of following units b, kb, mb, gb, tb, kib, mib, gib, tib
      - maximum volume size is 128tib
    required: True
    type: str
  large_virtual_extents:
    default: False
    description:
      - system will try to allocate pages in a sequentially optimized way to reduce i/o latency in ssd  applications to improve performance
    type: bool
  lun:
    description:
      - lun number to assign to the mapping on all ports
    type: int
  pool:
    aliases:
      - disk_group
      - vdisk
    description:
      - name of pool/disk group/vdisk to create volume in
    required: True
    type: str
  ports:
    description:
      - ports hosts can access the volume, default is all ports
      - specified ports must be of same type, I.E iscsi or fc
    elements: str
    type: list
  snapshot_retention_prio:
    choices:
      - never-delete
      - low
      - medium
      - high
    default: medium
    description:
      - retention priority for snapshots of the volume
      - used for volumes in virtual storage type pools
    type: str
  tier_affinity:
    choices:
      - no-affinity
      - archive
      - performance
    default: no-affinity
    description:
      - tier-migration algorithm setting
      - used for volumes in virtual storage type pools
    type: str
  volume_group:
    description:
      - name of a volume group to which to add the volume
      - non-existing volume groups wil be created
    type: str
  reserve_size:
    description:
      - size of the snap pool to create in the disk group
      - used for volumes in linear storage type pools
      - size suffixes can be any of following units b, kb, mb, gb, tb, kib, mib, gib, tib
    type: str
  state:
    choices:
      - absent
      - present
    default: present
    description:
      - C(absent) remove given volume
      - C(present) create or expand given volume
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
- name: create volume(s)
  dell_me4_volume:
    hostname: me4.management.address.tld
    username: manage
    password: "!manage"
    verify_cert: false
    name: "{{ item['name'] }}"
    size: "{{ item['size'] }}"
    disk_group: "{{ item['disk_group'] }}"
    access: no-access
  loop:
    - name: my-volume1
      size: 1tb
      disk_group: mydg1
    - name: another-vol
      size: 3tb
      disk_group: another-dg
'''

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
import copy
import hashlib
import os
import re
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


def get_volume_maps(session_key, module):
    url = 'https://{0}/api/show/maps'.format(module.params['hostname'])
    headers = {'sessionKey': session_key}
    ret = make_request(url, headers, module)
    return ret.get('volume-view', [])


def get_disks(session_key, module):
    url = 'https://{0}/api/show/disks'.format(module.params['hostname'])
    headers = {'sessionKey': session_key}
    ret = make_request(url, headers, module)
    return ret.get('drives', [])


def get_disk_groups(session_key, module):
    url = 'https://{0}/api/show/disk-groups'.format(module.params['hostname'])
    headers = {'sessionKey': session_key}
    ret = make_request(url, headers, module)
    return ret.get('disk-groups', [])


def get_volumes(session_key, module):
    url = 'https://{0}/api/show/volumes'.format(module.params['hostname'])
    headers = {'sessionKey': session_key}
    ret = make_request(url, headers, module)
    return ret.get('volumes', [])


def get_pools(session_key, module):
    url = 'https://{0}/api/show/pools'.format(module.params['hostname'])
    headers = {'sessionKey': session_key}
    ret = make_request(url, headers, module)
    return ret.get('pools', [])


def select_lun(session_key, module):
    volume_maps = get_volume_maps(session_key, module)
    existing_luns = [m.get('lun') for v in volume_maps for m in v.get('volume-view-mappings', [])]
    volumes = len(get_volumes(session_key, module))

    luns = sorted([int(n) for n in existing_luns if n.isdigit()])

    if not luns and not volumes:
        return 0

    if volumes + 1 not in luns:
        return volumes + 1

    return luns[-1] + 1


def expand_volume(session_key, expand_size, module):
    url = 'https://{0}/api/expand/volume/size/{1}B/{2}'.format(module.params['hostname'], expand_size, module.params['name'])
    headers = {'sessionKey': session_key}
    ret = make_request(url, headers, module)
    return ret['status'][0]['response']


def delete_volume(session_key, module):
    url = 'https://{0}/api/delete/volumes/{1}'.format(module.params['hostname'], module.params['name'])
    headers = {'sessionKey': session_key}
    ret = make_request(url, headers, module)
    return ret['status'][0]['response']


def suffixed_size_to_bytes(suffixed_size):
    suffix_map = {
        'b': 1, 'kb': 1000, 'kib': 1024,
        'mb': 1000000, 'mib': 1048576, 'gb': 1000000000,
        'gib': 1073741824, 'tb': 1000000000000, 'tib': 1099511627776
    }
    size_rx = re.compile('^([0-9]+)({0})$'.format('|'.join(suffix_map.keys())), re.I)
    size_str, size_unit = size_rx.match(suffixed_size.lower()).groups()
    return int(size_str) * suffix_map[size_unit]


def validate_params(module):
    size_rx = re.compile('^([0-9]+)(b|kb|kib|mb|mib|gb|gib|tb|tib)$', re.I)
    illegal_chars = ['"', ',', '.', '<', '\\']
    if any([c in module.params['name'] for c in illegal_chars]):
        module.fail_json(msg='volume name ({0}) contains illegal character(s): {1}'.format(module.params['name'], ', '.join(illegal_chars)))

    if len(module.params['name'].encode('utf-8')) > 32:
        module.fail_json(msg='volume name: {0} cannot be larger than 32 bytes'.format(module.params['name']))

    if not size_rx.match(module.params['size']):
        module.fail_json(msg='invalid format for size: {0}, sizes should be properly suffixed integers'.format(module.params['size']))
    if suffixed_size_to_bytes(module.params['size']) > 140737488355328:
        module.fail_json(msg='volume size cannot exceed 140737488355328 bytes (128TiB)')

    if module.params['reserve_size'] and not size_rx.match(module.params['reserve_size']):
        module.fail_json(msg='invalid format for reserve_size: {0}, sizes should be suffixed numbers'.format(module.params['reserve_size']))


def create_volume(session_key, module):
    rv = {'changed': False, 'volume': {}, 'msg': ''}
    base_url = 'https://{0}/api/create/volume'.format(module.params['hostname'])
    headers = {'sessionKey': session_key}

    pools = get_pools(session_key, module)
    if module.params['pool'] not in [p.get('name') for p in pools]:
        module.fail_json(msg='pool/disk group/vdisk {0} does not exist')

    pool = [p for p in pools if module.params['pool'] == p.get('name')][0]
    pool_avail_size = pool['blocksize'] * pool['total-avail-numeric']
    volume_size = suffixed_size_to_bytes(module.params['size'])

    if (volume_size > pool_avail_size) and pool['overcommit-numeric'] != 1:
        module.fail_json(
            msg='volume size larger ({0} bytes) than available in {1}: {2} bytes and pool does not support overcommit'.format(
                volume_size, pool['name'], pool_avail_size
            )
        )

    cmd = os.path.join(
        'size', '{0}b'.format(volume_size),
        'access', module.params['access']
    )

    if module.params['ports']:
        cmd = os.path.join(cmd, 'ports', ','.join(module.params['ports']))

    if module.params['lun'] is not None:
        cmd = os.path.join(cmd, 'lun', '{0}'.format(module.params['lun']))
    else:
        cmd = os.path.join(cmd, 'lun', '{0}'.format(select_lun(session_key, module)))

    if module.params['volume_group']:
        cmd = os.path.join(cmd, 'volume-group', module.params['volume_group'])

    if pool['storage-type'].lower() == 'linear':
        cmd = os.path.join(cmd, 'vdisk', module.params['pool'])
        if module.params['reserve_size']:
            cmd = os.path.join(cmd, 'reserve', module.params['reserve_size'])

    if pool['storage-type'].lower() == 'virtual':
        cmd = os.path.join(
            cmd,
            'pool', pool['name'],
            'snapshot-retention-priority', module.params['snapshot_retention_prio'],
            'tier-affinity', module.params['tier_affinity']
        )

    if module.check_mode:
        rv['changed'] = True
        # fabricate volume output for check-mode
        rv['volume'] = {'volume-name': module.params['name'], 'storage-pool-name': pool['name']}
        c_lst = cmd.split('/')
        rv['volume'].update({x: y for x, y in zip(c_lst[::2], c_lst[1::2])})
        rv['msg'] = 'created volume {0} (check mode)'.format(module.params['name'])
    else:
        url = os.path.join(base_url, cmd, module.params['name'])
        ret = make_request(url, headers, module)
        rv['msg'] = ret['status'][0]['response']

        # enterprise sleep! me4 is slow to update
        time.sleep(1)
        for vol in get_volumes(session_key, module):
            if vol.get('volume-name') == module.params['name']:
                rv['volume'] = vol
                rv['changed'] = True
                break

    return rv


def update_volume(session_key, module):
    rv = {'changed': False, 'volume': {}, 'msg': 'no change'}
    pools = get_pools(session_key, module)
    volumes = get_volumes(session_key, module)

    pool = [p for p in pools if p['name'] == module.params['pool']][0]
    volume = [v for v in volumes if v['volume-name'] == module.params['name']][0]
    volume_size = volume['blocksize'] * volume['blocks']
    new_size = suffixed_size_to_bytes(module.params['size'])
    if new_size < volume_size:
        module.fail_json(
            msg='size {0} ({1} bytes) is lower than current size, shrinking volumes is not supported'.format(
                module.params['size'], new_size
            )
        )

    if new_size > volume_size:
        if new_size / volume['blocksize'] > pool['total-avail-numeric'] and pool['overcommit-numeric'] != 1:
            module.fail_json(
                msg='{0} is larger than available pool/disk group space {1}, {2} type pool/disk group overcommit disabled or n/a'.format(
                    module.params['size'], pool['total-avail'], pool['storage-type']
                )
            )
        expand_size = new_size - volume_size

        if not module.check_mode:
            rv['msg'] = expand_volume(session_key, expand_size, module)
            rv['changed'] = True
            time.sleep(1)
            rv['volume'] = [v for v in get_volumes(session_key, module) if v['volume-name'] == module.params['name']][0]
        else:
            rv['changed'] = True
            rv['volume'] = copy.deepcopy(volume)
            rv['volume'].update(
                {
                    'total-size-numeric': new_size / volume['blocksize'],
                    'allocated-size-numeric': new_size / volume['blocksize'],
                    'blocks': new_size / volume['blocksize']
                }
            )
            rv['msg'] = 'volume {0} updated (check mode)'.module.params['name']
    return rv


def absent(module):
    changed = False
    diff = {'before': {}, 'after': {}}
    msg = 'no change'
    session_key = get_session_key(module)
    volumes = get_volumes(session_key, module)
    volume = None

    for v in volumes:
        if module.params['name'] == v['volume-name']:
            volume = copy.deepcopy(v)
            break

    if volume:
        diff['before'] = volume
        if not module.check_mode:
            msg = delete_volume(session_key, module)
            changed = True
        else:
            changed = True
            msg = 'volume {0} removed (check mode)'.format(module.params['name'])

    return changed, diff, msg


def present(module):
    rv = {'changed': False, 'msg': 'no change'}
    diff = {'before': {}, 'after': {}}
    session_key = get_session_key(module)
    volumes = get_volumes(session_key, module)
    volume = None

    for v in volumes:
        if module.params['name'] == v['volume-name']:
            volume = copy.deepcopy(v)
            break

    if volume:
        diff['before'] = volume
        rv = update_volume(session_key, module)
    else:
        rv = create_volume(session_key, module)

    diff['after'] = rv['volume']
    return rv['changed'], diff, rv['msg']


def main():
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(type='str', required=True),
            verify_cert=dict(type='bool', default=True),
            username=dict(type='str', default='manage'),
            password=dict(type='str', required=True, no_log=True),
            access=dict(type='str', choices=['no-access', 'read-only', 'read-write'], default='read-write'),
            name=dict(type='str', required=True),
            size=dict(type='str', required=True),
            large_virtual_extents=dict(type='bool', default=False),
            lun=dict(type='int'),
            pool=dict(type='str', aliases=['disk_group', 'vdisk'], required=True),
            ports=dict(type='list', default=[]),
            snapshot_retention_prio=dict(type='str', choices=['never-delete', 'high', 'medium', 'low'], default='medium'),
            tier_affinity=dict(type='str', choices=['no-affinity', 'archive', 'performance'], default='no-affinity'),
            volume_group=dict(type='str'),
            reserve_size=dict(type='str'),
            state=dict(type='str', choices=['absent', 'present'], default='present')
        ),
        supports_check_mode=True
    )

    if not REQUESTS_FOUND:
        module.fail_json(msg=missing_required_lib('requests'))

    validate_params(module)
    if module.params['state'] == 'present':
        changed, diff, msg = present(module)

    if module.params['state'] == 'absent':
        changed, diff, msg = absent(module)

    module.exit_json(changed=changed, diff=diff, msg=msg)


if __name__ == '__main__':
    main()
