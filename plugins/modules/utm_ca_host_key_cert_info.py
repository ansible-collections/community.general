#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2018, Stephan Schwarz <stearz@gmx.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: utm_ca_host_key_cert_info

author:
    - Stephan Schwarz (@stearz)

short_description: Get info for a ca host_key_cert entry in Sophos UTM

description:
    - Get info for a ca host_key_cert entry in SOPHOS UTM.

attributes:
    check_mode:
        version_added: 3.3.0
        # This was backported to 2.5.4 and 1.3.11 as well, since this was a bugfix

options:
    name:
        type: str
        description:
            - The name of the object. Will be used to identify the entry
        required: true

extends_documentation_fragment:
    - community.general.utm
    - community.general.attributes
    - community.general.attributes.info_module
'''

EXAMPLES = """
- name: Get info for a ca host_key_cert entry
  community.general.utm_ca_host_key_cert_info:
    utm_host: sophos.host.name
    utm_token: abcdefghijklmno1234
    name: TestHostKeyCertEntry
"""

RETURN = """
result:
    description: The utm object that was created
    returned: success
    type: complex
    contains:
        _ref:
            description: The reference name of the object
            type: str
        _locked:
            description: Whether or not the object is currently locked
            type: bool
        _type:
            description: The type of the object
            type: str
        name:
            description: The name of the object
            type: str
        ca:
            description: A reference to an existing utm_ca_signing_ca or utm_ca_verification_ca object.
            type: str
        meta:
            description: A reference to an existing utm_ca_meta_x509 object.
            type: str
        certificate:
            description: The certificate in PEM format
            type: str
        comment:
            description: Comment string (may be empty string)
            type: str
        encrypted:
            description: If encryption is enabled
            type: bool
        key:
            description: Private key in PEM format (may be empty string)
            type: str
"""

from ansible_collections.community.general.plugins.module_utils.utm_utils import UTM, UTMModule
from ansible.module_utils.common.text.converters import to_native


def main():
    endpoint = "ca/host_key_cert"
    key_to_check_for_changes = []
    module = UTMModule(
        argument_spec=dict(
            name=dict(type='str', required=True)
        ),
        supports_check_mode=True,
    )
    try:
        # This is needed because the bool value only accepts int values in the backend
        UTM(module, endpoint, key_to_check_for_changes, info_only=True).execute()
    except Exception as e:
        module.fail_json(msg=to_native(e))


if __name__ == '__main__':
    main()
