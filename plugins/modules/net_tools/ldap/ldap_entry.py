#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2016, Peter Sagerson <psagers@ignorare.net>
# Copyright: (c) 2016, Jiri Tyr <jiri.tyr@gmail.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: ldap_entry
short_description: Add or remove LDAP entries.
description:
  - Add or remove LDAP entries. This module only asserts the existence or
    non-existence of an LDAP entry, not its attributes. To assert the
    attribute values of an entry, see M(community.general.ldap_attrs).
notes:
  - The default authentication settings will attempt to use a SASL EXTERNAL
    bind over a UNIX domain socket. This works well with the default Ubuntu
    install for example, which includes a cn=peercred,cn=external,cn=auth ACL
    rule allowing root to modify the server configuration. If you need to use
    a simple bind to access your server, pass the credentials in I(bind_dn)
    and I(bind_pw).
author:
  - Jiri Tyr (@jtyr)
requirements:
  - python-ldap
options:
  attributes:
    description:
      - If I(state=present), attributes necessary to create an entry. Existing
        entries are never modified. To assert specific attribute values on an
        existing entry, use M(community.general.ldap_attrs) module instead.
    type: dict
  objectClass:
    description:
      - If I(state=present), value or list of values to use when creating
        the entry. It can either be a string or an actual list of
        strings.
    type: list
    elements: str
  state:
    description:
      - The target state of the entry.
    choices: [present, absent]
    default: present
    type: str
  recursive:
    description:
      - If I(state=delete), a flag indicating whether a single entry or the
        whole branch must be deleted.
    type: bool
    default: false
    version_added: 4.6.0
extends_documentation_fragment:
- community.general.ldap.documentation

'''


EXAMPLES = """
- name: Make sure we have a parent entry for users
  community.general.ldap_entry:
    dn: ou=users,dc=example,dc=com
    objectClass: organizationalUnit

- name: Make sure we have an admin user
  community.general.ldap_entry:
    dn: cn=admin,dc=example,dc=com
    objectClass:
      - simpleSecurityObject
      - organizationalRole
    attributes:
      description: An LDAP administrator
      userPassword: "{SSHA}tabyipcHzhwESzRaGA7oQ/SDoBZQOGND"

- name: Get rid of an old entry
  community.general.ldap_entry:
    dn: ou=stuff,dc=example,dc=com
    state: absent
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
- name: Get rid of an old entry
  community.general.ldap_entry:
    dn: ou=stuff,dc=example,dc=com
    state: absent
  args: "{{ ldap_auth }}"
"""


RETURN = """
# Default return values
"""

import traceback

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_native, to_bytes
from ansible_collections.community.general.plugins.module_utils.ldap import LdapGeneric, gen_specs

LDAP_IMP_ERR = None
try:
    import ldap.modlist
    import ldap.controls

    HAS_LDAP = True
except ImportError:
    LDAP_IMP_ERR = traceback.format_exc()
    HAS_LDAP = False


class LdapEntry(LdapGeneric):
    def __init__(self, module):
        LdapGeneric.__init__(self, module)

        # Shortcuts
        self.state = self.module.params['state']
        self.recursive = self.module.params['recursive']

        # Add the objectClass into the list of attributes
        self.module.params['attributes']['objectClass'] = (
            self.module.params['objectClass'])

        # Load attributes
        if self.state == 'present':
            self.attrs = self._load_attrs()

    def _load_attrs(self):
        """ Turn attribute's value to array. """
        attrs = {}

        for name, value in self.module.params['attributes'].items():
            if isinstance(value, list):
                attrs[name] = list(map(to_bytes, value))
            else:
                attrs[name] = [to_bytes(value)]

        return attrs

    def add(self):
        """ If self.dn does not exist, returns a callable that will add it. """
        def _add():
            self.connection.add_s(self.dn, modlist)

        if not self._is_entry_present():
            modlist = ldap.modlist.addModlist(self.attrs)
            action = _add
        else:
            action = None

        return action

    def delete(self):
        """ If self.dn exists, returns a callable that will delete either
        the item itself if the recursive option is not set or the whole branch
        if it is. """
        def _delete():
            self.connection.delete_s(self.dn)

        def _delete_recursive():
            """ Attempt recurive deletion using the subtree-delete control.
            If that fails, do it manually. """
            try:
                subtree_delete = ldap.controls.ValueLessRequestControl('1.2.840.113556.1.4.805')
                self.connection.delete_ext_s(self.dn, serverctrls=[subtree_delete])
            except ldap.NOT_ALLOWED_ON_NONLEAF:
                search = self.connection.search_s(self.dn, ldap.SCOPE_SUBTREE, attrlist=('dn',))
                search.reverse()
                for entry in search:
                    self.connection.delete_s(entry[0])

        if self._is_entry_present():
            if self.recursive:
                action = _delete_recursive
            else:
                action = _delete
        else:
            action = None

        return action

    def _is_entry_present(self):
        try:
            self.connection.search_s(self.dn, ldap.SCOPE_BASE)
        except ldap.NO_SUCH_OBJECT:
            is_present = False
        else:
            is_present = True

        return is_present


def main():
    module = AnsibleModule(
        argument_spec=gen_specs(
            attributes=dict(default={}, type='dict'),
            objectClass=dict(type='list', elements='str'),
            state=dict(default='present', choices=['present', 'absent']),
            recursive=dict(default=False, type='bool'),
        ),
        required_if=[('state', 'present', ['objectClass'])],
        supports_check_mode=True,
    )

    if not HAS_LDAP:
        module.fail_json(msg=missing_required_lib('python-ldap'),
                         exception=LDAP_IMP_ERR)

    state = module.params['state']

    # Instantiate the LdapEntry object
    ldap = LdapEntry(module)

    # Get the action function
    if state == 'present':
        action = ldap.add()
    elif state == 'absent':
        action = ldap.delete()

    # Perform the action
    if action is not None and not module.check_mode:
        try:
            action()
        except Exception as e:
            module.fail_json(msg="Entry action failed.", details=to_native(e), exception=traceback.format_exc())

    module.exit_json(changed=(action is not None))


if __name__ == '__main__':
    main()
