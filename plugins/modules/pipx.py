#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2021, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: pipx
short_description: Manages applications installed with pipx
version_added: 3.8.0
description:
    - Manage Python applications installed in isolated virtualenvs using pipx.
extends_documentation_fragment:
    - community.general.attributes
attributes:
    check_mode:
        support: full
    diff_mode:
        support: full
options:
    state:
        type: str
        choices: [present, absent, install, uninstall, uninstall_all, inject, upgrade, upgrade_all, reinstall, reinstall_all, latest]
        default: install
        description:
            - Desired state for the application.
            - The states V(present) and V(absent) are aliases to V(install) and V(uninstall), respectively.
            - The state V(latest) is equivalent to executing the task twice, with state V(install) and then V(upgrade).
              It was added in community.general 5.5.0.
    name:
        type: str
        description:
            - >
              The name of the application to be installed. It must to be a simple package name.
              For passing package specifications or installing from URLs or directories,
              please use the O(source) option.
    source:
        type: str
        description:
            - >
              If the application source, such as a package with version specifier, or an URL,
              directory or any other accepted specification. See C(pipx) documentation for more details.
            - When specified, the C(pipx) command will use O(source) instead of O(name).
    install_apps:
        description:
            - Add apps from the injected packages.
            - Only used when O(state=inject).
        type: bool
        default: false
        version_added: 6.5.0
    install_deps:
        description:
            - Include applications of dependent packages.
            - Only used when O(state=install), O(state=latest), or O(state=inject).
        type: bool
        default: false
    inject_packages:
        description:
            - Packages to be injected into an existing virtual environment.
            - Only used when O(state=inject).
        type: list
        elements: str
    force:
        description:
            - Force modification of the application's virtual environment. See C(pipx) for details.
            - Only used when O(state=install), O(state=upgrade), O(state=upgrade_all), O(state=latest), or O(state=inject).
        type: bool
        default: false
    include_injected:
        description:
            - Upgrade the injected packages along with the application.
            - Only used when O(state=upgrade), O(state=upgrade_all), or O(state=latest).
            - This is used with O(state=upgrade) and O(state=latest) since community.general 6.6.0.
        type: bool
        default: false
    index_url:
        description:
            - Base URL of Python Package Index.
            - Only used when O(state=install), O(state=upgrade), O(state=latest), or O(state=inject).
        type: str
    python:
        description:
            - Python version to be used when creating the application virtual environment. Must be 3.6+.
            - Only used when O(state=install), O(state=latest), O(state=reinstall), or O(state=reinstall_all).
        type: str
    system_site_packages:
        description:
            - Give application virtual environment access to the system site-packages directory.
            - Only used when O(state=install) or O(state=latest).
        type: bool
        default: false
        version_added: 6.6.0
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
    - >
      This module will honor C(pipx) environment variables such as but not limited to C(PIPX_HOME) and C(PIPX_BIN_DIR)
      passed using the R(environment Ansible keyword, playbooks_environment).
    - This module requires C(pipx) version 0.16.2.1 or above.
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

from ansible_collections.community.general.plugins.module_utils.module_helper import StateModuleHelper
from ansible_collections.community.general.plugins.module_utils.pipx import pipx_runner

from ansible.module_utils.facts.compat import ansible_facts


