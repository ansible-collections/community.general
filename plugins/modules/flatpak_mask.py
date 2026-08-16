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
  - This module masks flatpak applications, preventing them from being installed or updated.
  - It replicates the behavior of C(flatpak mask).
author:
  - Ilya Bogdanov (@zeerayne)
version_added: 13.3.0
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
      - The application ID or pattern to mask (for example C(org.gtk.Gtk3theme.Adwaita-dark)).
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
      - The installation method to use.
      - Defines if the C(flatpak) is supposed to be installed globally for the whole V(system) or only for the current V(user).
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
"""

from ansible_collections.community.general.plugins.module_utils._module_helper import StateModuleHelper


class FlatpakMask(StateModuleHelper):
    output_params = ("name", "state", "masked")
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
        self.vars.set("masked", self._check_is_masked(), change=True, diff=True)

    def _check_is_masked(self):
        check_cmd = [self.flatpak_bin, f"--{self.vars.method}", "mask"]

        rc, out, err = self.module.run_command(check_cmd)
        if rc != 0:
            self.do_raise(msg=f"Failed to query flatpak mask state: {err}", rc=rc, out=out, err=err)

        masked_apps = [line.strip() for line in out.splitlines()]
        return self.vars.name in masked_apps

    def _apply_mask(self):
        set_cmd = [self.flatpak_bin, "mask", self.vars.name]
        set_cmd.insert(1, f"--{self.vars.method}")

        rc, out, err = self.module.run_command(set_cmd)
        if rc != 0:
            self.do_raise(msg=f"Failed to mask flatpak app: {err}", rc=rc, out=out, err=err)

    def _apply_unmask(self):
        set_cmd = [self.flatpak_bin, "mask", "--remove", self.vars.name]
        set_cmd.insert(1, f"--{self.vars.method}")

        rc, out, err = self.module.run_command(set_cmd)
        if rc != 0:
            self.do_raise(msg=f"Failed to unmask flatpak app: {err}", rc=rc, out=out, err=err)

    def state_present(self):
        if self.vars.masked:
            return

        self.changed = True
        self.vars.masked = True
        if self.check_mode:
            return
        self._apply_mask()

    def state_absent(self):
        if not self.vars.masked:
            return

        self.changed = True
        self.vars.masked = False
        if self.check_mode:
            return
        self._apply_unmask()


def main():
    FlatpakMask.execute()


if __name__ == "__main__":
    main()
