#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2021, Roberto Moreda <moreda@allenta.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: dnf_versionlock
version_added: '4.0.0'
short_description: Locks package versions in C(dnf) based systems
description:
- Locks package versions using the C(versionlock) plugin in C(dnf) based
  systems. This plugin takes a set of name and versions for packages and
  excludes all other versions of those packages. This allows you to for example
  protect packages from being updated by newer versions. The state of the
  plugin that reflects locking of packages is the C(locklist).
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: partial
    details:
      - The logics of the C(versionlock) plugin for corner cases could be
        confusing, so please take in account that this module will do its best to
        give a C(check_mode) prediction on what is going to happen. In case of
        doubt, check the documentation of the plugin.
      - Sometimes the module could predict changes in C(check_mode) that will not
        be such because C(versionlock) concludes that there is already a entry in
        C(locklist) that already matches.
  diff_mode:
    support: none
options:
  name:
    description:
      - Package name spec to add or exclude to or delete from the C(locklist)
        using the format expected by the C(dnf repoquery) command.
      - This parameter is mutually exclusive with O(state=clean).
    type: list
    required: false
    elements: str
    default: []
  raw:
    description:
        - Do not resolve package name specs to NEVRAs to find specific version
          to lock to. Instead the package name specs are used as they are. This
          enables locking to not yet available versions of the package.
    type: bool
    default: false
  state:
    description:
        - Whether to add (V(present) or V(excluded)) to or remove (V(absent) or
          V(clean)) from the C(locklist).
        - V(present) will add a package name spec to the C(locklist). If there is a
          installed package that matches, then only that version will be added.
          Otherwise, all available package versions will be added.
        - V(excluded) will add a package name spec as excluded to the
          C(locklist). It means that packages represented by the package name
          spec will be excluded from transaction operations. All available
          package versions will be added.
        - V(absent) will delete entries in the C(locklist) that match the
          package name spec.
        - V(clean) will delete all entries in the C(locklist). This option is
          mutually exclusive with O(name).
    choices: [ 'absent', 'clean', 'excluded', 'present' ]
    type: str
    default: present
notes:
  - In an ideal world, the C(versionlock) plugin would have a dry-run option to
    know for sure what is going to happen. So far we have to work with a best
    guess as close as possible to the behaviour inferred from its code.
  - For most of cases where you want to lock and unlock specific versions of a
    package, this works fairly well.
requirements:
  - dnf
  - dnf-plugin-versionlock
author:
  - Roberto Moreda (@moreda) <moreda@allenta.com>
'''

EXAMPLES = r'''
- name: Prevent installed nginx from being updated
  community.general.dnf_versionlock:
    name: nginx
    state: present

- name: Prevent multiple packages from being updated
  community.general.dnf_versionlock:
    name:
      - nginx
      - haproxy
    state: present

- name: Remove lock from nginx to be updated again
  community.general.dnf_versionlock:
    package: nginx
    state: absent

- name: Exclude bind 32:9.11 from installs or updates
  community.general.dnf_versionlock:
    package: bind-32:9.11*
    state: excluded

- name: Keep bash package in major version 4
  community.general.dnf_versionlock:
    name: bash-0:4.*
    raw: true
    state: present

- name: Delete all entries in the locklist of versionlock
  community.general.dnf_versionlock:
    state: clean
'''

RETURN = r'''
locklist_pre:
    description: Locklist before module execution.
    returned: success
    type: list
    elements: str
    sample: [ 'bash-0:4.4.20-1.el8_4.*', '!bind-32:9.11.26-4.el8_4.*' ]
locklist_post:
    description: Locklist after module execution.
    returned: success and (not check mode or state is clean)
    type: list
    elements: str
    sample: [ 'bash-0:4.4.20-1.el8_4.*' ]
specs_toadd:
    description: Package name specs meant to be added by versionlock.
    returned: success
    type: list
    elements: str
    sample: [ 'bash' ]
specs_todelete:
    description: Package name specs meant to be deleted by versionlock.
    returned: success
    type: list
    elements: str
    sample: [ 'bind' ]
