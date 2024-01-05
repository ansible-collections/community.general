#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 Radek Sprta <mail@radeksprta.eu>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: cargo
short_description: Manage Rust packages with cargo
version_added: 4.3.0
description:
  - Manage Rust packages with cargo.
author: "Radek Sprta (@radek-sprta)"
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  executable:
    description:
      - Path to the C(cargo) installed in the system.
      - If not specified, the module will look C(cargo) in E(PATH).
    type: path
    version_added: 7.5.0
  name:
    description:
      - The name of a Rust package to install.
    type: list
    elements: str
    required: true
  path:
    description:
      ->
      The base path where to install the Rust packages. Cargo automatically appends
      V(/bin). In other words, V(/usr/local) will become V(/usr/local/bin).
    type: path
  registry:
    description:
      - Specify which registry to use.
      - This is used only when installing new packages or installing another version of a package.
    required: false
    type: str
    version_added: 8.3.0
  version:
    description:
      ->
      The version to install. If O(name) contains multiple values, the module will
      try to install all of them in this version.
    type: str
    required: false
  locked:
    description:
      - Install with locked dependencies.
      - This is only used when installing packages.
    required: false
    type: bool
    default: false
    version_added: 7.5.0
  state:
    description:
      - The state of the Rust package.
    required: false
    type: str
    default: present
    choices: [ "present", "absent", "latest" ]
requirements:
    - cargo installed
"""

EXAMPLES = r"""
- name: Install "ludusavi" Rust package
  community.general.cargo:
    name: ludusavi

- name: Install "ludusavi" Rust package with locked dependencies
  community.general.cargo:
    name: ludusavi
    locked: true

- name: Install "ludusavi" Rust package in version 0.10.0
  community.general.cargo:
    name: ludusavi
    version: '0.10.0'

- name: Install "ludusavi" Rust package to global location
  community.general.cargo:
    name: ludusavi
    path: /usr/local

- name: Remove "ludusavi" Rust package
  community.general.cargo:
    name: ludusavi
    state: absent

- name: Update "ludusavi" Rust package its latest version
  community.general.cargo:
    name: ludusavi
    state: latest

- name: Install "ludusavi" Rust package from "private" registry
  community.general.cargo:
    name: ludusavi
    registry: private
    state: latest
"""

import collections
import os
import re

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils import toml


PackageInfo = collections.namedtuple("PackageInfo", ["version", "registry_url"])


class CargoError(Exception):
    pass


class Cargo(object):
    def __init__(self, module, **kwargs):
        self.module = module
        self.executable = [kwargs["executable"] or module.get_bin_path("cargo", True)]
        self.name = kwargs["name"]
        self.path = kwargs["path"]
        self.registry = kwargs["registry"]
        self.state = kwargs["state"]
        self.version = kwargs["version"]
        self.locked = kwargs["locked"]

    @property
    def config_path(self):
        return os.path.expanduser("~/.cargo/config.toml")

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        if path is not None and not os.path.isdir(path):
            self.module.fail_json(msg="Path %s is not a directory" % path)
        self._path = path

    def _exec(
        self, args, run_in_check_mode=False, check_rc=True, add_package_name=True
    ):
        if not self.module.check_mode or (self.module.check_mode and run_in_check_mode):
            cmd = self.executable + args
            rc, out, err = self.module.run_command(cmd, check_rc=check_rc)
            return out, err
        return "", ""

    def get_installed(self):
        cmd = ["install", "--list"]
        data, dummy = self._exec(cmd, True, False, False)

        package_regex = re.compile(r"^([\w\-]+) v(.+?)(?: \(registry `(.+)`\))?:$")

        installed = {}
        for line in data.splitlines():
            package_match = package_regex.match(line)
            if package_match:
                package_name = package_match.group(1)
                package_info = PackageInfo(
                    version=package_match.group(2),
                    registry_url=package_match.group(3),
                )
                installed[package_name] = package_info

        return installed

    def get_registry_url_from_name(self, name):
        cargo_config = toml.load_toml(self.config_path)
        try:
            url = cargo_config['registries'][name]['index']
        except KeyError:
            raise CargoError("Registry {} not found in {}".format(name, self.config_path))
        return url

    def install(self, packages=None):
        cmd = ["install"]
        cmd.extend(packages or self.name)
        if self.locked:
            cmd.append("--locked")
        if self.path:
            cmd.append("--root")
            cmd.append(self.path)
        if self.registry:
            cmd.append("--registry")
            cmd.append(self.registry)
        if self.version:
            cmd.append("--version")
            cmd.append(self.version)
        return self._exec(cmd)

    def is_outdated(self, name):
        installed_version = self.get_installed().get(name).version

        cmd = ["search", name, "--limit", "1"]
        data, dummy = self._exec(cmd, True, False, False)

        match = re.search(r'"(.+)"', data)
        if match:
            latest_version = match.group(1)

        return installed_version != latest_version

    def uninstall(self, packages=None):
        cmd = ["uninstall"]
        cmd.extend(packages or self.name)
        return self._exec(cmd)


def main():
    arg_spec = dict(
        executable=dict(default=None, type="path"),
        name=dict(required=True, type="list", elements="str"),
        path=dict(default=None, type="path"), registry=dict(default=None, type="str"),
        state=dict(default="present", choices=["present", "absent", "latest"]),
        version=dict(default=None, type="str"),
        locked=dict(default=False, type="bool"),
    )
    module = AnsibleModule(argument_spec=arg_spec, supports_check_mode=True)

    name = module.params["name"]
    registry = module.params["registry"]
    state = module.params["state"]
    version = module.params["version"]

    if not name:
        module.fail_json(msg="Package name must be specified")

    # Set LANG env since we parse stdout
    module.run_command_environ_update = dict(
        LANG="C", LC_ALL="C", LC_MESSAGES="C", LC_CTYPE="C"
    )

    cargo = Cargo(module, **module.params)
    changed, out, err = False, None, None
    installed_packages = cargo.get_installed()
    if state == "present":
        to_install = [
            n
            for n in name
            if (n not in installed_packages)
            or (version and version != installed_packages[n].version)
            or (registry and cargo.get_registry_url_from_name(registry) != installed_packages[n].registry_url)
        ]
        if to_install:
            changed = True
            out, err = cargo.install(to_install)
    elif state == "latest":
        to_update = [
            n for n in name if n not in installed_packages or cargo.is_outdated(n)
        ]
        if to_update:
            changed = True
            out, err = cargo.install(to_update)
    else:  # absent
        to_uninstall = [n for n in name if n in installed_packages]
        if to_uninstall:
            changed = True
            out, err = cargo.uninstall(to_uninstall)

    module.exit_json(changed=changed, stdout=out, stderr=err)


if __name__ == "__main__":
    main()
