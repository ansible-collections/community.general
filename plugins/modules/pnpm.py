#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2023 Aritra Sen <aretrosen@proton.me>
# Copyright (c) 2017 Chris Hoffman <christopher.hoffman@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: pnpm
short_description: Manage Node.js packages with C(pnpm)
version_added: 7.4.0
description:
  - Manage Node.js packages with the L(pnpm package manager, https://pnpm.io/).
author:
  - "Aritra Sen (@aretrosen)"
  - "Chris Hoffman (@chrishoffman), creator of NPM Ansible module"
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
      - The name of a Node.js library to install.
      - All packages in C(package.json) are installed if not provided.
    type: str
    required: false
  alias:
    description:
      - Alias of the Node.js library.
    type: str
    required: false
  path:
    description:
      - The base path to install the Node.js libraries.
    type: path
    required: false
  version:
    description:
      - The version of the library to be installed, in semver format.
    type: str
    required: false
  global:
    description:
      - Install the Node.js library globally.
    required: false
    default: false
    type: bool
  executable:
    description:
      - The executable location for pnpm.
      - The default location it searches for is E(PATH), fails if not set.
    type: path
    required: false
  ignore_scripts:
    description:
      - Use the C(--ignore-scripts) flag when installing.
    required: false
    type: bool
    default: false
  no_optional:
    description:
      - Do not install optional packages, equivalent to C(--no-optional).
    required: false
    type: bool
    default: false
  production:
    description:
      - Install dependencies in production mode.
      - Pnpm ignores any dependencies under C(devDependencies) in package.json.
    required: false
    type: bool
    default: false
  dev:
    description:
      - Install dependencies in development mode.
      - Pnpm ignores any regular dependencies in C(package.json).
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
      - Installation state of the named Node.js library.
      - If V(absent) is selected, a name option must be provided.
    type: str
    required: false
    default: present
    choices: ["present", "absent", "latest"]
requirements:
  - Pnpm executable present in E(PATH).
"""

EXAMPLES = r"""
- name: Install "tailwindcss" Node.js package.
  community.general.pnpm:
    name: tailwindcss
    path: /app/location

- name: Install "tailwindcss" Node.js package on version 3.3.2
  community.general.pnpm:
    name: tailwindcss
    version: 3.3.2
    path: /app/location

- name: Install "tailwindcss" Node.js package globally.
  community.general.pnpm:
    name: tailwindcss
    global: true

- name: Install "tailwindcss" Node.js package as dev dependency.
  community.general.pnpm:
    name: tailwindcss
    path: /app/location
    dev: true

- name: Install "tailwindcss" Node.js package as optional dependency.
  community.general.pnpm:
    name: tailwindcss
    path: /app/location
    optional: true

- name: Install "tailwindcss" Node.js package version 0.1.3 as tailwind-1
  community.general.pnpm:
    name: tailwindcss
    alias: tailwind-1
    version: 0.1.3
    path: /app/location

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
        self.alias = kwargs["alias"]
        self.version = kwargs["version"]
        self.path = kwargs["path"]
        self.globally = kwargs["globally"]
        self.executable = kwargs["executable"]
        self.ignore_scripts = kwargs["ignore_scripts"]
        self.no_optional = kwargs["no_optional"]
        self.production = kwargs["production"]
        self.dev = kwargs["dev"]
        self.optional = kwargs["optional"]

        self.alias_name_ver = None

        if self.alias is not None:
            self.alias_name_ver = self.alias + "@npm:"

        if self.name is not None:
            self.alias_name_ver = (self.alias_name_ver or "") + self.name
            if self.version is not None:
                self.alias_name_ver = self.alias_name_ver + "@" + str(self.version)
            else:
                self.alias_name_ver = self.alias_name_ver + "@latest"

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
                    self.module.fail_json(msg="Path %s is not a directory" % self.path)

                if not self.alias_name_ver and not os.path.isfile(
                    os.path.join(self.path, "package.json")
                ):
                    self.module.fail_json(
                        msg="package.json does not exist in provided path"
                    )

                cwd = self.path

            _rc, out, err = self.module.run_command(cmd, check_rc=check_rc, cwd=cwd)
            return out, err

        return None, None

    def missing(self):
        if not os.path.isfile(os.path.join(self.path, "pnpm-lock.yaml")):
            return True

        cmd = ["list", "--json"]

        if self.name is not None:
            cmd.append(self.name)

        try:
            out, err = self._exec(cmd, True, False)
            if err is not None and err != "":
                raise Exception(out)

            data = json.loads(out)
        except Exception as e:
            self.module.fail_json(
                msg="Failed to parse pnpm output with error %s" % to_native(e)
            )

        if "error" in data:
            return True

        data = data[0]

        for typedep in [
            "dependencies",
            "devDependencies",
            "optionalDependencies",
            "unsavedDependencies",
        ]:
            if typedep not in data:
                continue

            for dep, prop in data[typedep].items():
                if self.alias is not None and self.alias != dep:
                    continue

                name = prop["from"] if self.alias is not None else dep
                if self.name != name:
                    continue

                if self.version is None or self.version == prop["version"]:
                    return False

                break

        return True

    def install(self):
        if self.alias_name_ver is not None:
            return self._exec(["add", self.alias_name_ver])
        return self._exec(["install"])

    def update(self):
        return self._exec(["update", "--latest"])

    def uninstall(self):
        if self.alias is not None:
            return self._exec(["remove", self.alias])
        return self._exec(["remove", self.name])

    def list_outdated(self):
        if not os.path.isfile(os.path.join(self.path, "pnpm-lock.yaml")):
            return list()

        cmd = ["outdated", "--format", "json"]
        try:
            out, err = self._exec(cmd, True, False)

            # BUG: It will not show correct error sometimes, like when it has
            # plain text output intermingled with a {}
            if err is not None and err != "":
                raise Exception(out)

            # HACK: To fix the above bug, the following hack is implemented
            data_lines = out.splitlines(True)

            out = None
            for line in data_lines:
                if len(line) > 0 and line[0] == "{":
                    out = line
                    continue

                if len(line) > 0 and line[0] == "}":
                    out += line
                    break

                if out is not None:
                    out += line

            data = json.loads(out)
        except Exception as e:
            self.module.fail_json(
                msg="Failed to parse pnpm output with error %s" % to_native(e)
            )

        return data.keys()


def main():
    arg_spec = dict(
        name=dict(default=None),
        alias=dict(default=None),
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
    alias = module.params["alias"]
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

    if name is None and version is not None:
        module.fail_json(msg="version is meaningless when name is not provided")

    if name is None and alias is not None:
        module.fail_json(msg="alias is meaningless when name is not provided")

    if path is None and not globally:
        module.fail_json(msg="path must be specified when not using global")
    elif path is not None and globally:
        module.fail_json(msg="Cannot specify path when doing global installation")

    if globally and (production or dev or optional):
        module.fail_json(
            msg="Options production, dev, and optional is meaningless when installing packages globally"
        )

    if name is not None and path is not None and globally:
        module.fail_json(msg="path should not be mentioned when installing globally")

    if production and dev and optional:
        module.fail_json(
            msg="Options production and dev and optional don't go together"
        )

    if production and dev:
        module.fail_json(msg="Options production and dev don't go together")

    if production and optional:
        module.fail_json(msg="Options production and optional don't go together")

    if dev and optional:
        module.fail_json(msg="Options dev and optional don't go together")

    if name is not None and name[0:4] == "http" and version is not None:
        module.fail_json(msg="Semver not supported on remote url downloads")

    if name is None and optional:
        module.fail_json(
            msg="Optional not available when package name not provided, use no_optional instead"
        )

    if state == "absent" and name is None:
        module.fail_json(msg="Package name is required for uninstalling")

    if globally:
        _rc, out, _err = module.run_command(executable + ["root", "-g"], check_rc=True)
        path, _tail = os.path.split(out.strip())

    pnpm = Pnpm(
        module,
        name=name,
        alias=alias,
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
        if pnpm.missing():
            changed = True
            out, err = pnpm.install()
    elif state == "latest":
        outdated = pnpm.list_outdated()
        if name is not None:
            if pnpm.missing() or name in outdated:
                changed = True
                out, err = pnpm.install()
        elif len(outdated):
            changed = True
            out, err = pnpm.update()
    else:  # absent
        if not pnpm.missing():
            changed = True
            out, err = pnpm.uninstall()

    module.exit_json(changed=changed, out=out, err=err)


if __name__ == "__main__":
    main()
