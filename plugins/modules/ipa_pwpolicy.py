#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2020, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: ipa_pwpolicy
author: Adralioh (@adralioh)
short_description: Manage FreeIPA password policies
description:
  - Add, modify, or delete a password policy using the IPA API.
version_added: 2.0.0
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  group:
    description:
      - Name of the group that the policy applies to.
      - If omitted, the global policy is used.
    aliases: ["name"]
    type: str
  state:
    description: State to ensure.
    default: "present"
    choices: ["absent", "present"]
    type: str
  maxpwdlife:
    description: Maximum password lifetime (in days).
    type: str
  minpwdlife:
    description: Minimum password lifetime (in hours).
    type: str
  historylength:
    description:
      - Number of previous passwords that are remembered.
      - Users cannot reuse remembered passwords.
    type: str
  minclasses:
    description: Minimum number of character classes.
    type: str
  minlength:
    description: Minimum password length.
    type: str
  priority:
    description:
      - Priority of the policy.
      - High number means lower priority.
      - Required when C(cn) is not the global policy.
    type: str
  maxfailcount:
    description: Maximum number of consecutive failures before lockout.
    type: str
  failinterval:
    description: Period (in seconds) after which the number of failed login attempts is reset.
    type: str
  lockouttime:
    description: Period (in seconds) for which users are locked out.
    type: str
  gracelimit:
    description: Maximum number of LDAP logins after password expiration.
    type: int
    version_added: 8.2.0
  maxrepeat:
    description: Maximum number of allowed same consecutive characters in the new password.
    type: int
    version_added: 8.2.0
  maxsequence:
    description: Maximum length of monotonic character sequences in the new password. An example of a monotonic sequence of
      length 5 is V(12345).
    type: int
    version_added: 8.2.0
  dictcheck:
    description: Check whether the password (with possible modifications) matches a word in a dictionary (using cracklib).
    type: bool
    version_added: 8.2.0
  usercheck:
    description: Check whether the password (with possible modifications) contains the user name in some form (if the name
      has > 3 characters).
    type: bool
    version_added: 8.2.0
extends_documentation_fragment:
  - community.general.ipa.documentation
  - community.general.attributes
"""

EXAMPLES = r"""
- name: Modify the global password policy
  community.general.ipa_pwpolicy:
    maxpwdlife: '90'
    minpwdlife: '1'
    historylength: '8'
    minclasses: '3'
    minlength: '16'
    maxfailcount: '6'
    failinterval: '60'
    lockouttime: '600'
    ipa_host: ipa.example.com
    ipa_user: admin
    ipa_pass: topsecret

- name: Ensure the password policy for the group admins is present
  community.general.ipa_pwpolicy:
    group: admins
    state: present
    maxpwdlife: '60'
    minpwdlife: '24'
    historylength: '16'
    minclasses: '4'
    priority: '10'
    minlength: '6'
    maxfailcount: '4'
    failinterval: '600'
    lockouttime: '1200'
    gracelimit: 3
    maxrepeat: 3
    maxsequence: 3
    dictcheck: true
    usercheck: true
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
"""

RETURN = r"""
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
"""

import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.ipa import IPAClient, ipa_argument_spec
from ansible.module_utils.common.text.converters import to_native


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


def get_pwpolicy_dict(maxpwdlife=None, minpwdlife=None, historylength=None, minclasses=None,
                      minlength=None, priority=None, maxfailcount=None, failinterval=None,
                      lockouttime=None, gracelimit=None, maxrepeat=None, maxsequence=None, dictcheck=None, usercheck=None):
    pwpolicy = {}
    pwpolicy_options = {
        'krbmaxpwdlife': maxpwdlife,
        'krbminpwdlife': minpwdlife,
        'krbpwdhistorylength': historylength,
        'krbpwdmindiffchars': minclasses,
        'krbpwdminlength': minlength,
        'cospriority': priority,
        'krbpwdmaxfailure': maxfailcount,
        'krbpwdfailurecountinterval': failinterval,
        'krbpwdlockoutduration': lockouttime,
        'passwordgracelimit': gracelimit,
        'ipapwdmaxrepeat': maxrepeat,
        'ipapwdmaxsequence': maxsequence,
    }

    pwpolicy_boolean_options = {
        'ipapwddictcheck': dictcheck,
        'ipapwdusercheck': usercheck,
    }

    for option, value in pwpolicy_options.items():
        if value is not None:
            pwpolicy[option] = to_native(value)

    for option, value in pwpolicy_boolean_options.items():
        if value is not None:
            pwpolicy[option] = bool(value)

    return pwpolicy


def get_pwpolicy_diff(client, ipa_pwpolicy, module_pwpolicy):
    return client.get_diff(ipa_data=ipa_pwpolicy, module_data=module_pwpolicy)


def ensure(module, client):
    state = module.params['state']
    name = module.params['group']

    module_pwpolicy = get_pwpolicy_dict(maxpwdlife=module.params.get('maxpwdlife'),
                                        minpwdlife=module.params.get('minpwdlife'),
                                        historylength=module.params.get('historylength'),
                                        minclasses=module.params.get('minclasses'),
                                        minlength=module.params.get('minlength'),
                                        priority=module.params.get('priority'),
                                        maxfailcount=module.params.get('maxfailcount'),
                                        failinterval=module.params.get('failinterval'),
                                        lockouttime=module.params.get('lockouttime'),
                                        gracelimit=module.params.get('gracelimit'),
                                        maxrepeat=module.params.get('maxrepeat'),
                                        maxsequence=module.params.get('maxsequence'),
                                        dictcheck=module.params.get('dictcheck'),
                                        usercheck=module.params.get('usercheck'),
                                        )

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
    argument_spec.update(group=dict(type='str', aliases=['name']),
                         state=dict(type='str', default='present', choices=['present', 'absent']),
                         maxpwdlife=dict(type='str'),
                         minpwdlife=dict(type='str'),
                         historylength=dict(type='str'),
                         minclasses=dict(type='str'),
                         minlength=dict(type='str'),
                         priority=dict(type='str'),
                         maxfailcount=dict(type='str'),
                         failinterval=dict(type='str'),
                         lockouttime=dict(type='str'),
                         gracelimit=dict(type='int'),
                         maxrepeat=dict(type='int'),
                         maxsequence=dict(type='int'),
                         dictcheck=dict(type='bool'),
                         usercheck=dict(type='bool'),
                         )

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
