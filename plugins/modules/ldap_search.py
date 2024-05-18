#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Peter Sagerson <psagers@ignorare.net>
# Copyright (c) 2020, Sebastian Pfahl <eryx@gmx.net>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: ldap_search
version_added: '0.2.0'
short_description: Search for entries in a LDAP server
description:
  - Return the results of an LDAP search.
notes:
  - The default authentication settings will attempt to use a SASL EXTERNAL
    bind over a UNIX domain socket. This works well with the default Ubuntu
    install for example, which includes a C(cn=peercred,cn=external,cn=auth) ACL
    rule allowing root to modify the server configuration. If you need to use
    a simple bind to access your server, pass the credentials in O(bind_dn)
    and O(bind_pw).
author:
  - Sebastian Pfahl (@eryx12o45)
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
      - The LDAP DN to search in.
  scope:
    choices: [base, onelevel, subordinate, children]
    default: base
    type: str
    description:
      - The LDAP scope to use.
      - V(subordinate) requires the LDAPv3 subordinate feature extension.
      - V(children) is equivalent to a "subtree" scope.
  filter:
    default: '(objectClass=*)'
    type: str
    description:
      - Used for filtering the LDAP search result.
  attrs:
    type: list
    elements: str
    description:
      - A list of attributes for limiting the result. Use an
        actual list or a comma-separated string.
  schema:
    default: false
    type: bool
    description:
      - Set to V(true) to return the full attribute schema of entries, not
        their attribute values. Overrides O(attrs) when provided.
  page_size:
    default: 0
    type: int
    description:
      - The page size when performing a simple paged result search (RFC 2696).
        This setting can be tuned to reduce issues with timeouts and server limits.
      - Setting the page size to V(0) (default) disables paged searching.
    version_added: 7.1.0
  base64_attributes:
    description:
      - If provided, all attribute values returned that are listed in this option
        will be Base64 encoded.
      - If the special value V(*) appears in this list, all attributes will be
        Base64 encoded.
      - All other attribute values will be converted to UTF-8 strings. If they
        contain binary data, please note that invalid UTF-8 bytes will be omitted.
    type: list
    elements: str
    version_added: 7.0.0
extends_documentation_fragment:
  - community.general.ldap.documentation
  - community.general.attributes
"""

EXAMPLES = r"""
- name: Return all entries within the 'groups' organizational unit.
  community.general.ldap_search:
    dn: "ou=groups,dc=example,dc=com"
  register: ldap_groups

- name: Return GIDs for all groups
  community.general.ldap_search:
    dn: "ou=groups,dc=example,dc=com"
    scope: "onelevel"
    attrs:
      - "gidNumber"
  register: ldap_group_gids
"""

RESULTS = """
results:
  description:
    - For every entry found, one dictionary will be returned.
    - Every dictionary contains a key C(dn) with the entry's DN as a value.
    - Every attribute of the entry found is added to the dictionary. If the key
      has precisely one value, that value is taken directly, otherwise the key's
      value is a list.
    - Note that all values (for single-element lists) and list elements (for multi-valued
      lists) will be UTF-8 strings. Some might contain Base64-encoded binary data; which
      ones is determined by the O(base64_attributes) option.
  type: list
  elements: dict
