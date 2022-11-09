#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: rax_cdb_user
short_description: Create / delete a Rackspace Cloud Database
description:
  - create / delete a database in the Cloud Databases.
options:
  cdb_id:
    type: str
    description:
      - The databases server UUID
    required: true
  db_username:
    type: str
    description:
      - Name of the database user
    required: true
  db_password:
    type: str
    description:
      - Database user password
    required: true
  databases:
    type: list
    elements: str
    description:
      - Name of the databases that the user can access
    default: []
  host:
    type: str
    description:
      - Specifies the host from which a user is allowed to connect to
        the database. Possible values are a string containing an IPv4 address
        or "%" to allow connecting from any host
    default: '%'
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
- name: Build a user in Cloud Databases
  tasks:
    - name: User build request
      local_action:
        module: rax_cdb_user
        credentials: ~/.raxpub
        region: IAD
        cdb_id: 323e7ce0-9cb0-11e3-a5e2-0800200c9a66
        db_username: user1
        db_password: user1
        databases: ['db1']
        state: present
      register: rax_db_user
'''

try:
    import pyrax
    HAS_PYRAX = True
except ImportError:
    HAS_PYRAX = False

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_text
from ansible_collections.community.general.plugins.module_utils.rax import rax_argument_spec, rax_required_together, rax_to_dict, setup_rax_module


def find_user(instance, name):
    try:
        user = instance.get_user(name)
    except Exception:
        return False

    return user


def save_user(module, cdb_id, name, password, databases, host):

    for arg, value in dict(cdb_id=cdb_id, name=name).items():
        if not value:
            module.fail_json(msg='%s is required for the "rax_cdb_user" '
                                 'module' % arg)

    cdb = pyrax.cloud_databases

    try:
        instance = cdb.get(cdb_id)
    except Exception as e:
        module.fail_json(msg='%s' % e.message)

    changed = False

    user = find_user(instance, name)

    if not user:
        action = 'create'
        try:
            user = instance.create_user(name=name,
                                        password=password,
                                        database_names=databases,
                                        host=host)
        except Exception as e:
            module.fail_json(msg='%s' % e.message)
        else:
            changed = True
    else:
        action = 'update'

        if user.host != host:
            changed = True

        user.update(password=password, host=host)

        former_dbs = set([item.name for item in user.list_user_access()])
        databases = set(databases)

        if databases != former_dbs:
            try:
                revoke_dbs = [db for db in former_dbs if db not in databases]
                user.revoke_user_access(db_names=revoke_dbs)

                new_dbs = [db for db in databases if db not in former_dbs]
                user.grant_user_access(db_names=new_dbs)
            except Exception as e:
                module.fail_json(msg='%s' % e.message)
            else:
                changed = True

    module.exit_json(changed=changed, action=action, user=rax_to_dict(user))


def delete_user(module, cdb_id, name):

    for arg, value in dict(cdb_id=cdb_id, name=name).items():
        if not value:
            module.fail_json(msg='%s is required for the "rax_cdb_user"'
                                 ' module' % arg)

    cdb = pyrax.cloud_databases

    try:
        instance = cdb.get(cdb_id)
    except Exception as e:
        module.fail_json(msg='%s' % e.message)

    changed = False

    user = find_user(instance, name)

    if user:
        try:
            user.delete()
        except Exception as e:
            module.fail_json(msg='%s' % e.message)
        else:
            changed = True

    module.exit_json(changed=changed, action='delete')


def rax_cdb_user(module, state, cdb_id, name, password, databases, host):

    # act on the state
    if state == 'present':
        save_user(module, cdb_id, name, password, databases, host)
    elif state == 'absent':
        delete_user(module, cdb_id, name)


def main():
    argument_spec = rax_argument_spec()
    argument_spec.update(
        dict(
            cdb_id=dict(type='str', required=True),
            db_username=dict(type='str', required=True),
            db_password=dict(type='str', required=True, no_log=True),
            databases=dict(type='list', elements='str', default=[]),
            host=dict(type='str', default='%'),
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
    name = module.params.get('db_username')
    password = module.params.get('db_password')
    databases = module.params.get('databases')
    host = to_text(module.params.get('host'), errors='surrogate_or_strict')
    state = module.params.get('state')

    setup_rax_module(module, pyrax)
    rax_cdb_user(module, state, cdb_id, name, password, databases, host)


if __name__ == '__main__':
    main()