'''

from ansible.module_utils.basic import AnsibleModule
import fnmatch
import os
import re

DNF_BIN = "/usr/bin/dnf"
VERSIONLOCK_CONF = "/etc/dnf/plugins/versionlock.conf"
# NEVRA regex.
NEVRA_RE = re.compile(r"^(?P<name>.+)-(?P<epoch>\d+):(?P<version>.+)-"
                      r"(?P<release>.+)\.(?P<arch>.+)$")


def do_versionlock(module, command, patterns=None, raw=False):
    patterns = [] if not patterns else patterns
    raw_parameter = ["--raw"] if raw else []
    # Call dnf versionlock using a just one full NEVR package-name-spec each
    # time because multiple package-name-spec and globs are not well supported.
    #
    # This is a workaround for two alleged bugs in the dnf versionlock plugin:
    # * Multiple package-name-spec arguments don't lock correctly
    #   (https://bugzilla.redhat.com/show_bug.cgi?id=2013324).
    # * Locking a version of a not installed package disallows locking other
    #   versions later (https://bugzilla.redhat.com/show_bug.cgi?id=2013332)
    #
    # NOTE: This is suboptimal in terms of performance if there are more than a
    # few package-name-spec patterns to lock, because there is a command
    # execution per each. This will improve by changing the strategy once the
    # mentioned alleged bugs in the dnf versionlock plugin are fixed.
    if patterns:
        outs = []
        for p in patterns:
            rc, out, err = module.run_command(
                [DNF_BIN, "-q", "versionlock", command] + raw_parameter + [p],
                check_rc=True)
            outs.append(out)
        out = "\n".join(outs)
    else:
        rc, out, err = module.run_command(
            [DNF_BIN, "-q", "versionlock", command], check_rc=True)
    return out


# This is equivalent to the _match function of the versionlock plugin.
def match(entry, pattern):
    entry = entry.lstrip('!')
    if entry == pattern:
        return True
    m = NEVRA_RE.match(entry)
    if not m:
        return False
    for name in (
        '%s' % m["name"],
        '%s.%s' % (m["name"], m["arch"]),
        '%s-%s' % (m["name"], m["version"]),
        '%s-%s-%s' % (m["name"], m["version"], m["release"]),
        '%s-%s:%s' % (m["name"], m["epoch"], m["version"]),
        '%s-%s-%s.%s' % (m["name"], m["version"], m["release"], m["arch"]),
        '%s-%s:%s-%s' % (m["name"], m["epoch"], m["version"], m["release"]),
        '%s:%s-%s-%s.%s' % (m["epoch"], m["name"], m["version"], m["release"],
                            m["arch"]),
        '%s-%s:%s-%s.%s' % (m["name"], m["epoch"], m["version"], m["release"],
                            m["arch"])
    ):
        if fnmatch.fnmatch(name, pattern):
            return True
    return False


def get_packages(module, patterns, only_installed=False):
    packages_available_map_name_evrs = {}
    rc, out, err = module.run_command(
        [DNF_BIN, "-q", "repoquery"] +
        (["--installed"] if only_installed else []) +
        patterns,
        check_rc=True)

    for p in out.split():
        # Extract the NEVRA pattern.
        m = NEVRA_RE.match(p)
        if not m:
            module.fail_json(
                msg="failed to parse nevra for %s" % p,
                rc=rc, out=out, err=err)

        evr = "%s:%s-%s" % (m["epoch"],
                            m["version"],
                            m["release"])

        packages_available_map_name_evrs.setdefault(m["name"], set())
        packages_available_map_name_evrs[m["name"]].add(evr)
    return packages_available_map_name_evrs


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type="list", elements="str", default=[]),
            raw=dict(type="bool", default=False),
            state=dict(type="str", default="present",
                       choices=["present", "absent", "excluded", "clean"]),
        ),
        supports_check_mode=True,
    )

    patterns = module.params["name"]
    raw = module.params["raw"]
    state = module.params["state"]
    changed = False
    msg = ""

    # Check module pre-requisites.
    if not os.path.exists(DNF_BIN):
        module.fail_json(msg="%s was not found" % DNF_BIN)
    if not os.path.exists(VERSIONLOCK_CONF):
        module.fail_json(msg="plugin versionlock is required")

    # Check incompatible options.
    if state == "clean" and patterns:
        module.fail_json(msg="clean state is incompatible with a name list")
    if state != "clean" and not patterns:
        module.fail_json(msg="name list is required for %s state" % state)

    locklist_pre = do_versionlock(module, "list").split()

    specs_toadd = []
    specs_todelete = []

    if state in ["present", "excluded"]:

        if raw:
            # Add raw patterns as specs to add.
            for p in patterns:
                if ((p if state == "present" else "!" + p)
                        not in locklist_pre):
                    specs_toadd.append(p)
        else:
            # Get available packages that match the patterns.
            packages_map_name_evrs = get_packages(
                module,
                patterns)

            # Get installed packages that match the patterns.
            packages_installed_map_name_evrs = get_packages(
                module,
                patterns,
                only_installed=True)

            # Obtain the list of package specs that require an entry in the
            # locklist. This list is composed by:
            #  a) the non-installed packages list with all available
            #     versions
            #  b) the installed packages list
            packages_map_name_evrs.update(packages_installed_map_name_evrs)
            for name in packages_map_name_evrs:
                for evr in packages_map_name_evrs[name]:
                    locklist_entry = "%s-%s.*" % (name, evr)

                    if (locklist_entry if state == "present"
                            else "!%s" % locklist_entry) not in locklist_pre:
                        specs_toadd.append(locklist_entry)

        if specs_toadd and not module.check_mode:
            cmd = "add" if state == "present" else "exclude"
            msg = do_versionlock(module, cmd, patterns=specs_toadd, raw=raw)

    elif state == "absent":

        if raw:
            # Add raw patterns as specs to delete.
            for p in patterns:
                if p in locklist_pre:
                    specs_todelete.append(p)

        else:
            # Get patterns that match the some line in the locklist.
            for p in patterns:
                for e in locklist_pre:
                    if match(e, p):
                        specs_todelete.append(p)

        if specs_todelete and not module.check_mode:
            msg = do_versionlock(
                module, "delete", patterns=specs_todelete, raw=raw)

    elif state == "clean":
        specs_todelete = locklist_pre

        if specs_todelete and not module.check_mode:
            msg = do_versionlock(module, "clear")

    if specs_toadd or specs_todelete:
        changed = True

    response = {
        "changed": changed,
        "msg": msg,
        "locklist_pre": locklist_pre,
        "specs_toadd": specs_toadd,
        "specs_todelete": specs_todelete
    }
    if not module.check_mode:
        response["locklist_post"] = do_versionlock(module, "list").split()
    else:
        if state == "clean":
            response["locklist_post"] = []

    module.exit_json(**response)


if __name__ == "__main__":
    main()
