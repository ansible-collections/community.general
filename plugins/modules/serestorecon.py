#!/usr/bin/python
# Copyright (c) 2026, Nicholas Brodersen <nicholasbrodersen01@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: serestorecon
short_description: Restore SELinux file contexts
version_added: 13.5.0
description:
  - Restores SELinux file contexts to the values defined by the active SELinux policy.
  - Similar to the C(restorecon) command.
extends_documentation_fragment:
  - community.general._attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: full
options:
  path:
    description:
      - Path whose SELinux file context should be restored.
    type: path
    required: true
  recurse:
    description:
      - Whether to process files and directories recursively below O(path).
    type: bool
    default: false
  exclude_paths:
    description:
      - Paths to exclude when recursively processing O(path).
      - An excluded directory and all of its contents are skipped.
      - O(path) itself is always processed.
    type: list
    elements: path
    default: []
  cross_filesystems:
    description:
      - Whether recursive processing can include paths on filesystems other than the
        filesystem containing O(path).
      - When V(false), paths whose device ID differs from O(path) are skipped.
      - This option only has an effect when O(recurse=true).
    type: bool
    default: true
  context:
    description:
      - Controls which components of the SELinux context are restored.
      - V(type) restores only the SELinux type component.
      - V(user_role) restores the SELinux user, role, and type components while
        preserving the existing range.
      - V(user_role) requires SELinux Python bindings that expose
        C(SELINUX_RESTORECON_SET_USER_ROLE), introduced in libselinux 3.9.
      - V(full) restores the complete policy-defined SELinux context.
    type: str
    choices:
      - type
      - user_role
      - full
    default: type
requirements:
  - SELinux Python bindings (C(libselinux-python) or distribution equivalent)
author:
  - Nicholas Brodersen (@NicholasBrodersen)
"""

EXAMPLES = r"""
- name: Restore the SELinux type for a file
  community.general.serestorecon:
    path: /etc/httpd/conf/httpd.conf

- name: Recursively restore SELinux types
  community.general.serestorecon:
    path: /var/www/html
    recurse: true

- name: Restore contexts while excluding a directory
  community.general.serestorecon:
    path: /var/www/html
    recurse: true
    exclude_paths:
      - /var/www/html/cache

- name: Do not process paths on other filesystems
  community.general.serestorecon:
    path: /srv
    recurse: true
    cross_filesystems: false

- name: Restore the SELinux user, role, and type
  community.general.serestorecon:
    path: /var/www/html
    recurse: true
    context: user_role

- name: Restore the complete policy-defined SELinux context
  community.general.serestorecon:
    path: /var/www/html
    recurse: true
    context: full
"""

RETURN = r"""
changed_paths:
  description:
    - Paths whose SELinux contexts were restored.
  returned: success
  type: list
  elements: dict
  contains:
    path:
      description:
        - Path whose SELinux context required restoration.
      type: str
      returned: success
      sample: /var/www/html/index.html
    previous:
      description:
        - SELinux context before restoration.
      type: str
      returned: success
      sample: system_u:object_r:var_t:s0
    restored:
      description:
        - SELinux context read back after restoration.
      type: str
      returned: success
      sample: system_u:object_r:httpd_sys_content_t:s0
