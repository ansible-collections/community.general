#!/usr/bin/python

# Copyright (c) 2019, Maciej Delmanowski <drybjed@gmail.com>
# Copyright (c) 2017, Alexander Korinek <noles@a3k.net>
# Copyright (c) 2016, Peter Sagerson <psagers@ignorare.net>
# Copyright (c) 2016, Jiri Tyr <jiri.tyr@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: ldap_attrs
short_description: Add or remove multiple LDAP attribute values
description:
  - Add or remove multiple LDAP attribute values.
notes:
  - This only deals with attributes on existing entries. To add or remove whole entries, see M(community.general.ldap_entry).
  - If O(honor_binary=true), an attribute that includes the C(binary) option as per
    L(RFC 4522, https://www.rfc-editor.org/rfc/rfc4522.html#section-3) will be considered as binary.  Its contents must be
    specified as Base64 and sent to the LDAP after decoding. If an attribute must be handled as binary without including
    the C(binary) option, it can be listed in O(binary_attributes).
  - For O(state=present) and O(state=absent), when handling text attributes, all value comparisons are performed on the
    server for maximum accuracy. For O(state=exact) or binary attributes, values have to be compared in Python, which
    obviously ignores LDAP matching rules. This should work out in most cases, but it is theoretically possible to see
    spurious changes when target and actual values are semantically identical but lexically distinct.
  - Support for binary values was added in community.general 12.5.0.
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
    type: str
    choices: [present, absent, exact]
    default: present
    description:
      - The state of the attribute values. If V(present), all given attribute values are added if they are missing. If V(absent),
        all given attribute values are removed if present. If V(exact), the set of attribute values is forced to exactly those
        provided and no others. If O(state=exact) and the attribute value is empty, all values for this attribute are removed.
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

- name: Replace a CA certificate
  community.general.ldap_attrs:
    dn: cn=ISRG Root X1,ou=ca,ou=certificates,dc=example,dc=org
    honor_binary: true
    state: exact
    attributes:
      cACertificate;binary: >-
        MIIFazCCA1OgAwIBAgIRAIIQz7DSQONZRGPgu2OCiwAwDQYJKoZIhvcNAQELBQAw
        TzELMAkGA1UEBhMCVVMxKTAnBgNVBAoTIEludGVybmV0IFNlY3VyaXR5IFJlc2Vh
        # ...

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

import base64
import binascii
import re
import traceback

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_bytes, to_text

from ansible_collections.community.general.plugins.module_utils.ldap import (
    LdapGeneric,
    gen_specs,
    ldap_required_together,
)

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
        self.attrs = self.module.params["attributes"]
        self.state = self.module.params["state"]
        self.ordered = self.module.params["ordered"]
        self.binary = set(attr.lower() for attr in self.module.params["binary_attributes"])
        self.honor_binary = self.module.params["honor_binary"]

        # Cached attribute values
        self._cached_values = {}

    def _order_values(self, values):
        """Prepend X-ORDERED index numbers to attribute's values."""
        ordered_values = []

        if isinstance(values, list):
            for index, value in enumerate(values):
                cleaned_value = re.sub(r"^\{\d+\}", "", value)
                ordered_values.append(f"{{{index!s}}}{cleaned_value}")

        return ordered_values

    def _is_binary(self, attr_name):
        """Check if an attribute must be considered binary."""
        lc_name = attr_name.lower()
        return (self.honor_binary and "binary" in lc_name.split(";")) or lc_name in self.binary

    def _normalize_values(self, values, is_binary):
        """Normalize attribute's values."""
        if is_binary:
            converter = base64.b64decode
        else:
            converter = to_bytes

        if not isinstance(values, list):
            values = [values]
        elif self.ordered and not is_binary:
            values = self._order_values([str(value) for value in values])

        try:
            return [converter(value) for value in values]
        except binascii.Error:
            return None

    def add(self):
        modlist = []
        new_attrs = {}
        bad_bin_attrs = []
        for name, values in self.module.params["attributes"].items():
            norm_values = self._normalize_values(values, self._is_binary(name))
            if norm_values is None:
                bad_bin_attrs.append(name)
                continue
            added_values = []
            for value in norm_values:
                if self._is_value_absent(name, value):
                    modlist.append((ldap.MOD_ADD, name, value))
                    added_values.append(value)
            if added_values:
                new_attrs[name] = norm_values
        return modlist, {}, new_attrs, bad_bin_attrs

    def delete(self):
        modlist = []
        old_attrs = {}
        new_attrs = {}
        bad_bin_attrs = []
        for name, values in self.module.params["attributes"].items():
            norm_values = self._normalize_values(values, self._is_binary(name))
            if norm_values is None:
                bad_bin_attrs.append(name)
                continue
            removed_values = []
            for value in norm_values:
                if self._is_value_present(name, value):
                    removed_values.append(value)
                    modlist.append((ldap.MOD_DELETE, name, value))
            if removed_values:
                old_attrs[name] = norm_values
                new_attrs[name] = [value for value in norm_values if value not in removed_values]
        return modlist, old_attrs, new_attrs, bad_bin_attrs

    def exact(self):
        modlist = []
        old_attrs = {}
        new_attrs = {}
        bad_bin_attrs = []
        for name, values in self.module.params["attributes"].items():
            norm_values = self._normalize_values(values, self._is_binary(name))
            if norm_values is None:
                bad_bin_attrs.append(name)
                continue
            current = self._get_all_values_of(name)

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

        return modlist, old_attrs, new_attrs, bad_bin_attrs

    def _is_value_present(self, name, value):
        """True if the target attribute has the given value."""
        if self._is_binary(name):
            return value in self._get_all_values_of(name)

        try:
            escaped_value = ldap.filter.escape_filter_chars(to_text(value))
            filterstr = f"({name}={escaped_value})"
            dns = self.connection.search_s(self.dn, ldap.SCOPE_BASE, filterstr)
            is_present = len(dns) == 1
        except ldap.NO_SUCH_OBJECT:
            is_present = False

        return is_present

    def _get_all_values_of(self, name):
        """Return all values of an attribute."""
        lc_name = name.lower()
        if lc_name not in self._cached_values:
            try:
                results = self.connection.search_s(self.dn, ldap.SCOPE_BASE, attrlist=[name])
            except ldap.LDAPError as e:
                self.fail(f"Cannot search for attribute {name}", e)
            self._cached_values[lc_name] = results[0][1].get(name, [])
        return self._cached_values[lc_name]

    def _is_value_absent(self, name, value):
        """True if the target attribute doesn't have the given value."""
        return not self._is_value_present(name, value)

    def _reencode_modlist(self, modlist):
        """Re-encode binary attribute values in the modlist into Base64 in
        order to avoid crashing the plugin when returning the modlist to
        Ansible."""
        output = []
        for mod_op, attr, values in modlist:
            if self._is_binary(attr) and values is not None:
                values = [base64.b64encode(value) for value in values]
            output.append((mod_op, attr, values))
        return output

    def _reencode_attributes(self, attributes):
        """Re-encode binary attribute values in an attribute dict into Base64 in
        order to avoid crashing the plugin when returning the dict to Ansible."""
        output = {}
        for name, values in attributes.items():
            if self._is_binary(name):
                if isinstance(values, list):
                    values = [base64.b64encode(value) for value in values]
                else:
                    values = base64.b64encode(values)
            output[name] = values
        return output


def main():
    module = AnsibleModule(
        argument_spec=gen_specs(
            attributes=dict(type="dict", required=True),
            binary_attributes=dict(default=[], type="list", elements="str"),
            honor_binary=dict(default=False, type="bool"),
            ordered=dict(type="bool", default=False),
            state=dict(type="str", default="present", choices=["absent", "exact", "present"]),
        ),
        supports_check_mode=True,
        required_together=ldap_required_together(),
    )

    if not HAS_LDAP:
        module.fail_json(msg=missing_required_lib("python-ldap"), exception=LDAP_IMP_ERR)

    # Instantiate the LdapAttr object
    ldap = LdapAttrs(module)
    old_attrs = None
    new_attrs = None
    modlist = []

    state = module.params["state"]

    # Perform action
    if state == "present":
        modlist, old_attrs, new_attrs, bad_attrs = ldap.add()
    elif state == "absent":
        modlist, old_attrs, new_attrs, bad_attrs = ldap.delete()
    elif state == "exact":
        modlist, old_attrs, new_attrs, bad_attrs = ldap.exact()

    if bad_attrs:
        s_bad_attrs = ", ".join(bad_attrs)
        module.fail_json(msg=f"Invalid Base64-encoded attribute values for {s_bad_attrs}")

    changed = False

    if len(modlist) > 0:
        changed = True

        if not module.check_mode:
            try:
                ldap.connection.modify_s(ldap.dn, modlist)
            except Exception as e:
                module.fail_json(msg="Attribute action failed.", details=f"{e}")

    # If the data contain binary attributes/changes, we need to re-encode them
    # using Base64.
    modlist = ldap._reencode_modlist(modlist)
    old_attrs = ldap._reencode_attributes(old_attrs)
    new_attrs = ldap._reencode_attributes(new_attrs)

    module.exit_json(changed=changed, modlist=modlist, diff={"before": old_attrs, "after": new_attrs})


if __name__ == "__main__":
    main()
