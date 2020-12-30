#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2020, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: ipa_pwpolicy
author: Adralioh (@adralioh)
short_description: Manage FreeIPA password policies
description:
- Add, modify, and delete password policy within IPA server.
version_added: 2.0.0
options:
    cn:
        description:
        - Name of the group that the policy applies to.
        - If omitted, the global policy is used.
        aliases: ["group", "name"]
        type: str
    state:
        description: State to ensure.
        default: "present"
        choices: ["absent", "present"]
        type: str
    krbmaxpwdlife:
        description: Maximum password lifetime (in days).
        aliases: ["maxlife"]
        type: str
    krbminpwdlife:
        description: Minimum password lifetime (in hours).
        aliases: ["minlife"]
        type: str
    krbpwdhistorylength:
        description: Password history size.
        aliases: ["history"]
        type: str
    krbpwdmindiffchars:
        description: Minimum number of character classes.
        aliases: ["minclasses"]
        type: str
    krbpwdminlength:
        description: Minimum length of password.
        aliases: ["minlength"]
        type: str
    cospriority:
        description:
        - Priority of the policy.
        - High number means lower priority.
        - Required when C(cn) is not the global policy.
        aliases: ["priority"]
        type: str
    krbpwdmaxfailure:
        description: Consecutive failures before lockout.
        aliases: ["maxfail"]
        type: str
    krbpwdfailurecountinterval:
        description: Period after which lockout is enforced (seconds).
        aliases: ["failinterval"]
        type: str
    krbpwdlockoutduration:
        description: Period for which lockout is enforced (seconds).
        aliases: ["lockouttime"]
        type: str
extends_documentation_fragment:
- community.general.ipa.documentation
notes:
- Supports C(check_mode).
'''

EXAMPLES = r'''
- name: Modify the global password policy
  community.general.ipa_pwpolicy:
      maxlife: '90'
      minlife: '1'
      history: '8'
      minclasses: '3'
      minlength: '16'
      maxfail: '6'
      failinterval: '60'
      lockouttime: '600'
      ipa_host: ipa.example.com
      ipa_user: admin
      ipa_pass: topsecret

- name: Ensure the password policy for the group admins is present
  community.general.ipa_pwpolicy:
      group: admins
      state: present
      maxlife: '60'
      minlife: '24'
      history: '16'
      minclasses: '4'
      priority: '10'
      maxfail: '4'
      failinterval: '600'
      lockouttime: '1200'
      ipa_host: ipa.example.com
      ipa_user: admin
      ipa_pass: topsecret

- name: Ensure that the group sysops does not have a unique password policy
  community.general.ipa_pwpolicy:
      group: sysops
      state: absent
      ipa_host: ipa.example.com
      ipa_user: admin
      ipa_pass: topsecret
'''

RETURN = r'''
pwpolicy:
    description: Password policy as returned by IPA API.
    returned: always
    type: dict
    sample:
        cn: ['admins']
        cospriority: ['10']
        dn: 'cn=admins,cn=EXAMPLE.COM,cn=kerberos,dc=example,dc=com'
        krbmaxpwdlife: ['60']
        krbminpwdlife: ['24']
        krbpwdfailurecountinterval: ['600']
        krbpwdhistorylength: ['16']
        krbpwdlockoutduration: ['1200']
        krbpwdmaxfailure: ['4']
        krbpwdmindiffchars: ['4']
        objectclass: ['top', 'nscontainer', 'krbpwdpolicy']
