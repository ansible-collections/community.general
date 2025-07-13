#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2012, Matt Wright <matt@nobien.net>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r"""
module: easy_install
short_description: Installs Python libraries
description:
  - Installs Python libraries, optionally in a C(virtualenv).
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
    description:
      - A Python library name.
    required: true
  virtualenv:
    type: str
    description:
      - An optional O(virtualenv) directory path to install into. If the O(virtualenv) does not exist, it is created automatically.
  virtualenv_site_packages:
    description:
      - Whether the virtual environment inherits packages from the global site-packages directory. Note that this setting
        has no effect on an already existing virtual environment, so if you want to change it, the environment must be deleted
        and newly created.
    type: bool
    default: false
  virtualenv_command:
    type: str
    description:
      - The command to create the virtual environment with. For example V(pyvenv), V(virtualenv), V(virtualenv2).
    default: virtualenv
  executable:
    type: str
    description:
      - The explicit executable or a pathname to the executable to be used to run easy_install for a specific version of Python
        installed in the system. For example V(easy_install-3.3), if there are both Python 2.7 and 3.3 installations in the
        system and you want to run easy_install for the Python 3.3 installation.
    default: easy_install
  state:
    type: str
    description:
      - The desired state of the library. V(latest) ensures that the latest version is installed.
    choices: [present, latest]
    default: present
notes:
  - Please note that the C(easy_install) module can only install Python libraries. Thus this module is not able to remove
    libraries. It is generally recommended to use the M(ansible.builtin.pip) module which you can first install using M(community.general.easy_install).
  - Also note that C(virtualenv) must be installed on the remote host if the O(virtualenv) parameter is specified.
requirements: ["virtualenv"]
author: "Matt Wright (@mattupstate)"
"""

EXAMPLES = r"""
- name: Install or update pip
  community.general.easy_install:
    name: pip
    state: latest

- name: Install Bottle into the specified virtualenv
  community.general.easy_install:
    name: bottle
    virtualenv: /webapps/myapp/venv

- name: Install a python package using pyvenv as the virtualenv tool
  community.general.easy_install:
    name: package_name
    virtualenv: /opt/myenv
    virtualenv_command: pyvenv
"""

import os
import os.path
import tempfile
from ansible.module_utils.basic import AnsibleModule


def install_package(module, name, easy_install, executable_arguments):
    cmd = '%s %s %s' % (easy_install, ' '.join(executable_arguments), name)
    rc, out, err = module.run_command(cmd)
    return rc, out, err


def _is_package_installed(module, name, easy_install, executable_arguments):
    # Copy and add to the arguments
    executable_arguments = executable_arguments[:]
    executable_arguments.append('--dry-run')
    rc, out, err = install_package(module, name, easy_install, executable_arguments)
    if rc:
        module.fail_json(msg=err)
    return 'Downloading' not in out


def _get_easy_install(module, env=None, executable=None):
    candidate_easy_inst_basenames = ['easy_install']
    easy_install = None
    if executable is not None:
        if os.path.isabs(executable):
            easy_install = executable
        else:
            candidate_easy_inst_basenames.insert(0, executable)
    if easy_install is None:
        if env is None:
            opt_dirs = []
        else:
            # Try easy_install with the virtualenv directory first.
            opt_dirs = ['%s/bin' % env]
        for basename in candidate_easy_inst_basenames:
            easy_install = module.get_bin_path(basename, False, opt_dirs)
            if easy_install is not None:
                break
    # easy_install should have been found by now.  The final call to
    # get_bin_path will trigger fail_json.
    if easy_install is None:
        basename = candidate_easy_inst_basenames[0]
        easy_install = module.get_bin_path(basename, True, opt_dirs)
    return easy_install


def main():
    arg_spec = dict(
        name=dict(required=True),
        state=dict(required=False,
                   default='present',
                   choices=['present', 'latest'],
                   type='str'),
        virtualenv=dict(default=None, required=False),
        virtualenv_site_packages=dict(default=False, type='bool'),
        virtualenv_command=dict(default='virtualenv', required=False),
        executable=dict(default='easy_install', required=False),
    )

    module = AnsibleModule(argument_spec=arg_spec, supports_check_mode=True)

    name = module.params['name']
    env = module.params['virtualenv']
    executable = module.params['executable']
    site_packages = module.params['virtualenv_site_packages']
    virtualenv_command = module.params['virtualenv_command']
    executable_arguments = []
    if module.params['state'] == 'latest':
        executable_arguments.append('--upgrade')

    rc = 0
    err = ''
    out = ''

    if env:
        virtualenv = module.get_bin_path(virtualenv_command, True)

        if not os.path.exists(os.path.join(env, 'bin', 'activate')):
            if module.check_mode:
                module.exit_json(changed=True)
            command = '%s %s' % (virtualenv, env)
            if site_packages:
                command += ' --system-site-packages'
            cwd = tempfile.gettempdir()
            rc_venv, out_venv, err_venv = module.run_command(command, cwd=cwd)

            rc += rc_venv
            out += out_venv
            err += err_venv

    easy_install = _get_easy_install(module, env, executable)

    cmd = None
    changed = False
    installed = _is_package_installed(module, name, easy_install, executable_arguments)

    if not installed:
        if module.check_mode:
            module.exit_json(changed=True)
        rc_easy_inst, out_easy_inst, err_easy_inst = install_package(module, name, easy_install, executable_arguments)

        rc += rc_easy_inst
        out += out_easy_inst
        err += err_easy_inst

        changed = True

    if rc != 0:
        module.fail_json(msg=err, cmd=cmd)

    module.exit_json(changed=changed, binary=easy_install,
                     name=name, virtualenv=env)


if __name__ == '__main__':
    main()
