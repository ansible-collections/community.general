#!/usr/bin/python

# Copyright (c) 2016, Peter Sagerson <psagers@ignorare.net>
# Copyright (c) 2016, Jiri Tyr <jiri.tyr@gmail.com>
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: ldap_entry
short_description: Add or remove LDAP entries
description:
  - Add or remove LDAP entries. This module only asserts the existence or non-existence of an LDAP entry, not its attributes.
    To assert the attribute values of an entry, see M(community.general.ldap_attrs).
author:
  - Jiri Tyr (@jtyr)
requirements:
  - python-ldap
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  attributes:
    description:
      - If O(state=present), attributes necessary to create an entry. Existing entries are never modified. To assert specific
        attribute values on an existing entry, use M(community.general.ldap_attrs) module instead.
      - Each attribute value can be a string for single-valued attributes or a list of strings for multi-valued attributes.
      - If you specify values for this option in YAML, please note that you can improve readability for long string values
        by using YAML block modifiers as seen in the examples for this module.
      - Note that when using values that YAML/ansible-core interprets as other types, like V(yes), V(no) (booleans), or V(2.10)
        (float), make sure to quote them if these are meant to be strings. Otherwise the wrong values may be sent to LDAP.
      - If O(honor_binary=true), an attribute that includes the C(binary) option as per
        L(RFC 4522, https://www.rfc-editor.org/rfc/rfc4522.html#section-3) will be considered as binary. Its contents must be
        specified as Base64 and sent to the LDAP after decoding. If an attribute must be handled as binary without including
        the C(binary) option, it can be listed in O(binary_attributes).
        Support for binary values was added in community.general 12.5.0.
    type: dict
    default: {}
  binary_attributes:
    description:
      - If O(state=present), attributes whose values must be handled as raw sequences of bytes must be listed here.
      - The values provided for the attributes will be converted from Base64.
    type: list
    elements: str
    default: []
    version_added: 12.5.0
  honor_binary:
    description:
      - If O(state=present) and this option is V(true), attributes whose name include the V(binary) option
        will be treated as Base64-encoded byte sequences automatically, even if they are not listed in O(binary_attributes).
    type: bool
    default: false
    version_added: 12.5.0
  objectClass:
    description:
      - If O(state=present), value or list of values to use when creating the entry. It can either be a string or an actual
        list of strings.
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
      - If O(state=delete), a flag indicating whether a single entry or the whole branch must be deleted.
    type: bool
    default: false
    version_added: 4.6.0
extends_documentation_fragment:
  - community.general.ldap.documentation
  - community.general.attributes
"""


EXAMPLES = r"""
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
      - myPhotoObject
    binary_attributes:
      - myPhoto
    attributes:
      description: An LDAP administrator
      userPassword: "{SSHA}tabyipcHzhwESzRaGA7oQ/SDoBZQOGND"
      myPhoto: >-
        /9j/4AAQSkZJRgABAQAAAQABAAD/4gIcSUNDX1BST0ZJTEUAAQEAAAIMbGNt
        cwIQAABtbnRyUkdCIFhZWiAH3AABABkAAwApADlhY3NwQVBQTAAAAAAAAAAA
        # ...

- name: Make sure a CA certificate is present
  community.general.ldap_attrs:
    dn: cn=ISRG Root X1,ou=ca,ou=certificates,dc=example,dc=org
    honor_binary: true
    objectClass:
      - pkiCA
      - applicationProcess
    attributes:
      cn: ISRG Root X1
      cACertificate;binary: >-
        MIIFazCCA1OgAwIBAgIRAIIQz7DSQONZRGPgu2OCiwAwDQYJKoZIhvcNAQELBQAw
        TzELMAkGA1UEBhMCVVMxKTAnBgNVBAoTIEludGVybmV0IFNlY3VyaXR5IFJlc2Vh
        # ...

- name: Set possible values for attributes elements
  community.general.ldap_entry:
    dn: cn=admin,dc=example,dc=com
    objectClass:
      - simpleSecurityObject
      - organizationalRole
    attributes:
      description: An LDAP Administrator
      roleOccupant:
        - cn=Chocs Puddington,ou=Information Technology,dc=example,dc=com
        - cn=Alice Stronginthebrain,ou=Information Technology,dc=example,dc=com
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


RETURN = r"""
# Default return values
"""

import base64
import binascii
import traceback

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.community.general.plugins.module_utils.ldap import (
    LdapGeneric,
    gen_specs,
    ldap_required_together,
)

LDAP_IMP_ERR = None
try:
    import ldap.controls
    import ldap.modlist

    HAS_LDAP = True
except ImportError:
    LDAP_IMP_ERR = traceback.format_exc()
    HAS_LDAP = False


class LdapEntry(LdapGeneric):
    def __init__(self, module):
        LdapGeneric.__init__(self, module)

        # Shortcuts
        self.state = self.module.params["state"]
        self.recursive = self.module.params["recursive"]
        self.binary = set(attr.lower() for attr in self.module.params["binary_attributes"])
        self.honor_binary = self.module.params["honor_binary"]

        # Add the objectClass into the list of attributes
        self.module.params["attributes"]["objectClass"] = self.module.params["objectClass"]

        # Load attributes
        if self.state == "present":
            self.attrs, bad_attrs = self._load_attrs()
            if bad_attrs:
                s_bad_attrs = ", ".join(bad_attrs)
                self.module.fail_json(msg=f"Invalid Base64-encoded attribute values for {s_bad_attrs}")

    def _is_binary(self, attr_name):
        """Check if an attribute must be considered binary."""
        lc_name = attr_name.lower()
        return (self.honor_binary and "binary" in lc_name.split(";")) or lc_name in self.binary

    def _load_attrs(self):
        """Turn attribute's value to array. Attribute values are converted to
        raw bytes, either by encoding the string itself, or by decoding it from
        base 64, depending on the binary attributes settings."""
        attrs = {}
        bad_attrs = []

        for name, value in self.module.params["attributes"].items():
            if self._is_binary(name):
                converter = base64.b64decode
            else:
                converter = to_bytes
            if not isinstance(value, list):
                value = [value]
            try:
                attrs[name] = [converter(v) for v in value]
            except binascii.Error:
                bad_attrs.append(name)

        return attrs, bad_attrs

    def add(self):
        """If self.dn does not exist, returns a callable that will add it."""

        def _add():
            self.connection.add_s(self.dn, modlist)

        if not self._is_entry_present():
            modlist = ldap.modlist.addModlist(self.attrs)
            action = _add
        else:
            action = None

        return action

    def delete(self):
        """If self.dn exists, returns a callable that will delete either
        the item itself if the recursive option is not set or the whole branch
        if it is."""

        def _delete():
            self.connection.delete_s(self.dn)

        def _delete_recursive():
            """Attempt recursive deletion using the subtree-delete control.
            If that fails, do it manually."""
            try:
                subtree_delete = ldap.controls.ValueLessRequestControl("1.2.840.113556.1.4.805")
                self.connection.delete_ext_s(self.dn, serverctrls=[subtree_delete])
            except ldap.NOT_ALLOWED_ON_NONLEAF:
                search = self.connection.search_s(self.dn, ldap.SCOPE_SUBTREE, attrlist=("dn",))
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
            attributes=dict(default={}, type="dict"),
            binary_attributes=dict(default=[], type="list", elements="str"),
            honor_binary=dict(default=False, type="bool"),
            objectClass=dict(type="list", elements="str"),
            state=dict(default="present", choices=["present", "absent"]),
            recursive=dict(default=False, type="bool"),
        ),
        required_if=[("state", "present", ["objectClass"])],
        supports_check_mode=True,
        required_together=ldap_required_together(),
    )

    if not HAS_LDAP:
        module.fail_json(msg=missing_required_lib("python-ldap"), exception=LDAP_IMP_ERR)

    state = module.params["state"]

    # Instantiate the LdapEntry object
    ldap = LdapEntry(module)

    # Get the action function
    if state == "present":
        action = ldap.add()
    elif state == "absent":
        action = ldap.delete()

    # Perform the action
    if action is not None and not module.check_mode:
        try:
            action()
        except Exception as e:
            module.fail_json(msg="Entry action failed.", details=f"{e}", exception=traceback.format_exc())

    module.exit_json(changed=(action is not None))


if __name__ == "__main__":
    main()
