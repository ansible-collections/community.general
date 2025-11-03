#!/usr/bin/python

# Copyright (c) 2017-2018, Keller Fuchs <kellerfuchs@hashbang.sh>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
module: ldap_passwd
short_description: Set passwords in LDAP
description:
  - Set a password for an LDAP entry. This module only asserts that a given password is valid for a given entry. To assert
    the existence of an entry, see M(community.general.ldap_entry).
author:
  - Keller Fuchs (@KellerFuchs)
requirements:
  - python-ldap
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  passwd:
    description:
      - The (plaintext) password to be set for O(dn).
    type: str
extends_documentation_fragment:
  - community.general.ldap.documentation
  - community.general.attributes
"""

EXAMPLES = r"""
- name: Set a password for the admin user
  community.general.ldap_passwd:
    dn: cn=admin,dc=example,dc=com
    passwd: "{{ vault_secret }}"

- name: Setting passwords in bulk
  community.general.ldap_passwd:
    dn: "{{ item.key }}"
    passwd: "{{ item.value }}"
  with_dict:
    alice: alice123123
    bob: "|30b!"
    admin: "{{ vault_secret }}"
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
from ansible_collections.community.general.plugins.module_utils.ldap import (
    LdapGeneric,
    gen_specs,
    ldap_required_together,
)

LDAP_IMP_ERR = None
try:
    import ldap

    HAS_LDAP = True
except ImportError:
    LDAP_IMP_ERR = traceback.format_exc()
    HAS_LDAP = False


class LdapPasswd(LdapGeneric):
    def __init__(self, module):
        LdapGeneric.__init__(self, module)

        # Shortcuts
        self.passwd = self.module.params["passwd"]

    def passwd_check(self):
        try:
            tmp_con = ldap.initialize(self.server_uri)
        except ldap.LDAPError as e:
            self.fail("Cannot initialize LDAP connection", e)

        if self.start_tls:
            try:
                tmp_con.start_tls_s()
            except ldap.LDAPError as e:
                self.fail("Cannot start TLS.", e)

        try:
            tmp_con.simple_bind_s(self.dn, self.passwd)
        except ldap.INVALID_CREDENTIALS:
            return True
        except ldap.LDAPError as e:
            self.fail("Cannot bind to the server.", e)
        else:
            return False
        finally:
            tmp_con.unbind()

    def passwd_set(self):
        # Exit early if the password is already valid
        if not self.passwd_check():
            return False

        # Change the password (or throw an exception)
        try:
            self.connection.passwd_s(self.dn, None, self.passwd)
        except ldap.LDAPError as e:
            self.fail("Unable to set password", e)

        # Password successfully changed
        return True


def main():
    module = AnsibleModule(
        argument_spec=gen_specs(passwd=dict(no_log=True)),
        supports_check_mode=True,
        required_together=ldap_required_together(),
    )

    if not HAS_LDAP:
        module.fail_json(msg=missing_required_lib("python-ldap"), exception=LDAP_IMP_ERR)

    ldap = LdapPasswd(module)

    if module.check_mode:
        module.exit_json(changed=ldap.passwd_check())

    module.exit_json(changed=ldap.passwd_set())


if __name__ == "__main__":
    main()
