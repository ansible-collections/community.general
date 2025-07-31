#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2019, Maciej Delmanowski <drybjed@gmail.com>
# Copyright (c) 2017, Alexander Korinek <noles@a3k.net>
# Copyright (c) 2016, Peter Sagerson <psagers@ignorare.net>
# Copyright (c) 2016, Jiri Tyr <jiri.tyr@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r"""
module: ldap_attrs
short_description: Add or remove multiple LDAP attribute values
description:
  - Add or remove multiple LDAP attribute values.
notes:
  - This only deals with attributes on existing entries. To add or remove whole entries, see M(community.general.ldap_entry).
  - For O(state=present) and O(state=absent), all value comparisons are performed on the server for maximum accuracy. For
    O(state=exact), values have to be compared in Python, which obviously ignores LDAP matching rules. This should work out
    in most cases, but it is theoretically possible to see spurious changes when target and actual values are semantically
    identical but lexically distinct.
version_added: '0.2.0'
author:
  - Jiri Tyr (@jtyr)
  - Alexander Korinek (@noles)
  - Maciej Delmanowski (@drybjed)
requirements:
  - python-ldap
attributes:
  check_mode:
    support: full
  diff_mode:
    support: full
    version_added: 8.5.0
options:
  state:
    required: false
    type: str
    choices: [present, absent, exact]
    default: present
    description:
      - The state of the attribute values. If V(present), all given attribute values are added if they are missing. If V(absent),
        all given attribute values are removed if present. If V(exact), the set of attribute values is forced to exactly those
        provided and no others. If O(state=exact) and the attribute value is empty, all values for this attribute are removed.
  attributes:
    required: true
    type: dict
    description:
      - The attribute(s) and value(s) to add or remove.
      - Each attribute value can be a string for single-valued attributes or a list of strings for multi-valued attributes.
      - If you specify values for this option in YAML, please note that you can improve readability for long string values
        by using YAML block modifiers as seen in the examples for this module.
      - Note that when using values that YAML/ansible-core interprets as other types, like V(yes), V(no) (booleans), or V(2.10)
        (float), make sure to quote them if these are meant to be strings. Otherwise the wrong values may be sent to LDAP.
  ordered:
    required: false
    type: bool
    default: false
    description:
      - If V(true), prepend list values with X-ORDERED index numbers in all attributes specified in the current task. This
        is useful mostly with C(olcAccess) attribute to easily manage LDAP Access Control Lists.
extends_documentation_fragment:
  - community.general.ldap.documentation
  - community.general.attributes
"""


EXAMPLES = r"""
- name: Configure directory number 1 for example.com
  community.general.ldap_attrs:
    dn: olcDatabase={1}hdb,cn=config
    attributes:
      olcSuffix: dc=example,dc=com
    state: exact

# The complex argument format is required here to pass a list of ACL strings.
- name: Set up the ACL
  community.general.ldap_attrs:
    dn: olcDatabase={1}hdb,cn=config
    attributes:
      olcAccess:
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

# An alternative approach with automatic X-ORDERED numbering
- name: Set up the ACL
  community.general.ldap_attrs:
    dn: olcDatabase={1}hdb,cn=config
    attributes:
      olcAccess:
        - >-
          to attrs=userPassword,shadowLastChange
          by self write
          by anonymous auth
          by dn="cn=admin,dc=example,dc=com" write
          by * none'
        - >-
          to dn.base="dc=example,dc=com"
          by dn="cn=admin,dc=example,dc=com" write
          by * read
    ordered: true
    state: exact

- name: Declare some indexes
  community.general.ldap_attrs:
    dn: olcDatabase={1}hdb,cn=config
    attributes:
      olcDbIndex:
        - objectClass eq
        - uid eq

- name: Set up a root user, which we can use later to bootstrap the directory
  community.general.ldap_attrs:
    dn: olcDatabase={1}hdb,cn=config
    attributes:
      olcRootDN: cn=root,dc=example,dc=com
      olcRootPW: "{SSHA}tabyipcHzhwESzRaGA7oQ/SDoBZQOGND"
    state: exact

- name: Remove an attribute with a specific value
  community.general.ldap_attrs:
    dn: uid=jdoe,ou=people,dc=example,dc=com
    attributes:
      description: "An example user account"
    state: absent
    server_uri: ldap://localhost/
    bind_dn: cn=admin,dc=example,dc=com
    bind_pw: password

- name: Remove specified attribute(s) from an entry
  community.general.ldap_attrs:
    dn: uid=jdoe,ou=people,dc=example,dc=com
    attributes:
      description: []
    state: exact
    server_uri: ldap://localhost/
    bind_dn: cn=admin,dc=example,dc=com
    bind_pw: password
"""


RETURN = r"""
modlist:
  description: List of modified parameters.
  returned: success
  type: list
  sample:
    - [2, "olcRootDN", ["cn=root,dc=example,dc=com"]]
