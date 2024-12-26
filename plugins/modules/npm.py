#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2017 Chris Hoffman <christopher.hoffman@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r"""
module: npm
short_description: Manage node.js packages with npm
description:
  - Manage node.js packages with Node Package Manager (npm).
author: "Chris Hoffman (@chrishoffman)"
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
      - The name of a node.js library to install.
    type: str
    required: false
  path:
    description:
      - The base path where to install the node.js libraries.
    type: path
    required: false
  version:
    description:
      - The version to be installed.
    type: str
    required: false
  global:
    description:
      - Install the node.js library globally.
    required: false
    default: false
    type: bool
  executable:
    description:
      - The executable location for npm.
      - This is useful if you are using a version manager, such as nvm.
    type: path
    required: false
  ignore_scripts:
    description:
      - Use the C(--ignore-scripts) flag when installing.
    required: false
    type: bool
    default: false
  unsafe_perm:
    description:
      - Use the C(--unsafe-perm) flag when installing.
    type: bool
    default: false
  ci:
    description:
      - Install packages based on package-lock file, same as running C(npm ci).
    type: bool
    default: false
  production:
    description:
      - Install dependencies in production mode, excluding devDependencies.
    required: false
    type: bool
    default: false
  registry:
    description:
      - The registry to install modules from.
    required: false
    type: str
  state:
    description:
      - The state of the node.js library.
    required: false
    type: str
    default: present
    choices: ["present", "absent", "latest"]
  no_optional:
    description:
      - Use the C(--no-optional) flag when installing.
    type: bool
    default: false
    version_added: 2.0.0
  no_bin_links:
    description:
      - Use the C(--no-bin-links) flag when installing.
    type: bool
    default: false
    version_added: 2.5.0
  force:
    description:
      - Use the C(--force) flag when installing.
    type: bool
    default: false
    version_added: 9.5.0
requirements:
  - npm installed in bin path (recommended /usr/local/bin)
"""

EXAMPLES = r"""
- name: Install "coffee-script" node.js package.
  community.general.npm:
    name: coffee-script
    path: /app/location

- name: Install "coffee-script" node.js package on version 1.6.1.
  community.general.npm:
    name: coffee-script
    version: '1.6.1'
    path: /app/location

- name: Install "coffee-script" node.js package globally.
  community.general.npm:
    name: coffee-script
    global: true

- name: Force Install "coffee-script" node.js package.
  community.general.npm:
    name: coffee-script
    force: true

- name: Remove the globally package "coffee-script".
  community.general.npm:
    name: coffee-script
    global: true
    state: absent

- name: Install "coffee-script" node.js package from custom registry.
  community.general.npm:
    name: coffee-script
    registry: 'http://registry.mysite.com'

- name: Install packages based on package.json.
  community.general.npm:
    path: /app/location

- name: Update packages based on package.json to their latest version.
  community.general.npm:
    path: /app/location
    state: latest

- name: Install packages based on package.json using the npm installed with nvm v0.10.1.
  community.general.npm:
    path: /app/location
    executable: /opt/nvm/v0.10.1/bin/npm
    state: present
