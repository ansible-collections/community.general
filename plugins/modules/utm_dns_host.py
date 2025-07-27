#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2018, Johannes Brunswicker <johannes.brunswicker@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: utm_dns_host

author:
  - Johannes Brunswicker (@MatrixCrawler)

short_description: Create, update or destroy DNS entry in Sophos UTM

description:
  - Create, update or destroy a DNS entry in SOPHOS UTM.
  - This module needs to have the REST Ability of the UTM to be activated.
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none

options:
  name:
    type: str
    description:
      - The name of the object that identifies the entry.
    required: true
  address:
    type: str
    description:
      - The IPV4 Address of the entry. Can be left empty for automatic resolving.
    default: 0.0.0.0
  address6:
    type: str
    description:
      - The IPV6 Address of the entry. Can be left empty for automatic resolving.
    default: "::"
  comment:
    type: str
    description:
      - An optional comment to add to the DNS host object.
    default: ''
  hostname:
    type: str
    description:
      - The hostname for the DNS host object.
  interface:
    type: str
    description:
      - The reference name of the interface to use. If not provided the default interface is used.
    default: ''
  resolved:
    description:
      - Whether the hostname's ipv4 address is already resolved or not.
    default: false
    type: bool
  resolved6:
    description:
      - Whether the hostname's ipv6 address is already resolved or not.
    default: false
    type: bool
  timeout:
    type: int
    description:
      - The timeout for the UTM to resolve the IP address for the hostname again.
    default: 0

extends_documentation_fragment:
  - community.general.utm
  - community.general.attributes
"""

EXAMPLES = r"""
- name: Create UTM dns host entry
  community.general.utm_dns_host:
    utm_host: sophos.host.name
    utm_token: abcdefghijklmno1234
    name: TestDNSEntry
    hostname: testentry.some.tld
    state: present

- name: Remove UTM dns host entry
  community.general.utm_dns_host:
    utm_host: sophos.host.name
    utm_token: abcdefghijklmno1234
    name: TestDNSEntry
    state: absent
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
    name:
      description: The name of the object.
      type: str
    address:
      description: The ipv4 address of the object.
      type: str
    address6:
      description: The ipv6 address of the object.
      type: str
    comment:
      description: The comment string.
      type: str
    hostname:
      description: The hostname of the object.
      type: str
    interface:
      description: The reference name of the interface the object is associated with.
      type: str
    resolved:
      description: Whether the ipv4 address is resolved or not.
      type: bool
    resolved6:
      description: Whether the ipv6 address is resolved or not.
      type: bool
    timeout:
      description: The timeout until a new resolving is attempted.
      type: int
"""

from ansible_collections.community.general.plugins.module_utils.utm_utils import UTM, UTMModule
from ansible.module_utils.common.text.converters import to_native


def main():
    endpoint = "network/dns_host"
    key_to_check_for_changes = ["comment", "hostname", "interface"]
    module = UTMModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            address=dict(type='str', required=False, default='0.0.0.0'),
            address6=dict(type='str', required=False, default='::'),
            comment=dict(type='str', required=False, default=""),
            hostname=dict(type='str', required=False),
            interface=dict(type='str', required=False, default=""),
            resolved=dict(type='bool', required=False, default=False),
            resolved6=dict(type='bool', required=False, default=False),
            timeout=dict(type='int', required=False, default=0),
        )
    )
    try:
        UTM(module, endpoint, key_to_check_for_changes).execute()
    except Exception as e:
        module.fail_json(msg=to_native(e))


if __name__ == '__main__':
    main()
