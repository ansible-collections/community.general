#!/usr/bin/python

# Copyright (c) 2017-2020, Yann Amar <quidame@poivron.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
module: dpkg_divert
short_description: Override a debian package's version of a file
version_added: '0.2.0'
author:
  - quidame (@quidame)
description:
  - A diversion is for C(dpkg) the knowledge that only a given package (or the local administrator) is allowed to install
    a file at a given location. Other packages shipping their own version of this file are forced to O(divert) it, that is
    to install it at another location. It allows one to keep changes in a file provided by a debian package by preventing
    it being overwritten on package upgrade.
  - This module manages diversions of debian packages files using the C(dpkg-divert) commandline tool. It can either create
    or remove a diversion for a given file, but also update an existing diversion to modify its O(holder) and/or its O(divert)
    location.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: full
options:
  path:
    description:
      - The original and absolute path of the file to be diverted or undiverted. This path is unique, in other words it is
        not possible to get two diversions for the same O(path).
    required: true
    type: path
  state:
    description:
      - When O(state=absent), remove the diversion of the specified O(path); when O(state=present), create the diversion if
        it does not exist, or update its package O(holder) or O(divert) location, if it already exists.
    type: str
    default: present
    choices: [absent, present]
  holder:
    description:
      - The name of the package whose copy of file is not diverted, also known as the diversion holder or the package the
        diversion belongs to.
      - The actual package does not have to be installed or even to exist for its name to be valid. If not specified, the
        diversion is hold by 'LOCAL', that is reserved by/for dpkg for local diversions.
      - This parameter is ignored when O(state=absent).
    type: str
  divert:
    description:
      - The location where the versions of file are diverted.
      - Default is to add suffix C(.distrib) to the file path.
      - This parameter is ignored when O(state=absent).
    type: path
  rename:
    description:
      - Actually move the file aside (when O(state=present)) or back (when O(state=absent)), but only when changing the state
        of the diversion. This parameter has no effect when attempting to add a diversion that already exists or when removing
        an unexisting one.
      - Unless O(force=true), renaming fails if the destination file already exists (this lock being a dpkg-divert feature,
        and bypassing it being a module feature).
    type: bool
    default: false
  force:
    description:
      - When O(rename=true) and O(force=true), renaming is performed even if the target of the renaming exists, in other words
        the existing contents of the file at this location are lost.
      - This parameter is ignored when O(rename=false).
    type: bool
    default: false
requirements:
  - dpkg-divert >= 1.15.0 (Debian family)
"""

EXAMPLES = r"""
- name: Divert /usr/bin/busybox to /usr/bin/busybox.distrib and keep file in place
  community.general.dpkg_divert:
    path: /usr/bin/busybox

- name: Divert /usr/bin/busybox by package 'branding'
  community.general.dpkg_divert:
    path: /usr/bin/busybox
    holder: branding

- name: Divert and rename busybox to busybox.dpkg-divert
  community.general.dpkg_divert:
    path: /usr/bin/busybox
    divert: /usr/bin/busybox.dpkg-divert
    rename: true

- name: Remove the busybox diversion and move the diverted file back
  community.general.dpkg_divert:
    path: /usr/bin/busybox
    state: absent
    rename: true
    force: true
"""

RETURN = r"""
commands:
  description: The dpkg-divert commands ran internally by the module.
  type: list
  returned: on_success
  elements: str
  sample: "/usr/bin/dpkg-divert --no-rename --remove /etc/foobarrc"
messages:
  description: The dpkg-divert relevant messages (stdout or stderr).
  type: list
  returned: on_success
  elements: str
  sample: "Removing 'local diversion of /etc/foobarrc to /etc/foobarrc.distrib'"
diversion:
  description: The status of the diversion after task execution.
  type: dict
  returned: always
  contains:
    divert:
      description: The location of the diverted file.
      type: str
    holder:
      description: The package holding the diversion.
      type: str
    path:
      description: The path of the file to divert/undivert.
      type: str
    state:
      description: The state of the diversion.
      type: str
  sample:
    {
      "divert": "/etc/foobarrc.distrib",
      "holder": "LOCAL",
      "path": "/etc/foobarrc",
      "state": "present"
    }
