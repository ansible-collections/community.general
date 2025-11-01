#!/usr/bin/python

# Copyright (c) 2014, Michael Warkentin <mwarkentin@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
module: bower
short_description: Manage bower packages with C(bower)
description:
  - Manage bower packages with C(bower).
author: "Michael Warkentin (@mwarkentin)"
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options:
  name:
    type: str
    description:
      - The name of a bower package to install.
  offline:
    description:
      - Install packages from local cache, if the packages were installed before.
    type: bool
    default: false
  production:
    description:
      - Install with C(--production) flag.
    type: bool
    default: false
  path:
    type: path
    description:
      - The base path where to install the bower packages.
    required: true
  relative_execpath:
    type: path
    description:
      - Relative path to bower executable from install path.
  state:
    type: str
    description:
      - The state of the bower package.
    default: present
    choices: ["present", "absent", "latest"]
  version:
    type: str
    description:
      - The version to be installed.
"""

EXAMPLES = r"""
- name: Install "bootstrap" bower package.
  community.general.bower:
    name: bootstrap

- name: Install "bootstrap" bower package on version 3.1.1.
  community.general.bower:
    name: bootstrap
    version: '3.1.1'

- name: Remove the "bootstrap" bower package.
  community.general.bower:
    name: bootstrap
    state: absent

- name: Install packages based on bower.json.
  community.general.bower:
    path: /app/location

- name: Update packages based on bower.json to their latest version.
  community.general.bower:
    path: /app/location
    state: latest

# install bower locally and run from there
- npm:
    path: /app/location
    name: bower
    global: false
- community.general.bower:
    path: /app/location
    relative_execpath: node_modules/.bin
"""

import json
import os

from ansible.module_utils.basic import AnsibleModule


class Bower:
    def __init__(self, module, **kwargs):
        self.module = module
        self.name = kwargs["name"]
        self.offline = kwargs["offline"]
        self.production = kwargs["production"]
        self.path = kwargs["path"]
        self.relative_execpath = kwargs["relative_execpath"]
        self.version = kwargs["version"]

        if kwargs["version"]:
            self.name_version = f"{self.name}#{self.version}"
        else:
            self.name_version = self.name

    def _exec(self, args, run_in_check_mode=False, check_rc=True):
        if not self.module.check_mode or (self.module.check_mode and run_in_check_mode):
            cmd = []

            if self.relative_execpath:
                cmd.append(os.path.join(self.path, self.relative_execpath, "bower"))
                if not os.path.isfile(cmd[-1]):
                    self.module.fail_json(msg=f"bower not found at relative path {self.relative_execpath}")
            else:
                cmd.append("bower")

            cmd.extend(args)
            cmd.extend(["--config.interactive=false", "--allow-root"])

            if self.name:
                cmd.append(self.name_version)

            if self.offline:
                cmd.append("--offline")

            if self.production:
                cmd.append("--production")

            # If path is specified, cd into that path and run the command.
            cwd = None
            if self.path:
                if not os.path.exists(self.path):
                    os.makedirs(self.path)
                if not os.path.isdir(self.path):
                    self.module.fail_json(msg=f"path {self.path} is not a directory")
                cwd = self.path

            rc, out, err = self.module.run_command(cmd, check_rc=check_rc, cwd=cwd)
            return out
        return ""

    def list(self):
        cmd = ["list", "--json"]

        installed = list()
        missing = list()
        outdated = list()
        data = json.loads(self._exec(cmd, True, False))
        if "dependencies" in data:
            for dep in data["dependencies"]:
                dep_data = data["dependencies"][dep]
                if dep_data.get("missing", False):
                    missing.append(dep)
                elif (
                    "version" in dep_data["pkgMeta"]
                    and "update" in dep_data
                    and dep_data["pkgMeta"]["version"] != dep_data["update"]["latest"]
                ):
                    outdated.append(dep)
                elif dep_data.get("incompatible", False):
                    outdated.append(dep)
                else:
                    installed.append(dep)
        # Named dependency not installed
        else:
            missing.append(self.name)

        return installed, missing, outdated

    def install(self):
        return self._exec(["install"])

    def update(self):
        return self._exec(["update"])

    def uninstall(self):
        return self._exec(["uninstall"])


def main():
    arg_spec = dict(
        name=dict(),
        offline=dict(default=False, type="bool"),
        production=dict(default=False, type="bool"),
        path=dict(required=True, type="path"),
        relative_execpath=dict(type="path"),
        state=dict(
            default="present",
            choices=[
                "present",
                "absent",
                "latest",
            ],
        ),
        version=dict(),
    )
    module = AnsibleModule(argument_spec=arg_spec)

    name = module.params["name"]
    offline = module.params["offline"]
    production = module.params["production"]
    path = module.params["path"]
    relative_execpath = module.params["relative_execpath"]
    state = module.params["state"]
    version = module.params["version"]

    if state == "absent" and not name:
        module.fail_json(msg="uninstalling a package is only available for named packages")

    bower = Bower(
        module,
        name=name,
        offline=offline,
        production=production,
        path=path,
        relative_execpath=relative_execpath,
        version=version,
    )

    changed = False
    if state == "present":
        installed, missing, outdated = bower.list()
        if missing:
            changed = True
            bower.install()
    elif state == "latest":
        installed, missing, outdated = bower.list()
        if missing or outdated:
            changed = True
            bower.update()
    else:  # Absent
        installed, missing, outdated = bower.list()
        if name in installed:
            changed = True
            bower.uninstall()

    module.exit_json(changed=changed)


if __name__ == "__main__":
    main()
