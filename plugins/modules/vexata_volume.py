#!/usr/bin/python

# Copyright (c) 2019, Sandeep Kasargod (sandeep@vexata.com)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
module: vexata_volume
short_description: Manage volumes on Vexata VX100 storage arrays
description:
  - Create, deletes or extend volumes on a Vexata VX100 array.
author:
  - Sandeep Kasargod (@vexata)
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  name:
    description:
      - Volume name.
    required: true
    type: str
  state:
    description:
      - Creates/Modifies volume when present or removes when absent.
    default: present
    choices: [present, absent]
    type: str
  size:
    description:
      - Volume size in M, G, T units. M=2^20, G=2^30, T=2^40 bytes.
    type: str
extends_documentation_fragment:
  - community.general.vexata.vx100
  - community.general.attributes
"""

EXAMPLES = r"""
- name: Create new 2 TiB volume named foo
  community.general.vexata_volume:
    name: foo
    size: 2T
    state: present
    array: vx100_ultra.test.com
    user: admin
    password: secret

- name: Expand volume named foo to 4 TiB
  community.general.vexata_volume:
    name: foo
    size: 4T
    state: present
    array: vx100_ultra.test.com
    user: admin
    password: secret

- name: Delete volume named foo
  community.general.vexata_volume:
    name: foo
    state: absent
    array: vx100_ultra.test.com
    user: admin
    password: secret
"""

RETURN = r"""
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.vexata import (
    argument_spec,
    get_array,
    required_together,
    size_to_MiB,
)


def get_volume(module, array):
    """Retrieve a named volume if it exists, None if absent."""
    name = module.params["name"]
    try:
        vols = array.list_volumes()
        vol = [v for v in vols if v["name"] == name]
        if len(vol) == 1:
            return vol[0]
        else:
            return None
    except Exception:
        module.fail_json(msg="Error while attempting to retrieve volumes.")


def validate_size(module, err_msg):
    size = module.params.get("size", False)
    if not size:
        module.fail_json(msg=err_msg)
    size = size_to_MiB(size)
    if size <= 0:
        module.fail_json(msg="Invalid volume size, must be <integer>[MGT].")
    return size


def create_volume(module, array):
    """ "Create a new volume."""
    changed = False
    size = validate_size(module, err_msg="Size is required to create volume.")
    if module.check_mode:
        module.exit_json(changed=changed)

    try:
        vol = array.create_volume(module.params["name"], "Ansible volume", size)
        if vol:
            module.log(msg=f"Created volume {vol['id']}")
            changed = True
        else:
            module.fail_json(msg="Volume create failed.")
    except Exception:
        pass
    module.exit_json(changed=changed)


def update_volume(module, array, volume):
    """Expand the volume size."""
    changed = False
    size = validate_size(module, err_msg="Size is required to update volume")
    prev_size = volume["volSize"]
    if size <= prev_size:
        module.log(msg="Volume expanded size needs to be larger than current size.")
    if module.check_mode:
        module.exit_json(changed=changed)

    try:
        vol = array.grow_volume(volume["name"], volume["description"], volume["id"], size)
        if vol:
            changed = True
    except Exception:
        pass

    module.exit_json(changed=changed)


def delete_volume(module, array, volume):
    changed = False
    vol_name = volume["name"]
    if module.check_mode:
        module.exit_json(changed=changed)

    try:
        ok = array.delete_volume(volume["id"])
        if ok:
            module.log(msg=f"Volume {vol_name} deleted.")
            changed = True
        else:
            raise Exception
    except Exception:
        pass
    module.exit_json(changed=changed)


def main():
    arg_spec = argument_spec()
    arg_spec.update(
        dict(
            name=dict(type="str", required=True),
            state=dict(default="present", choices=["present", "absent"]),
            size=dict(type="str"),
        )
    )

    module = AnsibleModule(arg_spec, supports_check_mode=True, required_together=required_together())

    state = module.params["state"]
    array = get_array(module)
    volume = get_volume(module, array)

    if state == "present":
        if not volume:
            create_volume(module, array)
        else:
            update_volume(module, array, volume)
    elif state == "absent" and volume:
        delete_volume(module, array, volume)
    else:
        module.exit_json(changed=False)


if __name__ == "__main__":
    main()