"""

import json
import os
import re

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native
from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, cmd_runner_fmt


class Npm(object):
    def __init__(self, module, **kwargs):
        self.module = module
        self.glbl = kwargs['glbl']
        self.name = kwargs['name']
        self.version = kwargs['version']
        self.path = kwargs['path']
        self.registry = kwargs['registry']
        self.production = kwargs['production']
        self.ignore_scripts = kwargs['ignore_scripts']
        self.unsafe_perm = kwargs['unsafe_perm']
        self.state = kwargs['state']
        self.no_optional = kwargs['no_optional']
        self.no_bin_links = kwargs['no_bin_links']
        self.force = kwargs['force']

        if kwargs['executable']:
            self.executable = kwargs['executable'].split(' ')
        else:
            self.executable = [module.get_bin_path('npm', True)]

        if kwargs['version'] and kwargs['state'] != 'absent':
            self.name_version = self.name + '@' + str(kwargs['version'])
        else:
            self.name_version = self.name

        self.runner = CmdRunner(
            module,
            command=self.executable,
            arg_formats=dict(
                exec_args=cmd_runner_fmt.as_list(),
                global_=cmd_runner_fmt.as_bool('--global'),
                production=cmd_runner_fmt.as_bool('--production'),
                ignore_scripts=cmd_runner_fmt.as_bool('--ignore-scripts'),
                unsafe_perm=cmd_runner_fmt.as_bool('--unsafe-perm'),
                name_version=cmd_runner_fmt.as_list(),
                registry=cmd_runner_fmt.as_opt_val('--registry'),
                no_optional=cmd_runner_fmt.as_bool('--no-optional'),
                no_bin_links=cmd_runner_fmt.as_bool('--no-bin-links'),
                force=cmd_runner_fmt.as_bool('--force'),
            )
        )

    def _exec(self, args, run_in_check_mode=False, check_rc=True, add_package_name=True):
        if not self.module.check_mode or (self.module.check_mode and run_in_check_mode):
            # If path is specified, cd into that path and run the command.
            cwd = None
            if self.path:
                if not os.path.exists(self.path):
                    os.makedirs(self.path)
                if not os.path.isdir(self.path):
                    self.module.fail_json(msg="path %s is not a directory" % self.path)
                cwd = self.path

            params = dict(self.module.params)
            params['exec_args'] = args
            params['global_'] = self.glbl
            params['production'] = self.production and ('install' in args or 'update' in args or 'ci' in args)
            params['name_version'] = self.name_version if add_package_name else None

            with self.runner(
                "exec_args global_ production ignore_scripts unsafe_perm name_version registry no_optional no_bin_links force",
                check_rc=check_rc, cwd=cwd
            ) as ctx:
                rc, out, err = ctx.run(**params)
            return out

        return ''

    def list(self):
        cmd = ['list', '--json', '--long']

        installed = list()
        missing = list()
        data = {}
        try:
            data = json.loads(self._exec(cmd, True, False, False) or '{}')
        except (getattr(json, 'JSONDecodeError', ValueError)) as e:
            self.module.fail_json(msg="Failed to parse NPM output with error %s" % to_native(e))
        if 'dependencies' in data:
            for dep, props in data['dependencies'].items():

                if 'missing' in props and props['missing']:
                    missing.append(dep)
                elif 'invalid' in props and props['invalid']:
                    missing.append(dep)
                else:
                    installed.append(dep)
                    if 'version' in props and props['version']:
                        dep_version = dep + '@' + str(props['version'])
                        installed.append(dep_version)
            if self.name_version and self.name_version not in installed:
                missing.append(self.name)
        # Named dependency not installed
        else:
            missing.append(self.name)

        return installed, missing

    def install(self):
        return self._exec(['install'])

    def ci_install(self):
        return self._exec(['ci'])

    def update(self):
        return self._exec(['update'])

    def uninstall(self):
        return self._exec(['uninstall'])

    def list_outdated(self):
        outdated = list()
        data = self._exec(['outdated'], True, False)
        for dep in data.splitlines():
            if dep:
                # node.js v0.10.22 changed the `npm outdated` module separator
                # from "@" to " ". Split on both for backwards compatibility.
                pkg, other = re.split(r'\s|@', dep, 1)
                outdated.append(pkg)

        return outdated


def main():
    arg_spec = dict(
        name=dict(type='str'),
        path=dict(type='path'),
        version=dict(type='str'),
        production=dict(default=False, type='bool'),
        executable=dict(type='path'),
        registry=dict(type='str'),
        state=dict(default='present', choices=['present', 'absent', 'latest']),
        ignore_scripts=dict(default=False, type='bool'),
        unsafe_perm=dict(default=False, type='bool'),
        ci=dict(default=False, type='bool'),
        no_optional=dict(default=False, type='bool'),
        no_bin_links=dict(default=False, type='bool'),
        force=dict(default=False, type='bool'),
    )
    arg_spec['global'] = dict(default=False, type='bool')
    module = AnsibleModule(
        argument_spec=arg_spec,
        required_if=[('state', 'absent', ['name'])],
        supports_check_mode=True,
    )

    name = module.params['name']
    path = module.params['path']
    version = module.params['version']
    glbl = module.params['global']
    state = module.params['state']

    if not path and not glbl:
        module.fail_json(msg='path must be specified when not using global')

    npm = Npm(module,
              name=name,
              path=path,
              version=version,
              glbl=glbl,
              production=module.params['production'],
              executable=module.params['executable'],
              registry=module.params['registry'],
              ignore_scripts=module.params['ignore_scripts'],
              unsafe_perm=module.params['unsafe_perm'],
              state=state,
              no_optional=module.params['no_optional'],
              no_bin_links=module.params['no_bin_links'],
              force=module.params['force'])

    changed = False
    if module.params['ci']:
        npm.ci_install()
        changed = True
    elif state == 'present':
        installed, missing = npm.list()
        if missing:
            changed = True
            npm.install()
    elif state == 'latest':
        installed, missing = npm.list()
        outdated = npm.list_outdated()
        if missing:
            changed = True
            npm.install()
        if outdated:
            changed = True
            npm.update()
    else:  # absent
        installed, missing = npm.list()
        if name in installed:
            changed = True
            npm.uninstall()

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