"""


import re
import os

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.community.general.plugins.module_utils.version import LooseVersion


def diversion_state(module, command, path):
    diversion = dict(path=path, state="absent", divert=None, holder=None)
    rc, out, err = module.run_command([command, "--listpackage", path], check_rc=True)
    if out:
        diversion["state"] = "present"
        diversion["holder"] = out.rstrip()
        rc, out, err = module.run_command([command, "--truename", path], check_rc=True)
        diversion["divert"] = out.rstrip()
    return diversion


def main():
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(required=True, type="path"),
            state=dict(type="str", default="present", choices=["absent", "present"]),
            holder=dict(type="str"),
            divert=dict(type="path"),
            rename=dict(type="bool", default=False),
            force=dict(type="bool", default=False),
        ),
        supports_check_mode=True,
    )

    path = module.params["path"]
    state = module.params["state"]
    holder = module.params["holder"]
    divert = module.params["divert"]
    rename = module.params["rename"]
    force = module.params["force"]

    diversion_wanted = dict(path=path, state=state)
    changed = False

    DPKG_DIVERT = module.get_bin_path("dpkg-divert", required=True)
    MAINCOMMAND = [DPKG_DIVERT]

    # Option --listpackage is needed and comes with 1.15.0
    rc, stdout, stderr = module.run_command([DPKG_DIVERT, "--version"], check_rc=True)
    [current_version] = [x for x in stdout.splitlines()[0].split() if re.match("^[0-9]+[.][0-9]", x)]
    if LooseVersion(current_version) < LooseVersion("1.15.0"):
        module.fail_json(msg="Unsupported dpkg version (<1.15.0).")
    no_rename_is_supported = LooseVersion(current_version) >= LooseVersion("1.19.1")

    b_path = to_bytes(path, errors="surrogate_or_strict")
    path_exists = os.path.exists(b_path)
    # Used for things not doable with a single dpkg-divert command (as forced
    # renaming of files, and diversion's 'holder' or 'divert' updates).
    target_exists = False
    truename_exists = False

    diversion_before = diversion_state(module, DPKG_DIVERT, path)
    if diversion_before["state"] == "present":
        b_divert = to_bytes(diversion_before["divert"], errors="surrogate_or_strict")
        truename_exists = os.path.exists(b_divert)

    # Append options as requested in the task parameters, but ignore some of
    # them when removing the diversion.
    if rename:
        MAINCOMMAND.append("--rename")
    elif no_rename_is_supported:
        MAINCOMMAND.append("--no-rename")

    if state == "present":
        if holder and holder != "LOCAL":
            MAINCOMMAND.extend(["--package", holder])
            diversion_wanted["holder"] = holder
        else:
            MAINCOMMAND.append("--local")
            diversion_wanted["holder"] = "LOCAL"

        if divert:
            MAINCOMMAND.extend(["--divert", divert])
            target = divert
        else:
            target = f"{path}.distrib"

        MAINCOMMAND.extend(["--add", path])
        diversion_wanted["divert"] = target
        b_target = to_bytes(target, errors="surrogate_or_strict")
        target_exists = os.path.exists(b_target)

    else:
        MAINCOMMAND.extend(["--remove", path])
        diversion_wanted["divert"] = None
        diversion_wanted["holder"] = None

    # Start to populate the returned objects.
    diversion = diversion_before.copy()
    maincommand = " ".join(MAINCOMMAND)
    commands = [maincommand]

    if module.check_mode or diversion_wanted == diversion_before:
        MAINCOMMAND.insert(1, "--test")
        diversion_after = diversion_wanted

    # Just try and see
    rc, stdout, stderr = module.run_command(MAINCOMMAND)

    if rc == 0:
        messages = [stdout.rstrip()]

    # else... cases of failure with dpkg-divert are:
    # - The diversion does not belong to the same package (or LOCAL)
    # - The divert filename is not the same (e.g. path.distrib != path.divert)
    # - The renaming is forbidden by dpkg-divert (i.e. both the file and the
    #   diverted file exist)

    elif state != diversion_before["state"]:
        # There should be no case with 'divert' and 'holder' when creating the
        # diversion from none, and they're ignored when removing the diversion.
        # So this is all about renaming...
        if (
            rename
            and path_exists
            and ((state == "absent" and truename_exists) or (state == "present" and target_exists))
        ):
            if not force:
                msg = "Set 'force' param to True to force renaming of files."
                module.fail_json(
                    changed=changed, cmd=maincommand, rc=rc, msg=msg, stderr=stderr, stdout=stdout, diversion=diversion
                )
        else:
            msg = "Unexpected error while changing state of the diversion."
            module.fail_json(
                changed=changed, cmd=maincommand, rc=rc, msg=msg, stderr=stderr, stdout=stdout, diversion=diversion
            )

        to_remove = path
        if state == "present":
            to_remove = target

        if not module.check_mode:
            try:
                b_remove = to_bytes(to_remove, errors="surrogate_or_strict")
                os.unlink(b_remove)
            except OSError as e:
                msg = f"Failed to remove {to_remove}: {e}"
                module.fail_json(
                    changed=changed, cmd=maincommand, rc=rc, msg=msg, stderr=stderr, stdout=stdout, diversion=diversion
                )
            rc, stdout, stderr = module.run_command(MAINCOMMAND, check_rc=True)

        messages = [stdout.rstrip()]

    # The situation is that we want to modify the settings (holder or divert)
    # of an existing diversion. dpkg-divert does not handle this, and we have
    # to remove the existing diversion first, and then set a new one.
    else:
        RMDIVERSION = [DPKG_DIVERT, "--remove", path]
        if no_rename_is_supported:
            RMDIVERSION.insert(1, "--no-rename")
        rmdiversion = " ".join(RMDIVERSION)

        if module.check_mode:
            RMDIVERSION.insert(1, "--test")

        if rename:
            MAINCOMMAND.remove("--rename")
            if no_rename_is_supported:
                MAINCOMMAND.insert(1, "--no-rename")
            maincommand = " ".join(MAINCOMMAND)

        commands = [rmdiversion, maincommand]
        rc, rmdout, rmderr = module.run_command(RMDIVERSION, check_rc=True)

        if module.check_mode:
            messages = [rmdout.rstrip(), "Running in check mode"]
        else:
            rc, stdout, stderr = module.run_command(MAINCOMMAND, check_rc=True)
            messages = [rmdout.rstrip(), stdout.rstrip()]

            # Avoid if possible to orphan files (i.e. to dereference them in diversion
            # database but let them in place), but do not make renaming issues fatal.
            # BTW, this module is not about state of files involved in the diversion.
            old = diversion_before["divert"]
            new = diversion_wanted["divert"]
            if new != old:
                b_old = to_bytes(old, errors="surrogate_or_strict")
                b_new = to_bytes(new, errors="surrogate_or_strict")
                if os.path.exists(b_old) and not os.path.exists(b_new):
                    try:
                        os.rename(b_old, b_new)
                    except OSError:
                        pass

    if not module.check_mode:
        diversion_after = diversion_state(module, DPKG_DIVERT, path)

    diversion = diversion_after.copy()
    diff = dict()
    if module._diff:
        diff["before"] = diversion_before
        diff["after"] = diversion_after

    if diversion_after != diversion_before:
        changed = True

    if diversion_after == diversion_wanted:
        module.exit_json(changed=changed, diversion=diversion, commands=commands, messages=messages, diff=diff)
    else:
        msg = "Unexpected error: see stdout and stderr for details."
        module.fail_json(
            changed=changed, cmd=maincommand, rc=rc, msg=msg, stderr=stderr, stdout=stdout, diversion=diversion
        )


if __name__ == "__main__":
    main()
