#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2020, Andreas Calminder <andreas.calminder@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: dell_me4_disk_group
short_description: Manage disk groups in a Dell EMC me4 series SAN
version_added: 1.3.0
description:
  - This module is used to add, update, delete disk groups in a Dell EMC ME4 SAN
requirements:
  - python >= 2.7
  - requests
author:
  - Andreas Calminder (@acalm)
notes:
  - Tested on Dell EMC ME4024
options:
  disks:
    description:
      - list of member disks
      - location format C(ENCLOSURE.DISK_NUMBER) for example C("0.3")
      - using r10 require at least 4 disks
      - using r50 require at least 6 disks
      - when creating a new disk group, member disks must be in available state
      - quote disk ids to ensure they're interpreted as strings
    elements: str
    type: list
  name:
    description:
      - disk group name
      - required
    required: True
    type: str
  raid:
    choices:
      - nraid
      - r0
      - r1
      - r3
      - r5
      - r6
      - r10
      - r50
      - adapt
    description:
      - raid level
      - linear only raid types C(nraid), C(r0), C(r3), C(r50)
    type: str
  mode:
    choices:
      - online
      - offline
    default: online
    description:
      - disk group creation state, offline will keep disk group offline until the initialization process is complete.
        During which, zeros are written to all data and parity sectors of the LBA extent of the disk group
    type: str
  state:
    default: present
    choices:
      - absent
      - present
    description:
      - when C(state=absent) group will be deleted. I.E completely destroyed along with any data
      - when C(state=present) create/update a disk group
      - removing a disk group can (and most probably will) take a _VERY_ long time
    type: str
  controller:
    choices:
      - a
      - auto
      - b
    default: auto
    description:
      - when using active-active ulp mode for linear storage, this specifies the controller owning the disk group.
    type: str
  chunk_size:
    choices:
      - 64k
      - 128k
      - 256k
      - 512k
    default: 512k
    description:
      - the amount of contiguous data, written to a disk-group member before moving to the next member of the group
      - only valid for linear storage, except for linear/adapt where this value is ignored
    type: str
  pool:
    description:
      - name of the virtual pool where disk group should reside
    type: str
  spare_disks:
    description:
      - list of dedicated spare disk ids
    elements: str
    type: list
  storage_type:
    choices:
      - linear
      - virtual
      - read-cache
    default: linear
    description:
      - disk group type
    type: str
  adapt_spare_capacity:
    default: 'default'
    description:
      - spare capacity for an adapt disk group
      - set to 0 for minimum space usage
      - suffix value with unit C(b, kb, mb, gb, tb, kib, mib, gib, tib)
      - C(default) will sets the target spare capacity to the sum of the two largest disks in the disk group
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
- name: add a linear raid10 disk group
  community.general.dell_me4_disk_group:
    username: manage
    password: "!manage"
    hostname: "{{ inventory_hostname }}"
    name: linear_disk_group_01
    raid: r10
    storage_type: linear
    state: present
    disks:
      - "0.1"
      - "0.2"
      - "0.3"
      - "0.4"
    spare_disks:
      - "0.5"

- name: add disk(s) to a linear disk group
  community.general.dell_me4_disk_group:
    username: manage
    password: "!manage"
    hostname: "{{ inventory_hostname }}"
    name: linear_disk_group_01
    state: present
    disks:
      - "0.6"
      - "0.7"
      - "0.8"
      - "0.9"

- name: remove disk group
  community.general.dell_me4_disk_group:
    username: manage
    password: "!manage"
    hostname: "{{ inventory_hostname }}"
    name: linear_disk_group_01
    state: absent
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


def expand_disk_group(session_key, disks, module):
    url = 'https://{0}/api/expand/disk-group/disks/{1}/{2}'.format(module.params['hostname'], ','.join(disks), module.params['name'])
    headers = {'sessionKey': session_key}
    ret = make_request(url, headers, module)
    return ret.get('status', [])[0]


def remove_disk_group(session_key, module):
    headers = {'sessionKey': session_key}
    url = 'https://{0}/api/remove/disk-groups/{1}'.format(module.params['hostname'], module.params['name'])
    ret = make_request(url, headers, module)
    return ret['status'][0]['response']


