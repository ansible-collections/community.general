#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2018, Johannes Brunswicker <johannes.brunswicker@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: utm_proxy_frontend_info

author:
    - Johannes Brunswicker (@MatrixCrawler)

short_description: Create, update or destroy reverse_proxy frontend entry in Sophos UTM

description:
    - Create, update or destroy a reverse_proxy frontend entry in SOPHOS UTM.
    - This module needs to have the REST Ability of the UTM to be activated.

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
- name: Get utm proxy_frontend
  community.general.utm_proxy_frontend_info:
    utm_host: sophos.host.name
    utm_token: abcdefghijklmno1234
    name: TestBackendEntry
    host: REF_OBJECT_STRING
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
        add_content_type_header:
            description: Whether to add the content type header
            type: bool
        address:
            description: The reference name of the address
            type: str
        allowed_networks:
            description: List of reference names of networks associated
            type: list
        certificate:
            description: Reference name of certificate (ca/host_key_cert)
            type: str
        comment:
            description: The comment string
            type: str
        disable_compression:
            description: State of compression support
            type: bool
        domain:
            description: List of hostnames
            type: list
        exceptions:
            description: List of associated proxy exceptions
            type: list
        htmlrewrite:
            description: State of html rewrite
            type: bool
        htmlrewrite_cookies:
            description: whether the html rewrite cookie will be set
            type: bool
        implicitredirect:
            description: whether to use implicit redirection
            type: bool
        lbmethod:
            description: The method of loadbalancer to use
            type: str
        locations:
            description: The reference names of reverse_proxy/locations associated with the object
            type: list
        port:
            description: The port of the frontend connection
            type: int
        preservehost:
            description: Preserve host header
            type: bool
        profile:
            description: The associated reverse_proxy/profile
            type: str
        status:
            description: Whether the frontend object is active or not
            type: bool
        type:
            description: The connection type
            type: str
        xheaders:
            description: The xheaders state
            type: bool
"""

from ansible_collections.community.general.plugins.module_utils.utm_utils import UTM, UTMModule
from ansible.module_utils.common.text.converters import to_native


def main():
    endpoint = "reverse_proxy/frontend"
    key_to_check_for_changes = []
    module = UTMModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
        ),
        supports_check_mode=True,
    )
    try:
        UTM(module, endpoint, key_to_check_for_changes, info_only=True).execute()
    except Exception as e:
        module.fail_json(msg=to_native(e))


if __name__ == '__main__':
    main()
