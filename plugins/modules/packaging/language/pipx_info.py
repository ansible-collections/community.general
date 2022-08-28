#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2021, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: pipx_info
short_description: Rretrieves information about applications installed with pipx
version_added: 5.6.0
description:
    - Retrieve details about Python applications installed in isolated virtualenvs using pipx.
options:
    name:
        description:
            - Name of an application with C(pipx).
        type: str
    include_deps:
        description:
            - Include dependent packages in the output.
        type: bool
        default: false
    include_injected:
        description:
            - Include injected packages in the output.
        type: bool
        default: false
    include_raw:
        description:
            - Returns the raw output of C(pipx list --json).
            - The raw output is not affected by I(include_deps) or I(include_injected).
        type: bool
        default: false
    executable:
        description:
            - Path to the C(pipx) installed in the system.
            - >
              If not specified, the module will use C(python -m pipx) to run the tool,
              using the same Python interpreter as ansible itself.
        type: path
notes:
    - This module does not install the C(pipx) python package, however that can be easily done with the module M(ansible.builtin.pip).
    - This module does not require C(pipx) to be in the shell C(PATH), but it must be loadable by Python as a module.
    - Please note that C(pipx) requires Python 3.6 or above.
    - See also the C(pipx) documentation at U(https://pypa.github.io/pipx/).
author:
    - "Alexei Znamensky (@russoz)"
'''

EXAMPLES = '''
'''

RETURN = '''
'''

import json

from ansible_collections.community.general.plugins.module_utils.module_helper import ModuleHelper
from ansible_collections.community.general.plugins.module_utils.pipx import pipx_runner

from ansible.module_utils.facts.compat import ansible_facts


class PipXInfo(ModuleHelper):
    output_params = ['name']
    module = dict(
        argument_spec=dict(
            name=dict(type='str'),
            include_deps=dict(type='bool', default=False),
            include_injected=dict(type='bool', default=False),
            include_raw=dict(type='bool', default=False),
            executable=dict(type='path'),
        ),
        supports_check_mode=True,
    )

    def __init_module__(self):
        if self.vars.executable:
            self.command = [self.vars.executable]
        else:
            facts = ansible_facts(self.module, gather_subset=['python'])
            self.command = [facts['python']['executable'], '-m', 'pipx']
        self.runner = pipx_runner(self.module, self.command)

        # self.vars.set('application', self._retrieve_installed(), change=True, diff=True)

    def __run__(self):
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
                    'dependencies': list(venv['metadata']['main_package']['app_paths_of_dependencies']),
                }

            return results

        with self.runner('_list', output_process=process_list) as ctx:
            installed = ctx.run(_list=1)
            self._capture_results(ctx)

        if self.vars.include_raw:
            self.vars.raw_list = installed

        if self.vars.name:
            app_entry = installed.get(self.vars.name)
            if app_entry:
                self.vars.application = self.vars.name
                self.vars.version = app_entry['version']
                if self.vars.include_injected:
                    self.vars.injected = app_entry['injected']
                if self.vars.include_deps:
                    self.vars.dependencies = app_entry['dependencies']

        else:
            results = {}
            for name, entry in installed.items():
                results[name] = {'version': entry['version']}
                if self.vars.include_injected:
                    results[name]['injected'] = entry['injected']
                if self.vars.include_deps:
                    results[name]['dependencies'] = entry['dependencies']

            self.vars.pipx_results = results

    def _capture_results(self, ctx):
        self.vars.cmd = ctx.cmd
        if self.verbosity >= 4:
            self.vars.run_info = ctx.run_info


def main():
    PipXInfo.execute()


if __name__ == '__main__':
    main()
