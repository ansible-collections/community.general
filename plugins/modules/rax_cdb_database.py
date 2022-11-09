#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
module: rax_cdb_database
short_description: Create / delete a database in the Cloud Databases
description:
  - create / delete a database in the Cloud Databases.
options:
  cdb_id:
    type: str
    description:
      - The databases server UUID
    required: true
  name:
    type: str
    description:
      - Name to give to the database
    required: true
  character_set:
    type: str
    description:
      - Set of symbols and encodings
    default: 'utf8'
  collate:
    type: str
    description:
      - Set of rules for comparing characters in a character set
    default: 'utf8_general_ci'
  state:
    type: str
    description:
      - Indicate desired state of the resource
    choices: ['present', 'absent']
    default: present
author: "Simon JAILLET (@jails)"
extends_documentation_fragment:
- community.general.rackspace
- community.general.rackspace.openstack

'''

EXAMPLES = '''
- name: Build a database in Cloud Databases
  tasks:
    - name: Database build request
      local_action:
        module: rax_cdb_database
        credentials: ~/.raxpub
        region: IAD
        cdb_id: 323e7ce0-9cb0-11e3-a5e2-0800200c9a66
        name: db1
        state: present
      register: rax_db_database
'''

try:
    import pyrax
    HAS_PYRAX = True
except ImportError:
    HAS_PYRAX = False

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.rax import rax_argument_spec, rax_required_together, rax_to_dict, setup_rax_module


def find_database(instance, name):
    try:
        database = instance.get_database(name)
    except Exception:
        return False

    return database


def save_database(module, cdb_id, name, character_set, collate):
    cdb = pyrax.cloud_databases

    try:
        instance = cdb.get(cdb_id)
    except Exception as e:
        module.fail_json(msg='%s' % e.message)

    changed = False

    database = find_database(instance, name)

    if not database:
        try:
            database = instance.create_database(name=name,
                                                character_set=character_set,
                                                collate=collate)
        except Exception as e:
            module.fail_json(msg='%s' % e.message)
        else:
            changed = True

    module.exit_json(changed=changed, action='create',
                     database=rax_to_dict(database))


def delete_database(module, cdb_id, name):
    cdb = pyrax.cloud_databases

    try:
        instance = cdb.get(cdb_id)
    except Exception as e:
        module.fail_json(msg='%s' % e.message)

    changed = False

    database = find_database(instance, name)

    if database:
        try:
            database.delete()
        except Exception as e:
            module.fail_json(msg='%s' % e.message)
        else:
            changed = True

    module.exit_json(changed=changed, action='delete',
                     database=rax_to_dict(database))


def rax_cdb_database(module, state, cdb_id, name, character_set, collate):

    # act on the state
    if state == 'present':
        save_database(module, cdb_id, name, character_set, collate)
    elif state == 'absent':
        delete_database(module, cdb_id, name)


def main():
    argument_spec = rax_argument_spec()
    argument_spec.update(
        dict(
            cdb_id=dict(type='str', required=True),
            name=dict(type='str', required=True),
            character_set=dict(type='str', default='utf8'),
            collate=dict(type='str', default='utf8_general_ci'),
            state=dict(default='present', choices=['present', 'absent'])
        )
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_together=rax_required_together(),
    )

    if not HAS_PYRAX:
        module.fail_json(msg='pyrax is required for this module')

    cdb_id = module.params.get('cdb_id')
    name = module.params.get('name')
    character_set = module.params.get('character_set')
    collate = module.params.get('collate')
    state = module.params.get('state')

    setup_rax_module(module, pyrax)
    rax_cdb_database(module, state, cdb_id, name, character_set, collate)


if __name__ == '__main__':
    main()
