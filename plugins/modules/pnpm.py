#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2023 Aritra Sen <aretrosen@proton.me>
# Copyright (c) 2017 Chris Hoffman <christopher.hoffman@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: pnpm
short_description: Manage node.js packages with pnpm
description:
  - Manage node.js packages with the pnpm package manager (https://pnpm.io/)
author:
  - "Aritra Sen (@aretrosen)"
  - "Chris Hoffman (@chrishoffman), creator of NPM Ansible module)"
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
      - The name of a node.js library to install
      - All packages in package.json are installed if not provided.
    type: str
    required: false
  path:
    description:
      - The base path to install the node.js libraries.
    type: path
    required: false
  version:
    description:
      - The version of the library to be installed, in semver format.
    type: str
    required: false
  global:
    description:
      - Install the node.js library globally
    required: false
    default: false
    type: bool
  executable:
    description:
      - The executable location for pnpm.
      - The default location it searches for is $PNPM_HOME, fails if not set.
    type: path
    required: false
  ignore_scripts:
    description:
      - Use the --ignore-scripts flag when installing.
    required: false
    type: bool
    default: false
  no_optional:
    description:
      - Don't install optional packages, equivalent to --no-optional.
    required: false
    type: bool
    default: false
  production:
    description:
      - Install dependencies in production mode.
      - Pnpm will ignore any dependencies under devDependencies in package.json
    required: false
    type: bool
    default: false
  dev:
    description:
      - Install dependencies in development mode.
      - Pnpm will ignore any regular dependencies in package.json
    required: false
    default: false
    type: bool
  optional:
    description:
      - Install dependencies in optional mode.
    required: false
    default: false
    type: bool
  state:
    description:
      - Installation state of the named node.js library
      - If absent is selected, a name option must be provided
    type: str
    required: false
    default: present
    choices: [ "present", "absent", "latest" ]
requirements:
    - Pnpm executable present in $PATH, preferably as $PNPM_HOME.
"""

EXAMPLES = """
- name: Install "tailwindcss" node.js package.
  community.general.pnpm:
    name: tailwindcss
    path: /app/location

- name: Install "tailwindcss" node.js package on version 3.3.2
  community.general.pnpm:
    name: tailwindcss
    version: '3.3.2'
    path: /app/location

- name: Install "tailwindcss" node.js package globally.
  community.general.pnpm:
    name: tailwindcss
    global: true

- name: Install "tailwindcss" node.js package as dev dependency.
  community.general.pnpm:
    name: tailwindcss
    path: /app/location
    dev: true

- name: Install "tailwindcss" node.js package as optional dependency.
  community.general.pnpm:
    name: tailwindcss
    path: /app/location
    optional: true

- name: Remove the globally-installed package "tailwindcss".
  community.general.pnpm:
    name: tailwindcss
    global: true
    state: absent

- name: Install packages based on package.json.
  community.general.pnpm:
    path: /app/location

- name: Update all packages in package.json to their latest version.
  community.general.pnpm:
    path: /app/location
    state: latest
"""
import json
import os

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native


class Pnpm(object):
    def __init__(self, module, **kwargs):
        self.module = module
        self.name = kwargs["name"]
        self.path = kwargs["path"]
        self.globally = kwargs["globally"]
        self.executable = kwargs["executable"]
        self.ignore_scripts = kwargs["ignore_scripts"]
        self.no_optional = kwargs["no_optional"]
        self.production = kwargs["production"]
        self.dev = kwargs["dev"]
        self.optional = kwargs["optional"]

        self.name_version = None

        if self.name is not None:
            self.name_version = self.name
            if kwargs["version"]:
                self.name_version = self.name_version + "@" + str(self.version)

    def _exec(self, args, run_in_check_mode=False, check_rc=True):
        if not self.module.check_mode or (self.module.check_mode and run_in_check_mode):
            cmd = self.executable + args

            if self.globally:
                cmd.append("-g")

            if self.ignore_scripts:
                cmd.append("--ignore-scripts")

            if self.no_optional:
                cmd.append("--no-optional")

            if self.production:
                cmd.append("-P")

            if self.dev:
                cmd.append("-D")

            if self.name and self.optional:
                cmd.append("-O")

            # If path is specified, cd into that path and run the command.
            cwd = None
            if self.path:
                if not os.path.exists(self.path):
                    os.makedirs(self.path)

                if not os.path.isdir(self.path):
                    self.module.fail_json(msg="path %s is not a directory" % self.path)

                if not self.name_version and not os.path.isfile(
                    os.path.join(self.path, "package.json")
                ):
                    self.module.fail_json(
                        msg="package.json does not exist in provided path"
                    )

                cwd = self.path

            _rc, out, err = self.module.run_command(cmd, check_rc=check_rc, cwd=cwd)
            return out, err

        return "", ""

    def missing(self):
        if not os.path.isfile(os.path.join(self.path, "pnpm-lock.yaml")):
            return True

        cmd = ["list", "--json"]
        try:
            _exe, err = self._exec(cmd, True, False)
            if err:
                raise Exception(err)
            data = json.loads(_exe or "{}")
        except Exception as e:
            self.module.fail_json(
                msg="Failed to parse pnpm output with error %s" % to_native(e)
            )

        for typedep in [
            "dependencies",
            "devDependencies",
            "optionalDependencies",
            "unsavedDependencies",
        ]:
            if typedep not in data[0]:
                continue

            for dep, props in data[0][typedep].items():
                if self.name_version == dep:
                    return False

                if "version" in props and props["version"]:
                    dep_version = dep + "@" + str(props["version"])
                    if self.name_version == dep_version:
                        return False

        return True

    def install(self):
        if self.name_version:
            return self._exec(["add", self.name_version])
        return self._exec(["install"])

    def update(self):
        return self._exec(["update"])

    def uninstall(self):
        return self._exec(["remove", self.name])

    def list_outdated(self):
        if not os.path.isfile(os.path.join(self.path, "pnpm-lock.yaml")):
            return list()

        cmd = ["outdated", "--format", "json"]
        try:
            _exe, err = self._exec(cmd, True, False)
            if err:
                raise Exception(err)
            data = json.loads(_exe or "{}")
        except Exception as e:
            self.module.fail_json(
                msg="Failed to parse pnpm output with error %s" % to_native(e)
            )

        return list(data.items().keys())


def main():
    arg_spec = dict(
        name=dict(default=None),
        path=dict(default=None, type="path"),
        version=dict(default=None),
        executable=dict(default=None, type="path"),
        ignore_scripts=dict(default=False, type="bool"),
        no_optional=dict(default=False, type="bool"),
        production=dict(default=False, type="bool"),
        dev=dict(default=False, type="bool"),
        optional=dict(default=False, type="bool"),
        state=dict(default="present", choices=["present", "absent", "latest"]),
    )
    arg_spec["global"] = dict(default=False, type="bool")
    module = AnsibleModule(argument_spec=arg_spec, supports_check_mode=True)

    name = module.params["name"]
    path = module.params["path"]
    version = module.params["version"]
    globally = module.params["global"]
    ignore_scripts = module.params["ignore_scripts"]
    no_optional = module.params["no_optional"]
    production = module.params["production"]
    dev = module.params["dev"]
    optional = module.params["optional"]
    state = module.params["state"]

    if module.params["executable"]:
        executable = module.params["executable"].split(" ")
    else:
        executable = [module.get_bin_path("pnpm", True)]

    if not name and version:
        module.fail_json(
            msg="version has no meaning when the package name is not provided"
        )

    if path is None and globally is False:
        module.fail_json(msg="path must be specified when not using global")
    elif path and globally is True:
        module.fail_json(msg="cannot specify path if doing global installation")

    if globally and (production or dev or optional):
        module.fail_json(
            msg="production, dev, and optional makes no sense when installing packages globally"
        )

    if name and globally and path:
        module.fail_json(msg="path should not be mentioned when installing globally")

    if production and dev and optional:
        module.fail_json(
            msg="production and dev and optional options don't go together"
        )

    if production and dev:
        module.fail_json(msg="production and dev options don't go together")

    if production and optional:
        module.fail_json(msg="production and optional options don't go together")

    if dev and optional:
        module.fail_json(msg="dev and optional options don't go together")

    if name and name[0:4] == "http" and version:
        module.fail_json(msg="semver not supported on remote url downloads")

    if not name and optional:
        module.fail_json(
            msg="optional not available when package name not provided, use no_optional instead"
        )

    if state == "absent" and not name:
        module.fail_json(msg="package name is required for uninstalling")

    if state == "latest":
        version = "latest"

    if globally:
        _rc, out, _err = module.run_command(executable + ["root", "-g"], check_rc=True)
        path, _tail = os.path.split(out.strip())

    pnpm = Pnpm(
        module,
        name=name,
        path=path,
        version=version,
        globally=globally,
        executable=executable,
        ignore_scripts=ignore_scripts,
        no_optional=no_optional,
        production=production,
        dev=dev,
        optional=optional,
    )

    changed = False
    out = ""
    err = ""
    if state == "present":
        if not name:
            changed = True
            out, err = pnpm.install()
        else:
            missing = pnpm.missing()
            if missing:
                changed = True
                out, err = pnpm.install()
    elif state == "latest":
        outdated = pnpm.list_outdated()
        if name:
            missing = pnpm.missing()
            if missing or name in outdated:
                changed = True
                out, err = pnpm.install()
        elif len(outdated):
            changed = True
            out, err = pnpm.update()
    else:  # absent
        missing = pnpm.missing()
        if not missing:
            changed = True
            out, err = pnpm.uninstall()

    module.exit_json(changed=changed, out=out, err=err)


if __name__ == "__main__":
    main()
