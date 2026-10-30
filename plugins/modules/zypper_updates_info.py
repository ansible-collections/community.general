#!/usr/bin/python

# Copyright (c) 2026, Harshvardhan Sharma <harshvardhan.sharma@suse.com>
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


from __future__ import annotations

DOCUMENTATION = r"""
module: zypper_updates_info
author: "Harshvardhan Sharma (@HVSharma12)"
version_added: 14.0.0
short_description: List available Zypper updates
description:
  - List the updates that C(zypper list-updates) reports on SUSE and openSUSE.
extends_documentation_fragment:
  - community.general._attributes
  - community.general._attributes.info_module
options:
  type:
    description:
      - The kind of updates to list.
    type: str
    choices:
      package: Package updates.
      patch:
        - Needed patches.
        - Patches affecting the package manager itself are returned with RV(updates[].pkgmanager=true). Zypper installs those
          before any other patch.
      pattern: Pattern updates.
      product: Product updates.
    default: package
  all:
    description:
      - Also list updates that cannot be installed because of dependency problems or locks.
    type: bool
    default: false
requirements:
  - "zypper >= 1.0 (included in openSUSE >= 11.1 or SUSE Linux Enterprise Server/Desktop >= 11.0)"
  - python-xml
notes:
  - Repositories with autorefresh enabled are refreshed when their metadata is outdated. To refresh all repositories
    first, use M(community.general.zypper) with O(community.general.zypper#module:update_cache=true).
  - For the installed packages, use M(ansible.builtin.package_facts).
"""

EXAMPLES = r"""
- name: List package updates
  community.general.zypper_updates_info:
  register: result

- name: List needed patches
  community.general.zypper_updates_info:
    type: patch
  register: patches

- name: Fail when a security patch is needed
  ansible.builtin.assert:
    that: patches.updates | selectattr('category', 'equalto', 'security') | list | length == 0
"""

RETURN = r"""
updates:
  description:
    - The available updates, as reported by C(zypper list-updates).
  type: list
  returned: always
  elements: dict
  contains:
    name:
      description: The name of the package or patch.
      type: str
      returned: always
      sample: openssl-3
    kind:
      description: The kind of the update.
      type: str
      returned: always
      sample: package
    edition:
      description: The version of the update.
      type: str
      returned: always
      sample: 3.2.4-150700.3.6.1
    edition_old:
      description: The installed version.
      type: str
      returned: when it differs from RV(updates[].edition)
      sample: 3.2.4-150700.3.3.1
    arch:
      description: The architecture of the update.
      type: str
      returned: always
      sample: x86_64
    arch_old:
      description: The installed architecture.
      type: str
      returned: when it differs from RV(updates[].arch)
      sample: i586
    summary:
      description: The summary of the package or patch.
      type: str
      returned: always
      sample: Secure Sockets and Transport Layer Security
    repository:
      description: The alias of the repository providing the update.
      type: str
      returned: when zypper reports it
      sample: SLE-Module-Basesystem15-SP7-Updates
    status:
      description: The status of the patch.
      type: str
      returned: when O(type=patch)
      sample: needed
    category:
      description: The category of the patch.
      type: str
      returned: when O(type=patch)
      sample: security
    severity:
      description: The severity of the patch.
      type: str
      returned: when O(type=patch)
      sample: important
    interactive:
      description: Whether the patch needs user interaction.
      type: bool
      returned: when O(type=patch)
      sample: false
    restart:
      description: Whether the patch suggests a reboot.
      type: bool
      returned: when O(type=patch)
      sample: false
    pkgmanager:
      description: Whether the patch affects the package manager itself.
      type: bool
      returned: when O(type=patch)
      sample: false
    issues:
      description: The issues the patch fixes.
      type: list
      elements: dict
      returned: when O(type=patch)
      sample: [{"type": "cve", "id": "CVE-2026-1234"}, {"type": "bugzilla", "id": "1234567"}]
"""


import typing as t

from ansible_collections.community.general.plugins.module_utils import _deps as deps

with deps.declare("parseXML"):
    from xml.dom.minidom import parseString as parseXML

from ansible.module_utils.basic import AnsibleModule

if t.TYPE_CHECKING:  # pragma: no cover
    from xml.dom.minidom import Element

    from ansible_collections.community.general.plugins.module_utils._typing import (
        ArgumentSpecT,
        ModuleReturnChangedReq,
    )

    class ResultDict(ModuleReturnChangedReq):
        updates: list[dict[str, object]]


UPDATE_ATTRS = ["name", "kind", "edition", "edition-old", "arch", "arch-old"]
PATCH_ATTRS = ["status", "category", "severity"]
PATCH_BOOL_ATTRS = ["interactive", "restart", "pkgmanager"]


def child_text(node: Element, tag: str) -> str:
    for child in node.childNodes:
        if child.nodeName == tag and child.firstChild and child.firstChild.nodeValue:
            return child.firstChild.nodeValue
    return ""


def parse_update(node: Element, kind: str) -> dict[str, object]:
    update: dict[str, object] = {}
    for attr in UPDATE_ATTRS:
        if node.hasAttribute(attr):
            update[attr.replace("-", "_")] = node.getAttribute(attr)
    update["summary"] = child_text(node, "summary")
    for source in node.getElementsByTagName("source"):
        update["repository"] = source.getAttribute("alias")
    if kind == "patch":
        for attr in PATCH_ATTRS:
            update[attr] = node.getAttribute(attr)
        for attr in PATCH_BOOL_ATTRS:
            update[attr] = node.getAttribute(attr) == "true"
        update["issues"] = [
            {"type": issue.getAttribute("type"), "id": issue.getAttribute("id")}
            for issue in node.getElementsByTagName("issue")
        ]
    return update


def list_updates(module: AnsibleModule, kind: str, list_all: bool) -> list[dict[str, object]]:
    cmd = [
        module.get_bin_path("zypper", required=True),
        "--non-interactive",
        "--xmlout",
        "--quiet",
        "list-updates",
        "--type",
        kind,
    ]
    if list_all:
        cmd.append("--all")
    rc, stdout, stderr = module.run_command(cmd, check_rc=False)
    # 6 is ZYPPER_EXIT_NO_REPOS
    if rc == 6:
        return []
    if rc != 0:
        module.fail_json(msg=f'Failed to execute "{" ".join(cmd)}"', rc=rc, stdout=stdout, stderr=stderr)
    dom = parseXML(stdout)
    return [parse_update(node, kind) for node in dom.getElementsByTagName("update")]


def get_argument_spec() -> ArgumentSpecT:
    return dict(
        type=dict(type="str", default="package", choices=["package", "patch", "pattern", "product"]),
        all=dict(type="bool", default=False),
    )


def main() -> None:
    module = AnsibleModule(argument_spec=get_argument_spec(), supports_check_mode=True)
    module.run_command_environ_update = {"LANGUAGE": "C", "LC_ALL": "C"}

    deps.validate(module)

    result: ResultDict = {
        "changed": False,
        "updates": list_updates(module, module.params["type"], module.params["all"]),
    }
    module.exit_json(**result)


if __name__ == "__main__":
    main()
