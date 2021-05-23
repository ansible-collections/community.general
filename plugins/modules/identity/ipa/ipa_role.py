#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2017, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: ipa_role
author: Thomas Krahn (@Nosmoht)
short_description: Manage FreeIPA role
description:
- Add, modify and delete a role within FreeIPA server using FreeIPA API.
options:
  cn:
    description:
    - Role name.
    - Can not be changed as it is the unique identifier.
    required: true
    aliases: ['name']
    type: str
  description:
    description:
    - A description of this role-group.
    type: str
  group:
    description:
    - List of group names assign to this role.
    - If an empty list is passed all assigned groups will be unassigned from the role.
    - If option is omitted groups will not be checked or changed.
    - If option is passed all assigned groups that are not passed will be unassigned from the role.
    type: list
    elements: str
  host:
    description:
    - List of host names to assign.
    - If an empty list is passed all assigned hosts will be unassigned from the role.
    - If option is omitted hosts will not be checked or changed.
    - If option is passed all assigned hosts that are not passed will be unassigned from the role.
    type: list
    elements: str
  hostgroup:
    description:
    - List of host group names to assign.
    - If an empty list is passed all assigned host groups will be removed from the role.
    - If option is omitted host groups will not be checked or changed.
    - If option is passed all assigned hostgroups that are not passed will be unassigned from the role.
    type: list
    elements: str
  privilege:
    description:
    - List of privileges granted to the role.
    - If an empty list is passed all assigned privileges will be removed.
    - If option is omitted privileges will not be checked or changed.
    - If option is passed all assigned privileges that are not passed will be removed.
    type: list
    elements: str
  service:
    description:
    - List of service names to assign.
    - If an empty list is passed all assigned services will be removed from the role.
    - If option is omitted services will not be checked or changed.
    - If option is passed all assigned services that are not passed will be removed from the role.
    type: list
    elements: str
  state:
    description: State to ensure.
    default: "present"
    choices: ["absent", "present"]
    type: str
  user:
    description:
    - List of user names to assign.
    - If an empty list is passed all assigned users will be removed from the role.
    - If option is omitted users will not be checked or changed.
    type: list
    elements: str
extends_documentation_fragment:
- community.general.ipa.documentation

'''

EXAMPLES = r'''
- name: Ensure role is present
  community.general.ipa_role:
    name: dba
    description: Database Administrators
    state: present
    user:
    - pinky
    - brain
    ipa_host: ipa.example.com
    ipa_user: admin
    ipa_pass: topsecret

- name: Ensure role with certain details
  community.general.ipa_role:
    name: another-role
    description: Just another role
    group:
    - editors
    host:
    - host01.example.com
    hostgroup:
    - hostgroup01
    privilege:
    - Group Administrators
    - User Administrators
    service:
    - service01

- name: Ensure role is absent
  community.general.ipa_role:
    name: dba
    state: absent
    ipa_host: ipa.example.com
    ipa_user: admin
    ipa_pass: topsecret
'''

RETURN = r'''
role:
  description: Role as returned by IPA API.
  returned: always
  type: dict
