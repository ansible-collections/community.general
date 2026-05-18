#!/usr/bin/python

# Copyright (c) 2017, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: xattr
short_description: Manage user defined extended attributes
description:
  - Manages filesystem user defined extended attributes, also known as 'xattr'.
  - Requires that extended attributes are enabled on the target filesystem.
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
notes:
    - Starting with community.general 13.0.0 this action no longer requires the xattr CLI tools installed on the target.
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

RETURN = r"""
xattr:
    description: The xattr key(s) and value(s) requested
    returned: success
    type: dict
    sample: '{"user.mykey": "heyo"}'
"""

import os

from ansible.module_utils.basic import AnsibleModule


class XattrFail(Exception):
    pass


def get_xattr(path, key, follow):
    try:
        return os.getxattr(path, attribute=key, follow_symlinks=follow)
    except OSError as e:
        raise XattrFail(f"Could not read key({key}) from {path}") from e


def set_xattr(path, key, value, follow):
    try:
        os.setxattr(path, attribute=key, value=value, follow_symlinks=follow)
    except OSError as e:
        raise XattrFail(f"Could not set key({key}) on {path}") from e


def rm_xattr(path, key, follow):
    try:
        os.removexattr(path, attribute=key, follow_symlinks=follow)
    except OSError as e:
        raise XattrFail(f"Could not remove key({key}) fron {path}") from e


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
        required_if=[
            ("state", "present", ["key", "value"]),
            ("state", "absent", ["key"]),
        ],
    )

    path = module.params["path"]
    namespace = module.params["namespace"]
    key = module.params["key"]
    value = module.params["value"]
    state = module.params["state"]
    follow = module.params["follow"]

    if not os.path.exists(path):
        module.fail_json(msg="path not found or not accessible!")

    if state == 'read' and key is None:
        #NOTE: This is backwards compatible, but should go away once we deprecate and remove 'info states'
        module.warn('No key provided for state "read", assuming you really want "all"')
        state == 'all'

    changed = False
    msg = ""
    res = {}

    # Prepend the key with the namespace if defined
    if (
        key is not None
        and namespace is not None
        and len(namespace) > 0
        and not (namespace == "user" and key.startswith("user."))
    ):
        key = f"{namespace}.{key}"

    try:
        res = {}
        if state == "all":
            keys = os.listxattr(path, follow_symlinks=follow)
            for k in keys:
                res[k] = get_xattr(path, k, follow)
            msg = "dumping all"
        elif state == "read":
            res[key] = get_xattr(path, key, follow)
            msg = f"returning {key}"
        elif state == "keys":
            res = os.listxattr(path, follow_symlinks=follow)
            msg = "returning all keys"
        elif state == "present":
            try:
                res[key] = get_xattr(path, key, follow)
            except XattrFail:
                pass  # does not exist

            value = value.encode()
            if not value == res.get(key):
                changed = True
                if not module.check_mode:
                    set_xattr(path, key, value, follow)
                msg = 'key is set'
                res = {key: value}
        elif state == "absent":
            msg = f"{key} is absent from {path}"
            try:
                current = os.listxattr(path, follow_symlinks=follow)
                if key in current:
                    changed = True
                    if not module.check_mode:
                        rm_xattr(path, key, follow)
            except XattrFail:
                module.exit_json(msg=msg, changed=changed, xattr=res)
        else:
            # this only happens if we mismatch code with the option definition choices
            module.exit_json(msg=f'The developer messed up and allowed unsupported option: {state}')

    except XattrFail as e:
        module.fail_json(xattr=res, msg=str(e), exception=e.__cause__)

    module.exit_json(changed=changed, msg=msg, xattr=res)


if __name__ == "__main__":
    main()
