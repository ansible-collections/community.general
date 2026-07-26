#!/usr/bin/python

# Copyright (c) 2026 Ilya Bogdanov (@zeerayne) <zeerayne1337@gmail.com>
# Copyright (c) 2026 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
---
module: flatpak_mask
short_description: Mask flatpak applications
description:
  - This module masks flatpak applications, preventing them from being installed or updated.
  - It replicates the behavior of "flatpak mask".
options:
  name:
    description:
      - The application ID or pattern to mask (e.g., org.gtk.Gtk3theme.Adwaita-dark).
    required: true
    type: str
    aliases: [ app ]
  state:
    description:
      - Whether the application should be masked (present) or unmasked (absent).
    type: str
    choices: [ present, absent ]
    default: present
  method:
    description:
      - The installation method to use.
      - Defines if the C(flatpak) is supposed to be installed globally for the whole V(system) or only for the current V(user).
    type: str
    choices: [system, user]
    default: system
author:
  - Automation
"""

EXAMPLES = r"""
- name: Mask flatpak gtk theme
  flatpak_mask:
    name: "org.gtk.Gtk3theme.Adwaita-dark"

- name: Unmask flatpak gtk theme
  flatpak_mask:
    name: "org.gtk.Gtk3theme.Adwaita-dark"
    state: absent
"""

from ansible.module_utils.basic import AnsibleModule


class FlatpakMaskModule(AnsibleModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                name=dict(type="str", required=True, aliases=["app"]),
                state=dict(type="str", default="present", choices=["present", "absent"]),
                method=dict(type="str", default="system", choices=["user", "system"]),
            ),
            supports_check_mode=True
        )

        self.app_name = self.params["name"]
        self.state = self.params["state"]
        self.method = self.params["method"]
        self.flatpak_bin = self.get_bin_path("flatpak", required=True)

    def check_is_masked(self):
        check_cmd = [self.flatpak_bin, "mask"]
        check_cmd.insert(1, f"--{self.method}")

        rc, out, err = self.run_command(check_cmd)
        
        masked_apps = [line.strip() for line in out.splitlines()]
        return self.app_name in masked_apps

    def apply_mask(self):
        set_cmd = [self.flatpak_bin, "mask", self.app_name]
        set_cmd.insert(1, f"--{self.method}")
        
        rc, out, err = self.run_command(set_cmd)
        if rc != 0:
            self.fail_json(msg=f"Failed to mask flatpak app: {err}", rc=rc, out=out, err=err)

    def apply_unmask(self):
        set_cmd = [self.flatpak_bin, "mask", "--remove", self.app_name]
        set_cmd.insert(1, f"--{self.method}")
        
        rc, out, err = self.run_command(set_cmd)
        if rc != 0:
            self.fail_json(msg=f"Failed to unmask flatpak app: {err}", rc=rc, out=out, err=err)

    def run(self):
        is_masked = self.check_is_masked()
        changed = False

        if self.state == "present" and not is_masked:
            changed = True
        elif self.state == "absent" and is_masked:
            changed = True

        if self.check_mode:
            self.exit_json(changed=changed)

        if changed:
            if self.state == "present":
                self.apply_mask()
            else:
                self.apply_unmask()
            
        self.exit_json(
            changed=changed, 
            name=self.app_name, 
            state=self.state,
            masked=(self.state == "present")
        )

def main():
    module = FlatpakMaskModule()
    module.run()

if __name__ == "__main__":
    main()
