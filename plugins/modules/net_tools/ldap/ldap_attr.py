#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2016, Peter Sagerson <psagers@ignorare.net>
# Copyright: (c) 2016, Jiri Tyr <jiri.tyr@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: ldap_attr
short_description: Add or remove LDAP attribute values
description:
  - Add or remove LDAP attribute values.
notes:
  - This only deals with attributes on existing entries. To add or remove
    whole entries, see M(community.general.ldap_entry).
  - The default authentication settings will attempt to use a SASL EXTERNAL
    bind over a UNIX domain socket. This works well with the default Ubuntu
    install for example, which includes a cn=peercred,cn=external,cn=auth ACL
    rule allowing root to modify the server configuration. If you need to use
    a simple bind to access your server, pass the credentials in I(bind_dn)
    and I(bind_pw).
  - For I(state=present) and I(state=absent), all value comparisons are
    performed on the server for maximum accuracy. For I(state=exact), values
    have to be compared in Python, which obviously ignores LDAP matching
    rules. This should work out in most cases, but it is theoretically
    possible to see spurious changes when target and actual values are
    semantically identical but lexically distinct.
  - "The I(params) parameter was removed due to circumventing Ansible's parameter
     handling.  The I(params) parameter started disallowing setting the I(bind_pw) parameter in
     Ansible-2.7 as it was insecure to set the parameter that way."
deprecated:
  removed_in: 3.0.0  # was Ansible 2.14
  why: 'The current "ldap_attr" module does not support LDAP attribute insertions or deletions with objectClass dependencies.'
  alternative: 'Use M(community.general.ldap_attrs) instead. Deprecated in community.general 0.2.0.'
author:
  - Jiri Tyr (@jtyr)
requirements:
  - python-ldap
options:
  name:
    description:
      - The name of the attribute to modify.
    type: str
    required: true
  state:
    description:
      - The state of the attribute values.
      - If C(present), all given values will be added if they're missing.
      - If C(absent), all given values will be removed if present.
      - If C(exact), the set of values will be forced to exactly those provided and no others.
      - If I(state=exact) and I(value) is an empty list, all values for this attribute will be removed.
    type: str
    choices: [ absent, exact, present ]
    default: present
  values:
    description:
      - The value(s) to add or remove. This can be a string or a list of
        strings. The complex argument format is required in order to pass
        a list of strings (see examples).
    type: raw
    required: true
extends_documentation_fragment:
- community.general.ldap.documentation

'''

EXAMPLES = r'''
- name: Configure directory number 1 for example.com
  community.general.ldap_attr:
    dn: olcDatabase={1}hdb,cn=config
    name: olcSuffix
    values: dc=example,dc=com
    state: exact

# The complex argument format is required here to pass a list of ACL strings.
- name: Set up the ACL
  community.general.ldap_attr:
    dn: olcDatabase={1}hdb,cn=config
    name: olcAccess
    values:
      - >-
        {0}to attrs=userPassword,shadowLastChange
        by self write
        by anonymous auth
        by dn="cn=admin,dc=example,dc=com" write
        by * none'
      - >-
        {1}to dn.base="dc=example,dc=com"
        by dn="cn=admin,dc=example,dc=com" write
        by * read
    state: exact

- name: Declare some indexes
  community.general.ldap_attr:
    dn: olcDatabase={1}hdb,cn=config
    name: olcDbIndex
    values: "{{ item }}"
  with_items:
    - objectClass eq
    - uid eq

- name: Set up a root user, which we can use later to bootstrap the directory
  community.general.ldap_attr:
    dn: olcDatabase={1}hdb,cn=config
    name: "{{ item.key }}"
    values: "{{ item.value }}"
    state: exact
  with_dict:
    olcRootDN: cn=root,dc=example,dc=com
    olcRootPW: "{SSHA}tabyipcHzhwESzRaGA7oQ/SDoBZQOGND"

- name: Get rid of an unneeded attribute
  community.general.ldap_attr:
    dn: uid=jdoe,ou=people,dc=example,dc=com
    name: shadowExpire
    values: []
    state: exact
    server_uri: ldap://localhost/
    bind_dn: cn=admin,dc=example,dc=com
    bind_pw: password