"""

import errno
import os
import stat
import typing as t
from pathlib import Path

from ansible_collections.community.general.plugins.module_utils import _deps as deps
from ansible_collections.community.general.plugins.module_utils._module_helper import ModuleHelper

with deps.declare("libselinux-python", reason="the SELinux Python bindings are required to restore file contexts"):
    import selinux


class SERestoreconModule(ModuleHelper):
    module = dict(
        argument_spec=dict(
            path=dict(
                type="path",
                required=True,
            ),
            recurse=dict(
                type="bool",
                default=False,
            ),
            exclude_paths=dict(
                type="list",
                elements="path",
                default=[],
            ),
            cross_filesystems=dict(
                type="bool",
                default=True,
            ),
            context=dict(
                type="str",
                choices=["type", "user_role", "full"],
                default="type",
            ),
        ),
        supports_check_mode=True,
    )

    def get_restorecon_flags(self) -> int:
        flags = (
            selinux.SELINUX_RESTORECON_REALPATH
            | selinux.SELINUX_RESTORECON_IGNORE_DIGEST
            | selinux.SELINUX_RESTORECON_ABORT_ON_ERROR
        )

        if self.vars.context == "user_role":
            if not hasattr(selinux, "SELINUX_RESTORECON_SET_USER_ROLE"):
                self.do_raise("`context: user_role` not available on SELinux version. Use `context: full`.")
            flags |= selinux.SELINUX_RESTORECON_SET_USER_ROLE
        elif self.vars.context == "full":
            flags |= selinux.SELINUX_RESTORECON_SET_SPECFILE_CTX

        return flags

    def get_desired_label(self, handle, path: Path) -> str | None:
        try:
            rc, desired = selinux.selabel_lookup_raw(handle, os.fspath(path), stat.S_IFMT(os.lstat(path).st_mode))
            if rc != 0:
                self.do_raise(f"Failed to get desired label for {path}")
            return desired
        except OSError as exc:
            if exc.errno == errno.ENOENT:
                return None
            raise exc

    def get_current_label(self, path: Path) -> str:
        rc, current = selinux.lgetfilecon_raw(os.fspath(path))
        if rc < 0:
            self.do_raise(f"Failed to get current SELinux context for {path}")
        return current

    def get_expected_label(self, desired: str, current: str) -> str:
        """Apply the selected policy components while preserving the others."""
        if self.vars.context == "full":
            return desired

        desired_parts = desired.split(":", 3)
        current_parts = current.split(":", 3)

        if self.vars.context == "user_role":
            current_parts[:3] = desired_parts[:3]
        else:
            current_parts[2] = desired_parts[2]

        return ":".join(current_parts)

    def labels_differ(self, desired: str, current: str) -> bool:
        return self.get_expected_label(desired, current) != current

    def restore_file_context(self, path: Path, flags: int) -> None:
        rc = selinux.selinux_restorecon(
            os.fspath(path),
            flags,
        )
        if rc != 0:
            self.do_raise(f"Failed to restore SELinux context for {path}")

    def get_contexts(self, key):
        return [
            {
                "path": item["path"],
                "context": item[key],
            }
            for item in self.changed_paths
        ]

    def iter_paths(self) -> t.Generator[Path, None, None]:
        # The python bindings do provide a way to recursively apply restorecon on files
        # and also to provide a list of exclusions.
        #
        # However if we use the python bindings recurive and exclusions functions, we
        # will not get back the file paths that have been changed which is needed for return information.
        # This feature may also not be available based on the OS version.
        #
        # Therefore, we want to manually iterate and exclude file paths on our own, and just apply restorecon
        # on each path we yield.
        yield self.path

        if not self.vars.recurse:
            return
        all_paths = self.path.rglob("*")
        exclude_paths = tuple(map(Path, self.vars.exclude_paths))

        all_paths_filtered = [
            path
            for path in all_paths
            if not any(path == excluded or excluded in path.parents for excluded in exclude_paths)
        ]

        primary_filesystem_id = self.path.lstat().st_dev
        if not self.vars.cross_filesystems:
            all_paths_filtered = list(
                filter(lambda path: path.lstat().st_dev == primary_filesystem_id, all_paths_filtered)
            )

        yield from all_paths_filtered

    def __init_module__(self):
        deps.validate(self.module)

        if not self.module.selinux_enabled():
            self.do_raise("SELinux is not enabled")

        self.path = Path(self.vars.path)
        self.changed_paths = []
        self.restorecon_flags = self.get_restorecon_flags()

    def __run__(self):
        se_label_handle = selinux.selabel_open(
            selinux.SELABEL_CTX_FILE,
            None,
            0,
        )

        try:
            for path in self.iter_paths():
                desired_label = self.get_desired_label(se_label_handle, path)

                if desired_label is None:
                    continue

                current_label = self.get_current_label(path)

                if not self.labels_differ(desired_label, current_label):
                    continue

                if self.check_mode:
                    restored_label = self.get_expected_label(desired_label, current_label)
                else:
                    self.restore_file_context(
                        path,
                        self.restorecon_flags,
                    )
                    restored_label = self.get_current_label(path)

                if restored_label == current_label:
                    continue

                self.changed_paths.append(
                    {
                        "path": str(path),
                        "previous": current_label,
                        "restored": restored_label,
                    }
                )

        finally:
            selinux.selabel_close(se_label_handle)

    def __quit_module__(self):
        self.changed = bool(self.changed_paths)

        self.vars.set(
            "file_contexts",
            self.get_contexts("previous"),
            output=False,
            diff=True,
            change=True,
        )

        self.vars.set(
            "file_contexts",
            self.get_contexts("restored"),
        )

        self.update_output(
            changed_paths=self.changed_paths,
        )


def main():
    SERestoreconModule().run()


if __name__ == "__main__":
    main()
