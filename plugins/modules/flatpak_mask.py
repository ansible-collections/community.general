#!/usr/bin/python

# Copyright (c) 2026 Ilya Bogdanov (@zeerayne) <zeerayne1337@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
---
module: flatpak_mask
short_description: Mask Flatpak applications
description:
  - This module masks Flatpak applications, preventing them from being installed or updated.
  - It encapsulates the behavior of C(flatpak mask).
author:
  - Ilya Bogdanov (@zeerayne)
version_added: 13.4.0
requirements:
  - flatpak
extends_documentation_fragment:
  - community.general._attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  name:
    description:
      - The application ID or pattern to mask (for example V(org.gtk.Gtk3theme.Adwaita-dark)).
    required: true
    type: str
    aliases: [app]
  state:
    description:
      - Whether the application should be masked (V(present)) or unmasked (V(absent)).
    type: str
    choices: [present, absent]
    default: present
  method:
    description:
      - Defines whether the mask or unmask operation applies system-wide (V(system)) or only to the current user (V(user)).
    type: str
    choices: [system, user]
    default: system
"""

EXAMPLES = r"""
- name: Mask flatpak gtk theme
  flatpak_mask:
    name: "org.gtk.Gtk3theme.Adwaita-dark"

- name: Unmask flatpak gtk theme
  flatpak_mask:
    name: "org.gtk.Gtk3theme.Adwaita-dark"
    state: absent

- name: Mask flatpak applications matching a pattern
  flatpak_mask:
    name: "org.gtk.*"

- name: Mask a flatpak application for the current user only
  flatpak_mask:
    name: "org.gtk.Gtk3theme.Adwaita-dark"
    method: user
"""

from ansible_collections.community.general.plugins.module_utils._module_helper import StateModuleHelper


class FlatpakMask(StateModuleHelper):
    output_params = ("name", "state", "method")
    module = dict(
        argument_spec=dict(
            name=dict(type="str", required=True, aliases=["app"]),
            state=dict(type="str", default="present", choices=["present", "absent"]),
            method=dict(type="str", default="system", choices=["user", "system"]),
        ),
        supports_check_mode=True,
    )

    def __init_module__(self):
        self.flatpak_bin = self.get_bin_path("flatpak", required=True)
        self.vars.set("masked", self.check_is_masked(), change=True)
        self.vars.masked = self.vars.state == "present"

    def check_is_masked(self):
        check_cmd = [self.flatpak_bin, f"--{self.vars.method}", "mask"]

        rc, out, err = self.module.run_command(check_cmd)
        if rc != 0:
            self.do_raise(msg="Failed to query flatpak mask state", rc=rc, stdout=out, stderr=err)

        masked_apps = [line.strip() for line in out.splitlines()]
        return self.vars.name in masked_apps

    def apply_mask(self):
        set_cmd = [self.flatpak_bin, f"--{self.vars.method}", "mask", self.vars.name]

        rc, out, err = self.module.run_command(set_cmd)
        if rc != 0:
            self.do_raise(msg="Failed to mask flatpak app", rc=rc, stdout=out, stderr=err)

    def apply_unmask(self):
        set_cmd = [self.flatpak_bin, f"--{self.vars.method}", "mask", "--remove", self.vars.name]

        rc, out, err = self.module.run_command(set_cmd)
        if rc != 0:
            self.do_raise(msg="Failed to unmask flatpak app", rc=rc, stdout=out, stderr=err)

    def state_present(self):
        if self.vars.has_changed and not self.check_mode:
            self.apply_mask()

    def state_absent(self):
        self.vars.masked = False
        if not self.vars.has_changed:
            return
        if not self.check_mode:
            self.apply_unmask()


def main():
    FlatpakMask.execute()


if __name__ == "__main__":
    main()