def validate_params(module):
    linear_only_raids = ['nraid', 'r0', 'r3', 'r50']
    illegal_chars = ['"', ',', '.', '<', '\\']
    if module.params['raid'] in linear_only_raids and module.params['storage_type'] != 'linear':
        module.fail_json(msg='raid type {0} only compatible with linear storage type'.format(module.params['raid']))
    if any([c in module.params['name'] for c in illegal_chars]):
        module.fail_json(msg='disk group name ({0}) contains illegal character(s): {1}'.format(module.params['name'], ', '.join(illegal_chars)))

    if len(module.params['name'].encode('utf-8')) > 32:
        module.fail_json(msg='disk group name {0} cannot be larger than 32 bytes'.format(module.params['name']))

    if module.params['state'] == 'present':
        if module.params['disks']:
            for disk in module.params['disks']:
                if not isinstance(disk, str):
                    module.fail_json(msg='disks should be strings in location format <LOCATION>.<ID> example: 0.1, not {0}'.format(disk))

    return True


def create_disk_group(session_key, module):
    rv = {'changed': False, 'disk_group': {}, 'msg': ''}
    # in the future(tm) there might be updates to disk groups
    # that doesn't include actual disks, hence the late
    # validation.
    if not module.params['disks']:
        module.fail_json(msg='cannot create disk group without disks')

    spec_disks = module.params['disks']
    disks = get_disks(session_key, module)
    available_disks = [d.get('location') for d in disks if d.get('usage-numeric') == 0]

    for disk in spec_disks:
        if disk not in available_disks:
            module.fail_json(msg='disk {0} is not in available state, available disks: {1}'.format(disk, ', '.join(available_disks)))

    base_url = 'https://{0}/api/add/disk-group/'.format(module.params['hostname'])
    disks = ','.join(spec_disks)

    if module.params['raid'].lower() in ['r10', 'r50']:
        d_num = 2
        if module.params['raid'].lower() in ['r50']:
            d_num = 3
        sub_groups = [','.join(spec_disks[i:i + d_num]) for i in range(0, len(spec_disks), d_num)]

        if len(sub_groups) < 2:
            module.fail_json(msg='{0} must contain at least {1} disks'.format(module.params['raid'], 2 * d_num))
        disks = ':'.join(sub_groups)

    cmd = os.path.join(
        'type', module.params['storage_type'],
        'disks', disks,
        'level', module.params['raid']
    )

    if module.params['storage_type'] == 'linear':
        if module.params['spare_disks'] and module.params['raid'] != 'adapt':
            cmd = os.path.join(cmd, 'spare', ','.join(module.params['spare_disks']))

        if module.params['raid'] != 'adapt':
            cmd = os.path.join(cmd, 'chunk-size', module.params['chunk_size'])

        cmd = os.path.join(
            cmd,
            'assigned-to', module.params['controller'],
            'mode', module.params['mode'],
        )

    if module.params['storage_type'] == 'virtual':
        if module.params['pool']:
            cmd = os.path.join(
                cmd,
                'pool', module.params['pool'],
            )

    if module.params['storage_type'] == 'read-cache':
        if module.params['pool']:
            cmd = os.path.join(
                cmd,
                'pool', module.params['pool'],
            )

    cmd = os.path.join(cmd, module.params['name'])
    url = os.path.join(base_url, cmd)
    if module.check_mode:
        rv['changed'] = True
        rv['msg'] = 'disk group created (check-mode)'
        rv['disk_group'] = {
            'storage-type': module.params['storage_type'],
            'name': module.params['name'],
            'raidtype': module.params['raid'],
            'chunksize': module.params['chunk_size']
        }
        return rv
    headers = {'sessionKey': session_key}
    ret = make_request(url, headers, module)
    rv['msg'] = ret['status'][0]['response']
    rv['changed'] = True

    disk_groups = get_disk_groups(session_key, module)
    for group in disk_groups:
        if group.get('name') == module.params['name']:
            rv['disk_group'] = group

    return rv


