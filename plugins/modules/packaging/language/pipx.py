#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2021, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: pipx
short_description: manages applications installed with pipx.
description:
    - Manage Python applications installed in isolated virtualenvs using pipx.
options:
    state:
        type: str
        choices: [present, absent, install, uninstall, uninstall_all, inject, upgrade, upgrade_all, reinstall, reinstall_all]
        default: install
        description:
            - Desired state for the application.
            - The states C(present) and C(absent) are aliases to C(install) and C(uninstall), respectively.
    name:
        type: str
        description:
            - >
              The name of the application to be installed. It must to be a simple package name.
              For passing package specifications or installing from URLs or directories,
              please use the I(source) option.
    source:
        type: str
        description:
            - >
              If the application source, such as a package with version specifier, or an URL,
              directory or any other accepted specification. See C(pipx) documentation for more details.
            - When specified, the C(pipx) command will use I(source) instead of I(name).
    installdeps:
        description:
            - Install dependencies for the application.
        type: bool
        default: false
    inject_packages:
        description:
            - Packages to be injected into an existing virtual environment.
            - Only used when I(state=inject).
        type: list
        elements: str
    force:
        description:
            - Force modification of the application's virtual environment. See C(pipx) for details.
        type: bool
        default: false
    include_injected:
        description:
            - Upgrade the injected packages along with the application.
            - Only used when I(state=upgrade) or I(state=upgrade_all).
        type: bool
        default: false
    index_url:
        description:
            - Base URL of Python Package Index.
        type: str
    python:
        description:
            - Python version to be used when creating the application virtual environment. Must be 3.6+.
        type: str
notes:
    - This module does not install the C(pipx) python package, however that can be easily done with the module C(ansible.builtin.pip).
    - This module does not require C(pipx) to be in the shell C(PATH), but it must be loadable by Python as a module.
    - Please note that C(pipx) requires Python 3.6 or above.
    - >
      This first implementation does not verify whether a specified version constraint has been installed or not.
      Hence, when using version operators, C(pipx) module will always try to execute the operation,
      even when the application was previously installed.
      This feature will be added in the future.
    - See also the C(pipx) documentation at U(https://pypa.github.io/pipx/).
author:
    - "Alexei Znamensky (@russoz)"
'''

EXAMPLES = ''' '''


import json

from ansible_collections.community.general.plugins.module_utils.module_helper import (
    CmdStateModuleHelper, ArgFormat, ModuleHelperException
)


_state_map = dict(
    present='install',
    absent='uninstall',
    uninstall_all='uninstall-all',
    upgrade_all='upgrade-all',
    reinstall_all='reinstall-all',
)


class PipX(CmdStateModuleHelper):
    output_params = ['name', 'source', 'index_url', 'force', 'installdeps']
    module = dict(
        argument_spec=dict(
            state=dict(type='str', default='install',
                       choices=[
                           'present', 'absent', 'install', 'uninstall', 'uninstall_all',
                           'inject', 'upgrade', 'upgrade_all', 'reinstall', 'reinstall_all']),
            name=dict(type='str'),
            source=dict(type='str'),
            installdeps=dict(type='bool', default=False),
            inject_packages=dict(type='list', elements='str'),
            force=dict(type='bool', default=False),
            include_injected=dict(type='bool', default=False),
            index_url=dict(type='str'),
            python=dict(type='str'),
        ),
        required_if=[
            ('state', 'present', ['name']),
            ('state', 'install', ['name']),
            ('state', 'absent', ['name']),
            ('state', 'uninstall', ['name']),
            ('state', 'inject', ['name', 'inject_packages']),
        ],
        supports_check_mode=True,
    )
    command = ['python3', '-m', 'pipx']
    command_args_formats = dict(
        state=dict(fmt=lambda v: [_state_map.get(v, v)]),
        name_source=dict(fmt=lambda n, s: [s] if s else [n], stars=1),
        installdeps=dict(fmt="--install-deps", style=ArgFormat.BOOLEAN),
        inject_packages=dict(fmt=lambda v: v),
        force=dict(fmt="--force", style=ArgFormat.BOOLEAN),
        include_injected=dict(fmt="--include-injected", style=ArgFormat.BOOLEAN),
        index_url=dict(fmt=('--index-url', '{0}'),),
        python=dict(fmt=('--python', '{0}'),),
        _list=dict(fmt=('list', '--include-injected', '--json')),
    )
    check_rc = True

    def _retrieve_installed(self):
        def process_list(rc, out, err):
            results = {}
            if out:
                raw_data = json.loads(out)
                for venv_name, venv in raw_data['venvs'].items():
                    results[venv_name] = {
                        'version': venv['metadata']['main_package']['package_version'],
                        'injected': dict(
                            (k, v['package_version']) for k, v in venv['metadata']['injected_packages']
                        ),
                    }
            return results

        installed = self.run_command(params=[{'_list': "dummy"}], process_output=process_list,
                                     publish_rc=False, publish_out=False, publish_err=False)

        if self.vars.name is not None:
            app_list = installed.get(self.vars.name)
            if app_list:
                return {self.vars.name: app_list}
            else:
                return {}

        return installed

    def __init_module__(self):
        self.vars.set('will_change', False, output=False, change=True)
        self.vars.set('application', self._retrieve_installed(), change=True, diff=True)

    def __quit_module__(self):
        self.vars.application = self._retrieve_installed()

    def state_install(self):
        if not self.vars.application or self.vars.force:
            self.vars.will_change = True
        if not self.module.check_mode:
            self.run_command(params=['state', 'index_url', 'installdeps', 'force', 'python',
                                     {'name_source': [self.vars.name, self.vars.source]}])

    state_present = state_install

    def state_upgrade(self):
        if not self.vars.application:
            raise ModuleHelperException(
                "Trying to upgrade a non-existent application: {0}".format(self.vars.name))

        if not self.module.check_mode:
            self.run_command(params=['state', 'index_url', 'installdeps', 'force', 'name'])

    def state_uninstall(self):
        if not self.vars.application:
            raise ModuleHelperException(
                "Trying to uninstall a non-existent application: {0}".format(self.vars.name))

        if not self.module.check_mode:
            self.run_command(params=['state', 'name'])

    state_absent = state_uninstall

    def state_reinstall(self):
        if not self.vars.application:
            raise ModuleHelperException(
                "Trying to reinstall a non-existent application: {0}".format(self.vars.name))
        self.vars.will_change = True
        if not self.module.check_mode:
            self.run_command(params=['state', 'name', 'python'])

    def state_inject(self):
        if not self.vars.application:
            raise ModuleHelperException(
                "Trying to inject packages into a non-existent application: {0}".format(self.vars.name))

        if not self.module.check_mode:
            self.run_command(params=['state', 'index_url', 'force', 'name', 'inject_packages'])

    def state_uninstall_all(self):
        if not self.module.check_mode:
            self.run_command(params=['state'])

    def state_reinstall_all(self):
        if not self.module.check_mode:
            self.run_command(params=['state', 'python'])

    def state_upgrade_all(self):
        if not self.module.check_mode:
            self.run_command(params=['state', 'include_injected', 'force'])


def main():
    PipX.execute()


if __name__ == '__main__':
    main()
