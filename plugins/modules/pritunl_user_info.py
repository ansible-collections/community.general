#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2021, Florian Dambrine <android.florian@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: pritunl_user_info
author: "Florian Dambrine (@Lowess)"
version_added: 2.3.0
short_description: List Pritunl Users using the Pritunl API
description:
  - A module to list Pritunl users using the Pritunl API.
extends_documentation_fragment:
  - community.general.pritunl
  - community.general.attributes
  - community.general.attributes.info_module
options:
  organization:
    type: str
    required: true
    aliases:
      - org
    description:
      - The name of the organization the user is part of.
  user_name:
    type: str
    required: false
    description:
      - Name of the user to filter on Pritunl.
  user_type:
    type: str
    required: false
    default: client
    choices:
      - client
      - server
    description:
      - Type of the user O(user_name).
"""

EXAMPLES = r"""
- name: List all existing users part of the organization MyOrg
  community.general.pritunl_user_info:
    state: list
    organization: MyOrg

- name: Search for the user named Florian part of the organization MyOrg
  community.general.pritunl_user_info:
    state: list
    organization: MyOrg
    user_name: Florian
"""

RETURN = r"""
users:
  description: List of Pritunl users.
  returned: success
  type: list
  elements: dict
  sample:
    [
      {
        "audit": false,
        "auth_type": "google",
        "bypass_secondary": false,
        "client_to_client": false,
        "disabled": false,
        "dns_mapping": null,
        "dns_servers": null,
        "dns_suffix": null,
        "email": "foo@bar.com",
        "gravatar": true,
        "groups": [
          "foo",
          "bar"
        ],
        "id": "5d070dafe63q3b2e6s472c3b",
        "name": "foo@acme.com",
        "network_links": [],
        "organization": "58070daee6sf342e6e4s2c36",
        "organization_name": "Acme",
        "otp_auth": true,
        "otp_secret": "35H5EJA3XB2$4CWG",
        "pin": false,
        "port_forwarding": [],
        "servers": []
      }
    ]
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native
from ansible.module_utils.common.dict_transformations import dict_merge
from ansible_collections.community.general.plugins.module_utils.net_tools.pritunl.api import (
    PritunlException,
    get_pritunl_settings,
    list_pritunl_organizations,
    list_pritunl_users,
    pritunl_argument_spec,
)


def get_pritunl_user(module):
    user_name = module.params.get("user_name")
    user_type = module.params.get("user_type")
    org_name = module.params.get("organization")

    org_obj_list = []

    org_obj_list = list_pritunl_organizations(
        **dict_merge(get_pritunl_settings(module), {"filters": {"name": org_name}})
    )

    if len(org_obj_list) == 0:
        module.fail_json(
            msg="Can not list users from the organization '%s' which does not exist"
            % org_name
        )

    org_id = org_obj_list[0]["id"]

    users = list_pritunl_users(
        **dict_merge(
            get_pritunl_settings(module),
            {
                "organization_id": org_id,
                "filters": (
                    {"type": user_type}
                    if user_name is None
                    else {"name": user_name, "type": user_type}
                ),
            },
        )
    )

    result = {}
    result["changed"] = False
    result["users"] = users

    module.exit_json(**result)


def main():
    argument_spec = pritunl_argument_spec()

    argument_spec.update(
        dict(
            organization=dict(required=True, type="str", aliases=["org"]),
            user_name=dict(type="str"),
            user_type=dict(choices=["client", "server"], default="client"),
        )
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    try:
        get_pritunl_user(module)
    except PritunlException as e:
        module.fail_json(msg=to_native(e))


if __name__ == "__main__":
    main()
