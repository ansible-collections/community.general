#!/usr/bin/python
#
# Scaleway user data management module
#
# Copyright (C) 2018 Online SAS.
# https://www.scaleway.com
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
module: scaleway_user_data
short_description: Scaleway user_data management module
author: Remy Leone (@remyleone)
description:
  - This module manages user_data on compute instances on Scaleway.
  - It can be used to configure cloud-init for instance.
extends_documentation_fragment:
  - community.general.scaleway
  - community.general.attributes
  - community.general.scaleway.actiongroup_scaleway

attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
  action_group:
    version_added: 11.3.0

options:

  server_id:
    type: str
    description:
      - Scaleway Compute instance ID of the server.
    required: true

  user_data:
    type: dict
    description:
      - User defined data. Typically used with C(cloud-init).
      - Pass your C(cloud-init) script here as a string.

  region:
    type: str
    description:
      - Scaleway compute zone.
    required: true
    choices:
      - ams1
      - EMEA-NL-EVS
      - ams2
      - ams3
      - par1
      - EMEA-FR-PAR1
      - par2
      - EMEA-FR-PAR2
      - par3
      - waw1
      - EMEA-PL-WAW1
      - waw2
      - waw3
"""

EXAMPLES = r"""
- name: Update the cloud-init
  community.general.scaleway_user_data:
    server_id: '5a33b4ab-57dd-4eb6-8b0a-d95eb63492ce'
    region: ams1
    user_data:
      cloud-init: 'final_message: "Hello World!"'
"""

RETURN = r"""
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.scaleway import (
    SCALEWAY_LOCATION,
    scaleway_argument_spec,
    Scaleway,
)


def patch_user_data(compute_api, server_id, key, value):
    compute_api.module.debug("Starting patching user_data attributes")

    path = f"servers/{server_id}/user_data/{key}"
    response = compute_api.patch(path=path, data=value, headers={"Content-Type": "text/plain"})
    if not response.ok:
        msg = f"Error during user_data patching: {response.status_code} {response.body}"
        compute_api.module.fail_json(msg=msg)

    return response


def delete_user_data(compute_api, server_id, key):
    compute_api.module.debug(f"Starting deleting user_data attributes: {key}")

    response = compute_api.delete(path=f"servers/{server_id}/user_data/{key}")

    if not response.ok:
        msg = "Error during user_data deleting: (%s) %s" % response.status_code, response.body
        compute_api.module.fail_json(msg=msg)

    return response


def get_user_data(compute_api, server_id, key):
    compute_api.module.debug("Starting patching user_data attributes")

    path = f"servers/{server_id}/user_data/{key}"
    response = compute_api.get(path=path)
    if not response.ok:
        msg = f"Error during user_data patching: {response.status_code} {response.body}"
        compute_api.module.fail_json(msg=msg)

    return response.json


def core(module):
    region = module.params["region"]
    server_id = module.params["server_id"]
    user_data = module.params["user_data"]
    changed = False

    module.params["api_url"] = SCALEWAY_LOCATION[region]["api_endpoint"]
    compute_api = Scaleway(module=module)

    user_data_list = compute_api.get(path=f"servers/{server_id}/user_data")
    if not user_data_list.ok:
        msg = "Error during user_data fetching: %s %s" % user_data_list.status_code, user_data_list.body
        compute_api.module.fail_json(msg=msg)

    present_user_data_keys = user_data_list.json["user_data"]
    present_user_data = {
        key: get_user_data(compute_api=compute_api, server_id=server_id, key=key) for key in present_user_data_keys
    }

    if present_user_data == user_data:
        module.exit_json(changed=changed, msg=user_data_list.json)

    # First we remove keys that are not defined in the wished user_data
    for key in present_user_data:
        if key not in user_data:
            changed = True
            if compute_api.module.check_mode:
                module.exit_json(changed=changed, msg={"status": f"User-data of {server_id} would be patched."})

            delete_user_data(compute_api=compute_api, server_id=server_id, key=key)

    # Then we patch keys that are different
    for key, value in user_data.items():
        if key not in present_user_data or value != present_user_data[key]:
            changed = True
            if compute_api.module.check_mode:
                module.exit_json(changed=changed, msg={"status": f"User-data of {server_id} would be patched."})

            patch_user_data(compute_api=compute_api, server_id=server_id, key=key, value=value)

    module.exit_json(changed=changed, msg=user_data)


def main():
    argument_spec = scaleway_argument_spec()
    argument_spec.update(
        dict(
            region=dict(required=True, choices=list(SCALEWAY_LOCATION.keys())),
            user_data=dict(type="dict"),
            server_id=dict(required=True),
        )
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    core(module)


if __name__ == "__main__":
    main()
