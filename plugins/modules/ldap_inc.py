#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2024, Philippe Duveau <pduvax@gmail.com>
# Copyright (c) 2019, Maciej Delmanowski <drybjed@gmail.com> (ldap_attrs.py)
# Copyright (c) 2017, Alexander Korinek <noles@a3k.net> (ldap_attrs.py)
# Copyright (c) 2016, Peter Sagerson <psagers@ignorare.net> (ldap_attrs.py)
# Copyright (c) 2016, Jiri Tyr <jiri.tyr@gmail.com> (ldap_attrs.py)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# The code of this module is derived from that of ldap_attrs.py

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: ldap_inc
short_description: Use the Modify-Increment ldap V3 feature to increment an attribute value
description:
  - Atomically increments the value of an attribute and return its new value.
notes:
  - This only deals with integer attribute of an existing entry. To modify attributes
    of an entry, see M(community.general.ldap_attrs) or to add or remove whole entries,
    see M(community.general.ldap_entry).
  - The default authentication settings will attempt to use a SASL EXTERNAL
    bind over a UNIX domain socket. If you need to use a simple bind to access
    your server, pass the credentials in O(bind_dn) and O(bind_pw).
author:
  - Philippe Duveau (@pduveau)
requirements:
  - python-ldap
attributes:
  check_mode:
    support: full
  diff_mode:
    support: full
options:
  attribute:
    required: true
    type: str
    description:
      - The attribute to increment.
  increment:
    required: false
    type: int
    default: 1
    description:
      - The value of the increment to apply.
extends_documentation_fragment:
  - community.general.ldap.documentation
  - community.general.attributes

'''


EXAMPLES = r'''
- name: Increments uidNumber 1 Number for example.com
  community.general.ldap_inc:
    dn: "cn=uidNext,ou=unix-management,dc=example,dc=com"
    attribute: "uidNumber"
    increment: "1"
  register: ldap_uidNumber_sequence

- name: Modifies the user to define its identification number (uidNumber) when incrementation is successful.
  community.general.ldap_attrs:
    dn: "cn=john,ou=posix-users,dc=example,dc=com"
    state: present
    attributes:
      - uidNumber: "{{ ldap_uidNumber_sequence.value }}"
  when: ldap_uidNumber_sequence.incremented
'''


RETURN = r'''
result:
  description:
    - attribute received the attributeType changed
    - value receive the new value of the attribute in the specificied object
  returned: success
  type: int
  sample:
    - incremented: true
    - attribute: "uidNumber"
    - value: "2"
'''

import traceback

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_native, to_bytes
from ansible_collections.community.general.plugins.module_utils.ldap import LdapGeneric, gen_specs, ldap_required_together

LDAP_IMP_ERR = None
try:
    import ldap

    HAS_LDAP = True
except ImportError:
    LDAP_IMP_ERR = traceback.format_exc()
    HAS_LDAP = False


class LdapInc(LdapGeneric):
    def __init__(self, module):
        LdapGeneric.__init__(self, module)
        # Shortcuts
        self.attr = self.module.params['attribute']
        self.increment = self.module.params['increment']

    def inc(self):
        return [(ldap.MOD_INCREMENT, self.attr, [to_bytes(str(self.increment))])]

    def serverControls(self):
        return [ldap.controls.readentry.PostReadControl(attrList=[self.attr])]


def main():
    module = AnsibleModule(
        argument_spec=gen_specs(
            attribute=dict(type='str', required=True),
            increment=dict(type='int', default=1, required=False),
        ),
        supports_check_mode=True,
        required_together=ldap_required_together(),
    )

    if not HAS_LDAP:
        module.fail_json(msg=missing_required_lib('python-ldap'),
                         exception=LDAP_IMP_ERR)

    # Instantiate the LdapAttr object
    mod = LdapInc(module)

    changed = False
    ret = ""

    try:
        if mod.increment != 0:
            changed = True

            if not module.check_mode:
                i0, i1, i2, resp_ctrls = mod.connection.modify_ext_s(
                    dn=mod.dn,
                    modlist=mod.inc(),
                    serverctrls=mod.serverControls(),
                    clientctrls=None)
                if len(resp_ctrls) == 1:
                    ret = resp_ctrls[0].entry[mod.attr][0]
        else:
            if not module.check_mode:
                result = mod.connection.search_ext_s(
                    base=mod.dn,
                    scope=ldap.SCOPE_BASE,
                    filterstr="(%s=*)" % mod.attr,
                    attrlist=[mod.attr])
                if len(result) == 1:
                    ret = result[0][1][mod.attr][0]

    except Exception as e:
        module.fail_json(msg="Attribute action failed.", details=to_native(e))

    module.exit_json(changed=changed, incremented=changed, attribute=mod.attr, value=ret)


if __name__ == '__main__':
    main()