"""

import traceback

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_native, to_bytes, to_text
from ansible_collections.community.general.plugins.module_utils.ldap import LdapGeneric, gen_specs, ldap_required_together

import re

LDAP_IMP_ERR = None
try:
    import ldap
    import ldap.filter

    HAS_LDAP = True
except ImportError:
    LDAP_IMP_ERR = traceback.format_exc()
    HAS_LDAP = False


class LdapAttrs(LdapGeneric):
    def __init__(self, module):
        LdapGeneric.__init__(self, module)

        # Shortcuts
        self.attrs = self.module.params['attributes']
        self.state = self.module.params['state']
        self.ordered = self.module.params['ordered']

    def _order_values(self, values):
        """ Prepend X-ORDERED index numbers to attribute's values. """
        ordered_values = []

        if isinstance(values, list):
            for index, value in enumerate(values):
                cleaned_value = re.sub(r'^\{\d+\}', '', value)
                ordered_values.append('{' + str(index) + '}' + cleaned_value)

        return ordered_values

    def _normalize_values(self, values):
        """ Normalize attribute's values. """
        norm_values = []

        if isinstance(values, list):
            if self.ordered:
                norm_values = list(map(to_bytes,
                                   self._order_values(list(map(str,
                                                               values)))))
            else:
                norm_values = list(map(to_bytes, values))
        else:
            norm_values = [to_bytes(str(values))]

        return norm_values

    def add(self):
        modlist = []
        new_attrs = {}
        for name, values in self.module.params['attributes'].items():
            norm_values = self._normalize_values(values)
            added_values = []
            for value in norm_values:
                if self._is_value_absent(name, value):
                    modlist.append((ldap.MOD_ADD, name, value))
                    added_values.append(value)
            if added_values:
                new_attrs[name] = norm_values
        return modlist, {}, new_attrs

    def delete(self):
        modlist = []
        old_attrs = {}
        new_attrs = {}
        for name, values in self.module.params['attributes'].items():
            norm_values = self._normalize_values(values)
            removed_values = []
            for value in norm_values:
                if self._is_value_present(name, value):
                    removed_values.append(value)
                    modlist.append((ldap.MOD_DELETE, name, value))
            if removed_values:
                old_attrs[name] = norm_values
                new_attrs[name] = [value for value in norm_values if value not in removed_values]
        return modlist, old_attrs, new_attrs

    def exact(self):
        modlist = []
        old_attrs = {}
        new_attrs = {}
        for name, values in self.module.params['attributes'].items():
            norm_values = self._normalize_values(values)
            try:
                results = self.connection.search_s(
                    self.dn, ldap.SCOPE_BASE, attrlist=[name])
            except ldap.LDAPError as e:
                self.fail("Cannot search for attribute %s" % name, e)

            current = results[0][1].get(name, [])

            if frozenset(norm_values) != frozenset(current):
                if len(current) == 0:
                    modlist.append((ldap.MOD_ADD, name, norm_values))
                elif len(norm_values) == 0:
                    modlist.append((ldap.MOD_DELETE, name, None))
                else:
                    modlist.append((ldap.MOD_REPLACE, name, norm_values))
                old_attrs[name] = current
                new_attrs[name] = norm_values
                if len(current) == 1 and len(norm_values) == 1:
                    old_attrs[name] = current[0]
                    new_attrs[name] = norm_values[0]

        return modlist, old_attrs, new_attrs

    def _is_value_present(self, name, value):
        """ True if the target attribute has the given value. """
        try:
            escaped_value = ldap.filter.escape_filter_chars(to_text(value))
            filterstr = "(%s=%s)" % (name, escaped_value)
            dns = self.connection.search_s(self.dn, ldap.SCOPE_BASE, filterstr)
            is_present = len(dns) == 1
        except ldap.NO_SUCH_OBJECT:
            is_present = False

        return is_present

    def _is_value_absent(self, name, value):
        """ True if the target attribute doesn't have the given value. """
        return not self._is_value_present(name, value)


def main():
    module = AnsibleModule(
        argument_spec=gen_specs(
            attributes=dict(type='dict', required=True),
            ordered=dict(type='bool', default=False),
            state=dict(type='str', default='present', choices=['absent', 'exact', 'present']),
        ),
        supports_check_mode=True,
        required_together=ldap_required_together(),
    )

    if not HAS_LDAP:
        module.fail_json(msg=missing_required_lib('python-ldap'),
                         exception=LDAP_IMP_ERR)

    # Instantiate the LdapAttr object
    ldap = LdapAttrs(module)
    old_attrs = None
    new_attrs = None

    state = module.params['state']

    # Perform action
    if state == 'present':
        modlist, old_attrs, new_attrs = ldap.add()
    elif state == 'absent':
        modlist, old_attrs, new_attrs = ldap.delete()
    elif state == 'exact':
        modlist, old_attrs, new_attrs = ldap.exact()

    changed = False

    if len(modlist) > 0:
        changed = True

        if not module.check_mode:
            try:
                ldap.connection.modify_s(ldap.dn, modlist)
            except Exception as e:
                module.fail_json(msg="Attribute action failed.", details=to_native(e))

    module.exit_json(changed=changed, modlist=modlist, diff={"before": old_attrs, "after": new_attrs})


if __name__ == '__main__':
    main()
