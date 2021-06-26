#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2016, Peter Sagerson <psagers@ignorare.net>
# Copyright: (c) 2020, Sebastian Pfahl <eryx@gmx.net>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

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
    a simple bind to access your server, pass the credentials in I(bind_dn)
    and I(bind_pw).
author:
  - Sebastian Pfahl (@eryx12o45)
requirements:
  - python-ldap
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
      - Set to C(true) to return the full attribute schema of entries, not
        their attribute values. Overrides I(attrs) when provided.
extends_documentation_fragment:
    - community.general.ldap.documentation
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

import traceback

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_native
from ansible_collections.community.general.plugins.module_utils.ldap import LdapGeneric, gen_specs

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
        ),
        supports_check_mode=True,
    )

    if not HAS_LDAP:
        module.fail_json(msg=missing_required_lib('python-ldap'),
                         exception=LDAP_IMP_ERR)

    if not module.check_mode:
        try:
            LdapSearch(module).main()
        except Exception as exception:
            module.fail_json(msg="Attribute action failed.", details=to_native(exception))

    module.exit_json(changed=False)


def _extract_entry(dn, attrs):
    extracted = {'dn': dn}
    for attr, val in list(attrs.items()):
        if len(val) == 1:
            extracted[attr] = val[0]
        else:
            extracted[attr] = val
    return extracted


class LdapSearch(LdapGeneric):
    def __init__(self, module):
        LdapGeneric.__init__(self, module)

        self.dn = self.module.params['dn']
        self.filterstr = self.module.params['filter']
        self.attrlist = []
        self._load_scope()
        self._load_attrs()
        self._load_schema()

    def _load_schema(self):
        self.schema = self.module.boolean(self.module.params['schema'])
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
        try:
            results = self.connection.search_s(
                self.dn,
                self.scope,
                filterstr=self.filterstr,
                attrlist=self.attrlist,
                attrsonly=self.attrsonly
            )
            ldap_entries = []
            for result in results:
                if isinstance(result[1], dict):
                    if self.schema:
                        ldap_entries.append(dict(dn=result[0], attrs=list(result[1].keys())))
                    else:
                        ldap_entries.append(_extract_entry(result[0], result[1]))
            return ldap_entries
        except ldap.NO_SUCH_OBJECT:
            self.module.fail_json(msg="Base not found: {0}".format(self.dn))


if __name__ == '__main__':
    main()
