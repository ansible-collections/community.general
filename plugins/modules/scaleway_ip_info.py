#!/usr/bin/python
#
# Copyright (c) 2018, Yanis Guenane <yanis+ansible@guenane.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: scaleway_ip_info
short_description: Gather information about the Scaleway IPs available
description:
  - Gather information about the Scaleway IPs available.
author:
  - "Yanis Guenane (@Spredzy)"
  - "Remy Leone (@remyleone)"
extends_documentation_fragment:
  - community.general.scaleway
  - community.general.attributes
  - community.general.scaleway.actiongroup_scaleway
  - community.general.attributes.info_module

attributes:
  action_group:
    version_added: 11.3.0

options:
  region:
    type: str
    description:
      - Scaleway region to use (for example C(par1)) (deprecated).
    required: false
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

  zone:
    type: str
    description:
      - Scaleway zone to use (for example (nl-ams-1))
    required: false
    choices:
      - fr-par-1
      - fr-par-2
      - fr-par-3
      - nl-ams-1
      - nl-ams-2
      - nl-ams-3
      - pl-waw-1
      - pl-waw-2
      - pl-waw-3
      - it-mil-1
"""

EXAMPLES = r"""
- name: Gather Scaleway IPs information
  community.general.scaleway_ip_info:
    zone: fr-par-1
  register: result

- ansible.builtin.debug:
    msg: "{{ result.scaleway_ip_info }}"

- name: Gather Scaleway IPs information (deprecated)
  community.general.scaleway_ip_info:
    region: par-1
  register: result
"""

RETURN = r"""
scaleway_ip_info:
  description:
    - Response from Scaleway API.
    - For more details please refer to U(https://developers.scaleway.com/en/products/instance/api/).
  returned: success
  type: list
  elements: dict
  sample:
    [
      {
        "address": "163.172.170.243",
        "id": "ea081794-a581-8899-8451-386ddaf0a451",
        "organization": "3f709602-5e6c-4619-b80c-e324324324af",
        "reverse": null,
        "server": {
          "id": "12f19bc7-109c-4517-954c-e6b3d0311363",
          "name": "scw-e0d158"
        }
      }
    ]
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.general.plugins.module_utils.scaleway import (
    SCALEWAY_LOCATION,
    SCALEWAY_ENDPOINT,
    SCALEWAY_ZONES,
    Scaleway,
    ScalewayException,
    scaleway_argument_spec,
)


class ScalewayIpInfo(Scaleway):
    def __init__(self, module):
        super().__init__(module)
        self.name = "ips"

        if self.module.params.get("zone"):
            self.module.params["api_url"] = SCALEWAY_ENDPOINT
        else:
            self.module.params["api_url"] = SCALEWAY_LOCATION[self.module.params.get("region")]["api_endpoint"]


def main():
    argument_spec = scaleway_argument_spec()
    argument_spec.update(
        dict(
            region=dict(required=False, choices=list(SCALEWAY_LOCATION.keys())),
            zone=dict(required=False, choices=list(SCALEWAY_ZONES)),
        )
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[
            ("zone", "region"),
        ],
        required_one_of=[
            ("zone", "region"),
        ],
    )

    api = ScalewayIpInfo(module=module)

    if module.params["zone"]:
        zone = module.params["zone"]
        api_path = f"instance/v1/zones/{zone}/ips"
        response = scaleway_ip_info=api.get(path=api_path)
        module.exit_json(scaleway_ip_info=response.json.get('ips'))
    else:
        module.deprecate(
            msg="The 'region' parameter is deprecated. Use 'zone' to specify the Scaleway zone instead.",
            version="14.0.0",
            collection_name="community.general",
        )

        try:
            module.exit_json(scaleway_ip_info=ScalewayIpInfo(module).get_resources())
        except ScalewayException as exc:
            module.fail_json(msg=exc.message)


if __name__ == "__main__":
    main()
