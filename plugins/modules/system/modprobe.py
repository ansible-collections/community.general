#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2013, David Stygstra <david.stygstra@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: modprobe
short_description: Load or unload kernel modules
author:
    - David Stygstra (@stygstra)
    - Julien Dauphant (@jdauphant)
    - Matt Jeffery (@mattjeffery)
description:
    - Load or unload kernel modules.
options:
    name:
        type: str
        required: true
        description:
            - Name of kernel module to manage.
    state:
        type: str
        description:
            - Whether the module should be present or absent.
        choices: [ absent, present ]
        default: present
    params:
        type: str
        description:
            - Modules parameters.
        default: ''
'''

EXAMPLES = '''
- name: Add the 802.1q module
  community.general.modprobe:
    name: 8021q
    state: present

- name: Add the dummy module
  community.general.modprobe:
    name: dummy
    state: present
    params: 'numdummies=2'
'''

import os.path
import platform
import shlex
import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native

RELEASE_VER = platform.release()


class Modprobe(object):
    def __init__(self, module):
        self.module = module
        self.modprobe_bin = module.get_bin_path('modprobe', True)

        self.check_mode = module.check_mode
        self.desired_state = module.params['state']
        self.name = module.params['name']
        self.params = module.params['params']

        self.changed = False

    def load_module(self):
        command = [self.modprobe_bin]
        if self.check_mode:
            command.append('-n')
        command.extend([self.name] + shlex.split(self.params))

        rc, out, err = self.module.run_command(command)

        if rc != 0:
            return self.module.fail_json(msg=err, rc=rc, stdout=out, stderr=err, **self.result)

        if self.check_mode or self.module_loaded():
            self.changed = True
        else:
            rc, stdout, stderr = self.module.run_command(
                [self.modprobe_bin, '-n', '--first-time', self.name] + shlex.split(self.params)
            )
            if rc != 0:
                self.module.warn(stderr)

    def module_loaded(self):
        is_loaded = False
        try:
            with open('/proc/modules') as modules:
                module_name = self.name.replace('-', '_') + ' '
                for line in modules:
                    if line.startswith(module_name):
                        is_loaded = True
                        break

            if not is_loaded:
                module_file = '/' + self.name + '.ko'
                builtin_path = os.path.join('/lib/modules/', RELEASE_VER, 'modules.builtin')
                with open(builtin_path) as builtins:
                    for line in builtins:
                        if line.rstrip().endswith(module_file):
                            is_loaded = True
                            break
        except (IOError, OSError) as e:
            self.module.fail_json(msg=to_native(e), exception=traceback.format_exc(), **self.result)

        return is_loaded

    def unload_module(self):
        command = [self.modprobe_bin, '-r', self.name]
        if self.check_mode:
            command.append('-n')

        rc, out, err = self.module.run_command(command)
        if rc != 0:
            return self.module.fail_json(msg=err, rc=rc, stdout=out, stderr=err, **self.result)

        self.changed = True

    @property
    def result(self):
        return {
            'changed': self.changed,
            'name': self.name,
            'params': self.params,
            'state': self.desired_state,
        }


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            state=dict(type='str', default='present', choices=['absent', 'present']),
            params=dict(type='str', default=''),
        ),
        supports_check_mode=True,
    )

    modprobe = Modprobe(module)

    if modprobe.desired_state == 'present' and not modprobe.module_loaded():
        modprobe.load_module()
    elif modprobe.desired_state == 'absent' and modprobe.module_loaded():
        modprobe.unload_module()

    module.exit_json(**modprobe.result)


if __name__ == '__main__':
    main()
