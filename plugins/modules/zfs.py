#!/usr/bin/python

# Copyright (c) 2013, Johan Wiren <johan.wiren.se@gmail.com>
# Copyright (c) 2017, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: zfs
short_description: Manage ZFS
description:
  - Manages ZFS file systems, volumes, clones and snapshots.
extends_documentation_fragment:
  - community.general._attributes
attributes:
  check_mode:
    support: partial
    details:
      - In certain situations it may report a task as changed that is not reported as changed when C(check_mode) is disabled.
      - For example, this might occur when the zpool C(altroot) option is set.
  diff_mode:
    support: full
options:
  name:
    description:
      - File system, snapshot or volume name, for example V(rpool/myfs).
    required: true
    type: str
  state:
    description:
      - Whether to create (V(present)), or remove (V(absent)) a file system, snapshot or volume. All parents/children are
        created/destroyed as needed to reach the desired state.
    choices: [absent, present]
    required: true
    type: str
  origin:
    description:
      - Snapshot from which to create a clone.
    type: str
  extra_zfs_properties:
    description:
      - A dictionary of zfs properties to be set.
      - See the zfs(8) man page for more information.
      - Properties that can only be set when the dataset is created (V(casesensitivity), V(encryption), V(keyformat),
        V(normalization), V(pbkdf2iters), V(utf8only), V(volblocksize)) are not changed if the dataset already exists.
        A warning is issued if their current value differs from the requested one.
      - Values of size properties (V(quota), V(recordsize), V(refquota), V(refreservation), V(reservation),
        V(special_small_blocks), V(volblocksize), V(volsize)) written in human-readable notation, such as V(4k)
        or V(1.5G), are compared to the current value as byte counts.
    type: dict
    default: {}
author:
  - Johan Wiren (@johanwiren)
"""

EXAMPLES = r"""
- name: Create a new file system called myfs in pool rpool with the setuid property turned off
  community.general.zfs:
    name: rpool/myfs
    state: present
    extra_zfs_properties:
      setuid: 'off'

- name: Create a new volume called myvol in pool rpool.
  community.general.zfs:
    name: rpool/myvol
    state: present
    extra_zfs_properties:
      volsize: 10M

- name: Create a snapshot of rpool/myfs file system.
  community.general.zfs:
    name: rpool/myfs@mysnapshot
    state: present

- name: Create a new file system called myfs2 with snapdir enabled
  community.general.zfs:
    name: rpool/myfs2
    state: present
    extra_zfs_properties:
      snapdir: enabled

- name: Create a new file system by cloning a snapshot
  community.general.zfs:
    name: rpool/cloned_fs
    state: present
    origin: rpool/myfs@mysnapshot

- name: Destroy a filesystem
  community.general.zfs:
    name: rpool/myfs
    state: absent
