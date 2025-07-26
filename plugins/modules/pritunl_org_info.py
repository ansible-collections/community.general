#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2021, Florian Dambrine <android.florian@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: pritunl_org_info
author: Florian Dambrine (@Lowess)
version_added: 2.5.0
short_description: List Pritunl Organizations using the Pritunl API
description:
  - A module to list Pritunl organizations using the Pritunl API.
extends_documentation_fragment:
  - community.general.pritunl
  - community.general.attributes
  - community.general.attributes.info_module
options:
  organization:
    type: str
    required: false
    aliases:
      - org
    default: null
    description:
      - Name of the Pritunl organization to search for. If none provided, the module returns all Pritunl organizations.
"""

EXAMPLES = r"""
- name: List all existing Pritunl organizations
  community.general.pritunl_org_info:

- name: Search for an organization named MyOrg
  community.general.pritunl_user_info:
    organization: MyOrg
"""

RETURN = r"""
organizations:
  description: List of Pritunl organizations.
  returned: success
  type: list
  elements: dict
  sample:
    [
      {
        "auth_api": false,
        "name": "FooOrg",
        "auth_token": null,
        "user_count": 0,
        "auth_secret": null,
        "id": "csftwlu6uhralzi2dpmhekz3"
      },
      {
        "auth_api": false,
        "name": "MyOrg",
        "auth_token": null,
        "user_count": 3,
        "auth_secret": null,
        "id": "58070daee63f3b2e6e472c36"
      },
      {
        "auth_api": false,
        "name": "BarOrg",
        "auth_token": null,
        "user_count": 0,
        "auth_secret": null,
        "id": "v1sncsxxybnsylc8gpqg85pg"
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
    pritunl_argument_spec,
)


def get_pritunl_organizations(module):
    org_name = module.params.get("organization")

    organizations = []

    organizations = list_pritunl_organizations(
        **dict_merge(
            get_pritunl_settings(module),
            {"filters": {"name": org_name} if org_name else None},
        )
    )

    if org_name and len(organizations) == 0:
        # When an org_name is provided but no organization match return an error
        module.fail_json(msg="Organization '%s' does not exist" % org_name)

    result = {}
    result["changed"] = False
    result["organizations"] = organizations

    module.exit_json(**result)


def main():
    argument_spec = pritunl_argument_spec()

    argument_spec.update(
        dict(
            organization=dict(required=False, type="str", default=None, aliases=["org"])
        )
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    try:
        get_pritunl_organizations(module)
    except PritunlException as e:
        module.fail_json(msg=to_native(e))


if __name__ == "__main__":
    main()