#
# The same as in the previous example but with the authentication details
# stored in the ldap_auth variable:
#
# ldap_auth:
#   server_uri: ldap://localhost/
#   bind_dn: cn=admin,dc=example,dc=com
#   bind_pw: password
#
# In the example below, 'args' is a task keyword, passed at the same level as the module
- name: Get rid of an unneeded attribute
  community.general.ldap_attr:
    dn: uid=jdoe,ou=people,dc=example,dc=com
    name: shadowExpire
    values: []
    state: exact
  args: "{{ ldap_auth }}"
'''

RETURN = r'''
modlist:
  description: list of modified parameters
  returned: success
  type: list
  sample: '[[2, "olcRootDN", ["cn=root,dc=example,dc=com"]]]'
'''

import traceback

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils._text import to_native, to_bytes
from ansible_collections.community.general.plugins.module_utils.ldap import LdapGeneric, gen_specs

LDAP_IMP_ERR = None
try:
    import ldap

    HAS_LDAP = True
except ImportError:
    LDAP_IMP_ERR = traceback.format_exc()
    HAS_LDAP = False


class LdapAttr(LdapGeneric):
    def __init__(self, module):
        LdapGeneric.__init__(self, module)

        # Shortcuts
        self.name = self.module.params['name']
        self.state = self.module.params['state']

        # Normalize values
        if isinstance(self.module.params['values'], list):
            self.values = list(map(to_bytes, self.module.params['values']))
        else:
            self.values = [to_bytes(self.module.params['values'])]

    def add(self):
        values_to_add = list(filter(self._is_value_absent, self.values))

        if len(values_to_add) > 0:
            modlist = [(ldap.MOD_ADD, self.name, values_to_add)]
        else:
            modlist = []

        return modlist

    def delete(self):
        values_to_delete = list(filter(self._is_value_present, self.values))

        if len(values_to_delete) > 0:
            modlist = [(ldap.MOD_DELETE, self.name, values_to_delete)]
        else:
            modlist = []

        return modlist

    def exact(self):
        try:
            results = self.connection.search_s(
                self.dn, ldap.SCOPE_BASE, attrlist=[self.name])
        except ldap.LDAPError as e:
            self.fail("Cannot search for attribute %s" % self.name, e)

        current = results[0][1].get(self.name, [])
        modlist = []

        if frozenset(self.values) != frozenset(current):
            if len(current) == 0:
                modlist = [(ldap.MOD_ADD, self.name, self.values)]
            elif len(self.values) == 0:
                modlist = [(ldap.MOD_DELETE, self.name, None)]
            else:
                modlist = [(ldap.MOD_REPLACE, self.name, self.values)]

        return modlist

    def _is_value_present(self, value):
        """ True if the target attribute has the given value. """
        try:
            is_present = bool(
                self.connection.compare_s(self.dn, self.name, value))
        except ldap.NO_SUCH_ATTRIBUTE:
            is_present = False

        return is_present

    def _is_value_absent(self, value):
        """ True if the target attribute doesn't have the given value. """
        return not self._is_value_present(value)


def main():
    module = AnsibleModule(
        argument_spec=gen_specs(
            name=dict(type='str', required=True),
            params=dict(type='dict'),
            state=dict(type='str', default='present', choices=['absent', 'exact', 'present']),
            values=dict(type='raw', required=True),
        ),
        supports_check_mode=True,
    )

    if not HAS_LDAP:
        module.fail_json(msg=missing_required_lib('python-ldap'),
                         exception=LDAP_IMP_ERR)

    if module.params['params']:
        module.fail_json(msg="The `params` option to ldap_attr was removed in since it circumvents Ansible's option handling")

    # Instantiate the LdapAttr object
    ldap = LdapAttr(module)

    state = module.params['state']

    # Perform action
    if state == 'present':
        modlist = ldap.add()
    elif state == 'absent':
        modlist = ldap.delete()
    elif state == 'exact':
        modlist = ldap.exact()

    changed = False

    if len(modlist) > 0:
        changed = True

        if not module.check_mode:
            try:
                ldap.connection.modify_s(ldap.dn, modlist)
            except Exception as e:
                module.fail_json(msg="Attribute action failed.", details=to_native(e))

    module.exit_json(changed=changed, modlist=modlist)


if __name__ == '__main__':
    main()