"""

import os
import re
from decimal import Decimal

from ansible.module_utils.basic import AnsibleModule

# properties that cannot be changed with "zfs set" once the dataset exists
CREATE_ONLY_PROPERTIES = frozenset(
    (
        "casesensitivity",
        "encryption",
        "keyformat",
        "normalization",
        "pbkdf2iters",
        "utf8only",
        "volblocksize",
    )
)

SIZE_PROPERTIES = frozenset(
    (
        "quota",
        "recordsize",
        "refquota",
        "refreservation",
        "reservation",
        "special_small_blocks",
        "volblocksize",
        "volsize",
    )
)
SIZE_SUFFIXES = "BKMGTPEZ"
SIZE_RE = re.compile(r"(?P<number>\d+(?:\.\d+)?)(?:(?P<suffix>[KMGTPEZ])(?:i?B)?|B)?", re.IGNORECASE)


# convert human-readable sizes, such as 4k or 1.5G, to the byte count reported by "zfs get -p"
def normalize_value(prop, value):
    if value is None or prop not in SIZE_PROPERTIES:
        return value
    match = SIZE_RE.fullmatch(str(value))
    if not match:
        return value
    suffix = (match.group("suffix") or "B").upper()
    multiplier = 1024 ** SIZE_SUFFIXES.index(suffix)
    return str(int(Decimal(match.group("number")) * multiplier))


class Zfs:
    def __init__(self, module, name, extra_zfs_properties):
        self.module = module
        self.name = name
        self.extra_zfs_properties = extra_zfs_properties
        self.changed = False
        self.zfs_cmd = module.get_bin_path("zfs", True)
        self.zpool_cmd = module.get_bin_path("zpool", True)
        self.pool = name.split("/")[0].split("@")[0]
        self.is_solaris = os.uname()[0] == "SunOS"
        self.is_openzfs = self.check_openzfs()
        self.enhanced_sharing = self.check_enhanced_sharing()

    def check_openzfs(self):
        cmd = [self.zpool_cmd]
        cmd.extend(["get", "version"])
        cmd.append(self.pool)
        (rc, out, err) = self.module.run_command(cmd, check_rc=True)
        version = out.splitlines()[-1].split()[2]
        if version == "-":
            return True
        return int(version) == 5000

    def check_enhanced_sharing(self):
        if self.is_solaris and not self.is_openzfs:
            cmd = [self.zpool_cmd]
            cmd.extend(["get", "version"])
            cmd.append(self.pool)
            (rc, out, err) = self.module.run_command(cmd, check_rc=True)
            version = out.splitlines()[-1].split()[2]
            if int(version) >= 34:
                return True
        return False

    def exists(self):
        cmd = [self.zfs_cmd, "list", "-t", "all", self.name]
        rc, dummy, dummy = self.module.run_command(cmd)
        return rc == 0

    def create(self):
        if self.module.check_mode:
            self.changed = True
            return
        extra_zfs_properties = self.extra_zfs_properties
        origin = self.module.params.get("origin")
        cmd = [self.zfs_cmd]

        if "@" in self.name:
            action = "snapshot"
        elif origin:
            action = "clone"
        else:
            action = "create"

        cmd.append(action)

        if action in ["create", "clone"]:
            cmd += ["-p"]

        if extra_zfs_properties:
            for prop, value in extra_zfs_properties.items():
                if prop == "volsize":
                    cmd += ["-V", value]
                elif prop == "volblocksize":
                    cmd += ["-b", value]
                else:
                    cmd += ["-o", f"{prop}={value}"]
        if origin and action == "clone":
            cmd.append(origin)
        cmd.append(self.name)
        self.module.run_command(cmd, check_rc=True)
        self.changed = True

    def destroy(self):
        if self.module.check_mode:
            self.changed = True
            return
        cmd = [self.zfs_cmd, "destroy", "-R", self.name]
        self.module.run_command(cmd, check_rc=True)
        self.changed = True

    def set_property(self, prop, value):
        if self.module.check_mode:
            self.changed = True
            return
        cmd = [self.zfs_cmd, "set", f"{prop}={value!s}", self.name]
        self.module.run_command(cmd, check_rc=True)

    def set_properties_if_changed(self):
        diff = {"before": {"extra_zfs_properties": {}}, "after": {"extra_zfs_properties": {}}}
        current_properties = self.list_properties()
        previous_values = {}
        settable_properties = {}
        for prop, value in self.extra_zfs_properties.items():
            if prop not in CREATE_ONLY_PROPERTIES:
                settable_properties[prop] = value
                continue
            current_value = self.get_property(prop, current_properties)
            if normalize_value(prop, current_value) != normalize_value(prop, value):
                self.module.warn(
                    f"Property {prop} can only be set when the dataset is created, "
                    f"current value {current_value!r} differs from requested value {value!r}"
                )
        for prop, value in settable_properties.items():
            current_value = self.get_property(prop, current_properties)
            if normalize_value(prop, current_value) != normalize_value(prop, value):
                previous_values[prop] = current_value
                self.set_property(prop, value)
                diff["before"]["extra_zfs_properties"][prop] = current_value
                diff["after"]["extra_zfs_properties"][prop] = value
        if self.module.check_mode:
            return diff
        updated_properties = self.list_properties()
        for prop in settable_properties:
            value = self.get_property(prop, updated_properties)
            if value is None:
                self.module.fail_json(msg=f"zfsprop was not present after being successfully set: {prop}")
            if prop in previous_values and previous_values[prop] != value:
                self.changed = True
            if prop in diff["after"]["extra_zfs_properties"]:
                diff["after"]["extra_zfs_properties"][prop] = value
        return diff

    def list_properties(self):
        cmd = [self.zfs_cmd, "get", "-H", "-p", "-o", "property,source"]
        if self.enhanced_sharing:
            cmd += ["-e"]
        cmd += ["all", self.name]
        rc, out, err = self.module.run_command(cmd)
        properties = []
        for line in out.splitlines():
            prop, source = line.split("\t")
            # include source '-' so that creation-only properties are not removed
            # to avoids errors when the dataset already exists and the property is not changed
            # this scenario is most likely when the same playbook is run more than once
            if source in ("local", "received", "-"):
                properties.append(prop)
        return properties

    def get_property(self, name, list_of_properties):
        # Add alias for enhanced sharing properties
        if self.enhanced_sharing:
            if name == "sharenfs":
                name = "share.nfs"
            elif name == "sharesmb":
                name = "share.smb"
        if name not in list_of_properties:
            return None
        cmd = [self.zfs_cmd, "get", "-H", "-p", "-o", "value"]
        if self.enhanced_sharing:
            cmd += ["-e"]
        cmd += [name, self.name]
        rc, out, err = self.module.run_command(cmd)
        if rc != 0:
            return None
        #
        # Strip last newline
        #
        return out[:-1]


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type="str", required=True),
            state=dict(type="str", required=True, choices=["absent", "present"]),
            origin=dict(type="str"),
            extra_zfs_properties=dict(type="dict", default={}),
        ),
        supports_check_mode=True,
    )
    module.run_command_environ_update = {"LANGUAGE": "C", "LC_ALL": "C"}

    state = module.params.get("state")
    name = module.params.get("name")

    if module.params.get("origin") and "@" in name:
        module.fail_json(msg="cannot specify origin when operating on a snapshot")

    # Reverse the boolification of zfs properties
    for prop, value in module.params["extra_zfs_properties"].items():
        if isinstance(value, bool):
            if value is True:
                module.params["extra_zfs_properties"][prop] = "on"
            else:
                module.params["extra_zfs_properties"][prop] = "off"
        else:
            module.params["extra_zfs_properties"][prop] = value

    result = dict(
        name=name,
        state=state,
    )

    zfs = Zfs(module, name, module.params["extra_zfs_properties"])

    if state == "present":
        if zfs.exists():
            result["diff"] = zfs.set_properties_if_changed()
        else:
            zfs.create()
            result["diff"] = {"before": {"state": "absent"}, "after": {"state": state}}

    elif state == "absent":
        if zfs.exists():
            zfs.destroy()
            result["diff"] = {"before": {"state": "present"}, "after": {"state": state}}
        else:
            result["diff"] = {}

    result["diff"]["before_header"] = name
    result["diff"]["after_header"] = name

    result.update(zfs.extra_zfs_properties)
    result["changed"] = zfs.changed
    module.exit_json(**result)


if __name__ == "__main__":
    main()
