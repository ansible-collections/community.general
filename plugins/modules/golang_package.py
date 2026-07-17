#!/usr/bin/python
# Copyright (c) 2026 Shreyash Bhosale <shreyashpb16@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: golang_package
short_description: Manage Go packages with C(go install)
version_added: 13.1.0
description:
  - Manage Go packages with C(go install).
  - Packages are installed as binaries into the Go binary directory (E(GOBIN)).
  - Uninstalling a package removes its binary from E(GOBIN).
author: "Shreyash Bhosale (@shrbhosa)"
extends_documentation_fragment:
  - community.general._attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  executable:
    description:
      - Path to the C(go) binary.
      - If not specified, the module looks for C(go) in E(PATH).
    type: path
  name:
    description:
      - The name of a Go package to install.
      - Must be a full Go package path, for example V(golang.org/x/tools/cmd/stringer).
      - A version can be specified inline using the V(@) suffix, for example
        V(golang.org/x/tools/cmd/stringer@v0.29.0). This allows pinning different
        versions when installing multiple packages.
      - The inline V(@version) syntax cannot be combined with the O(version) parameter.
    type: list
    elements: str
    required: true
  version:
    description:
      - The version to install, for example V(v1.55.2).
      - The version must include the V(v) prefix as required by Go module versioning.
      - Can only be used when O(name) contains a single package without an inline V(@version).
      - When not specified and O(state=present), the latest version is installed for new packages.
    type: str
  state:
    description:
      - The desired state of the Go package.
    type: str
    default: present
    choices: ["present", "absent", "latest"]
requirements:
  - Go >= 1.16
notes:
  - The Go binary directory is determined by C(go env GOBIN). To customize the install location,
    set the E(GOBIN) environment variable using the task's C(environment) directive.
  - Go does not provide a native uninstall command. When O(state=absent), the module removes the
    binary file from E(GOBIN) directly.
"""

EXAMPLES = r"""
- name: Install stringer
  community.general.golang_package:
    name: golang.org/x/tools/cmd/stringer

- name: Install golangci-lint at a specific version
  community.general.golang_package:
    name: github.com/golangci/golangci-lint/cmd/golangci-lint
    version: v1.55.2

- name: Install multiple packages at specific versions
  community.general.golang_package:
    name:
      - golang.org/x/tools/cmd/stringer@v0.29.0
      - github.com/golangci/golangci-lint/cmd/golangci-lint@v1.55.2

- name: Install multiple packages
  community.general.golang_package:
    name:
      - golang.org/x/tools/cmd/stringer
      - golang.org/x/tools/cmd/goimports

- name: Remove stringer
  community.general.golang_package:
    name: golang.org/x/tools/cmd/stringer
    state: absent

- name: Update golangci-lint to the latest version
  community.general.golang_package:
    name: github.com/golangci/golangci-lint/cmd/golangci-lint
    state: latest

- name: Install into a custom directory
  community.general.golang_package:
    name: golang.org/x/tools/cmd/stringer
  environment:
    GOBIN: /usr/local/bin
