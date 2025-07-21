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


DOCUMENTATION = r"""
module: ldap_inc
short_description: Use the Modify-Increment LDAP V3 feature to increment an attribute value
version_added: 10.2.0
description:
  - Atomically increments the value of an attribute and return its new value.
notes:
  - When implemented by the directory server, the module uses the ModifyIncrement extension defined in L(RFC4525, https://www.rfc-editor.org/rfc/rfc4525.html)
    and the control PostRead. This extension and the control are implemented in OpenLdap but not all directory servers implement
    them. In this case, the module automatically uses a more classic method based on two phases, first the current value is
    read then the modify operation remove the old value and add the new one in a single request. If the value has changed
    by a concurrent call then the remove action fails. Then the sequence is retried 3 times before raising an error to the
    playbook. In an heavy modification environment, the module does not guarante to be systematically successful.
  - This only deals with integer attribute of an existing entry. To modify attributes of an entry, see M(community.general.ldap_attrs)
    or to add or remove whole entries, see M(community.general.ldap_entry).
author:
  - Philippe Duveau (@pduveau)
requirements:
  - python-ldap
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  dn:
    required: true
    type: str
    description:
      - The DN entry containing the attribute to increment.
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
  method:
    required: false
    type: str
    default: auto
    choices: [auto, rfc4525, legacy]
    description:
      - If V(auto), the module determines automatically the method to use.
      - If V(rfc4525) or V(legacy) force to use the corresponding method.
extends_documentation_fragment:
  - community.general.ldap.documentation
  - community.general.attributes
"""


EXAMPLES = r"""
- name: Increments uidNumber 1 Number for example.com
  community.general.ldap_inc:
    dn: "cn=uidNext,ou=unix-management,dc=example,dc=com"
    attribute: "uidNumber"
    increment: "1"
  register: ldap_uidNumber_sequence

- name: Modifies the user to define its identification number (uidNumber) when incrementation is successful
  community.general.ldap_attrs:
    dn: "cn=john,ou=posix-users,dc=example,dc=com"
    state: present
    attributes:
      - uidNumber: "{{ ldap_uidNumber_sequence.value }}"
  when: ldap_uidNumber_sequence.incremented
"""


RETURN = r"""
incremented:
  description:
    - It is set to V(true) if the attribute value has changed.
  returned: success
  type: bool
  sample: true

attribute:
  description:
    - The name of the attribute that was incremented.
  returned: success
  type: str
  sample: uidNumber

value:
  description:
    - The new value after incrementing.
  returned: success
  type: str
  sample: "2"

rfc4525:
  description:
    - Is V(true) if the method used to increment is based on RFC4525, V(false) if legacy.
  returned: success
  type: bool
  sample: true
"""

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_native, to_bytes
from ansible_collections.community.general.plugins.module_utils import deps
from ansible_collections.community.general.plugins.module_utils.ldap import LdapGeneric, gen_specs, ldap_required_together

with deps.declare("ldap", reason=missing_required_lib('python-ldap')):
    import ldap
    import ldap.controls.readentry


class LdapInc(LdapGeneric):
    def __init__(self, module):
        LdapGeneric.__init__(self, module)
        # Shortcuts
        self.attr = self.module.params['attribute']
        self.increment = self.module.params['increment']
        self.method = self.module.params['method']

    def inc_rfc4525(self):
        return [(ldap.MOD_INCREMENT, self.attr, [to_bytes(str(self.increment))])]

    def inc_legacy(self, curr_val, new_val):
        return [(ldap.MOD_DELETE, self.attr, [to_bytes(curr_val)]),
                (ldap.MOD_ADD, self.attr, [to_bytes(new_val)])]

    def serverControls(self):
        return [ldap.controls.readentry.PostReadControl(attrList=[self.attr])]

    LDAP_MOD_INCREMENT = to_bytes("1.3.6.1.1.14")


def main():
    module = AnsibleModule(
        argument_spec=gen_specs(
            attribute=dict(type='str', required=True),
            increment=dict(type='int', default=1, required=False),
            method=dict(type='str', default='auto', choices=['auto', 'rfc4525', 'legacy']),
        ),
        supports_check_mode=True,
        required_together=ldap_required_together(),
    )

    deps.validate(module)

    # Instantiate the LdapAttr object
    mod = LdapInc(module)

    changed = False
    ret = ""
    rfc4525 = False

    try:
        if mod.increment != 0 and not module.check_mode:
            changed = True

            if mod.method != "auto":
                rfc4525 = mod.method == "rfc425"
            else:
                rootDSE = mod.connection.search_ext_s(
                    base="",
                    scope=ldap.SCOPE_BASE,
                    attrlist=["*", "+"])
                if len(rootDSE) == 1:
                    if to_bytes(ldap.CONTROL_POST_READ) in rootDSE[0][1]["supportedControl"] and (
                        mod.LDAP_MOD_INCREMENT in rootDSE[0][1]["supportedFeatures"] or
                        mod.LDAP_MOD_INCREMENT in rootDSE[0][1]["supportedExtension"]
                    ):
                        rfc4525 = True

            if rfc4525:
                dummy, dummy, dummy, resp_ctrls = mod.connection.modify_ext_s(
                    dn=mod.dn,
                    modlist=mod.inc_rfc4525(),
                    serverctrls=mod.serverControls(),
                    clientctrls=None)
                if len(resp_ctrls) == 1:
                    ret = resp_ctrls[0].entry[mod.attr][0]

            else:
                tries = 0
                max_tries = 3
                while tries < max_tries:
                    tries = tries + 1
                    result = mod.connection.search_ext_s(
                        base=mod.dn,
                        scope=ldap.SCOPE_BASE,
                        filterstr="(%s=*)" % mod.attr,
                        attrlist=[mod.attr])
                    if len(result) != 1:
                        module.fail_json(msg="The entry does not exist or does not contain the specified attribute.")
                        return
                    try:
                        ret = str(int(result[0][1][mod.attr][0]) + mod.increment)
                        # if the current value first arg in inc_legacy has changed then the modify will fail
                        mod.connection.modify_s(
                            dn=mod.dn,
                            modlist=mod.inc_legacy(result[0][1][mod.attr][0], ret))
                        break
                    except ldap.NO_SUCH_ATTRIBUTE:
                        if tries == max_tries:
                            module.fail_json(msg="The increment could not be applied after " + str(max_tries) + " tries.")
                            return

        else:
            result = mod.connection.search_ext_s(
                base=mod.dn,
                scope=ldap.SCOPE_BASE,
                filterstr="(%s=*)" % mod.attr,
                attrlist=[mod.attr])
            if len(result) == 1:
                ret = str(int(result[0][1][mod.attr][0]) + mod.increment)
                changed = mod.increment != 0
            else:
                module.fail_json(msg="The entry does not exist or does not contain the specified attribute.")

    except Exception as e:
        module.fail_json(msg="Attribute action failed.", details=to_native(e))

    module.exit_json(changed=changed, incremented=changed, attribute=mod.attr, value=ret, rfc4525=rfc4525)


if __name__ == '__main__':
    main()
