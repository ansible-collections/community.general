#!/usr/bin/python
#
# Copyright (c) 2018, Yanis Guenane <yanis+ansible@guenane.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: scaleway_organization_info
short_description: Gather information about the Scaleway organizations available
description:
  - Gather information about the Scaleway organizations available.
  - The organizations are determined from the projects that the API token can access.
author:
  - "Yanis Guenane (@Spredzy)"
  - "Remy Leone (@remyleone)"

attributes:
  action_group:
    version_added: 11.3.0

options:
  api_url:
    description:
      - Scaleway API URL.
    default: 'https://api.scaleway.com'
    aliases: ['base_url']
extends_documentation_fragment:
  - community.general._scaleway
  - community.general._attributes
  - community.general._scaleway.actiongroup_scaleway
  - community.general._attributes.info_module
"""

EXAMPLES = r"""
- name: Gather Scaleway organizations information
  community.general.scaleway_organization_info:
  register: result

- ansible.builtin.debug:
    msg: "{{ result.scaleway_organization_info }}"
"""

RETURN = r"""
scaleway_organization_info:
  description:
    - List of the organizations of the projects that the API token can access.
    - Earlier versions of this module used a legacy Scaleway API that is no longer available.
      The organization details that API returned, such as address, currency, and users, cannot be obtained anymore.
  returned: success
  type: list
  elements: dict
  contains:
    id:
      description: ID of the organization.
      type: str
      sample: 3f709602-5e6c-4619-b80c-e8432ferewtr
  sample:
    [
      {
        "id": "3f709602-5e6c-4619-b80c-e8432ferewtr"
      }
    ]
"""

from ansible.module_utils.basic import AnsibleModule, env_fallback

from ansible_collections.community.general.plugins.module_utils._scaleway import (
    Scaleway,
    scaleway_argument_spec,
)


def get_organizations(api):
    projects = api.fetch_all_resources("projects")
    organization_ids = dict.fromkeys(project["organization_id"] for project in projects)
    return [{"id": organization_id} for organization_id in organization_ids]


def main():
    argument_spec = scaleway_argument_spec()
    argument_spec.update(
        dict(
            api_url=dict(
                fallback=(env_fallback, ["SCW_API_URL"]), default="https://api.scaleway.com", aliases=["base_url"]
            ),
        )
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    api = Scaleway(module)
    api.api_path = "account/v3/projects"

    module.exit_json(scaleway_organization_info=get_organizations(api))


if __name__ == "__main__":
    main()
