#!/usr/bin/python
# Copyright (c) 2026, Travis Beale (@travisbeale)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: nix_env
short_description: Manage packages in a Nix user profile
version_added: "14.1.0"
description:
  - Manage packages in a Nix user profile using C(nix-env) as the effective user.
author:
  - Travis Beale (@travisbeale)
requirements:
  - C(nix-env)
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
      - For installation, a Nix attribute path. For removal, the installed package's base name.
    type: str
    required: true
  state:
    description:
      - Desired package state in the current user's profile.
    choices:
      present: Install the selected package if its base name is missing.
      latest: Install the build currently selected by the attribute, including when the channel rolls back.
      absent: Remove installed builds with the given base name.
    type: str
    default: present
"""

EXAMPLES = r"""
- name: Install hello from nixpkgs
  community.general.nix_env:
    name: nixpkgs.hello

- name: Remove hello
  community.general.nix_env:
    name: hello
    state: absent
"""

RETURN = r"""
"""

import typing as t
import xml.etree.ElementTree as ET

from ansible.module_utils.basic import AnsibleModule

if t.TYPE_CHECKING:  # pragma: no cover
    from ansible_collections.community.general.plugins.module_utils._typing import ArgumentSpecT, ModuleReturnChangedReq


def get_argument_spec() -> ArgumentSpecT:
    return dict(
        name=dict(type="str", required=True),
        state=dict(type="str", choices=["present", "latest", "absent"], default="present"),
    )


def main() -> None:
    module = AnsibleModule(argument_spec=get_argument_spec(), supports_check_mode=True)
    nix_env = module.get_bin_path("nix-env", required=True)
    name = module.params["name"]
    state = module.params["state"]

    def run(args: list[str]) -> str:
        rc, stdout, stderr = module.run_command([nix_env] + args, check_rc=True, expand_user_and_vars=False)
        for line in stderr.splitlines():
            if line.startswith("warning: "):
                module.warn(line[len("warning: ") :])
        return stdout

    def query(args: list[str]) -> list[ET.Element]:
        return ET.fromstring(run(["--query", "--xml", "--out-path"] + args)).findall("item")

    if not name or name.startswith("-"):
        module.fail_json(msg="Expected a nonempty package name or attribute path that does not start with a dash.")
    installed = query(["--installed"])
    if state == "absent":
        paths = [
            output.attrib["path"] for pkg in installed if pkg.get("pname") == name for output in pkg.findall("output")
        ]
        changed = bool(paths)
        action = ["--uninstall"] + paths
    else:
        candidates = query(["--available", "--attr", name])
        if len(candidates) != 1 or candidates[0].get("attrPath") != name:
            module.fail_json(msg="The attribute must select one package.")
        candidate = candidates[0]
        matching = [pkg for pkg in installed if pkg.get("pname") == candidate.attrib["pname"]]
        selected_paths = {output.attrib["path"] for output in candidate.findall("output")}
        changed = not matching or (
            state == "latest"
            and not any(
                all(output.attrib["path"] in selected_paths for output in pkg.findall("output")) for pkg in matching
            )
        )
        action = ["--install", "--attr", name]

    if changed and not module.check_mode:
        run(action)
    result: ModuleReturnChangedReq = {"changed": changed}
    module.exit_json(**result)


if __name__ == "__main__":
    main()
