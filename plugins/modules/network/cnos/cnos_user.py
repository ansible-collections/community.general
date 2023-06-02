#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
#
# Copyright (C) 2019 Lenovo.
# (c) 2017, Ansible by Red Hat, inc
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#
# Module to work on management of local users on Lenovo CNOS Switches
# Lenovo Networking
#
ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: cnos_user
author: "Anil Kumar Muraleedharan (@amuraleedhar)"
short_description: Manage the collection of local users on Lenovo CNOS devices
description:
  - This module provides declarative management of the local usernames
    configured on Lenovo CNOS devices.  It allows playbooks to manage
    either individual usernames or the collection of usernames in the
    current running config.  It also supports purging usernames from the
    configuration that are not explicitly defined.
options:
  aggregate:
    description:
      - The set of username objects to be configured on the remote
        Lenovo CNOS device.  The list entries can either be the username
        or a hash of username and properties.  This argument is mutually
        exclusive with the C(name) argument.
    aliases: ['users', 'collection']
  name:
    description:
      - The username to be configured on the remote Lenovo CNOS
        device.  This argument accepts a string value and is mutually
        exclusive with the C(aggregate) argument.
  configured_password:
    description:
      - The password to be configured on the network device. The
        password needs to be provided in cleartext and it will be encrypted
        on the device.
        Please note that this option is not same as C(provider password).
  update_password:
    description:
      - Since passwords are encrypted in the device running config, this
        argument will instruct the module when to change the password.  When
        set to C(always), the password will always be updated in the device
        and when set to C(on_create) the password will be updated only if
        the username is created.
    default: always
    choices: ['on_create', 'always']
  role:
    description:
      - The C(role) argument configures the role for the username in the
        device running configuration.  The argument accepts a string value
        defining the role name.  This argument does not check if the role
        has been configured on the device.
    aliases: ['roles']
  sshkey:
    description:
      - The C(sshkey) argument defines the SSH public key to configure
        for the username.  This argument accepts a valid SSH key value.
  purge:
    description:
      - The C(purge) argument instructs the module to consider the
        resource definition absolute.  It will remove any previously
        configured usernames on the device with the exception of the
        `admin` user which cannot be deleted per cnos constraints.
    type: bool
    default: 'no'
  state:
    description:
      - The C(state) argument configures the state of the username definition
        as it relates to the device operational configuration.  When set
        to I(present), the username(s) should be configured in the device active
        configuration and when set to I(absent) the username(s) should not be
        in the device active configuration
    default: present
    choices: ['present', 'absent']
