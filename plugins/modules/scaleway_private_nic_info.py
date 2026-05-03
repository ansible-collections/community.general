#!/usr/bin/python
#
# Copyright (c) 2018, Yanis Guenane <yanis+ansible@guenane.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: scaleway_private_nic_info
short_description: List all private NICs
description:
  - List all private NICs of a specified Instance.
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
      - Scaleway region to use (for example C(par1)).
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
  instance_id:
    type: str
    description:
      - ID of the insance.
    required: true
"""

EXAMPLES = r"""
- name: Get information about all private NICs of specified instance and register it in a variable
  community.general.scaleway_private_nic_info:
    region: par1
    instance_id: "1234ab-ab12-12ab-12a3-12345678ab9c"
  register: nics

- name: Display nics
  debug:
    var: nics
"""

RETURN = r"""
private_nics:
  description:
    - Response from Scaleway API.
    - For more details please refer to U(https://developers.scaleway.com/en/products/instance/api/).
  returned: always
  type: list
  elements: dict
  contains:
    "creation_date":
      description: Private NIC creation date.
      sample: "2026-04-09T00:00:00.000000+00:00"
      type: str
    "id":
      description: Private NIC unique ID.
      sample: "abc123ab-12ab-12ab-12ab-123abc123abc"
      type: str
    "ipam_ip_ids":
      description: UUID of IPAM ips.
      sample:
        [
          "1234abcd-34cd-12ab-56ab-123abc123abc",
          "5678abcd-12ab-34cd-ab56-123abc123abc"
        ]
      type: list
      elements: str
    "mac_address":
      description: Private NIC MAC address.
      sample: "12:34:ab:cd:1a:2b"
      type: str
    "modification_date":
      description: Private NIC last modified date.
      sample: "2026-04-09T00:00:01.000000+00:00"
      type: str
    "private_network_id":
      description: ID of the private Network the private NIC is attached to.
      sample: "1234abcd-12ab-12ab-12ab-123abc123abc"
      type: str
    "server_id":
      description: ID of the server which is used for request.
      sample: "1234ab-ab12-12ab-12a3-12345678ab9c"
      type: str
    "state":
      description: Private NIC state.
      sample: "available"
      type: str
    "tags":
      description: Tags associated with Private NIC.
      sample:
        [
          "main",
          "test"
        ]
      type: list
      elements: str
    "zone":
      description: The zone in which the Private NIC is located.
      sample: "fr-par-1"
      type: str
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.general.plugins.module_utils.scaleway import (
    SCALEWAY_LOCATION,
    Scaleway,
    ScalewayException,
    scaleway_argument_spec,
)


def list_strategy(api):
    private_nics = api.get(path=api.api_path)

    return private_nics.json


def core(module):
    region = module.params["region"]
    instance_id = module.params["instance_id"]

    module.params["api_url"] = SCALEWAY_LOCATION[region]["api_endpoint"]
    api = Scaleway(module=module)
    api.api_path = f"servers/{instance_id}/private_nics"

    try:
        list = list_strategy(api=api)
        module.exit_json(private_nics=list["private_nics"])
    except ScalewayException as exc:
        module.fail_json(msg=exc.message)


def main():
    argument_spec = scaleway_argument_spec()
    argument_spec.update(
        dict(region=dict(required=True, choices=list(SCALEWAY_LOCATION.keys())), instance_id=dict(required=True))
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    core(module)


if __name__ == "__main__":
    main()
