#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Scaleway database backups management module
#
# Copyright (C) 2020 Guillaume Rodriguez (g.rodriguez@opendecide.com).
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: scaleway_database_backup
short_description: Scaleway database backups management module
version_added: 1.2.0
author: Guillaume Rodriguez (@guillaume_ro_fr)
description:
  - This module manages database backups on Scaleway account U(https://developer.scaleway.com).
extends_documentation_fragment:
  - community.general.scaleway
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  state:
    description:
      - Indicate desired state of the database backup.
      - V(present) creates a backup.
      - V(absent) deletes the backup.
      - V(exported) creates a download link for the backup.
      - V(restored) restores the backup to a new database.
    type: str
    default: present
    choices:
      - present
      - absent
      - exported
      - restored

  region:
    description:
      - Scaleway region to use (for example V(fr-par)).
    type: str
    required: true
    choices:
      - fr-par
      - nl-ams
      - pl-waw

  id:
    description:
      - UUID used to identify the database backup.
      - Required for V(absent), V(exported) and V(restored) states.
    type: str

  name:
    description:
      - Name used to identify the database backup.
      - Required for V(present) state.
      - Ignored when O(state=absent), O(state=exported) or O(state=restored).
    type: str
    required: false

  database_name:
    description:
      - Name used to identify the database.
      - Required for V(present) and V(restored) states.
      - Ignored when O(state=absent) or O(state=exported).
    type: str
    required: false

  instance_id:
    description:
      - UUID of the instance associated to the database backup.
      - Required for V(present) and V(restored) states.
      - Ignored when O(state=absent) or O(state=exported).
    type: str
    required: false

  expires_at:
    description:
      - Expiration datetime of the database backup (ISO 8601 format).
      - Ignored when O(state=absent), O(state=exported) or O(state=restored).
    type: str
    required: false

  wait:
    description:
      - Wait for the instance to reach its desired state before returning.
    type: bool
    default: false

  wait_timeout:
    description:
      - Time to wait for the backup to reach the expected state.
    type: int
    required: false
    default: 300

  wait_sleep_time:
    description:
      - Time to wait before every attempt to check the state of the backup.
    type: int
    required: false
    default: 3
"""

EXAMPLES = r"""
- name: Create a backup
  community.general.scaleway_database_backup:
    name: 'my_backup'
    state: present
    region: 'fr-par'
    database_name: 'my-database'
    instance_id: '50968a80-2909-4e5c-b1af-a2e19860dddb'

- name: Export a backup
  community.general.scaleway_database_backup:
    id: '6ef1125a-037e-494f-a911-6d9c49a51691'
    state: exported
    region: 'fr-par'

- name: Restore a backup
  community.general.scaleway_database_backup:
    id: '6ef1125a-037e-494f-a911-6d9c49a51691'
    state: restored
    region: 'fr-par'
    database_name: 'my-new-database'
    instance_id: '50968a80-2909-4e5c-b1af-a2e19860dddb'

- name: Remove a backup
  community.general.scaleway_database_backup:
    id: '6ef1125a-037e-494f-a911-6d9c49a51691'
    state: absent
    region: 'fr-par'
"""

RETURN = r"""
metadata:
  description: Backup metadata.
  returned: when O(state=present), O(state=exported), or O(state=restored)
  type: dict
  sample:
    {
      "metadata": {
        "created_at": "2020-08-06T12:42:05.631049Z",
        "database_name": "my-database",
        "download_url": null,
        "download_url_expires_at": null,
        "expires_at": null,
        "id": "a15297bd-0c4a-4b4f-8fbb-b36a35b7eb07",
        "instance_id": "617be32e-6497-4ed7-b4c7-0ee5a81edf49",
        "instance_name": "my-instance",
        "name": "backup_name",
        "region": "fr-par",
        "size": 600000,
        "status": "ready",
        "updated_at": "2020-08-06T12:42:10.581649Z"
      }
    }
"""

import datetime
import time

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.datetime import (
    now,
)
from ansible_collections.community.general.plugins.module_utils.scaleway import (
    Scaleway,
    scaleway_argument_spec,
    SCALEWAY_REGIONS,
)

stable_states = (
    'ready',
    'deleting',
)


def wait_to_complete_state_transition(module, account_api, backup=None):
    wait_timeout = module.params['wait_timeout']
    wait_sleep_time = module.params['wait_sleep_time']

    if backup is None or backup['status'] in stable_states:
        return backup

    start = now()
    end = start + datetime.timedelta(seconds=wait_timeout)
    while now() < end:
        module.debug('We are going to wait for the backup to finish its transition')

        response = account_api.get('/rdb/v1/regions/%s/backups/%s' % (module.params.get('region'), backup['id']))
        if not response.ok:
            module.fail_json(msg='Error getting backup [{0}: {1}]'.format(response.status_code, response.json))
            break
        response_json = response.json

        if response_json['status'] in stable_states:
            module.debug('It seems that the backup is not in transition anymore.')
            module.debug('Backup in state: %s' % response_json['status'])
            return response_json
        time.sleep(wait_sleep_time)
    else:
        module.fail_json(msg='Backup takes too long to finish its transition')


def present_strategy(module, account_api, backup):
    name = module.params['name']
    database_name = module.params['database_name']
    instance_id = module.params['instance_id']
    expiration_date = module.params['expires_at']

    if backup is not None:
        if (backup['name'] == name or name is None) and (
                backup['expires_at'] == expiration_date or expiration_date is None):
            wait_to_complete_state_transition(module, account_api, backup)
            module.exit_json(changed=False)

        if module.check_mode:
            module.exit_json(changed=True)

        payload = {}
        if name is not None:
            payload['name'] = name
        if expiration_date is not None:
            payload['expires_at'] = expiration_date

        response = account_api.patch('/rdb/v1/regions/%s/backups/%s' % (module.params.get('region'), backup['id']),
                                     payload)
        if response.ok:
            result = wait_to_complete_state_transition(module, account_api, response.json)
            module.exit_json(changed=True, metadata=result)

        module.fail_json(msg='Error modifying backup [{0}: {1}]'.format(response.status_code, response.json))

    if module.check_mode:
        module.exit_json(changed=True)

    payload = {'name': name, 'database_name': database_name, 'instance_id': instance_id}
    if expiration_date is not None:
        payload['expires_at'] = expiration_date

    response = account_api.post('/rdb/v1/regions/%s/backups' % module.params.get('region'), payload)

    if response.ok:
        result = wait_to_complete_state_transition(module, account_api, response.json)
        module.exit_json(changed=True, metadata=result)

    module.fail_json(msg='Error creating backup [{0}: {1}]'.format(response.status_code, response.json))


def absent_strategy(module, account_api, backup):
    if backup is None:
        module.exit_json(changed=False)

    if module.check_mode:
        module.exit_json(changed=True)

    response = account_api.delete('/rdb/v1/regions/%s/backups/%s' % (module.params.get('region'), backup['id']))
    if response.ok:
        result = wait_to_complete_state_transition(module, account_api, response.json)
        module.exit_json(changed=True, metadata=result)

    module.fail_json(msg='Error deleting backup [{0}: {1}]'.format(response.status_code, response.json))


def exported_strategy(module, account_api, backup):
    if backup is None:
        module.fail_json(msg=('Backup "%s" not found' % module.params['id']))

    if backup['download_url'] is not None:
        module.exit_json(changed=False, metadata=backup)

    if module.check_mode:
        module.exit_json(changed=True)

    backup = wait_to_complete_state_transition(module, account_api, backup)
    response = account_api.post(
        '/rdb/v1/regions/%s/backups/%s/export' % (module.params.get('region'), backup['id']), {})

    if response.ok:
        result = wait_to_complete_state_transition(module, account_api, response.json)
        module.exit_json(changed=True, metadata=result)

    module.fail_json(msg='Error exporting backup [{0}: {1}]'.format(response.status_code, response.json))


def restored_strategy(module, account_api, backup):
    if backup is None:
        module.fail_json(msg=('Backup "%s" not found' % module.params['id']))

    database_name = module.params['database_name']
    instance_id = module.params['instance_id']

    if module.check_mode:
        module.exit_json(changed=True)

    backup = wait_to_complete_state_transition(module, account_api, backup)

    payload = {'database_name': database_name, 'instance_id': instance_id}
    response = account_api.post('/rdb/v1/regions/%s/backups/%s/restore' % (module.params.get('region'), backup['id']),
                                payload)

    if response.ok:
        result = wait_to_complete_state_transition(module, account_api, response.json)
        module.exit_json(changed=True, metadata=result)

    module.fail_json(msg='Error restoring backup [{0}: {1}]'.format(response.status_code, response.json))


state_strategy = {
    'present': present_strategy,
    'absent': absent_strategy,
    'exported': exported_strategy,
    'restored': restored_strategy,
}


def core(module):
    state = module.params['state']
    backup_id = module.params['id']

    account_api = Scaleway(module)

    if backup_id is None:
        backup_by_id = None
    else:
        response = account_api.get('/rdb/v1/regions/%s/backups/%s' % (module.params.get('region'), backup_id))
        status_code = response.status_code
        backup_json = response.json
        backup_by_id = None
        if status_code == 404:
            backup_by_id = None
        elif response.ok:
            backup_by_id = backup_json
        else:
            module.fail_json(msg='Error getting backup [{0}: {1}]'.format(status_code, response.json['message']))

    state_strategy[state](module, account_api, backup_by_id)


def main():
    argument_spec = scaleway_argument_spec()
    argument_spec.update(dict(
        state=dict(default='present', choices=['absent', 'present', 'exported', 'restored']),
        region=dict(required=True, choices=SCALEWAY_REGIONS),
        id=dict(),
        name=dict(type='str'),
        database_name=dict(required=False),
        instance_id=dict(required=False),
        expires_at=dict(),
        wait=dict(type='bool', default=False),
        wait_timeout=dict(type='int', default=300),
        wait_sleep_time=dict(type='int', default=3),
    ))
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_together=[
            ['database_name', 'instance_id'],
        ],
        required_if=[
            ['state', 'present', ['name', 'database_name', 'instance_id']],
            ['state', 'absent', ['id']],
            ['state', 'exported', ['id']],
            ['state', 'restored', ['id', 'database_name', 'instance_id']],
        ],
    )

    core(module)


if __name__ == '__main__':
    main()
