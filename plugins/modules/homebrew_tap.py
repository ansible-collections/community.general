#!/usr/bin/python

# Copyright (c) 2013, Daniel Jaouen <dcj24@cornell.edu>
# Copyright (c) 2016, Indrajit Raychaudhuri <irc+code@indrajit.com>
#
# Based on homebrew (Andrew Dunham <andrew@du.nham.ca>)
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: homebrew_tap
author:
  - "Indrajit Raychaudhuri (@indrajitr)"
  - "Daniel Jaouen (@danieljaouen)"
short_description: Tap a Homebrew repository
description:
  - Tap external Homebrew repositories.
  - Optionally control whether Homebrew trusts the tapped repositories.
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
      - The GitHub user/organization repository to tap.
    required: true
    aliases: ['tap']
    type: list
    elements: str
  url:
    description:
      - The optional git URL of the repository to tap. The URL is not assumed to be on GitHub, and the protocol does not have
        to be HTTP. Any location and protocol that git can handle is fine.
      - O(name) option may not be a list of multiple taps (but a single tap instead) when this option is provided.
    type: str
  state:
    description:
      - State of the repository.
    choices: ['present', 'absent']
    default: 'present'
    type: str
  trust:
    description:
      - Whether Homebrew trusts the repository. Homebrew refuses to load formulae, casks and commands from untrusted
        third-party taps.
      - V(true) trusts the repository, V(false) stops trusting it. When this option is not specified, the trust state
        of the repository is left untouched.
      - Combining V(true) with O(state=absent) is an error.
      - This requires a Homebrew version providing the C(brew trust) command.
    type: bool
    version_added: '13.3.0'
  path:
    description:
      - A V(:) separated list of paths to search for C(brew) executable.
    default: '/usr/local/bin:/opt/homebrew/bin:/home/linuxbrew/.linuxbrew/bin'
    type: path
    version_added: '2.1.0'
requirements: [homebrew]
"""

EXAMPLES = r"""
- name: Tap a Homebrew repository, state present
  community.general.homebrew_tap:
    name: homebrew/dupes

- name: Tap a Homebrew repository, state absent
  community.general.homebrew_tap:
    name: homebrew/dupes
    state: absent

- name: Tap a Homebrew repository, state present
  community.general.homebrew_tap:
    name: homebrew/dupes,homebrew/science
    state: present

- name: Tap a Homebrew repository using url, state present
  community.general.homebrew_tap:
    name: telemachus/brew
    url: 'https://bitbucket.org/telemachus/brew'

- name: Tap a Homebrew repository and trust it
  community.general.homebrew_tap:
    name: hashicorp/tap
    trust: true

- name: Stop trusting a Homebrew repository, but keep it tapped
  community.general.homebrew_tap:
    name: hashicorp/tap
    trust: false

- name: Untrust and untap a Homebrew repository
  community.general.homebrew_tap:
    name: hashicorp/tap
    trust: false
    state: absent
