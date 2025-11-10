#!/usr/bin/python

# Copyright (c) 2014, Kim Nørgaard
# Written by Kim Nørgaard <jasen@jasen.dk>
# Based on pkgng module written by bleader <bleader@ratonland.org>
# that was based on pkgin module written by Shaun Zinck <shaun.zinck at gmail.com>
# that was based on pacman module written by Afterburn <https://github.com/afterburn>
# that was based on apt module written by Matthew Williams <matthew@flowroute.com>
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
module: slackpkg
short_description: Package manager for Slackware >= 12.2
description:
  - Manage binary packages for Slackware using C(slackpkg) which is available in versions after 12.2.
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
      - Name of package to install/remove.
    required: true
    type: list
    elements: str
    aliases: [pkg]

  state:
    description:
      - State of the package, you can use V(installed) as an alias for V(present) and V(removed) as one for V(absent).
    choices: ['present', 'absent', 'latest', 'installed', 'removed']
    default: present
    type: str

  update_cache:
    description:
      - Update the package database first.
    default: false
    type: bool

author: Kim Nørgaard (@KimNorgaard)
requirements: ["Slackware >= 12.2"]
"""

EXAMPLES = r"""
- name: Install package foo
  community.general.slackpkg:
    name: foo
    state: present

- name: Remove packages foo and bar
  community.general.slackpkg:
    name: foo,bar
    state: absent

- name: Make sure that it is the most updated package
  community.general.slackpkg:
    name: foo
    state: latest
"""

from ansible.module_utils.basic import AnsibleModule


def query_package(module, slackpkg_path, name):
    import platform
    import os
    import re

    machine = platform.machine()
    # Exception for kernel-headers package on x86_64
    if name == "kernel-headers" and machine == "x86_64":
        machine = "x86"
    pattern = re.compile(f"^{re.escape(name)}-[^-]+-({re.escape(machine)}|noarch|fw)-[^-]+$")
    packages = [f for f in os.listdir("/var/log/packages") if pattern.match(f)]

    if len(packages) > 0:
        return True

    return False


def remove_packages(module, slackpkg_path, packages):
    remove_c = 0
    # Using a for loop in case of error, we can report the package that failed
    for package in packages:
        # Query the package first, to see if we even need to remove
        if not query_package(module, slackpkg_path, package):
            continue

        if not module.check_mode:
            rc, out, err = module.run_command([slackpkg_path, "-default_answer=y", "-batch=on", "remove", package])

        if not module.check_mode and query_package(module, slackpkg_path, package):
            module.fail_json(msg=f"failed to remove {package}: {out}")

        remove_c += 1

    if remove_c > 0:
        module.exit_json(changed=True, msg=f"removed {remove_c} package(s)")

    module.exit_json(changed=False, msg="package(s) already absent")


def install_packages(module, slackpkg_path, packages):
    install_c = 0

    for package in packages:
        if query_package(module, slackpkg_path, package):
            continue

        if not module.check_mode:
            rc, out, err = module.run_command([slackpkg_path, "-default_answer=y", "-batch=on", "install", package])

        if not module.check_mode and not query_package(module, slackpkg_path, package):
            module.fail_json(msg=f"failed to install {package}: {out}", stderr=err)

        install_c += 1

    if install_c > 0:
        module.exit_json(changed=True, msg=f"present {install_c} package(s)")

    module.exit_json(changed=False, msg="package(s) already present")


def upgrade_packages(module, slackpkg_path, packages):
    install_c = 0

    for package in packages:
        if not module.check_mode:
            rc, out, err = module.run_command([slackpkg_path, "-default_answer=y", "-batch=on", "upgrade", package])

        if not module.check_mode and not query_package(module, slackpkg_path, package):
            module.fail_json(msg=f"failed to install {package}: {out}", stderr=err)

        install_c += 1

    if install_c > 0:
        module.exit_json(changed=True, msg=f"present {install_c} package(s)")

    module.exit_json(changed=False, msg="package(s) already present")


def update_cache(module, slackpkg_path):
    rc, out, err = module.run_command([slackpkg_path, "-batch=on", "update"])
    if rc != 0:
        module.fail_json(msg="Could not update package cache")


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default="present", choices=["installed", "removed", "absent", "present", "latest"]),
            name=dict(aliases=["pkg"], required=True, type="list", elements="str"),
            update_cache=dict(default=False, type="bool"),
        ),
        supports_check_mode=True,
    )

    slackpkg_path = module.get_bin_path("slackpkg", True)

    p = module.params

    pkgs = p["name"]

    if p["update_cache"]:
        update_cache(module, slackpkg_path)

    if p["state"] == "latest":
        upgrade_packages(module, slackpkg_path, pkgs)

    elif p["state"] in ["present", "installed"]:
        install_packages(module, slackpkg_path, pkgs)

    elif p["state"] in ["removed", "absent"]:
        remove_packages(module, slackpkg_path, pkgs)


if __name__ == "__main__":
    main()