class PipX(StateModuleHelper):
    output_params = ['name', 'source', 'index_url', 'force', 'installdeps']
    module = dict(
        argument_spec=dict(
            state=dict(type='str', default='install',
                       choices=['present', 'absent', 'install', 'uninstall', 'uninstall_all',
                                'inject', 'upgrade', 'upgrade_all', 'reinstall', 'reinstall_all', 'latest']),
            name=dict(type='str'),
            source=dict(type='str'),
            install_apps=dict(type='bool', default=False),
            install_deps=dict(type='bool', default=False),
            inject_packages=dict(type='list', elements='str'),
            force=dict(type='bool', default=False),
            include_injected=dict(type='bool', default=False),
            index_url=dict(type='str'),
            python=dict(type='str'),
            system_site_packages=dict(type='bool', default=False),
            executable=dict(type='path'),
            editable=dict(type='bool', default=False),
            pip_args=dict(type='str'),
        ),
        required_if=[
            ('state', 'present', ['name']),
            ('state', 'install', ['name']),
            ('state', 'absent', ['name']),
            ('state', 'uninstall', ['name']),
            ('state', 'upgrade', ['name']),
            ('state', 'reinstall', ['name']),
            ('state', 'latest', ['name']),
            ('state', 'inject', ['name', 'inject_packages']),
        ],
        supports_check_mode=True,
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

        installed = self.runner('_list', output_process=process_list).run(_list=1)

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
        self.runner = pipx_runner(self.module, self.command)

        self.vars.set('application', self._retrieve_installed(), change=True, diff=True)

    def __quit_module__(self):
        self.vars.application = self._retrieve_installed()

    def _capture_results(self, ctx):
        self.vars.stdout = ctx.results_out
        self.vars.stderr = ctx.results_err
        self.vars.cmd = ctx.cmd
        if self.verbosity >= 4:
            self.vars.run_info = ctx.run_info

    def state_install(self):
        if not self.vars.application or self.vars.force:
            self.changed = True
            with self.runner('state index_url install_deps force python system_site_packages editable pip_args name_source', check_mode_skip=True) as ctx:
                ctx.run(name_source=[self.vars.name, self.vars.source])
                self._capture_results(ctx)

    state_present = state_install

    def state_upgrade(self):
        if not self.vars.application:
            self.do_raise("Trying to upgrade a non-existent application: {0}".format(self.vars.name))
        if self.vars.force:
            self.changed = True

        with self.runner('state include_injected index_url force editable pip_args name', check_mode_skip=True) as ctx:
            ctx.run()
            self._capture_results(ctx)

    def state_uninstall(self):
        if self.vars.application:
            with self.runner('state name', check_mode_skip=True) as ctx:
                ctx.run()
                self._capture_results(ctx)

    state_absent = state_uninstall

    def state_reinstall(self):
        if not self.vars.application:
            self.do_raise("Trying to reinstall a non-existent application: {0}".format(self.vars.name))
        self.changed = True
        with self.runner('state name python', check_mode_skip=True) as ctx:
            ctx.run()
            self._capture_results(ctx)

    def state_inject(self):
        if not self.vars.application:
            self.do_raise("Trying to inject packages into a non-existent application: {0}".format(self.vars.name))
        if self.vars.force:
            self.changed = True
        with self.runner('state index_url install_apps install_deps force editable pip_args name inject_packages', check_mode_skip=True) as ctx:
            ctx.run()
            self._capture_results(ctx)

    def state_uninstall_all(self):
        with self.runner('state', check_mode_skip=True) as ctx:
            ctx.run()
            self._capture_results(ctx)

    def state_reinstall_all(self):
        with self.runner('state python', check_mode_skip=True) as ctx:
            ctx.run()
            self._capture_results(ctx)

    def state_upgrade_all(self):
        if self.vars.force:
            self.changed = True
        with self.runner('state include_injected force', check_mode_skip=True) as ctx:
            ctx.run()
            self._capture_results(ctx)

    def state_latest(self):
        if not self.vars.application or self.vars.force:
            self.changed = True
            with self.runner('state index_url install_deps force python system_site_packages editable pip_args name_source', check_mode_skip=True) as ctx:
                ctx.run(state='install', name_source=[self.vars.name, self.vars.source])
                self._capture_results(ctx)

        with self.runner('state include_injected index_url force editable pip_args name', check_mode_skip=True) as ctx:
            ctx.run(state='upgrade')
            self._capture_results(ctx)


def main():
    PipX.execute()


if __name__ == '__main__':
    main()