"""

import base64
import traceback

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_bytes, to_native, to_text
from ansible.module_utils.six import binary_type, string_types, text_type
from ansible_collections.community.general.plugins.module_utils.ldap import LdapGeneric, gen_specs, ldap_required_together

LDAP_IMP_ERR = None
try:
    import ldap

    HAS_LDAP = True
except ImportError:
    LDAP_IMP_ERR = traceback.format_exc()
    HAS_LDAP = False


def main():
    module = AnsibleModule(
        argument_spec=gen_specs(
            dn=dict(type='str', required=True),
            scope=dict(type='str', default='base', choices=['base', 'onelevel', 'subordinate', 'children']),
            filter=dict(type='str', default='(objectClass=*)'),
            attrs=dict(type='list', elements='str'),
            schema=dict(type='bool', default=False),
            page_size=dict(type='int', default=0),
            base64_attributes=dict(type='list', elements='str'),
        ),
        supports_check_mode=True,
        required_together=ldap_required_together(),
    )

    if not HAS_LDAP:
        module.fail_json(msg=missing_required_lib('python-ldap'),
                         exception=LDAP_IMP_ERR)

    try:
        LdapSearch(module).main()
    except Exception as exception:
        module.fail_json(msg="Attribute action failed.", details=to_native(exception))


def _normalize_string(val, convert_to_base64):
    if isinstance(val, (string_types, binary_type)):
        if isinstance(val, text_type):
            val = to_bytes(val, encoding='utf-8')
        if convert_to_base64:
            val = to_text(base64.b64encode(val))
        else:
            # See https://github.com/ansible/ansible/issues/80258#issuecomment-1477038952 for details.
            # We want to make sure that all strings are properly UTF-8 encoded, even if they were not,
            # or happened to be byte strings.
            val = to_text(val, 'utf-8', errors='replace')
            # See also https://github.com/ansible-collections/community.general/issues/5704.
    return val


def _extract_entry(dn, attrs, base64_attributes):
    extracted = {'dn': dn}
    for attr, val in list(attrs.items()):
        convert_to_base64 = '*' in base64_attributes or attr in base64_attributes
        if len(val) == 1:
            extracted[attr] = _normalize_string(val[0], convert_to_base64)
        else:
            extracted[attr] = [_normalize_string(v, convert_to_base64) for v in val]
    return extracted


class LdapSearch(LdapGeneric):
    def __init__(self, module):
        LdapGeneric.__init__(self, module)

        self.filterstr = self.module.params['filter']
        self.attrlist = []
        self.page_size = self.module.params['page_size']
        self._load_scope()
        self._load_attrs()
        self._load_schema()
        self._base64_attributes = set(self.module.params['base64_attributes'] or [])

    def _load_schema(self):
        self.schema = self.module.params['schema']
        if self.schema:
            self.attrsonly = 1
        else:
            self.attrsonly = 0

    def _load_scope(self):
        spec = dict(
            base=ldap.SCOPE_BASE,
            onelevel=ldap.SCOPE_ONELEVEL,
            subordinate=ldap.SCOPE_SUBORDINATE,
            children=ldap.SCOPE_SUBTREE,
        )
        self.scope = spec[self.module.params['scope']]

    def _load_attrs(self):
        self.attrlist = self.module.params['attrs'] or None

    def main(self):
        results = self.perform_search()
        self.module.exit_json(changed=False, results=results)

    def perform_search(self):
        ldap_entries = []
        controls = []
        if self.page_size > 0:
            controls.append(ldap.controls.libldap.SimplePagedResultsControl(True, size=self.page_size, cookie=''))
        try:
            while True:
                response = self.connection.search_ext(
                    self.dn,
                    self.scope,
                    filterstr=self.filterstr,
                    attrlist=self.attrlist,
                    attrsonly=self.attrsonly,
                    serverctrls=controls,
                )
                rtype, results, rmsgid, serverctrls = self.connection.result3(response)
                for result in results:
                    if isinstance(result[1], dict):
                        if self.schema:
                            ldap_entries.append(dict(dn=result[0], attrs=list(result[1].keys())))
                        else:
                            ldap_entries.append(_extract_entry(result[0], result[1], self._base64_attributes))
                cookies = [c.cookie for c in serverctrls if c.controlType == ldap.controls.libldap.SimplePagedResultsControl.controlType]
                if self.page_size > 0 and cookies and cookies[0]:
                    controls[0].cookie = cookies[0]
                else:
                    return ldap_entries
        except ldap.NO_SUCH_OBJECT:
            self.module.fail_json(msg="Base not found: {0}".format(self.dn))


if __name__ == '__main__':
    main()
