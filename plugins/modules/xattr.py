#!/usr/bin/python

# Copyright (c) 2017, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: xattr
short_description: Manage user defined extended attributes
description:
  - Manages filesystem user defined extended attributes.
  - Requires that extended attributes are enabled on the target filesystem and that the C(setfattr)/C(getfattr) utilities
    are present.
extends_documentation_fragment:
  - community.general._attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  path:
    description:
      - The full path of the file/object to get the facts of.
    type: path
    required: true
    aliases: [name]
  namespace:
    description:
      - Namespace of the named name/key.
    type: str
    default: user
  key:
    description:
      - The name of a specific Extended attribute key to set/retrieve.
    type: str
  value:
    description:
      - The value to set the named name/key to, it automatically sets the O(state) to V(present).
    type: str
  state:
    description:
      - Defines which state you want to do.
      - V(read) retrieves the current value for a O(key).
      - V(present) sets O(path) to O(value), default if value is set.
      - V(all) dumps all data.
      - V(keys) retrieves all keys.
      - V(absent) deletes the key.
    type: str
    choices: [absent, all, keys, present, read]
    default: read
  follow:
    description:
      - If V(true), dereferences symlinks and sets/gets attributes on symlink target, otherwise acts on symlink itself.
    type: bool
    default: true
author:
  - Brian Coca (@bcoca)
"""

EXAMPLES = r"""
- name: Obtain the extended attributes of /etc/foo.conf
  community.general.xattr:
    path: /etc/foo.conf

- name: Set the key 'user.foo' to value 'bar'
  community.general.xattr:
    path: /etc/foo.conf
    key: foo
    value: bar

- name: Set the key 'trusted.glusterfs.volume-id' to value '0x817b94343f164f199e5b573b4ea1f914'
  community.general.xattr:
    path: /mnt/bricks/brick1
    namespace: trusted
    key: glusterfs.volume-id
    value: "0x817b94343f164f199e5b573b4ea1f914"

- name: Remove the key 'user.foo'
  community.general.xattr:
    path: /etc/foo.conf
    key: foo
    state: absent

- name: Remove the key 'trusted.glusterfs.volume-id'
  community.general.xattr:
    path: /mnt/bricks/brick1
    namespace: trusted
    key: glusterfs.volume-id
    state: absent
"""

import os

# import module snippets
from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.general.plugins.module_utils._xattr import (
    full_key,
    getfattr_runner,
    parse_getfattr,
    setfattr_runner,
)


def get_xattr_keys(module):
    return _run_xattr(module, getfattr_runner(module), "absolute_names follow path")


def get_xattr(module, key):
    if key is None:
        return _run_xattr(module, getfattr_runner(module), "absolute_names follow dump path", False)
    return _run_xattr(module, getfattr_runner(module), "absolute_names follow attr_name path", False, attr_name=key)


def set_xattr(module, key):
    return _run_xattr(module, setfattr_runner(module), "follow attr_name value path", attr_name=key)


def rm_xattr(module, key):
    return _run_xattr(module, setfattr_runner(module), "follow remove path", False, remove=key)


def _run_xattr(module, runner, args_order, check_rc=True, **kwargs):
    try:
        (rc, out, err) = runner(args_order, check_rc=check_rc).run(**kwargs)
    except Exception as e:
        module.fail_json(msg=f"{e}!")

    return parse_getfattr(out)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(type="path", required=True, aliases=["name"]),
            namespace=dict(type="str", default="user"),
            key=dict(type="str", no_log=False),
            value=dict(type="str"),
            state=dict(type="str", default="read", choices=["absent", "all", "keys", "present", "read"]),
            follow=dict(type="bool", default=True),
        ),
        supports_check_mode=True,
    )
    path = module.params["path"]
    namespace = module.params["namespace"]
    key = module.params["key"]
    value = module.params["value"]
    state = module.params["state"]

    if not os.path.exists(path):
        module.fail_json(msg="path not found or not accessible!")

    changed = False
    msg = ""
    res = {}

    if key is None and state in ["absent", "present"]:
        module.fail_json(msg=f"{state} needs a key parameter")

    # Prepend the key with the namespace if defined
    if key is not None:
        key = full_key(namespace, key)

    if state == "present" or value is not None:
        current = get_xattr(module, key)
        if current is None or key not in current or value != current[key]:
            if not module.check_mode:
                res = set_xattr(module, key)
            changed = True
        res = current
        msg = f"{key} set to {value}"
    elif state == "absent":
        current = get_xattr(module, key)
        if current is not None and key in current:
            if not module.check_mode:
                res = rm_xattr(module, key)
            changed = True
        res = current
        msg = f"{key} removed"
    elif state == "keys":
        res = get_xattr_keys(module)
        msg = "returning all keys"
    elif state == "all":
        res = get_xattr(module, None)
        msg = "dumping all"
    else:
        res = get_xattr(module, key)
        msg = f"returning {key}"

    module.exit_json(changed=changed, msg=msg, xattr=res)


if __name__ == "__main__":
    main()
