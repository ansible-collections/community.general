#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2013, David Stygstra <david.stygstra@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

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
extends_documentation_fragment:
    - community.general.attributes
attributes:
    check_mode:
        support: full
    diff_mode:
        support: none
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
    persistent:
        type: str
        choices: [ disabled, absent, present ]
        default: disabled
        description:
            - Persistency between reboots for configured module.
            - This option creates files in C(/etc/modules-load.d/) and C(/etc/modprobe.d/) that make your module configuration persistent during reboots.
            - If V(present), adds module name to C(/etc/modules-load.d/) and params to C(/etc/modprobe.d/) so the module will be loaded on next reboot.
            - If V(absent), will comment out module name from C(/etc/modules-load.d/) and comment out params from C(/etc/modprobe.d/) so the module will not be
              loaded on next reboot.
            - If V(disabled), will not touch anything and leave C(/etc/modules-load.d/) and C(/etc/modprobe.d/) as it is.
            - Note that it is usually a better idea to rely on the automatic module loading by PCI IDs, USB IDs, DMI IDs or similar triggers encoded in the
              kernel modules themselves instead of configuration like this.
            - In fact, most modern kernel modules are prepared for automatic loading already.
            - "B(Note:) This option works only with distributions that use C(systemd) when set to values other than V(disabled)."
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

- name: Add the dummy module and make sure it is loaded after reboots
  community.general.modprobe:
    name: dummy
    state: present
    params: 'numdummies=2'
    persistent: present
'''

import os.path
import platform
import shlex
import traceback
import re

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native

RELEASE_VER = platform.release()
MODULES_LOAD_LOCATION = '/etc/modules-load.d'
PARAMETERS_FILES_LOCATION = '/etc/modprobe.d'


class Modprobe(object):

    def __init__(self, module):
        self.module = module
        self.modprobe_bin = module.get_bin_path('modprobe', True)

        self.check_mode = module.check_mode
        self.desired_state = module.params['state']
        self.name = module.params['name']
        self.params = module.params['params']
        self.persistent = module.params['persistent']

        self.changed = False

        self.re_find_module = re.compile(r'^ *{0} *(?:[#;].*)?\n?\Z'.format(self.name))
        self.re_find_params = re.compile(r'^options {0} \w+=\S+ *(?:[#;].*)?\n?\Z'.format(self.name))
        self.re_get_params_and_values = re.compile(r'^options {0} (\w+=\S+) *(?:[#;].*)?\n?\Z'.format(self.name))

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

    @property
    def module_is_loaded_persistently(self):
        for module_file in self.modules_files:
            with open(module_file) as file:
                for line in file:
                    if self.re_find_module.match(line):
                        return True

        return False

    @property
    def params_is_set(self):
        desired_params = set(self.params.split())

        return desired_params == self.permanent_params

    @property
    def permanent_params(self):
        params = set()

        for modprobe_file in self.modprobe_files:
            with open(modprobe_file) as file:
                for line in file:
                    match = self.re_get_params_and_values.match(line)
                    if match:
                        params.add(match.group(1))

        return params

    def create_module_file(self):
        file_path = os.path.join(MODULES_LOAD_LOCATION,
                                 self.name + '.conf')
        with open(file_path, 'w') as file:
            file.write(self.name + '\n')

    @property
    def module_options_file_content(self):
        file_content = ['options {0} {1}'.format(self.name, param)
                        for param in self.params.split()]
        return '\n'.join(file_content) + '\n'

    def create_module_options_file(self):
        new_file_path = os.path.join(PARAMETERS_FILES_LOCATION,
                                     self.name + '.conf')
        with open(new_file_path, 'w') as file:
            file.write(self.module_options_file_content)

    def disable_old_params(self):

        for modprobe_file in self.modprobe_files:
            with open(modprobe_file) as file:
                file_content = file.readlines()

            content_changed = False
            for index, line in enumerate(file_content):
                if self.re_find_params.match(line):
                    file_content[index] = '#' + line
                    content_changed = True

            if content_changed:
                with open(modprobe_file, 'w') as file:
                    file.write('\n'.join(file_content))

    def disable_module_permanent(self):

        for module_file in self.modules_files:
            with open(module_file) as file:
                file_content = file.readlines()

            content_changed = False
            for index, line in enumerate(file_content):
                if self.re_find_module.match(line):
                    file_content[index] = '#' + line
                    content_changed = True

            if content_changed:
                with open(module_file, 'w') as file:
                    file.write('\n'.join(file_content))

    def load_module_permanent(self):

        if not self.module_is_loaded_persistently:
            self.create_module_file()
            self.changed = True

        if not self.params_is_set:
            self.disable_old_params()
            self.create_module_options_file()
            self.changed = True

    def unload_module_permanent(self):
        if self.module_is_loaded_persistently:
            self.disable_module_permanent()
            self.changed = True

        if self.permanent_params:
            self.disable_old_params()
            self.changed = True

    @property
    def modules_files(self):
        modules_paths = [os.path.join(MODULES_LOAD_LOCATION, path)
                         for path in os.listdir(MODULES_LOAD_LOCATION)]
        return [path for path in modules_paths if os.path.isfile(path)]

    @property
    def modprobe_files(self):
        modules_paths = [os.path.join(PARAMETERS_FILES_LOCATION, path)
                         for path in os.listdir(PARAMETERS_FILES_LOCATION)]
        return [path for path in modules_paths if os.path.isfile(path)]

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


def build_module():
    return AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            state=dict(type='str', default='present', choices=['absent', 'present']),
            params=dict(type='str', default=''),
            persistent=dict(type='str', default='disabled', choices=['disabled', 'present', 'absent']),
        ),
        supports_check_mode=True,
    )


def main():
    module = build_module()

    modprobe = Modprobe(module)

    if modprobe.desired_state == 'present' and not modprobe.module_loaded():
        modprobe.load_module()
    elif modprobe.desired_state == 'absent' and modprobe.module_loaded():
        modprobe.unload_module()

    if modprobe.persistent == 'present' and not (modprobe.module_is_loaded_persistently and modprobe.params_is_set):
        modprobe.load_module_permanent()
    elif modprobe.persistent == 'absent' and (modprobe.module_is_loaded_persistently or modprobe.permanent_params):
        modprobe.unload_module_permanent()

    module.exit_json(**modprobe.result)


if __name__ == '__main__':
    main()
