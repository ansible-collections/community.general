#!/usr/bin/python
# Copyright (c) 2018, Florian Paul Azim Hoberg (@gyptazy) <gyptazy@gyptazy.ch>
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: yum_versionlock
version_added: 2.0.0
short_description: Locks / unlocks a installed package(s) from being updated by yum package manager
description:
  - This module adds installed packages to yum versionlock to prevent the package(s) from being updated.
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
      - Package name or a list of package names with optional version or wildcards.
      - Specifying versions is supported since community.general 7.2.0.
    type: list
    required: true
    elements: str
  state:
    description:
      - If state is V(present), package(s) is/are added to yum versionlock list.
      - If state is V(absent), package(s) is/are removed from yum versionlock list.
    choices: ['absent', 'present']
    type: str
    default: present
notes:
  - Requires yum-plugin-versionlock package on the remote node.
  - With dnf5, O(state=absent) removes all lock entries of the matching packages, regardless of the version given in O(name).
requirements:
  - yum
  - yum-versionlock
author:
  - Florian Paul Azim Hoberg (@gyptazy)
  - Amin Vakil (@aminvakil)
"""

EXAMPLES = r"""
- name: Prevent Apache / httpd from being updated
  community.general.yum_versionlock:
    state: present
    name:
      - httpd

- name: Prevent Apache / httpd version 2.4.57-2 from being updated
  community.general.yum_versionlock:
    state: present
    name:
      - httpd-0:2.4.57-2.el9

- name: Prevent multiple packages from being updated
  community.general.yum_versionlock:
    state: present
    name:
      - httpd
      - nginx
      - haproxy
      - curl

- name: Remove lock from Apache / httpd to be updated again
  community.general.yum_versionlock:
    state: absent
    name: httpd
"""

RETURN = r"""
packages:
  description: A list of package(s) in versionlock list.
  returned: success
  type: list
  elements: str
  sample: ["httpd"]
state:
  description: State of package(s).
  returned: success
  type: str
  sample: present
"""

import os
import re
from fnmatch import fnmatch

from ansible.module_utils.basic import AnsibleModule

# on DNF-based distros, yum is a symlink to dnf, so we try to handle their different entry formats.
NEVRA_RE_YUM = re.compile(
    r"^(?P<exclude>!)?(?P<epoch>\d+):(?P<name>.+)-"
    r"(?P<version>.+)-(?P<release>.+)\.(?P<arch>.+)$"
)
NEVRA_RE_DNF = re.compile(
    r"^(?P<exclude>!)?(?P<name>.+)-(?P<epoch>\d+):(?P<version>.+)-"
    r"(?P<release>.+)\.(?P<arch>.+)$"
)
# dnf5 lists each entry as a stanza: a "Package name:" line followed by its conditions
DNF5_EVR_RE = re.compile(r"^evr\s*(?P<comparator>!?=)\s*(?P<evr>\S+)$")


def parse_dnf5_list(output):
    """Convert the stanzas listed by dnf5 into entries in the dnf format"""
    entries = []
    name = None
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("Package name:"):
            name = line.split(":", 1)[1].strip()
            continue
        m = DNF5_EVR_RE.match(line)
        if name and m:
            evr = m.group("evr") if ":" in m.group("evr") else f"0:{m.group('evr')}"
            exclude = "!" if m.group("comparator") == "!=" else ""
            entries.append(f"{exclude}{name}-{evr}.*")
    return entries


class YumVersionLock:
    def __init__(self, module):
        self.module = module
        self.params = module.params
        self.yum_bin = module.get_bin_path("yum", required=True)
        self.dnf5 = os.path.basename(os.path.realpath(self.yum_bin)) == "dnf5"

    def get_versionlock_packages(self):
        """Get an overview of all packages on yum versionlock"""
        rc, out, err = self.module.run_command([self.yum_bin, "versionlock", "list"])
        if rc == 0:
            if self.dnf5:
                return parse_dnf5_list(out)
            return out.split()
        elif rc == 1 and "o such command:" in err:
            self.module.fail_json(msg=f"Error: Please install rpm package yum-plugin-versionlock : {err}{out}")
        self.module.fail_json(msg=f"Error: {err}{out}")

    def ensure_state(self, packages, command):
        """Ensure packages state"""
        rc, out, err = self.module.run_command([self.yum_bin, "-q", "versionlock", command] + packages)
        # If no package can be found this will be written with rc 0, on stdout (dnf) or stderr (dnf5)
        for output in (out, err):
            if "No package found for" in output:
                self.module.fail_json(msg=output)
        if rc == 0:
            return True
        self.module.fail_json(msg=f"Error: {err}{out}")


def match(entry, name):
    match = False
    m = NEVRA_RE_YUM.match(entry)
    if not m:
        m = NEVRA_RE_DNF.match(entry)
    if not m:
        return False
    if fnmatch(m.group("name"), name):
        match = True
    if entry.rstrip(".*") == name:
        match = True
    return match


def main():
    """start main program to add/delete a package to yum versionlock"""
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default="present", choices=["present", "absent"]),
            name=dict(required=True, type="list", elements="str"),
        ),
        supports_check_mode=True,
    )
    module.run_command_environ_update = {"LANGUAGE": "C", "LC_ALL": "C"}

    state = module.params["state"]
    packages = module.params["name"]
    changed = False

    yum_v = YumVersionLock(module)

    # Get an overview of all packages that have a version lock
    versionlock_packages = yum_v.get_versionlock_packages()

    # Ensure versionlock state of packages
    packages_list = []
    if state in ("present",):
        command = "add"
        for single_pkg in packages:
            if not any(match(pkg, single_pkg) for pkg in versionlock_packages):
                packages_list.append(single_pkg)
        if packages_list:
            if module.check_mode:
                changed = True
            else:
                changed = yum_v.ensure_state(packages_list, command)
    elif state in ("absent",):
        command = "delete"
        for single_pkg in packages:
            matched = [pkg for pkg in versionlock_packages if match(pkg, single_pkg)]
            if not matched:
                continue
            if yum_v.dnf5:
                # dnf5 only deletes locks by their exact package name
                for pkg in matched:
                    name = NEVRA_RE_DNF.match(pkg).group("name")
                    if name not in packages_list:
                        packages_list.append(name)
            else:
                packages_list.append(single_pkg)
        if packages_list:
            if module.check_mode:
                changed = True
            else:
                changed = yum_v.ensure_state(packages_list, command)

    module.exit_json(changed=changed, meta={"packages": packages, "state": state})


if __name__ == "__main__":
    main()