'''

import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.ipa import IPAClient, ipa_argument_spec
from ansible.module_utils._text import to_native


class PwPolicyIPAClient(IPAClient):
    '''The global policy will be selected when `name` is `None`'''
    def __init__(self, module, host, port, protocol):
        super(PwPolicyIPAClient, self).__init__(module, host, port, protocol)

    def pwpolicy_find(self, name):
        if name is None:
            # Manually set the cn to the global policy because pwpolicy_find will return a random
            # different policy if cn is `None`
            name = 'global_policy'
        return self._post_json(method='pwpolicy_find', name=None, item={'all': True, 'cn': name})

    def pwpolicy_add(self, name, item):
        return self._post_json(method='pwpolicy_add', name=name, item=item)

    def pwpolicy_mod(self, name, item):
        return self._post_json(method='pwpolicy_mod', name=name, item=item)

    def pwpolicy_del(self, name):
        return self._post_json(method='pwpolicy_del', name=name)


def get_pwpolicy_dict(maxlife=None, minlife=None, history=None, minclasses=None,
                      minlength=None, priority=None, maxfail=None, failinterval=None,
                      lockouttime=None):
    pwpolicy = {}
    if maxlife is not None:
        pwpolicy['krbmaxpwdlife'] = maxlife
    if minlife is not None:
        pwpolicy['krbminpwdlife'] = minlife
    if history is not None:
        pwpolicy['krbpwdhistorylength'] = history
    if minclasses is not None:
        pwpolicy['krbpwdmindiffchars'] = minclasses
    if minlength is not None:
        pwpolicy['krbpwdminlength'] = minlength
    if priority is not None:
        pwpolicy['cospriority'] = priority
    if maxfail is not None:
        pwpolicy['krbpwdmaxfailure'] = maxfail
    if failinterval is not None:
        pwpolicy['krbpwdfailurecountinterval'] = failinterval
    if lockouttime is not None:
        pwpolicy['krbpwdlockoutduration'] = lockouttime

    return pwpolicy


def get_pwpolicy_diff(client, ipa_pwpolicy, module_pwpolicy):
    return client.get_diff(ipa_data=ipa_pwpolicy, module_data=module_pwpolicy)


def ensure(module, client):
    state = module.params['state']
    name = module.params['cn']

    module_pwpolicy = get_pwpolicy_dict(maxlife=module.params.get('krbmaxpwdlife'),
                                        minlife=module.params.get('krbminpwdlife'),
                                        history=module.params.get('krbpwdhistorylength'),
                                        minclasses=module.params.get('krbpwdmindiffchars'),
                                        minlength=module.params.get('krbpwdminlength'),
                                        priority=module.params.get('cospriority'),
                                        maxfail=module.params.get('krbpwdmaxfailure'),
                                        failinterval=module.params.get('krbpwdfailurecountinterval'),
                                        lockouttime=module.params.get('krbpwdlockoutduration'))

    ipa_pwpolicy = client.pwpolicy_find(name=name)

    changed = False
    if state == 'present':
        if not ipa_pwpolicy:
            changed = True
            if not module.check_mode:
                ipa_pwpolicy = client.pwpolicy_add(name=name, item=module_pwpolicy)
        else:
            diff = get_pwpolicy_diff(client, ipa_pwpolicy, module_pwpolicy)
            if len(diff) > 0:
                changed = True
                if not module.check_mode:
                    ipa_pwpolicy = client.pwpolicy_mod(name=name, item=module_pwpolicy)
    else:
        if ipa_pwpolicy:
            changed = True
            if not module.check_mode:
                client.pwpolicy_del(name=name)

    return changed, ipa_pwpolicy


def main():
    argument_spec = ipa_argument_spec()
    argument_spec.update(cn=dict(type='str', aliases=['group', 'name']),
                         state=dict(type='str', default='present', choices=['present', 'absent']),
                         krbmaxpwdlife=dict(type='str', aliases=['maxlife']),
                         krbminpwdlife=dict(type='str', aliases=['minlife']),
                         krbpwdhistorylength=dict(type='str', aliases=['history']),
                         krbpwdmindiffchars=dict(type='str', aliases=['minclasses']),
                         krbpwdminlength=dict(type='str', aliases=['minlength']),
                         cospriority=dict(type='str', aliases=['priority']),
                         krbpwdmaxfailure=dict(type='str', aliases=['maxfail']),
                         krbpwdfailurecountinterval=dict(type='str', aliases=['failinterval']),
                         krbpwdlockoutduration=dict(type='str', aliases=['lockouttime']))

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    client = PwPolicyIPAClient(module=module,
                               host=module.params['ipa_host'],
                               port=module.params['ipa_port'],
                               protocol=module.params['ipa_prot'])

    try:
        client.login(username=module.params['ipa_user'],
                     password=module.params['ipa_pass'])
        changed, pwpolicy = ensure(module, client)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=traceback.format_exc())

    module.exit_json(changed=changed, pwpolicy=pwpolicy)


if __name__ == '__main__':
    main()
