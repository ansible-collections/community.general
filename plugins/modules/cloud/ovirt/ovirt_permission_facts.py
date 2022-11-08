#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 Red Hat, Inc.
#
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

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: ovirt_permission_facts
short_description: Retrieve information about one or more oVirt/RHV permissions
author: "Ondra Machacek (@machacekondra)"
deprecated:
    removed_in: 3.0.0  # was Ansible 2.13
    why: When migrating to collection we decided to use only _info modules.
    alternative: Use M(ovirt.ovirt.ovirt_permission_info) instead.
description:
    - "Retrieve information about one or more oVirt/RHV permissions."
notes:
    - "This module returns a variable C(ovirt_permissions), which
       contains a list of permissions. You need to register the result with
       the I(register) keyword to use it."
options:
    user_name:
        description:
            - "Username of the user to manage. In most LDAPs it's I(uid) of the user, but in Active Directory you must specify I(UPN) of the user."
    group_name:
        description:
            - "Name of the group to manage."
    authz_name:
        description:
            - "Authorization provider of the user/group. In previous versions of oVirt/RHV known as domain."
        required: true
        aliases: ['domain']
    namespace:
        description:
            - "Namespace of the authorization provider, where user/group resides."
        required: false
extends_documentation_fragment:
- community.general.ovirt_facts

'''

EXAMPLES = '''
# Examples don't contain auth parameter for simplicity,
# look at ovirt_auth module to see how to reuse authentication:

- name: Gather information about all permissions of user with username john
  ovirt_permission_info:
    user_name: john
    authz_name: example.com-authz
  register: result

- name: Print gathered information
  ansible.builtin.debug:
    msg: "{{ result.ovirt_permissions }}"
'''

RETURN = '''
ovirt_permissions:
    description: "List of dictionaries describing the permissions. Permission attributes are mapped to dictionary keys,
                  all permissions attributes can be found at following url: http://ovirt.github.io/ovirt-engine-api-model/master/#types/permission."
    returned: On success.
    type: list
'''

import traceback

try:
    import ovirtsdk4 as sdk
except ImportError:
    pass

from ansible.module_utils.common.removed import removed_module
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils._ovirt import (
    check_sdk,
    create_connection,
    get_link_name,
    ovirt_info_full_argument_spec,
    search_by_name,
)


def _permissions_service(connection, module):
    if module.params['user_name']:
        service = connection.system_service().users_service()
        entity = next(
            iter(
                service.list(
                    search='usrname={0}'.format(
                        '{0}@{1}'.format(module.params['user_name'], module.params['authz_name'])
                    )
                )
            ),
            None
        )
    else:
        service = connection.system_service().groups_service()
        entity = search_by_name(service, module.params['group_name'])

    if entity is None:
        raise Exception("User/Group wasn't found.")

    return service.service(entity.id).permissions_service()


def main():
    argument_spec = ovirt_info_full_argument_spec(
        authz_name=dict(required=True, aliases=['domain']),
        user_name=dict(default=None),
        group_name=dict(default=None),
        namespace=dict(default=None),
    )
    module = AnsibleModule(argument_spec)
    is_old_facts = module._name in ('ovirt_permission_facts', 'community.general.ovirt_permission_facts')
    if is_old_facts:
        module.deprecate("The 'ovirt_permission_facts' module has been renamed to 'ovirt_permission_info', "
                         "and the renamed one no longer returns ansible_facts",
                         version='3.0.0', collection_name='community.general')  # was Ansible 2.13

    check_sdk(module)

    try:
        auth = module.params.pop('auth')
        connection = create_connection(auth)
        permissions_service = _permissions_service(connection, module)
        permissions = []
        for p in permissions_service.list():
            newperm = dict()
            for key, value in p.__dict__.items():
                if value and isinstance(value, sdk.Struct):
                    newperm[key[1:]] = get_link_name(connection, value)
                    newperm['%s_id' % key[1:]] = value.id
            permissions.append(newperm)

        result = dict(ovirt_permissions=permissions)
        if is_old_facts:
            module.exit_json(changed=False, ansible_facts=result)
        else:
            module.exit_json(changed=False, **result)
    except Exception as e:
        module.fail_json(msg=str(e), exception=traceback.format_exc())
    finally:
        connection.close(logout=auth.get('token') is None)


if __name__ == '__main__':
    main()
