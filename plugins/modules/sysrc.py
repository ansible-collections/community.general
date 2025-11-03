#!/usr/bin/python

# Copyright (c) 2019 David Lundgren <dlundgren@syberisle.net>
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
author:
  - David Lundgren (@dlundgren)
module: sysrc
short_description: Manage FreeBSD using sysrc
version_added: '2.0.0'
description:
  - Manages C(/etc/rc.conf) for FreeBSD.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  name:
    description:
      - Name of variable in C(/etc/rc.conf) to manage.
    type: str
    required: true
  value:
    description:
      - The value to set when O(state=present).
      - The value to add when O(state=value_present).
      - The value to remove when O(state=value_absent).
    type: str
  state:
    description:
      - Use V(present) to add the variable.
      - Use V(absent) to remove the variable.
      - Use V(value_present) to add the value to the existing variable.
      - Use V(value_absent) to remove the value from the existing variable.
    type: str
    default: "present"
    choices: [absent, present, value_present, value_absent]
  path:
    description:
      - Path to file to use instead of V(/etc/rc.conf).
    type: str
    default: "/etc/rc.conf"
  delim:
    description:
      - Delimiter to be used instead of V(" ") (space).
      - Only used when O(state=value_present) or O(state=value_absent).
    default: " "
    type: str
  jail:
    description:
      - Name or ID of the jail to operate on.
    type: str
notes:
  - The O(name) cannot contain periods as sysrc does not support OID style names.
"""

EXAMPLES = r"""
# enable mysql in the /etc/rc.conf
- name: Configure mysql pid file
  community.general.sysrc:
    name: mysql_pidfile
    value: "/var/run/mysqld/mysqld.pid"

# enable accf_http kld in the boot loader
- name: Enable accf_http kld
  community.general.sysrc:
    name: accf_http_load
    state: present
    value: "YES"
    path: /boot/loader.conf

# add gif0 to cloned_interfaces
- name: Add gif0 interface
  community.general.sysrc:
    name: cloned_interfaces
    state: value_present
    value: "gif0"

# enable nginx on a jail
- name: Enable nginx in test jail
  community.general.sysrc:
    name: nginx_enable
    value: "YES"
    jail: testjail
"""


from ansible_collections.community.general.plugins.module_utils.module_helper import StateModuleHelper

import os
import re


class Sysrc(StateModuleHelper):
    module = dict(
        argument_spec=dict(
            name=dict(type="str", required=True),
            value=dict(type="str"),
            state=dict(type="str", default="present", choices=["absent", "present", "value_present", "value_absent"]),
            path=dict(type="str", default="/etc/rc.conf"),
            delim=dict(type="str", default=" "),
            jail=dict(type="str"),
        ),
        supports_check_mode=True,
    )
    output_params = ("value",)
    use_old_vardict = False

    def __init_module__(self):
        # OID style names are not supported
        if not re.match(r"^\w+$", self.vars.name, re.ASCII):
            self.module.fail_json(msg="Name may only contain alpha-numeric and underscore characters")

        self.sysrc = self.module.get_bin_path("sysrc", True)

    def _contains(self):
        value = self._get()
        if value is None:
            return False, None

        value = value.split(self.vars.delim)

        return self.vars.value in value, value

    def _get(self):
        if not os.path.exists(self.vars.path):
            return None

        (rc, out, err) = self._sysrc("-v", "-n", self.vars.name)
        if "unknown variable" in err or "unknown variable" in out:
            # Prior to FreeBSD 11.1 sysrc would write "unknown variable" to stdout and not stderr
            # https://bugs.freebsd.org/bugzilla/show_bug.cgi?id=229806
            return None

        if out.startswith(self.vars.path):
            return out.split(":", 1)[1].strip()

        return None

    def _modify(self, op, changed):
        (rc, out, err) = self._sysrc(f"{self.vars.name}{op}={self.vars.delim}{self.vars.value}")
        if out.startswith(f"{self.vars.name}:"):
            return changed(out.split(" -> ")[1].strip().split(self.vars.delim))

        return False

    def _sysrc(self, *args):
        cmd = [self.sysrc, "-f", self.vars.path]
        if self.vars.jail:
            cmd += ["-j", self.vars.jail]
        cmd.extend(args)

        (rc, out, err) = self.module.run_command(cmd)
        if "Permission denied" in err:
            self.module.fail_json(msg=f"Permission denied for {self.vars.path}")

        return rc, out, err

    def state_absent(self):
        if self._get() is None:
            return

        if not self.check_mode:
            self._sysrc("-x", self.vars.name)

        self.changed = True

    def state_present(self):
        value = self._get()
        if value == self.vars.value:
            return

        if self.vars.value is None:
            self.vars.set("value", value)
            return

        if not self.check_mode:
            self._sysrc(f"{self.vars.name}={self.vars.value}")

        self.changed = True

    def state_value_absent(self):
        (contains, _unused) = self._contains()
        if not contains:
            return

        self.changed = self.check_mode or self._modify("-", lambda values: self.vars.value not in values)

    def state_value_present(self):
        (contains, value) = self._contains()
        if contains:
            return

        if self.vars.value is None:
            self.vars.set("value", value)
            return

        self.changed = self.check_mode or self._modify("+", lambda values: self.vars.value in values)


def main():
    Sysrc.execute()


if __name__ == "__main__":
    main()