def update_disk_group(session_key, disk_group, module):
    rv = {'changed': False, 'disk_group': {}, 'msgs': []}
    disks = get_disks(session_key, module)
    available_disks = [d.get('location') for d in disks if d.get('usage-numeric') == 0]
    current_disks = [d.get('location') for d in disks if d.get('disk-group') == module.params['name']]

    if module.params['disks'] and disk_group['raidtype'].lower() != 'nraid':
        expand_disks = [d for d in module.params['disks'] if d not in current_disks]
        if expand_disks:
            if not all([d in available_disks for d in expand_disks]):
                module.fail_json(
                    msg='disk(s): {0} missing or not in available state'.format(
                        ', '.join([d for d in expand_disks if d not in available_disks])
                    )
                )
            expanded_total = len(expand_disks) + disk_group['diskcount']
            if disk_group['raidtype'].lower() in ['raid0', 'raid3'] and disk_group['storage-type'].lower() != 'linear':
                module.fail_json(msg='unable to expand disk group {0} with raid type {1} and storage type {2}'.format(
                    module.params['name'], module.params['raid_type'], module.params['storage_type'])
                )
            if disk_group['raidtype'].lower() not in ['raid50', 'adapt'] and expanded_total > 16:
                module.fail_json(msg='{0} cannot have more than 16 disks in disk group {1}'.format(module.params['raid_type'], module.params['name']))
            if disk_group['raidtype'].lower() == 'raid50' and expanded_total > 32:
                module.fail_json(msg='{0} cannot have more than 32 disks in disk group {1}'.format(module.params['raid_type'], module.params['name']))
            if disk_group['raidtype'].lower() == 'adapt' and expanded_total > 32:
                module.fail_json(msg='{0} cannot have more than 128 disks in disk group {1}'.format(module.params['raid_type'], module.params['name']))
            if module.check_mode:
                rv['changed'] = True
                rv['disk_group'] = copy.deepcopy(disk_group)
                rv['disk_group']['diskcount'] = expanded_total
                rv['msg'].append('disk group expanded (check mode)')
            else:
                # split expand_disks in groups by 4 unless raid_type = adapt
                num_disks = 4
                if disk_group['raidtype'].lower() == 'adapt':
                    num_disks = 64
                d_chunks = [expand_disks[i:i + num_disks] for i in range(0, len(expand_disks), num_disks)]
                for e_disks in d_chunks:
                    rv['msgs'].append(expand_disk_group(session_key, e_disks, module))
                rv['changed'] = True

    if not module.check_mode:
        for group in get_disk_groups(session_key, module):
            if group.get('name') == module.params['name']:
                rv['disk_group'] = group
                break
    return rv


def present(module):
    changed = False
    diff = {'before': {}, 'after': {}}
    msg = 'no change'
    session_key = get_session_key(module)

    disk_groups = get_disk_groups(session_key, module)

    for disk_group in disk_groups:
        if module.params['name'] == disk_group.get('name'):
            diff['before'] = disk_group
            ret = update_disk_group(session_key, disk_group, module)
            diff['after'] = ret['disk_group']
            changed = ret['changed']
            if ret['msgs']:
                msg = 'disk group {0} updated, me4 output: {1}'.format(module.params['name'], ret['msgs'])
            return changed, diff, msg

    if module.params['name'] not in [g.get('name') for g in disk_groups]:
        ret = create_disk_group(session_key, module)
        changed = ret['changed']
        diff['after'] = ret['disk_group']
        if ret['msg']:
            msg = ret['msg']
        return changed, diff, msg


def absent(module):
    changed = False
    diff = {'before': {}, 'after': {}}
    msg = 'no change'
    session_key = get_session_key(module)

    disk_groups = get_disk_groups(session_key, module)
    for disk_group in disk_groups:
        if disk_group.get('name') == module.params['name']:
            diff['before'] = disk_group
        if module.check_mode:
            changed = True
            msg = 'disk group {0} removed (check mode)'.format(module.params['name'])
        else:
            msg = remove_disk_group(session_key, module)
        return changed, diff, msg


def main():
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(type='str', required=True),
            verify_cert=dict(type='bool', default=True),
            username=dict(type='str', default='manage'),
            password=dict(type='str', required=True, no_log=True),
            state=dict(type='str', choices=['absent', 'present'], default='present'),
            name=dict(type='str', required=True),
            raid=dict(type='str', choices=['nraid', 'r0', 'r1', 'r3', 'r5', 'r6', 'r10', 'r50', 'adapt']),
            mode=dict(type='str', choices=['offline', 'online'], default='online'),
            controller=dict(type='str', choices=['a', 'auto', 'b'], default='auto'),
            chunk_size=dict(type='str', choices=['64k', '128k', '256k', '512k'], default='512k'),
            spare_disks=dict(type='list', elements='str', default=[]),
            storage_type=dict(type='str', choices=['linear', 'virtual', 'read-cache'], default='linear'),
            disks=dict(type='list', elements='str'),
            pool=dict(type='str'),
            adapt_spare_capacity=dict(type='str', default='default'),
        ),
        supports_check_mode=True
    )

    if not REQUESTS_FOUND:
        module.fail_json(msg=missing_required_lib('requests'))

    if not validate_params(module):
        module.fail_json(msg='parameter validation failed')

    if module.params['state'] == 'present':
        changed, diff, msg = present(module)

    if module.params['state'] == 'absent':
        changed, diff, msg = absent(module)

    module.exit_json(changed=changed, diff=diff, msg=msg)


if __name__ == '__main__':
    main()
