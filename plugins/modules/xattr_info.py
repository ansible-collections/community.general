#!/usr/bin/python

# Copyright (c) 2026, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: xattr_info
short_description: Retrieve filesystem extended attributes
version_added: 14.0.0
description:
  - Retrieves filesystem extended attributes of a file or directory, with the help of C(getfattr).
  - Requires that extended attributes are enabled on the target filesystem.
extends_documentation_fragment:
  - community.general._attributes
  - community.general._attributes.info_module
options:
  path:
    description:
      - The full path of the file or directory to retrieve the extended attributes from.
    type: path
    required: true
  namespace:
    description:
      - Namespace of the extended attributes.
      - When O(key) is not set, only the attributes in this namespace are returned.
        If set to an empty string, the attributes of all namespaces are returned.
    type: str
    default: user
  key:
    description:
      - The name of a specific extended attribute to retrieve.
      - The value of O(namespace) is prepended to it, unless O(namespace) is an empty string,
        or O(namespace=user) and O(key) already starts with C(user.).
      - If not set, all the extended attributes in O(namespace) are retrieved.
    type: str
  follow:
    description:
      - If V(true), dereferences symlinks and retrieves the attributes of the symlink target, otherwise retrieves the
        attributes of the symlink itself.
    type: bool
    default: true
requirements:
  - getfattr
seealso:
  - module: community.general.xattr
  - name: C(getfattr) command manual page
    description: Manual page for the command.
    link: https://man7.org/linux/man-pages/man1/getfattr.1.html
author:
  - Alexei Znamensky (@russoz)
"""

EXAMPLES = r"""
- name: Obtain the extended attributes of /etc/foo.conf
  community.general.xattr_info:
    path: /etc/foo.conf
  register: result

- name: List the names of the extended attributes of /etc/foo.conf
  ansible.builtin.debug:
    msg: "{{ result.xattr.keys() }}"

- name: Obtain the value of the key 'user.foo'
  community.general.xattr_info:
    path: /etc/foo.conf
    key: foo
  register: result

- name: Obtain the value of the key 'trusted.glusterfs.volume-id'
  community.general.xattr_info:
    path: /mnt/bricks/brick1
    namespace: trusted
    key: glusterfs.volume-id
  register: result
"""

RETURN = r"""
xattr:
  description:
    - The extended attributes, mapping their full names to their values.
    - Text values are returned without the surrounding quotes, binary values are returned encoded as by C(getfattr).
    - When O(key) is set and the attribute does not exist, an empty dictionary is returned.
  type: dict
  returned: success
  sample:
    user.foo: bar
    user.empty: ""
    user.binary: 0sAP8=
"""

import re
import typing as t

from ansible_collections.community.general.plugins.module_utils._module_helper import ModuleHelper
from ansible_collections.community.general.plugins.module_utils._xattr import full_key, getfattr_runner, parse_getfattr

if t.TYPE_CHECKING:  # pragma: no cover
    from ansible_collections.community.general.plugins.module_utils._typing import ArgumentSpecT


def get_argument_spec() -> ArgumentSpecT:
    return dict(
        path=dict(type="path", required=True),
        namespace=dict(type="str", default="user"),
        key=dict(type="str", no_log=False),
        follow=dict(type="bool", default=True),
    )


class XAttrInfo(ModuleHelper):
    module = dict(
        argument_spec=get_argument_spec(),
        supports_check_mode=True,
    )

    def __init_module__(self) -> None:
        self.runner = getfattr_runner(self.module)

    def __run__(self) -> None:
        if self.vars.key is None:
            match = f"^{re.escape(self.vars.namespace)}\\." if self.vars.namespace else "-"
            with self.runner("absolute_names follow dump match path") as ctx:
                rc, out, err = ctx.run(match=match)
        else:
            with self.runner("absolute_names follow attr_name path") as ctx:
                rc, out, err = ctx.run(attr_name=full_key(self.vars.namespace, self.vars.key))
                if rc != 0 and err.rstrip().endswith(": No such attribute"):
                    self.vars.xattr = {}
                    return
        if rc != 0:
            self.do_raise(f"getfattr failed: {err.strip()}", rc=rc, stdout=out, stderr=err)
        self.vars.xattr = parse_getfattr(out)


def main():
    XAttrInfo.execute()


if __name__ == "__main__":
    main()