"""

import json
import os

from ansible.module_utils.basic import AnsibleModule


class Go:
    def __init__(self, module, **kwargs):
        self.module = module
        self.executable = [kwargs["executable"] or module.get_bin_path("go", True)]
        self.state = kwargs["state"]
        self.version = kwargs["version"]
        self._gobin = None

        self.packages = []
        for name in kwargs["name"]:
            if "@" in name:
                pkg, ver = name.rsplit("@", 1)
                self.packages.append((pkg, ver))
            else:
                self.packages.append((name, None))

    @property
    def package_names(self):
        return [pkg for pkg, dummy in self.packages]

    def _exec(self, args, run_in_check_mode=False, check_rc=True):
        if not self.module.check_mode or run_in_check_mode:
            cmd = self.executable + args
            rc, out, err = self.module.run_command(cmd, check_rc=check_rc)
            return out, err
        return "", ""

    def _get_gobin(self):
        if self._gobin is not None:
            return self._gobin

        out, dummy = self._exec(["env", "GOBIN"], run_in_check_mode=True, check_rc=True)
        gobin = out.strip()
        if gobin:
            self._gobin = gobin
            return self._gobin

        out, dummy = self._exec(["env", "GOPATH"], run_in_check_mode=True, check_rc=True)
        gopath = out.strip()
        if not gopath:
            self.module.fail_json(msg="Could not determine Go binary directory: GOBIN and GOPATH are both empty")
        self._gobin = os.path.join(gopath.split(os.pathsep)[0], "bin")
        return self._gobin

    def _get_binary_info(self, binary_path):
        out, dummy = self._exec(["version", "-m", binary_path], run_in_check_mode=True, check_rc=False)
        if not out:
            return None

        path = None
        version = None
        mod_path = None
        for line in out.splitlines():
            parts = line.strip().split("\t")
            if len(parts) >= 2 and parts[0] == "path":
                path = parts[1]
            elif len(parts) >= 3 and parts[0] == "mod":
                mod_path = parts[1]
                version = parts[2]

        if path and version:
            return {"path": path, "version": version, "mod_path": mod_path}
        return None

    def get_installed(self):
        gobin = self._get_gobin()
        installed = {}
        for pkg_name in self.package_names:
            binary_name = pkg_name.rsplit("/", 1)[-1]
            binary_path = os.path.join(gobin, binary_name)
            if not os.path.isfile(binary_path):
                continue
            info = self._get_binary_info(binary_path)
            if info and info["path"] == pkg_name:
                installed[pkg_name] = info["version"]
        return installed

    def _get_latest_version(self, mod_path):
        out, dummy = self._exec(
            ["list", "-m", "-json", mod_path + "@latest"],
            run_in_check_mode=True,
            check_rc=False,
        )
        if out:
            try:
                data = json.loads(out)
                return data.get("Version")
            except (json.JSONDecodeError, ValueError):
                pass
        return None

    def is_outdated(self, package):
        gobin = self._get_gobin()
        binary_name = package.rsplit("/", 1)[-1]
        binary_path = os.path.join(gobin, binary_name)
        info = self._get_binary_info(binary_path)
        if not info or info["path"] != package:
            return True
        installed_version = info["version"]
        mod_path = info.get("mod_path")
        if not mod_path:
            self.module.fail_json(msg=f"Could not determine module path for package {package}")
        latest_version = self._get_latest_version(mod_path)
        if not latest_version:
            self.module.fail_json(msg=f"Could not determine latest version for package {package}")
        return installed_version != latest_version

    def install(self, packages):
        by_version = {}
        for pkg, ver in packages:
            effective = ver or self.version or "latest"
            by_version.setdefault(effective, []).append(pkg)

        out_all, err_all = "", ""
        for ver, pkgs in by_version.items():
            cmd = ["install"] + [p + "@" + ver for p in pkgs]
            out, err = self._exec(cmd)
            out_all += out
            err_all += err
        return out_all, err_all

    def uninstall(self, packages):
        gobin = self._get_gobin()
        for package in packages:
            binary_name = package.rsplit("/", 1)[-1]
            binary_path = os.path.join(gobin, binary_name)
            if os.path.isfile(binary_path) and not self.module.check_mode:
                os.remove(binary_path)


def main():
    arg_spec = dict(
        executable=dict(type="path"),
        name=dict(required=True, type="list", elements="str"),
        state=dict(default="present", choices=["present", "absent", "latest"]),
        version=dict(type="str"),
    )
    module = AnsibleModule(argument_spec=arg_spec, supports_check_mode=True)

    name = module.params["name"]
    state = module.params["state"]
    version = module.params["version"]

    has_inline_version = any("@" in n for n in name)
    if version and has_inline_version:
        module.fail_json(msg="Cannot combine the 'version' parameter with inline @version in package names")
    if version and len(name) > 1:
        module.fail_json(msg="The 'version' parameter can only be used when 'name' contains a single package")
    if state == "latest" and (version or has_inline_version):
        module.fail_json(msg="Cannot specify a version when state=latest")

    module.run_command_environ_update = dict(LANGUAGE="C", LC_ALL="C")

    go = Go(module, **module.params)
    changed, out, err = False, None, None
    installed_packages = go.get_installed()

    if state == "present":
        to_install = []
        for pkg, ver in go.packages:
            effective_ver = ver or version
            if pkg not in installed_packages:
                to_install.append((pkg, ver))
            elif effective_ver and effective_ver != installed_packages[pkg]:
                to_install.append((pkg, ver))
        if to_install:
            changed = True
            out, err = go.install(to_install)
    elif state == "latest":
        to_update = [(pkg, ver) for pkg, ver in go.packages if pkg not in installed_packages or go.is_outdated(pkg)]
        if to_update:
            changed = True
            out, err = go.install(to_update)
    else:  # absent
        to_uninstall = [pkg for pkg in go.package_names if pkg in installed_packages]
        if to_uninstall:
            changed = True
            go.uninstall(to_uninstall)

    module.exit_json(changed=changed, stdout=out, stderr=err)


if __name__ == "__main__":
    main()
