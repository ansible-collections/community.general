#!/usr/bin/python
# Copyright (c) 2026, Travis Beale (@travisbeale)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: nix_channel
short_description: Manage Nix channel subscriptions
version_added: "14.1.0"
description:
  - Manage Nix channel subscriptions using C(nix-channel) as the effective user.
author:
  - Travis Beale (@travisbeale)
requirements:
  - C(nix-channel)
extends_documentation_fragment:
  - community.general._attributes
attributes:
  check_mode:
    support: partial
    details:
      - In check mode, a requested refresh of a subscribed channel predicts a change because its remote contents are unknown.
  diff_mode:
    support: none
options:
  name:
    description:
      - Channel names. When adding a URL, specify at most one name. By default the last URL component is used,
        with a trailing C(-stable) or C(-unstable) removed.
      - Omit to update all subscribed channels with O(update=true).
    type: list
    elements: str
  url:
    description:
      - Channel URL to subscribe to.
    type: str
  state:
    description:
      - Desired subscription state.
    choices:
      present: Manage a subscription or update subscribed channels.
      absent: Remove the named subscriptions.
    type: str
    default: present
  update:
    description:
      - Refresh the selected channels after managing subscriptions.
    type: bool
    default: false
"""

EXAMPLES = r"""
- name: Subscribe to the unstable channel
  community.general.nix_channel:
    name: nixpkgs-unstable
    url: https://nixos.org/channels/nixpkgs-unstable
    update: true

- name: Refresh all subscribed channels
  community.general.nix_channel:
    update: true
"""

RETURN = r"""
"""

import re
import typing as t

from ansible.module_utils.basic import AnsibleModule

if t.TYPE_CHECKING:  # pragma: no cover
    from ansible_collections.community.general.plugins.module_utils._typing import ArgumentSpecT, ModuleReturnChangedReq


def get_argument_spec() -> ArgumentSpecT:
    return dict(
        name=dict(type="list", elements="str"),
        url=dict(type="str"),
        state=dict(type="str", choices=["present", "absent"], default="present"),
        update=dict(type="bool", default=False),
    )


def main() -> None:
    module = AnsibleModule(
        argument_spec=get_argument_spec(), supports_check_mode=True, required_if=[("state", "absent", ["name"])]
    )
    binary = module.get_bin_path("nix-channel", required=True)
    names = module.params["name"]
    url = module.params["url"]
    update = module.params["update"]
    absent = module.params["state"] == "absent"

    def run(args: list[str]) -> str:
        rc, stdout, stderr = module.run_command([binary] + args, check_rc=True, expand_user_and_vars=False)
        for line in stderr.splitlines():
            if line.startswith("warning: "):
                module.warn(line[len("warning: ") :])
        return stdout

    if names == [] or url == "":
        module.fail_json(msg="Channel names and URL must be nonempty when supplied.")
    names = list(dict.fromkeys(names or []))
    if absent and (url or update):
        module.fail_json(msg="Removing subscriptions requires names only.")
    if not absent and not (url or update):
        module.fail_json(msg="Supply a URL to subscribe, or request an update.")
    if url:
        if len(names) > 1 or url.startswith("-"):
            module.fail_json(msg="A channel URL requires at most one name and cannot start with a dash.")
        url = url.rstrip("/")
        names = names or [re.sub(r"-(un)?stable$", "", url.rsplit("/", 1)[-1])]
    if any(not re.fullmatch(r"[A-Za-z0-9_.][A-Za-z0-9_.-]*", name) or name in (".", "..") for name in names):
        module.fail_json(msg="Invalid channel name.")

    channels = dict(line.split(None, 1) for line in run(["--list"]).splitlines())
    changed = False
    for name in names:
        if absent and name in channels:
            changed = True
            if not module.check_mode:
                run(["--remove", name])
        elif url and channels.get(name) != url:
            changed = True
            if not module.check_mode:
                run(["--add", url, name])
        elif update and name not in channels:
            module.fail_json(msg=f"Unknown channel: {name}")
    if update and (channels or url):
        if module.check_mode:
            changed = True
        else:
            before = run(["--list-generations"])
            run(["--update"] + names)
            changed = run(["--list-generations"]) != before or changed

    result: ModuleReturnChangedReq = {"changed": changed}
    module.exit_json(**result)


if __name__ == "__main__":
    main()
