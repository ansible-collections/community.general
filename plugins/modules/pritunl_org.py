#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2021, Florian Dambrine <android.florian@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: pritunl_org
author: Florian Dambrine (@Lowess)
version_added: 2.5.0
short_description: Manages Pritunl Organizations using the Pritunl API
description:
    - A module to manage Pritunl organizations using the Pritunl API.
extends_documentation_fragment:
    - community.general.pritunl
    - community.general.attributes
attributes:
    check_mode:
        support: none
    diff_mode:
        support: none
options:
    name:
        type: str
        required: true
        aliases:
            - org
        description:
            - The name of the organization to manage in Pritunl.

    force:
        type: bool
        default: false
        description:
            - If I(force) is C(true) and I(state) is C(absent), the module
              will delete the organization, no matter if it contains users
              or not. By default I(force) is C(false), which will cause the
              module to fail the deletion of the organization when it contains
              users.

    state:
        type: str
        default: 'present'
        choices:
            - present
            - absent
        description:
            - If C(present), the module adds organization I(name) to
              Pritunl. If C(absent), attempt to delete the organization
              from Pritunl (please read about I(force) usage).
"""

EXAMPLES = """
- name: Ensure the organization named MyOrg exists
  community.general.pritunl_org:
    state: present
    name: MyOrg

- name: Ensure the organization named MyOrg does not exist
  community.general.pritunl_org:
    state: absent
    name: MyOrg
"""

RETURN = """
response:
    description: JSON representation of a Pritunl Organization.
    returned: success
    type: dict
    sample:
        {
            "auth_api": false,
            "name": "Foo",
            "auth_token": null,
            "user_count": 0,
            "auth_secret": null,
            "id": "csftwlu6uhralzi2dpmhekz3",
        }
"""


from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native
from ansible.module_utils.common.dict_transformations import dict_merge
from ansible_collections.community.general.plugins.module_utils.net_tools.pritunl.api import (
    PritunlException,
    delete_pritunl_organization,
    post_pritunl_organization,
    list_pritunl_organizations,
    get_pritunl_settings,
    pritunl_argument_spec,
)


def add_pritunl_organization(module):
    result = {}

    org_name = module.params.get("name")

    org_obj_list = list_pritunl_organizations(
        **dict_merge(
            get_pritunl_settings(module),
            {"filters": {"name": org_name}},
        )
    )

    # If the organization already exists
    if len(org_obj_list) > 0:
        result["changed"] = False
        result["response"] = org_obj_list[0]
    else:
        # Otherwise create it
        response = post_pritunl_organization(
            **dict_merge(
                get_pritunl_settings(module),
                {"organization_name": org_name},
            )
        )
        result["changed"] = True
        result["response"] = response

    module.exit_json(**result)


def remove_pritunl_organization(module):
    result = {}

    org_name = module.params.get("name")
    force = module.params.get("force")

    org_obj_list = []

    org_obj_list = list_pritunl_organizations(
        **dict_merge(
            get_pritunl_settings(module),
            {
                "filters": {"name": org_name},
            },
        )
    )

    # No organization found
    if len(org_obj_list) == 0:
        result["changed"] = False
        result["response"] = {}

    else:
        # Otherwise attempt to delete it
        org = org_obj_list[0]

        # Only accept deletion under specific conditions
        if force or org["user_count"] == 0:
            response = delete_pritunl_organization(
                **dict_merge(
                    get_pritunl_settings(module),
                    {"organization_id": org["id"]},
                )
            )
            result["changed"] = True
            result["response"] = response
        else:
            module.fail_json(
                msg=(
                    "Can not remove organization '%s' with %d attached users. "
                    "Either set 'force' option to true or remove active users "
                    "from the organization"
                )
                % (org_name, org["user_count"])
            )

    module.exit_json(**result)


def main():
    argument_spec = pritunl_argument_spec()

    argument_spec.update(
        dict(
            name=dict(required=True, type="str", aliases=["org"]),
            force=dict(required=False, type="bool", default=False),
            state=dict(
                required=False, choices=["present", "absent"], default="present"
            ),
        )
    )

    module = AnsibleModule(argument_spec=argument_spec)

    state = module.params.get("state")

    try:
        if state == "present":
            add_pritunl_organization(module)
        elif state == "absent":
            remove_pritunl_organization(module)
    except PritunlException as e:
        module.fail_json(msg=to_native(e))


if __name__ == "__main__":
    main()
