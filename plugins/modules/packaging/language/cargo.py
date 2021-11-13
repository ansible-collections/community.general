#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 Radek Sprta <mail@radeksprta.eu>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: cargo
short_description: Manage Rust packages with cargo
description:
  - Manage Rust packages with cargo.
author: "Radek Sprta (@radek-sprta)"
options:
  name:
    description:
      - The name of a Rust package to install.
    type: str
    required: true
  path:
    description:
      - >
      The base path where to install the Rust packages. Cargo automatically appends
      /bin. In other words, /usr/local will become /usr/local/bin.
    type: path
    required: false
  version:
    description:
      - The version to be installed.
    type: str
    required: false
  state:
    description:
      - The state of the Rust package.
    required: false
    type: str
    default: present
    choices: [ "present", "absent", "latest" ]
requirements:
    - cargo installed in bin path (recommended /usr/local/bin)
'''

EXAMPLES = r'''
- name: Install "ludusavi" Rust package.
  community.general.cargo:
    name: ludusavi

- name: Install "ludusavi" Rust package in version 0.10.0.
  community.general.cargo:
    name: ludusavi
    version: '0.10.0'

- name: Install "ludusavi" Rust package to global location.
  community.general.cargo:
    name: ludusavi
    path: /usr/local

- name: Remove "ludusavi" Rust package.
  community.general.cargo:
    name: ludusavi
    state: absent

- name: Update "ludusavi" Rust package its latest version.
  community.general.cargo:
    name: ludusavi
    state: latest
'''

import os
import re

from ansible.module_utils.basic import AnsibleModule


class Cargo(object):
    def __init__(self, module, **kwargs):
        self.module = module
        self.name = kwargs['name']
        self._path = None
        self.path = kwargs['path']
        self.state = kwargs['state']
        self.version = kwargs['version']

        self.executable = [module.get_bin_path('cargo', True)]

    @property
    def installed_packages(self):
        cmd = ['install', '--list']
        data = self._exec(cmd, True, False, False)

        package_regex = re.compile(r'^(\w+) v(.+):$')
        installed_packages = {}
        for line in data.splitlines():
            package_info = package_regex.match(line)
            if package_info:
                installed_packages[package_info[1]] = package_info[2]

        return installed_packages

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        if path is not None and not os.path.isdir(path):
            self.module.fail_json(msg="Path %s is not a directory" % path)
        self._path = path

    def _exec(self, args, run_in_check_mode=False, check_rc=True, add_package_name=True):
        if not self.module.check_mode or (self.module.check_mode and run_in_check_mode):
            cmd = self.executable + args
            rc, out, err = self.module.run_command(cmd, check_rc=check_rc)
            return out
        return ''

    def install(self):
        cmd = ['install']
        if self.name:
            cmd.append(self.name)
        if self.path:
            cmd.append('--root')
            cmd.append(self.path)
        if self.version:
            cmd.append('--version')
            cmd.append(self.version)
        return self._exec(cmd)

    def is_outdated(self, name):
        installed_version = self.installed_packages.get(name)

        cmd = ['search', name, '--limit', '1']
        data = self._exec(cmd, True, False, False)

        match = re.search(r'"(.+)"', data)
        if match:
            latest_version = match[1]

        return installed_version != latest_version

    def uninstall(self):
        cmd = ['uninstall']
        if self.name:
            cmd.append(self.name)
        return self._exec(cmd)


def main():
    arg_spec = dict(
        name=dict(default=None, type='str'),
        path=dict(default=None, type='path'),
        state=dict(default='present', choices=['present', 'absent', 'latest']),
        version=dict(default=None, type='str'),
    )
    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    name = module.params['name']
    path = module.params['path']
    state = module.params['state']
    version = module.params['version']

    if not name:
        module.fail_json(msg='Package name must be specified')

    cargo = Cargo(module, name=name, path=path, state=state, version=version)

    changed = False
    if state == 'present':
        # TODO write get_version function and installed_packages -> installed
        if name not in cargo.installed_packages or version != cargo.installed_packages.get(name):
            changed = True
            cargo.install()
    elif state == 'latest':
        if name not in cargo.installed_packages or cargo.is_outdated(name):
            changed = True
            cargo.install()
    else:  # absent
        if name in cargo.installed_packages:
            changed = True
            cargo.uninstall()

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
