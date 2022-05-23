#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2021, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: pipx
short_description: Manages applications installed with pipx
version_added: 3.8.0
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
    install_deps:
        description:
            - Include applications of dependent packages.
            - Only used when I(state=install) or I(state=upgrade).
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
            - Only used when I(state=install), I(state=upgrade), I(state=upgrade_all), or I(state=inject).
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
            - Only used when I(state=install), I(state=upgrade), or I(state=inject).
        type: str
    python:
        description:
            - Python version to be used when creating the application virtual environment. Must be 3.6+.
            - Only used when I(state=install), I(state=reinstall), or I(state=reinstall_all).
        type: str
    executable:
        description:
            - Path to the C(pipx) installed in the system.
            - >
              If not specified, the module will use C(python -m pipx) to run the tool,
              using the same Python interpreter as ansible itself.
        type: path
    editable:
        description:
            - Install the project in editable mode.
        type: bool
        default: false
        version_added: 4.6.0
    pip_args:
        description:
            - Arbitrary arguments to pass directly to C(pip).
        type: str
        version_added: 4.6.0
notes:
    - This module does not install the C(pipx) python package, however that can be easily done with the module M(ansible.builtin.pip).
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

EXAMPLES = '''
- name: Install tox
  community.general.pipx:
    name: tox

- name: Install tox from git repository
  community.general.pipx:
    name: tox
    source: git+https://github.com/tox-dev/tox.git

- name: Upgrade tox
  community.general.pipx:
    name: tox
    state: upgrade

- name: Reinstall black with specific Python version
  community.general.pipx:
    name: black
    state: reinstall
    python: 3.7

- name: Uninstall pycowsay
  community.general.pipx:
    name: pycowsay
    state: absent
'''


import json

from ansible_collections.community.general.plugins.module_utils.module_helper import (
    CmdStateModuleHelper, ArgFormat
)
from ansible.module_utils.facts.compat import ansible_facts


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
                       choices=['present', 'absent', 'install', 'uninstall', 'uninstall_all',
                                'inject', 'upgrade', 'upgrade_all', 'reinstall', 'reinstall_all']),
            name=dict(type='str'),
            source=dict(type='str'),
            install_deps=dict(type='bool', default=False),
            inject_packages=dict(type='list', elements='str'),
            force=dict(type='bool', default=False),
            include_injected=dict(type='bool', default=False),
            index_url=dict(type='str'),
            python=dict(type='str'),
            executable=dict(type='path'),
            editable=dict(type='bool', default=False),
            pip_args=dict(type='str'),
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
    command_args_formats = dict(
        state=dict(fmt=lambda v: [_state_map.get(v, v)]),
        name_source=dict(fmt=lambda n, s: [s] if s else [n], stars=1),
        install_deps=dict(fmt="--include-deps", style=ArgFormat.BOOLEAN),
        inject_packages=dict(fmt=lambda v: v),
        force=dict(fmt="--force", style=ArgFormat.BOOLEAN),
        include_injected=dict(fmt="--include-injected", style=ArgFormat.BOOLEAN),
        index_url=dict(fmt=('--index-url', '{0}'),),
        python=dict(fmt=('--python', '{0}'),),
        _list=dict(fmt=('list', '--include-injected', '--json'), style=ArgFormat.BOOLEAN),
        editable=dict(fmt="--editable", style=ArgFormat.BOOLEAN),
        pip_args=dict(fmt=('--pip-args', '{0}'),),
    )
    check_rc = True
    run_command_fixed_options = dict(
        environ_update={'USE_EMOJI': '0'}
    )

    def _retrieve_installed(self):
        def process_list(rc, out, err):
            if not out:
                return {}

            results = {}
            raw_data = json.loads(out)
            for venv_name, venv in raw_data['venvs'].items():
                results[venv_name] = {
                    'version': venv['metadata']['main_package']['package_version'],
                    'injected': dict(
                        (k, v['package_version']) for k, v in venv['metadata']['injected_packages'].items()
                    ),
                }
            return results

        installed = self.run_command(params=[{'_list': True}], process_output=process_list,
                                     publish_rc=False, publish_out=False, publish_err=False, publish_cmd=False)

        if self.vars.name is not None:
            app_list = installed.get(self.vars.name)
            if app_list:
                return {self.vars.name: app_list}
            else:
                return {}

        return installed

    def __init_module__(self):
        if self.vars.executable:
            self.command = [self.vars.executable]
        else:
            facts = ansible_facts(self.module, gather_subset=['python'])
            self.command = [facts['python']['executable'], '-m', 'pipx']

        self.vars.set('application', self._retrieve_installed(), change=True, diff=True)

    def __quit_module__(self):
        self.vars.application = self._retrieve_installed()

    def state_install(self):
        if not self.vars.application or self.vars.force:
            self.changed = True
            if not self.module.check_mode:
                self.run_command(params=[
                    'state', 'index_url', 'install_deps', 'force', 'python', 'editable', 'pip_args',
                    {'name_source': [self.vars.name, self.vars.source]}])

    state_present = state_install

    def state_upgrade(self):
        if not self.vars.application:
            self.do_raise("Trying to upgrade a non-existent application: {0}".format(self.vars.name))
        if self.vars.force:
            self.changed = True
        if not self.module.check_mode:
            self.run_command(params=['state', 'index_url', 'install_deps', 'force', 'editable', 'pip_args', 'name'])

    def state_uninstall(self):
        if self.vars.application and not self.module.check_mode:
            self.run_command(params=['state', 'name'])

    state_absent = state_uninstall

    def state_reinstall(self):
        if not self.vars.application:
            self.do_raise("Trying to reinstall a non-existent application: {0}".format(self.vars.name))
        self.changed = True
        if not self.module.check_mode:
            self.run_command(params=['state', 'name', 'python'])

    def state_inject(self):
        if not self.vars.application:
            self.do_raise("Trying to inject packages into a non-existent application: {0}".format(self.vars.name))
        if self.vars.force:
            self.changed = True
        if not self.module.check_mode:
            self.run_command(params=['state', 'index_url', 'force', 'editable', 'pip_args', 'name', 'inject_packages'])

    def state_uninstall_all(self):
        if not self.module.check_mode:
            self.run_command(params=['state'])

    def state_reinstall_all(self):
        if not self.module.check_mode:
            self.run_command(params=['state', 'python'])

    def state_upgrade_all(self):
        if self.vars.force:
            self.changed = True
        if not self.module.check_mode:
            self.run_command(params=['state', 'include_injected', 'force'])


def main():
    PipX.execute()


if __name__ == '__main__':
    main()
