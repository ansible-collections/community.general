#!/usr/bin/python

# Copyright (c) 2018, Bruce Smith <Bruce.Smith.IT@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: nictagadm
short_description: Manage nic tags on SmartOS systems
description:
  - Create or delete nic tags on SmartOS systems.
author:
  - Bruce Smith (@SmithX10)
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  name:
    description:
      - Name of the nic tag.
    required: true
    type: str
  mac:
    description:
      - Specifies the O(mac) address to attach the nic tag to when not creating an O(etherstub).
      - Parameters O(mac) and O(etherstub) are mutually exclusive.
    type: str
  etherstub:
    description:
      - Specifies that the nic tag is attached to a created O(etherstub).
      - Parameter O(etherstub) is mutually exclusive with both O(mtu), and O(mac).
    type: bool
    default: false
  mtu:
    description:
      - Specifies the size of the O(mtu) of the desired nic tag.
      - Parameters O(mtu) and O(etherstub) are mutually exclusive.
    type: int
  force:
    description:
      - When O(state=absent) this switch uses the C(-f) parameter and delete the nic tag regardless of existing VMs.
    type: bool
    default: false
  state:
    description:
      - Create or delete a SmartOS nic tag.
    type: str
    choices: [absent, present]
    default: present
"""

EXAMPLES = r"""
- name: Create 'storage0' on '00:1b:21:a3:f5:4d'
  community.general.nictagadm:
    name: storage0
    mac: 00:1b:21:a3:f5:4d
    mtu: 9000
    state: present

- name: Remove 'storage0' nic tag
  community.general.nictagadm:
    name: storage0
    state: absent
"""

RETURN = r"""
name:
  description: Nic tag name.
  returned: always
  type: str
  sample: storage0
mac:
  description: MAC Address that the nic tag was attached to.
  returned: always
  type: str
  sample: 00:1b:21:a3:f5:4d
etherstub:
  description: Specifies if the nic tag was created and attached to an etherstub.
  returned: always
  type: bool
  sample: false
mtu:
  description: Specifies which MTU size was passed during the nictagadm add command. mtu and etherstub are mutually exclusive.
  returned: always
  type: int
  sample: 1500
force:
  description: Shows if C(-f) was used during the deletion of a nic tag.
  returned: always
  type: bool
  sample: false
state:
  description: State of the target.
  returned: always
  type: str
  sample: present
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.network import is_mac


class NicTag:
    def __init__(self, module):
        self.module = module

        self.name = module.params["name"]
        self.mac = module.params["mac"]
        self.etherstub = module.params["etherstub"]
        self.mtu = module.params["mtu"]
        self.force = module.params["force"]
        self.state = module.params["state"]

        self.nictagadm_bin = self.module.get_bin_path("nictagadm", True)

    def is_valid_mac(self):
        return is_mac(self.mac.lower())

    def nictag_exists(self):
        cmd = [self.nictagadm_bin, "exists", self.name]
        (rc, dummy, dummy) = self.module.run_command(cmd)

        return rc == 0

    def add_nictag(self):
        cmd = [self.nictagadm_bin, "-v", "add"]

        if self.etherstub:
            cmd.append("-l")

        if self.mtu:
            cmd.append("-p")
            cmd.append(f"mtu={self.mtu}")

        if self.mac:
            cmd.append("-p")
            cmd.append(f"mac={self.mac}")

        cmd.append(self.name)

        return self.module.run_command(cmd)

    def delete_nictag(self):
        cmd = [self.nictagadm_bin, "-v", "delete"]

        if self.force:
            cmd.append("-f")

        cmd.append(self.name)

        return self.module.run_command(cmd)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type="str", required=True),
            mac=dict(type="str"),
            etherstub=dict(type="bool", default=False),
            mtu=dict(type="int"),
            force=dict(type="bool", default=False),
            state=dict(type="str", default="present", choices=["absent", "present"]),
        ),
        mutually_exclusive=[
            ["etherstub", "mac"],
            ["etherstub", "mtu"],
        ],
        required_if=[
            ["etherstub", False, ["name", "mac"]],
            ["state", "absent", ["name", "force"]],
        ],
        supports_check_mode=True,
    )

    nictag = NicTag(module)

    rc = None
    out = ""
    err = ""
    result = dict(
        changed=False,
        etherstub=nictag.etherstub,
        force=nictag.force,
        name=nictag.name,
        mac=nictag.mac,
        mtu=nictag.mtu,
        state=nictag.state,
    )

    if not nictag.is_valid_mac():
        module.fail_json(msg="Invalid MAC Address Value", name=nictag.name, mac=nictag.mac, etherstub=nictag.etherstub)

    if nictag.state == "absent":
        if nictag.nictag_exists():
            if module.check_mode:
                module.exit_json(changed=True)
            (rc, out, err) = nictag.delete_nictag()
            if rc != 0:
                module.fail_json(name=nictag.name, msg=err, rc=rc)
    elif nictag.state == "present":
        if not nictag.nictag_exists():
            if module.check_mode:
                module.exit_json(changed=True)
            (rc, out, err) = nictag.add_nictag()
            if rc is not None and rc != 0:
                module.fail_json(name=nictag.name, msg=err, rc=rc)

    if rc is not None:
        result["changed"] = True
    if out:
        result["stdout"] = out
    if err:
        result["stderr"] = err

    module.exit_json(**result)


if __name__ == "__main__":
    main()