'''

import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.ipa import IPAClient, ipa_argument_spec
from ansible.module_utils._text import to_native


class RoleIPAClient(IPAClient):
    def __init__(self, module, host, port, protocol):
        super(RoleIPAClient, self).__init__(module, host, port, protocol)

    def role_find(self, name):
        return self._post_json(method='role_find', name=None, item={'all': True, 'cn': name})

    def role_add(self, name, item):
        return self._post_json(method='role_add', name=name, item=item)

    def role_mod(self, name, item):
        return self._post_json(method='role_mod', name=name, item=item)

    def role_del(self, name):
        return self._post_json(method='role_del', name=name)

    def role_add_member(self, name, item):
        return self._post_json(method='role_add_member', name=name, item=item)

    def role_add_group(self, name, item):
        return self.role_add_member(name=name, item={'group': item})

    def role_add_host(self, name, item):
        return self.role_add_member(name=name, item={'host': item})

    def role_add_hostgroup(self, name, item):
        return self.role_add_member(name=name, item={'hostgroup': item})

    def role_add_service(self, name, item):
        return self.role_add_member(name=name, item={'service': item})

    def role_add_user(self, name, item):
        return self.role_add_member(name=name, item={'user': item})

    def role_remove_member(self, name, item):
        return self._post_json(method='role_remove_member', name=name, item=item)

    def role_remove_group(self, name, item):
        return self.role_remove_member(name=name, item={'group': item})

    def role_remove_host(self, name, item):
        return self.role_remove_member(name=name, item={'host': item})

    def role_remove_hostgroup(self, name, item):
        return self.role_remove_member(name=name, item={'hostgroup': item})

    def role_remove_service(self, name, item):
        return self.role_remove_member(name=name, item={'service': item})

    def role_remove_user(self, name, item):
        return self.role_remove_member(name=name, item={'user': item})

    def role_add_privilege(self, name, item):
        return self._post_json(method='role_add_privilege', name=name, item={'privilege': item})

    def role_remove_privilege(self, name, item):
        return self._post_json(method='role_remove_privilege', name=name, item={'privilege': item})


def get_role_dict(description=None):
    data = {}
    if description is not None:
        data['description'] = description
    return data


def get_role_diff(client, ipa_role, module_role):
    return client.get_diff(ipa_data=ipa_role, module_data=module_role)


def ensure(module, client):
    state = module.params['state']
    name = module.params['cn']
    group = module.params['group']
    host = module.params['host']
    hostgroup = module.params['hostgroup']
    privilege = module.params['privilege']
    service = module.params['service']
    user = module.params['user']

    module_role = get_role_dict(description=module.params['description'])
    ipa_role = client.role_find(name=name)

    changed = False
    if state == 'present':
        if not ipa_role:
            changed = True
            if not module.check_mode:
                ipa_role = client.role_add(name=name, item=module_role)
        else:
            diff = get_role_diff(client, ipa_role, module_role)
            if len(diff) > 0:
                changed = True
                if not module.check_mode:
                    data = {}
                    for key in diff:
                        data[key] = module_role.get(key)
                    client.role_mod(name=name, item=data)

        if group is not None:
            changed = client.modify_if_diff(name, ipa_role.get('member_group', []), group,
                                            client.role_add_group,
                                            client.role_remove_group) or changed
        if host is not None:
            changed = client.modify_if_diff(name, ipa_role.get('member_host', []), host,
                                            client.role_add_host,
                                            client.role_remove_host) or changed

        if hostgroup is not None:
            changed = client.modify_if_diff(name, ipa_role.get('member_hostgroup', []), hostgroup,
                                            client.role_add_hostgroup,
                                            client.role_remove_hostgroup) or changed

        if privilege is not None:
            changed = client.modify_if_diff(name, ipa_role.get('memberof_privilege', []), privilege,
                                            client.role_add_privilege,
                                            client.role_remove_privilege) or changed
        if service is not None:
            changed = client.modify_if_diff(name, ipa_role.get('member_service', []), service,
                                            client.role_add_service,
                                            client.role_remove_service) or changed
        if user is not None:
            changed = client.modify_if_diff(name, ipa_role.get('member_user', []), user,
                                            client.role_add_user,
                                            client.role_remove_user) or changed

    else:
        if ipa_role:
            changed = True
            if not module.check_mode:
                client.role_del(name)

    return changed, client.role_find(name=name)


def main():
    argument_spec = ipa_argument_spec()
    argument_spec.update(cn=dict(type='str', required=True, aliases=['name']),
                         description=dict(type='str'),
                         group=dict(type='list', elements='str'),
                         host=dict(type='list', elements='str'),
                         hostgroup=dict(type='list', elements='str'),
                         privilege=dict(type='list', elements='str'),
                         service=dict(type='list', elements='str'),
                         state=dict(type='str', default='present', choices=['present', 'absent']),
                         user=dict(type='list', elements='str'))

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    client = RoleIPAClient(module=module,
                           host=module.params['ipa_host'],
                           port=module.params['ipa_port'],
                           protocol=module.params['ipa_prot'])

    try:
        client.login(username=module.params['ipa_user'],
                     password=module.params['ipa_pass'])
        changed, role = ensure(module, client)
        module.exit_json(changed=changed, role=role)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=traceback.format_exc())


if __name__ == '__main__':
    main()
