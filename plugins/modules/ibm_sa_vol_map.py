#!/usr/bin/python

# Copyright (C) 2018 IBM CORPORATION
# Author(s): Tzur Eliyahu <tzure@il.ibm.com>
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: ibm_sa_vol_map
short_description: Handles volume mapping on IBM Spectrum Accelerate Family storage systems

description:
  - This module maps volumes to or unmaps them from the hosts on IBM Spectrum Accelerate Family storage systems.
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none

options:
  vol:
    description:
      - Volume name.
    required: true
    type: str
  state:
    default: "present"
    choices: ["present", "absent"]
    description:
      - When the state is present the volume is mapped. When the state is absent, the volume is meant to be unmapped.
    type: str

  cluster:
    description:
      - Maps the volume to a cluster.
    type: str
  host:
    description:
      - Maps the volume to a host.
    type: str
  lun:
    description:
      - The LUN identifier.
    type: str
  override:
    description:
      - Overrides the existing volume mapping.
    type: str

extends_documentation_fragment:
  - community.general.ibm_storage
  - community.general.attributes

author:
  - Tzur Eliyahu (@tzure)
"""

EXAMPLES = r"""
- name: Map volume to host.
  community.general.ibm_sa_vol_map:
    vol: volume_name
    lun: 1
    host: host_name
    username: admin
    password: secret
    endpoints: hostdev-system
    state: present

- name: Map volume to cluster.
  community.general.ibm_sa_vol_map:
    vol: volume_name
    lun: 1
    cluster: cluster_name
    username: admin
    password: secret
    endpoints: hostdev-system
    state: present

- name: Unmap volume.
  community.general.ibm_sa_vol_map:
    host: host_name
    username: admin
    password: secret
    endpoints: hostdev-system
    state: absent
"""
RETURN = r"""
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.ibm_sa_utils import (
    execute_pyxcli_command,
    connect_ssl,
    spectrum_accelerate_spec,
    is_pyxcli_installed,
)


def main():
    argument_spec = spectrum_accelerate_spec()
    argument_spec.update(
        dict(
            state=dict(default="present", choices=["present", "absent"]),
            vol=dict(required=True),
            lun=dict(),
            cluster=dict(),
            host=dict(),
            override=dict(),
        )
    )

    module = AnsibleModule(argument_spec)
    is_pyxcli_installed(module)

    xcli_client = connect_ssl(module)
    # required args
    mapping = False
    try:
        mapped_hosts = xcli_client.cmd.vol_mapping_list(vol=module.params.get("vol")).as_list
        for host in mapped_hosts:
            if host["host"] == module.params.get("host", ""):
                mapping = True
    except Exception:
        pass
    state = module.params["state"]

    state_changed = False
    if state == "present" and not mapping:
        state_changed = execute_pyxcli_command(module, "map_vol", xcli_client)
    if state == "absent" and mapping:
        state_changed = execute_pyxcli_command(module, "unmap_vol", xcli_client)

    module.exit_json(changed=state_changed)


if __name__ == "__main__":
    main()