"""

import json
import re

from ansible.module_utils.basic import AnsibleModule


def a_valid_tap(tap):
    """Returns True if the tap is valid."""
    regex = re.compile(r"^([\w-]+)/(homebrew-)?([\w-]+)$")
    return regex.match(tap)


def normalized_tap(tap: str) -> str:
    """Returns the tap name in the form Homebrew itself reports it."""
    user, dummy, repo = tap.lower().partition("/")
    return f"{user}/{re.sub('^homebrew-', '', repo)}"


def already_tapped(module, brew_path, tap, taps=None):
    """Returns True if already tapped."""
    if taps is None:
        rc, out, err = module.run_command([brew_path, "tap"])
        taps = [tap_.strip().lower() for tap_ in out.split("\n") if tap_]
    return normalized_tap(tap) in taps


def add_tap(module, brew_path, tap, url=None, taps=None):
    """Adds a single tap."""
    failed, changed, msg = False, False, ""

    if not a_valid_tap(tap):
        failed = True
        msg = f"not a valid tap: {tap}"

    elif not already_tapped(module, brew_path, tap, taps):
        if module.check_mode:
            module.exit_json(changed=True)

        cmd = [brew_path, "tap", tap]
        if url:
            cmd.append(url)
        rc, out, err = module.run_command(cmd)
        if rc == 0:
            changed = True
            msg = f"successfully tapped: {tap}"
        else:
            failed = True
            msg = f"failed to tap: {tap} due to {err}"

    else:
        msg = f"already tapped: {tap}"

    return (failed, changed, msg)


def add_taps(module, brew_path, taps):
    """Adds one or more taps."""
    failed, changed, unchanged, added, msg = False, False, 0, 0, ""

    rc, out, err = module.run_command([brew_path, "tap"])
    tapped = [t.strip().lower() for t in out.split("\n") if t]

    for tap in taps:
        (failed, changed, msg) = add_tap(module, brew_path, tap, taps=tapped)
        if failed:
            break
        if changed:
            added += 1
        else:
            unchanged += 1

    if failed:
        msg = f"added: {added}, unchanged: {unchanged}, error: {msg}"
    elif added:
        changed = True
        msg = f"added: {added}, unchanged: {unchanged}"
    else:
        msg = f"added: {added}, unchanged: {unchanged}"

    return (failed, changed, msg)


def remove_tap(module, brew_path, tap, taps=None):
    """Removes a single tap."""
    failed, changed, msg = False, False, ""

    if not a_valid_tap(tap):
        failed = True
        msg = f"not a valid tap: {tap}"

    elif already_tapped(module, brew_path, tap, taps):
        if module.check_mode:
            module.exit_json(changed=True)

        rc, out, err = module.run_command([brew_path, "untap", tap])
        if not already_tapped(module, brew_path, tap):
            changed = True
            msg = f"successfully untapped: {tap}"
        else:
            failed = True
            msg = f"failed to untap: {tap} due to {err}"

    else:
        msg = f"already untapped: {tap}"

    return (failed, changed, msg)


def remove_taps(module, brew_path, taps):
    """Removes one or more taps."""
    failed, changed, unchanged, removed, msg = False, False, 0, 0, ""

    rc, out, err = module.run_command([brew_path, "tap"])
    tapped = [t.strip().lower() for t in out.split("\n") if t]

    for tap in taps:
        (failed, changed, msg) = remove_tap(module, brew_path, tap, taps=tapped)
        if failed:
            break
        if changed:
            removed += 1
        else:
            unchanged += 1

    if failed:
        msg = f"removed: {removed}, unchanged: {unchanged}, error: {msg}"
    elif removed:
        changed = True
        msg = f"removed: {removed}, unchanged: {unchanged}"
    else:
        msg = f"removed: {removed}, unchanged: {unchanged}"

    return (failed, changed, msg)


def trusted_taps(module: AnsibleModule, brew_path: str) -> set[str]:
    """Returns the set of currently trusted taps."""
    rc, out, err = module.run_command([brew_path, "trust", "--json", "v1"])
    if rc != 0:
        module.fail_json(
            msg=f"failed to list trusted taps, the 'trust' option requires a Homebrew version providing 'brew trust': {err}"
        )

    try:
        taps = json.loads(out)["taps"]
    except (ValueError, KeyError, TypeError) as e:
        module.fail_json(msg=f"failed to parse the output of 'brew trust --json v1': {e}")

    return {normalized_tap(tap) for tap in taps}


def taps_to_change(module: AnsibleModule, brew_path: str, taps: list[str], trust: bool) -> list[str]:
    """Returns the taps whose trust state does not match `trust` yet."""
    trusted = trusted_taps(module, brew_path)
    return [tap for tap in taps if (normalized_tap(tap) in trusted) != trust]


def set_trust(module: AnsibleModule, brew_path: str, taps: list[str], trust: bool) -> tuple[bool, bool, str]:
    """Trusts or untrusts one or more taps."""
    command = "trust" if trust else "untrust"
    outstanding = taps_to_change(module, brew_path, taps, trust)
    unchanged = len(taps) - len(outstanding)

    if not outstanding:
        return (False, False, f"{command}ed: 0, already {command}ed: {unchanged}")

    if module.check_mode:
        module.exit_json(changed=True)

    rc, out, err = module.run_command([brew_path, command, "--tap"] + outstanding)

    # `brew trust` and `brew untrust` exit successfully even when they changed
    # nothing, so read the resulting state back instead of trusting the rc.
    still_outstanding = taps_to_change(module, brew_path, outstanding, trust)
    if still_outstanding:
        failures = ", ".join(still_outstanding)
        return (
            True,
            False,
            f"{command}ed: 0, already {command}ed: {unchanged}, error: failed to {command}: {failures} due to {err}",
        )

    return (False, True, f"{command}ed: {len(outstanding)}, already {command}ed: {unchanged}")


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(aliases=["tap"], type="list", required=True, elements="str"),
            url=dict(),
            state=dict(default="present", choices=["present", "absent"]),
            trust=dict(type="bool"),
            path=dict(
                default="/usr/local/bin:/opt/homebrew/bin:/home/linuxbrew/.linuxbrew/bin",
                type="path",
            ),
        ),
        supports_check_mode=True,
    )

    path = module.params["path"]
    if path:
        path = path.split(":")

    brew_path = module.get_bin_path(
        "brew",
        required=True,
        opt_dirs=path,
    )

    taps = module.params["name"]
    url = module.params["url"]
    trust = module.params["trust"]

    if module.params["state"] == "present":
        failed, changed, msg = False, False, ""

        if url is None:
            # No tap URL provided explicitly, continue with bulk addition
            # of all the taps.
            failed, changed, msg = add_taps(module, brew_path, taps)
        else:
            # When an tap URL is provided explicitly, we allow adding
            # *single* tap only. Validate and proceed to add single tap.
            if len(taps) > 1:
                msg = "List of multiple taps may not be provided with 'url' option."
                module.fail_json(msg=msg)
            else:
                failed, changed, msg = add_tap(module, brew_path, taps[0], url)

        if not failed and trust is not None:
            # Adjust trust after tapping, so that a tap added by this very run
            # is immediately usable.
            failed, trust_changed, trust_msg = set_trust(module, brew_path, taps, trust)
            changed = changed or trust_changed
            msg = f"{msg}, {trust_msg}"

        if failed:
            module.fail_json(msg=msg)
        else:
            module.exit_json(changed=changed, msg=msg)

    elif module.params["state"] == "absent":
        if trust:
            module.fail_json(msg="trust=true may not be used with state=absent.")

        failed, changed, msg = False, False, ""
        if trust is False:
            # Untapping does not drop the trust entry, so untrust explicitly.
            failed, changed, msg = set_trust(module, brew_path, taps, False)

        if not failed:
            failed, remove_changed, remove_msg = remove_taps(module, brew_path, taps)
            changed = changed or remove_changed
            msg = f"{msg}, {remove_msg}" if msg else remove_msg

        if failed:
            module.fail_json(msg=msg)
        else:
            module.exit_json(changed=changed, msg=msg)


if __name__ == "__main__":
    main()
