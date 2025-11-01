#!/usr/bin/python

# Copyright (c) 2018, Johannes Brunswicker <johannes.brunswicker@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: utm_aaa_group_info

author:
  - Johannes Brunswicker (@MatrixCrawler)

short_description: Get info for reverse_proxy frontend entry in Sophos UTM

description:
  - Get info for a reverse_proxy frontend entry in SOPHOS UTM.
attributes:
  check_mode:
    version_added: 3.3.0
    # This was backported to 2.5.4 and 1.3.11 as well, since this was a bugfix

options:
  name:
    type: str
    description:
      - The name of the object that identifies the entry.
    required: true

extends_documentation_fragment:
  - community.general.utm
  - community.general.attributes
  - community.general.attributes.info_module
"""

EXAMPLES = r"""
- name: Remove UTM aaa_group
  community.general.utm_aaa_group_info:
    utm_host: sophos.host.name
    utm_token: abcdefghijklmno1234
    name: TestAAAGroupEntry
"""

RETURN = r"""
result:
  description: The utm object that was created.
  returned: success
  type: complex
  contains:
    _ref:
      description: The reference name of the object.
      type: str
    _locked:
      description: Whether or not the object is currently locked.
      type: bool
    _type:
      description: The type of the object.
      type: str
    name:
      description: The name of the object.
      type: str
    adirectory_groups:
      description: List of Active Directory Groups.
      type: str
    adirectory_groups_sids:
      description: List of Active Directory Groups SIDS.
      type: list
    backend_match:
      description: The backend to use.
      type: str
    comment:
      description: The comment string.
      type: str
    dynamic:
      description: Whether the group match is V(ipsec_dn) or V(directory_group).
      type: str
    edirectory_groups:
      description: List of eDirectory Groups.
      type: str
    ipsec_dn:
      description: Ipsec_dn identifier to match.
      type: str
    ldap_attribute:
      description: The LDAP Attribute to match against.
      type: str
    ldap_attribute_value:
      description: The LDAP Attribute Value to match against.
      type: str
    members:
      description: List of member identifiers of the group.
      type: list
    network:
      description: The identifier of the network (network/aaa).
      type: str
    radius_group:
      description: The radius group identifier.
      type: str
    tacacs_group:
      description: The tacacs group identifier.
      type: str
"""

from ansible_collections.community.general.plugins.module_utils.utm_utils import UTM, UTMModule
from ansible.module_utils.common.text.converters import to_native


def main():
    endpoint = "aaa/group"
    key_to_check_for_changes = []
    module = UTMModule(
        argument_spec=dict(name=dict(type="str", required=True)),
        supports_check_mode=True,
    )
    try:
        UTM(module, endpoint, key_to_check_for_changes, info_only=True).execute()
    except Exception as e:
        module.fail_json(msg=to_native(e))


if __name__ == "__main__":
    main()
