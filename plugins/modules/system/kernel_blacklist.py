#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Alexei Znamensky (@russoz) <russoz@gmail.com>
# Copyright: (c) 2013, Matthias Vogelgesang <matthias.vogelgesang@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: kernel_blacklist
author:
- Matthias Vogelgesang (@matze)
short_description: Blacklist kernel modules
description:
    - Add or remove kernel modules from blacklist.
options:
    name:
        type: str
        description:
            - Name of kernel module to black- or whitelist.
        required: true
    state:
        type: str
        description:
            - Whether the module should be present in the blacklist or absent.
        choices: [ absent, present ]
        default: present
    blacklist_file:
        type: str
        description:
            - If specified, use this blacklist file instead of
              C(/etc/modprobe.d/blacklist-ansible.conf).
        default: /etc/modprobe.d/blacklist-ansible.conf
'''

EXAMPLES = '''
- name: Blacklist the nouveau driver module
  community.general.kernel_blacklist:
    name: nouveau
    state: present
'''

import os
import re

from ansible_collections.community.general.plugins.module_utils.module_helper import StateModuleHelper


class Blacklist(StateModuleHelper):
    output_params = ('name', 'state')
    module = dict(
        argument_spec=dict(
            name=dict(type='str', required=True),
            state=dict(type='str', default='present', choices=['absent', 'present']),
            blacklist_file=dict(type='str', default='/etc/modprobe.d/blacklist-ansible.conf'),
        ),
        supports_check_mode=True,
    )

    def __init_module__(self):
        self.vars.filename = self.default_file if not self.vars.blacklist_file else self.vars.blacklist_file
        self.vars.set('file_exists', os.path.exists(self.vars.filename), output=False, change=True)
        if not self.vars.file_exists:
            open(self.vars.filename, 'a').close()
            self.vars.file_exists = True
            self.vars.set('lines', [], change=True, diff=True)
        else:
            with open(self.vars.filename) as fd:
                self.vars.set('lines', fd.readlines(), change=True, diff=True)
        self.vars.set('is_blacklisted', self._is_module_blocked(), change=True)

        self.pattern = re.compile(r'^blacklist\s+' + self.vars.name + '$')

    def _is_module_blocked(self):
        for line in self.vars.lines:
            stripped = line.strip()
            if stripped.startswith('#'):
                continue
            if self.pattern.match(stripped):
                return True
        return False

    def state_absent(self):
        if not self.vars.is_blacklisted:
            return
        self.vars.is_blacklisted = False
        self.vars.lines = [line for line in self.vars.lines if not self.pattern.match(line.strip())]
        if self.has_changed() and not self.module.check_module:
            with open(self.vars.filename, 'w') as fd:
                fd.writelines(self.vars.lines)

    def state_present(self):
        if self.vars.is_blacklisted:
            return
        self.vars.is_blacklisted = True
        self.vars.lines = self.vars.lines + ['blacklist %s\n' % self.vars.name]
        if self.has_changed() and not self.module.check_module:
            with open(self.vars.filename, 'a') as fd:
                fd.writelines(self.vars.lines[-1:])


def main():
    Blacklist.execute()


if __name__ == '__main__':
    main()