'''

EXAMPLES = """
- name: create a new user
  cnos_user:
    name: ansible
    sshkey: "{{ lookup('file', '~/.ssh/id_rsa.pub') }}"
    state: present

- name: remove all users except admin
  cnos_user:
    purge: yes

- name: set multiple users role
  aggregate:
    - name: netop
    - name: netend
  role: network-operator
  state: present
"""

RETURN = """
commands:
  description: The list of configuration mode commands to send to the device
  returned: always
  type: list
  sample:
    - name ansible
    - name ansible password password
start:
  description: The time the job started
  returned: always
  type: str
  sample: "2016-11-16 10:38:15.126146"
end:
  description: The time the job ended
  returned: always
  type: str
  sample: "2016-11-16 10:38:25.595612"
delta:
  description: The time elapsed to perform all operations
  returned: always
  type: str
  sample: "0:00:10.469466"
"""
import re

from copy import deepcopy
from functools import partial

from ansible_collections.community.general.plugins.module_utils.network.cnos.cnos import run_commands, load_config
from ansible_collections.community.general.plugins.module_utils.network.cnos.cnos import get_config
from ansible_collections.community.general.plugins.module_utils.network.cnos.cnos import cnos_argument_spec
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six import string_types, iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import to_list
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import remove_default_spec
from ansible_collections.community.general.plugins.module_utils.network.cnos.cnos import get_user_roles


def validate_roles(value, module):
    for item in value:
        if item not in get_user_roles():
            module.fail_json(msg='invalid role specified')


def map_obj_to_commands(updates, module):
    commands = list()
    state = module.params['state']
    update_password = module.params['update_password']

    for update in updates:
        want, have = update

        def needs_update(x):
            return want.get(x) and (want.get(x) != have.get(x))

        def add(x):
            return commands.append('username %s %s' % (want['name'], x))

        def remove(x):
            return commands.append('no username %s %s' % (want['name'], x))

        if want['state'] == 'absent':
            commands.append('no username %s' % want['name'])
            continue

        if want['state'] == 'present' and not have:
            commands.append('username %s' % want['name'])

        if needs_update('configured_password'):
            if update_password == 'always' or not have:
                add('password %s' % want['configured_password'])

        if needs_update('sshkey'):
            add('sshkey %s' % want['sshkey'])

        if want['roles']:
            if have:
                for item in set(have['roles']).difference(want['roles']):
                    remove('role %s' % item)

                for item in set(want['roles']).difference(have['roles']):
                    add('role %s' % item)
            else:
                for item in want['roles']:
                    add('role %s' % item)

    return commands


def parse_password(data):
    if 'no password set' in data:
        return None
    return '<PASSWORD>'


def parse_roles(data):
    roles = list()
    if 'role:' in data:
        items = data.split()
        my_item = items[items.index('role:') + 1]
        roles.append(my_item)
    return roles


def parse_username(data):
    name = data.split(' ', 1)[0]
    username = name[1:]
    return username


def parse_sshkey(data):
    key = None
    if 'sskkey:' in data:
        items = data.split()
        key = items[items.index('sshkey:') + 1]
    return key


def map_config_to_obj(module):
    out = run_commands(module, ['show user-account'])
    data = out[0]
    objects = list()
    datum = data.split('User')

    for item in datum:
        objects.append({
            'name': parse_username(item),
            'configured_password': parse_password(item),
            'sshkey': parse_sshkey(item),
            'roles': parse_roles(item),
            'state': 'present'
        })
    return objects


def get_param_value(key, item, module):
    # if key doesn't exist in the item, get it from module.params
    if not item.get(key):
        value = module.params[key]

    # if key does exist, do a type check on it to validate it
    else:
        value_type = module.argument_spec[key].get('type', 'str')
        type_checker = module._CHECK_ARGUMENT_TYPES_DISPATCHER[value_type]
        type_checker(item[key])
        value = item[key]

    return value


def map_params_to_obj(module):
    aggregate = module.params['aggregate']
    if not aggregate:
        if not module.params['name'] and module.params['purge']:
            return list()
        elif not module.params['name']:
            module.fail_json(msg='username is required')
        else:
            collection = [{'name': module.params['name']}]
    else:
        collection = list()
        for item in aggregate:
            if not isinstance(item, dict):
                collection.append({'name': item})
            elif 'name' not in item:
                module.fail_json(msg='name is required')
            else:
                collection.append(item)

    objects = list()

    for item in collection:
        get_value = partial(get_param_value, item=item, module=module)
        item.update({
            'configured_password': get_value('configured_password'),
            'sshkey': get_value('sshkey'),
            'roles': get_value('roles'),
            'state': get_value('state')
        })

        for key, value in iteritems(item):
            if value:
                # validate the param value (if validator func exists)
                validator = globals().get('validate_%s' % key)
                if all((value, validator)):
                    validator(value, module)

        objects.append(item)

    return objects


def update_objects(want, have):
    updates = list()
    for entry in want:
        item = next((i for i in have if i['name'] == entry['name']), None)
        if all((item is None, entry['state'] == 'present')):
            updates.append((entry, {}))
        elif item:
            for key, value in iteritems(entry):
                if value and value != item[key]:
                    updates.append((entry, item))
    return updates


def main():
    """ main entry point for module execution
    """
    element_spec = dict(
        name=dict(),
        configured_password=dict(no_log=True),
        update_password=dict(default='always', choices=['on_create', 'always']),
        roles=dict(type='list', aliases=['role']),
        sshkey=dict(),
        state=dict(default='present', choices=['present', 'absent'])
    )

    aggregate_spec = deepcopy(element_spec)

    # remove default in aggregate spec, to handle common arguments
    remove_default_spec(aggregate_spec)

    argument_spec = dict(
        aggregate=dict(type='list', elements='dict',
                       options=aggregate_spec, aliases=['collection', 'users']),
        purge=dict(type='bool', default=False)
    )

    argument_spec.update(element_spec)

    mutually_exclusive = [('name', 'aggregate')]

    module = AnsibleModule(argument_spec=argument_spec,
                           mutually_exclusive=mutually_exclusive,
                           supports_check_mode=True)

    warnings = list()

    result = {'changed': False}
    result['warnings'] = warnings

    want = map_params_to_obj(module)
    have = map_config_to_obj(module)

    commands = map_obj_to_commands(update_objects(want, have), module)

    if module.params['purge']:
        want_users = [x['name'] for x in want]
        have_users = [x['name'] for x in have]
        for item in set(have_users).difference(want_users):
            if item != 'admin':
                if not item.strip():
                    continue
                item = item.replace("\\", "\\\\")
                commands.append('no username %s' % item)

    result['commands'] = commands

    # the cnos cli prevents this by rule but still
    if 'no username admin' in commands:
        module.fail_json(msg='Cannot delete the `admin` account')

    if commands:
        if not module.check_mode:
            load_config(module, commands)
        result['changed'] = True

    module.exit_json(**result)


if __name__ == '__main__':
    main()
