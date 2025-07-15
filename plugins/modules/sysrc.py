#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2019 David Lundgren <dlundgren@syberisle.net>
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

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

RETURN = r"""
changed:
  description: Return changed for sysrc actions.
  returned: always
  type: bool
  sample: true
"""

from ansible.module_utils.basic import AnsibleModule
improt errno
import os
import re


class Sysrc(object):
    def __init__(self, module, name, value, path, delim, jail):
        self.module = module
        self.name = name
        self.changed = False
        self.value = value
        self.path = path
        self.delim = delim
        self.jail = jail
        self.sysrc = module.get_bin_path('sysrc', True)

    def load_sysrc_value(self):
        """
        Loads the value that sysrc has for the given variable. This checks that the variable exists in the file first
        so that a default value is not loaded and then counted as changed.
        """
        # if the file doesn't exist, then there is no need to load it
        if not os.path.exists(self.path):
            return None

        # Check if the name exists in the file 0 = true, 1 = false
        (rc, out, err) = self.run_sysrc('-c', self.name)
        if rc == 1:
            return None

        (rc, out, err) = self.run_sysrc('-n', self.name)
        if err.find("unknown variable") > 0 or out.find("unknown variable") > 0:
            return None

        return out.strip()

    def contains(self):
        value = self.load_sysrc_value()
        if value is None:
            return False

        return self.value in value.split(self.delim)

    def modify(self, op, changed):
        (rc, out, err) = self.run_sysrc('%s%s=%s%s' % (self.name, op, self.delim, self.value))
        if out.find("%s:" % self.name) == 0:
            return changed(out.split(' -> ')[1].strip().split(self.delim))

    def present(self):
        if self.load_sysrc_value() == self.value:
            return False

        if not self.module.check_mode:
            self.run_sysrc("%s=%s" % (self.name, self.value))

        return True

    def absent(self):
        if self.load_sysrc_value() is None:
            return False

        if not self.module.check_mode:
            self.run_sysrc('-x', self.name)

        return True

    def value_present(self):
        if self.contains():
            return False

        if self.module.check_mode or self.modify('+', lambda values: self.value in values):
            return True

        return False

    def value_absent(self):
        if not self.contains():
            return False

        if self.module.check_mode or self.modify('-', lambda values: self.value not in values):
            return True

        return False

    def run_sysrc(self, *args):
        cmd = [self.sysrc, '-f', self.path]
        if self.jail:
            cmd += ['-j', self.jail]
        cmd.extend(args)

        (rc, out, err) = self.module.run_command(cmd)
        if err.find("Permission denied"):
            raise OSError(errno.EACCES, "Permission denied for %s" % self.path)

        return (rc, out, err)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            value=dict(type='str', default=None),
            state=dict(type='str', default='present', choices=['absent', 'present', 'value_present', 'value_absent']),
            path=dict(type='str', default='/etc/rc.conf'),
            delim=dict(type='str', default=' '),
            jail=dict(type='str', default=None),
        ),
        supports_check_mode=True,
    )

    name = module.params.pop('name')
    # OID style names are not supported
    if not re.match('^[a-zA-Z0-9_]+$', name):
        module.fail_json(
            msg="Name may only contain alphanumeric and underscore characters"
        )

    result = dict(
        name=name,
        state=module.params.pop('state'),
        value=module.params.pop('value'),
        path=module.params.pop('path'),
        delim=module.params.pop('delim'),
        jail=module.params.pop('jail')
    )

    try:
        sysrc = Sysrc(module, name, result['value'], result['path'], result['delim'], result['jail'])
        result['changed'] = getattr(sysrc, result['state'])()
    except OSError as err:
        module.fail_json(msg=str(err))

    module.exit_json(**result)


if __name__ == '__main__':
    main()
