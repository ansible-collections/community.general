#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2019 David Lundgren <dlundgren@syberisle.net>
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
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
        choices: [ absent, present, value_present, value_absent ]
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
'''

EXAMPLES = r'''
---
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
'''

RETURN = r'''
changed:
  description: Return changed for sysrc actions.
  returned: always
  type: bool
  sample: true
'''

from ansible.module_utils.basic import AnsibleModule
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

    def has_unknown_variable(self, out, err):
        # newer versions of sysrc use stderr instead of stdout
        return err.find("unknown variable") > 0 or out.find("unknown variable") > 0

    def exists(self):
        # sysrc doesn't really use exit codes
        (rc, out, err) = self.run_sysrc(self.name)
        if self.value is None:
            regex = "%s: " % re.escape(self.name)
        else:
            regex = "%s: %s$" % (re.escape(self.name), re.escape(self.value))

        return not self.has_unknown_variable(out, err) and re.match(regex, out) is not None

    def contains(self):
        (rc, out, err) = self.run_sysrc('-n', self.name)
        if self.has_unknown_variable(out, err):
            return False

        return self.value in out.strip().split(self.delim)

    def present(self):
        if self.exists():
            return

        if self.module.check_mode:
            self.changed = True
            return

        (rc, out, err) = self.run_sysrc("%s=%s" % (self.name, self.value))
        if out.find("%s:" % self.name) == 0 and re.search("-> %s$" % re.escape(self.value), out) is not None:
            self.changed = True

    def absent(self):
        if not self.exists():
            return

        # inversed since we still need to mark as changed
        if not self.module.check_mode:
            (rc, out, err) = self.run_sysrc('-x', self.name)
            if self.has_unknown_variable(out, err):
                return

        self.changed = True

    def value_present(self):
        if self.contains():
            return

        if self.module.check_mode:
            self.changed = True
            return

        setstring = '%s+=%s%s' % (self.name, self.delim, self.value)
        (rc, out, err) = self.run_sysrc(setstring)
        if out.find("%s:" % self.name) == 0:
            values = out.split(' -> ')[1].strip().split(self.delim)
            if self.value in values:
                self.changed = True

    def value_absent(self):
        if not self.contains():
            return

        if self.module.check_mode:
            self.changed = True
            return

        setstring = '%s-=%s%s' % (self.name, self.delim, self.value)
        (rc, out, err) = self.run_sysrc(setstring)
        if out.find("%s:" % self.name) == 0:
            values = out.split(' -> ')[1].strip().split(self.delim)
            if self.value not in values:
                self.changed = True

    def run_sysrc(self, *args):
        cmd = [self.sysrc, '-f', self.path]
        if self.jail:
            cmd += ['-j', self.jail]
        cmd.extend(args)

        (rc, out, err) = self.module.run_command(cmd)

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

    value = module.params.pop('value')
    state = module.params.pop('state')
    path = module.params.pop('path')
    delim = module.params.pop('delim')
    jail = module.params.pop('jail')
    result = dict(
        name=name,
        state=state,
        value=value,
        path=path,
        delim=delim,
        jail=jail
    )

    rc_value = Sysrc(module, name, value, path, delim, jail)

    if state == 'present':
        rc_value.present()
    elif state == 'absent':
        rc_value.absent()
    elif state == 'value_present':
        rc_value.value_present()
    elif state == 'value_absent':
        rc_value.value_absent()

    result['changed'] = rc_value.changed

    module.exit_json(**result)


if __name__ == '__main__':
    main()
