#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2017, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from ansible.module_utils._text import to_native
from ansible_collections.community.general.plugins.module_utils.ipa import IPAClient, ipa_argument_spec
from ansible.module_utils.basic import AnsibleModule
import traceback
__metaclass__ = type

DOCUMENTATION = r'''
---
module: ipa_automember
author: Mark Hahl (@wolskie)
short_description: Add and delete FreeIPA Auto Membership Rules.
description:
- Add, modify and delete an IPA Auto Membership Rule using IPA API.
options:
  cn:
    description:
    - Automember Rule.
    - Can not be changed as it is the unique identifier.
    required: true
    aliases: ["name"]
    type: str
  description:
    description:
    - A description of this auto member rule.
    type: str
  type:
    description:
    - Grouping to which the rule applies
    required: true
    choices: ["group", "hostgroup"]
extends_documentation_fragment:
- community.general.ipa.documentation

'''

EXAMPLES = r'''
- name: Ensure user group rule is present
  community.general.ipa_automember:
    name: admins
    type: group
    description: Example user group rule
    community.general.ipa_host: ipa.example.com
    ipa_user: admin
    ipa_pass: topsecret

- name: Ensure hostgroup group rule is present
  community.general.ipa_automember:
    name: ipaservers
    type: hostgroup
    description: Example host group rule
    community.general.ipa_host: ipa.example.com
    ipa_user: admin
    ipa_pass: topsecret

- name: Ensure user group rule is is absent
  community.general.ipa_automember:
    name: admins
    type: group
    state: absent
    community.general.ipa_host: ipa.example.com
    ipa_user: admin
    ipa_pass: topsecret

- name: Ensure host group rule is is absent
  community.general.ipa_automember:
    name: admins
    type: hostgroup
    state: absent
    community.general.ipa_host: ipa.example.com
    ipa_user: admin
    ipa_pass: topsecret
'''

RETURN = r'''
automember:
  description: Automember Rule as returned by IPA API.
  returned: always
  type: dict
'''


class AutoMemberIPAClient(IPAClient):
    def __init__(self, module, host, port, protocol):
        super(AutoMemberIPAClient, self).__init__(module, host, port, protocol)

    def automember_find(self, name, member_type):
        return self._post_json(method='automember_find', name=name, item={'type': member_type, 'all': True})

    def automember_add(self, name, rule):
        return self._post_json(method='automember_add', name=name, item=rule)

    def automember_mod(self, name, rule):
        return self._post_json(method='automember_mod', name=name, item=rule)

    def automember_del(self, name, member_type):
        return self._post_json(method='automember_del', name=name, item={'type': member_type})


def get_automember_dict(member_type, description=None):
    data = {}
    data['type'] = member_type
    if description is not None:
        data['description'] = description
    return data


def get_automember_diff(client, ipa_automember, module_automember):
    non_updateable_keys = ['cn', 'dn', 'automembertargetgroup']
    for key in non_updateable_keys:
        if key in module_automember:
            del module_automember[key]
    return client.get_diff(ipa_data=ipa_automember, module_data=module_automember)


def ensure(module, client):
    name = module.params['cn']
    state = module.params['state']
    description = module.params['description']
    member_type = module.params['type']

    module_automember = get_automember_dict(description=description,
                                            member_type=member_type)
    ipa_automember = client.automember_find(name=name, member_type=member_type)
    changed = False
    diff = None
    if state == 'present':
        if not ipa_automember:
            changed = True
            if not module.check_mode:
                ipa_automember = client.automember_add(
                    name=name, rule=module_automember)
        else:
            diff = get_automember_diff(
                client, ipa_automember, module_automember)
            if len(diff) > 0:
                changed = True
                if not module.check_mode:
                    data = {}
                    for key in diff:
                        data[key] = module_automember.get(key)
                    return changed, client.automember_mod(name=name, rule=data)
    else:
        if ipa_automember:
            changed = True
            if not module.check_mode:
                client.automember_del(name=name, member_type=member_type)

    return changed, client.automember_find(name=name, member_type=member_type)


def main():
    argument_spec = ipa_argument_spec()
    argument_spec.update(description=dict(type='str'),
                         cn=dict(type='str', required=True, aliases=['name']),
                         type=dict(type='str', choices=['group', 'hostgroup']),
                         state=dict(type='str', default='present', choices=['present', 'absent', 'enabled', 'disabled']))

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    client = AutoMemberIPAClient(module=module,
                                 host=module.params['ipa_host'],
                                 port=module.params['ipa_port'],
                                 protocol=module.params['ipa_prot'])

    try:
        client.login(username=module.params['ipa_user'],
                     password=module.params['ipa_pass'])
        changed, automember = ensure(module, client)
        module.exit_json(changed=changed, automember=automember)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=traceback.format_exc())


if __name__ == '__main__':
    main()
