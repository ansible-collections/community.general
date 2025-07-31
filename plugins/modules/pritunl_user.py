#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2021, Florian Dambrine <android.florian@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: pritunl_user
author: "Florian Dambrine (@Lowess)"
version_added: 2.3.0
short_description: Manage Pritunl Users using the Pritunl API
description:
  - A module to manage Pritunl users using the Pritunl API.
extends_documentation_fragment:
  - community.general.pritunl
  - community.general.attributes
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options:
  organization:
    type: str
    required: true
    aliases:
      - org
    description:
      - The name of the organization the user is part of.
  state:
    type: str
    default: 'present'
    choices:
      - present
      - absent
    description:
      - If V(present), the module adds user O(user_name) to the Pritunl O(organization). If V(absent), removes the user O(user_name)
        from the Pritunl O(organization).
  user_name:
    type: str
    required: true
    default:
    description:
      - Name of the user to create or delete from Pritunl.
  user_email:
    type: str
    required: false
    default:
    description:
      - Email address associated with the user O(user_name).
  user_type:
    type: str
    required: false
    default: client
    choices:
      - client
      - server
    description:
      - Type of the user O(user_name).
  user_groups:
    type: list
    elements: str
    required: false
    default:
    description:
      - List of groups associated with the user O(user_name).
  user_disabled:
    type: bool
    required: false
    default:
    description:
      - Enable/Disable the user O(user_name).
  user_gravatar:
    type: bool
    required: false
    default:
    description:
      - Enable/Disable Gravatar usage for the user O(user_name).
  user_mac_addresses:
    type: list
    elements: str
    description:
      - Allowed MAC addresses for the user O(user_name).
    version_added: 5.0.0
"""

EXAMPLES = r"""
- name: Create the user Foo with email address foo@bar.com in MyOrg
  community.general.pritunl_user:
    state: present
    organization: MyOrg
    user_name: Foo
    user_email: foo@bar.com
    user_mac_addresses:
      - "00:00:00:00:00:99"

- name: Disable the user Foo but keep it in Pritunl
  community.general.pritunl_user:
    state: present
    organization: MyOrg
    user_name: Foo
    user_email: foo@bar.com
    user_disabled: true

- name: Make sure the user Foo is not part of MyOrg anymore
  community.general.pritunl_user:
    state: absent
    organization: MyOrg
    user_name: Foo
"""

RETURN = r"""
response:
  description: JSON representation of Pritunl Users.
  returned: success
  type: dict
  sample:
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
"""


from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native
from ansible.module_utils.common.dict_transformations import dict_merge
from ansible_collections.community.general.plugins.module_utils.net_tools.pritunl.api import (
    PritunlException,
    delete_pritunl_user,
    get_pritunl_settings,
    list_pritunl_organizations,
    list_pritunl_users,
    post_pritunl_user,
    pritunl_argument_spec,
)


def add_or_update_pritunl_user(module):
    result = {}

    org_name = module.params.get("organization")
    user_name = module.params.get("user_name")

    user_params = {
        "name": user_name,
        "email": module.params.get("user_email"),
        "groups": module.params.get("user_groups"),
        "disabled": module.params.get("user_disabled"),
        "gravatar": module.params.get("user_gravatar"),
        "mac_addresses": module.params.get("user_mac_addresses"),
        "type": module.params.get("user_type"),
    }

    org_obj_list = list_pritunl_organizations(
        **dict_merge(
            get_pritunl_settings(module),
            {"filters": {"name": org_name}},
        )
    )

    if len(org_obj_list) == 0:
        module.fail_json(
            msg="Can not add user to organization '%s' which does not exist" % org_name
        )

    org_id = org_obj_list[0]["id"]

    # Grab existing users from this org
    users = list_pritunl_users(
        **dict_merge(
            get_pritunl_settings(module),
            {
                "organization_id": org_id,
                "filters": {"name": user_name},
            },
        )
    )

    # Check if the pritunl user already exists
    if len(users) > 0:
        # Compare remote user params with local user_params and trigger update if needed
        user_params_changed = False
        for key in user_params.keys():
            # When a param is not specified grab existing ones to prevent from changing it with the PUT request
            if user_params[key] is None:
                user_params[key] = users[0][key]

            # 'groups' and 'mac_addresses' are list comparison
            if key == "groups" or key == "mac_addresses":
                if set(users[0][key]) != set(user_params[key]):
                    user_params_changed = True

            # otherwise it is either a boolean or a string
            else:
                if users[0][key] != user_params[key]:
                    user_params_changed = True

        # Trigger a PUT on the API to update the current user if settings have changed
        if user_params_changed:
            response = post_pritunl_user(
                **dict_merge(
                    get_pritunl_settings(module),
                    {
                        "organization_id": org_id,
                        "user_id": users[0]["id"],
                        "user_data": user_params,
                    },
                )
            )

            result["changed"] = True
            result["response"] = response
        else:
            result["changed"] = False
            result["response"] = users
    else:
        response = post_pritunl_user(
            **dict_merge(
                get_pritunl_settings(module),
                {
                    "organization_id": org_id,
                    "user_data": user_params,
                },
            )
        )
        result["changed"] = True
        result["response"] = response

    module.exit_json(**result)


def remove_pritunl_user(module):
    result = {}

    org_name = module.params.get("organization")
    user_name = module.params.get("user_name")

    org_obj_list = []

    org_obj_list = list_pritunl_organizations(
        **dict_merge(
            get_pritunl_settings(module),
            {
                "filters": {"name": org_name},
            },
        )
    )

    if len(org_obj_list) == 0:
        module.fail_json(
            msg="Can not remove user '%s' from a non existing organization '%s'"
            % (user_name, org_name)
        )

    org_id = org_obj_list[0]["id"]

    # Grab existing users from this org
    users = list_pritunl_users(
        **dict_merge(
            get_pritunl_settings(module),
            {
                "organization_id": org_id,
                "filters": {"name": user_name},
            },
        )
    )

    # Check if the pritunl user exists, if not, do nothing
    if len(users) == 0:
        result["changed"] = False
        result["response"] = {}

    # Otherwise remove the org from Pritunl
    else:
        response = delete_pritunl_user(
            **dict_merge(
                get_pritunl_settings(module),
                {
                    "organization_id": org_id,
                    "user_id": users[0]["id"],
                },
            )
        )
        result["changed"] = True
        result["response"] = response

    module.exit_json(**result)


def main():
    argument_spec = pritunl_argument_spec()

    argument_spec.update(
        dict(
            organization=dict(required=True, type="str", aliases=["org"]),
            state=dict(choices=["present", "absent"], default="present"),
            user_name=dict(required=True, type="str"),
            user_type=dict(choices=["client", "server"], default="client"),
            user_email=dict(type="str"),
            user_groups=dict(type="list", elements="str"),
            user_disabled=dict(type="bool"),
            user_gravatar=dict(type="bool"),
            user_mac_addresses=dict(type="list", elements="str"),
        )
    )

    module = AnsibleModule(argument_spec=argument_spec)

    state = module.params.get("state")

    try:
        if state == "present":
            add_or_update_pritunl_user(module)
        elif state == "absent":
            remove_pritunl_user(module)
    except PritunlException as e:
        module.fail_json(msg=to_native(e))


if __name__ == "__main__":
    main()
