#!/usr/bin/python

# Copyright (c) 2012, Michael DeHaan <michael.dehaan@gmail.com>
# Copyright (c) 2017, Ansible Project
# Copyright 2026, Felix Fontein (felix@fontein.de)
# Copyright 2026, Plexim GmbH
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: write_binary_file
short_description: Write binary file from Base64 encoded input
version_added: 13.3.0
description:
  - Given Base64 encoded content, write it to a file.
  - This is useful when Base64-encoded binary content (that is not valid UTF-8)
    is retrieved from a credentials store (or similar sources) and needs to be written to a file.
    The M(ansible.builtin.copy) module with its O(ansible.builtin.copy#module:content) parameter
    can only be used to write content that is valid UTF-8 encoded text.
extends_documentation_fragment:
  - ansible.builtin.files
  - community.general._attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  path:
    description:
      - The file to write to.
    type: path
    required: true
    aliases:
      - dest
  content:
    description:
      - The Base64 encoded content.
    type: str
    required: true
  follow:
    description:
      - Whether filesystem links in the destination should be followed.
      - If set to V(true) and O(path) is a symlink, the file pointed to by O(path)
        (resp. after following further links) is modified, instead of O(path) itself.
    type: bool
    default: false
  force:
    description:
      - Influence whether the remote file must always be replaced.
      - If V(true), the remote file will be replaced when contents are different than the source.
      - If V(false), the file will only be transferred if the destination does not exist.
    type: bool
    default: true
  backup:
    description:
      - Create a backup file including the timestamp information so you can get the original file back if you somehow clobbered it incorrectly.
    type: bool
    default: false

seealso:
  - plugin: community.general.binary_file
    plugin_type: lookup
  - module: ansible.builtin.copy

author:
  - Felix Fontein (@felixfontein) <felix@fontein.de>
"""

EXAMPLES = r"""
- name: Write binary file
  community.general.write_binary_file:
    path: /foo
    content: "{{ lookup('community.general.binary_file', '/bar') }}"
    mode: "0600"
    owner: root
    group: root
  become: true

- name: Write binary decrypted from SOPS
  community.general.write_binary_file:
    path: /etc/encrypted.bin
    content: "{{ lookup('community.sops.sops', 'encrypted.sops.bin', base64=true, rstrip=false) }}"
    mode: "0600"
    owner: root
    group: root
  become: true
"""

RETURN = r"""
backup_file:
  description:
    - Name of backup file created.
  returned: changed and if O(backup=true)
  type: str
  sample: /path/to/file.txt.2015-02-12@22:09~
"""

import base64
import os
import tempfile

from ansible.module_utils.basic import AnsibleModule


def main() -> None:
    module = AnsibleModule(
        {
            "path": {"type": "path", "required": True, "aliases": ["dest"]},
            "content": {"type": "str", "required": True, "no_log": True},
            "follow": {"type": "bool", "default": False},
            "force": {"type": "bool", "default": True},
            "backup": {"type": "bool", "default": False},
        },
        supports_check_mode=True,
        add_file_common_args=True,
    )

    path: str = module.params["path"]
    content_b64: str = module.params["content"]
    force: bool = module.params["force"]
    follow: bool = module.params["follow"]
    backup: bool = module.params["backup"]

    try:
        content = base64.b64decode(content_b64)
    except Exception as exc:
        module.fail_json(msg=f"Cannot decode Base64-encoded content: {exc}")

    current_content: bytes | None = None
    if os.path.exists(path):
        if os.path.islink(path) and follow:
            path = os.path.realpath(path)
        dirname = os.path.dirname(path)
        if os.path.isfile(path):
            if not force:
                module.exit_json(msg="File already exists", changed=False)
            if not os.path.islink(path) and os.access(path, os.R_OK):
                try:
                    with open(path, "rb") as f:
                        current_content = f.read()
                except FileNotFoundError:
                    pass
                except Exception as exc:
                    module.fail_json(msg=f"Cannot read {path}: {exc}")
    else:
        dirname = os.path.dirname(path)
        if dirname and not os.path.exists(dirname):
            try:
                # os.path.exists() can return false in some
                # circumstances where the directory does not have
                # the execute bit for the current user set, in
                # which case the stat() call will raise an OSError
                os.stat(dirname)
            except OSError as e:
                if "permission denied" in str(e).lower():
                    module.fail_json(msg=f"Destination directory {dirname} is not accessible")
            module.fail_json(msg=f"Destination directory {dirname} does not exist")

    if not os.access(dirname, os.W_OK) and not module.params["unsafe_writes"]:
        module.fail_json(msg=f"Destination {dirname} not writable")

    if force:
        changed = content != current_content
    else:
        changed = current_content is None

    backup_file: str | None = None
    if changed and not module.check_mode:
        if backup:
            if os.path.exists(path):
                backup_file = module.backup_local(path)
        if os.path.islink(path):
            try:
                os.unlink(path)
            except OSError as exc:
                module.fail_json(msg=f"Cannot unlink symbolic link: {exc}")

        try:
            src_f, src = tempfile.mkstemp(dir=dirname)
            module.add_cleanup_file(src)
            try:
                to_write = len(content)
                while to_write > 0:
                    written = os.write(src_f, content[-to_write:])
                    if written <= 0:
                        raise OSError(f"os.write returned {written}")
                    to_write -= written
            finally:
                os.close(src_f)
        except OSError as exc:
            module.fail_json(msg=f"Cannot write data to temporary file: {exc}")

        module.atomic_move(src, path, unsafe_writes=module.params["unsafe_writes"], keep_dest_attrs=True)

    file_args = module.load_file_common_arguments(module.params, path=path)
    changed = module.set_fs_attributes_if_different(file_args, changed)

    module.exit_json(changed=changed, backup_file=backup_file)


if __name__ == "__main__":
    main()
