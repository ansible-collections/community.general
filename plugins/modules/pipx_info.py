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
extends_documentation_fragment:
    - community.general.attributes
    - community.general.attributes.info_module
options:
    name:
        description:
            - Name of an application installed with C(pipx).
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
    - >
      This module will honor C(pipx) environment variables such as but not limited to C(PIPX_HOME) and C(PIPX_BIN_DIR)
      passed using the R(environment Ansible keyword, playbooks_environment).
    - This module requires C(pipx) version 0.16.2.1 or above.
    - Please note that C(pipx) requires Python 3.6 or above.
    - See also the C(pipx) documentation at U(https://pypa.github.io/pipx/).
author:
    - "Alexei Znamensky (@russoz)"
'''

EXAMPLES = '''
- name: retrieve all installed applications
  community.general.pipx_info: {}

- name: retrieve all installed applications, include dependencies and injected packages
  community.general.pipx_info:
    include_deps: true
    include_injected: true

- name: retrieve application tox
  community.general.pipx_info:
    name: tox
    include_deps: true

- name: retrieve application ansible-lint, include dependencies
  community.general.pipx_info:
    name: ansible-lint
    include_deps: true
'''

RETURN = '''
application:
  description: The list of installed applications
  returned: success
  type: list
  elements: dict
  contains:
    name:
      description: The name of the installed application.
      returned: success
      type: str
      sample: "tox"
    version:
      description: The version of the installed application.
      returned: success
      type: str
      sample: "3.24.0"
    dependencies:
      description: The dependencies of the installed application, when I(include_deps=true).
      returned: success
      type: list
      elements: str
      sample: ["virtualenv"]
    injected:
      description: The injected packages for the installed application, when I(include_injected=true).
      returned: success
      type: dict
      sample:
        licenses: "0.6.1"

raw_output:
  description: The raw output of the C(pipx list) command, when I(include_raw=true). Used for debugging.
  returned: success
  type: dict

cmd:
  description: Command executed to obtain the list of installed applications.
  returned: success
  type: list
  elements: str
  sample: [
    "/usr/bin/python3.10",
    "-m",
    "pipx",
    "list",
    "--include-injected",
    "--json"
  ]
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
                return []

            results = []
            raw_data = json.loads(out)
            if self.vars.include_raw:
                self.vars.raw_output = raw_data

            if self.vars.name:
                if self.vars.name in raw_data['venvs']:
                    data = {self.vars.name: raw_data['venvs'][self.vars.name]}
                else:
                    data = {}
            else:
                data = raw_data['venvs']

            for venv_name, venv in data.items():
                entry = {
                    'name': venv_name,
                    'version': venv['metadata']['main_package']['package_version']
                }
                if self.vars.include_injected:
                    entry['injected'] = dict(
                        (k, v['package_version']) for k, v in venv['metadata']['injected_packages'].items()
                    )
                if self.vars.include_deps:
                    entry['dependencies'] = list(venv['metadata']['main_package']['app_paths_of_dependencies'])
                results.append(entry)

            return results

        with self.runner('_list', output_process=process_list) as ctx:
            self.vars.application = ctx.run(_list=1)
            self._capture_results(ctx)

    def _capture_results(self, ctx):
        self.vars.cmd = ctx.cmd
        if self.verbosity >= 4:
            self.vars.run_info = ctx.run_info


def main():
    PipXInfo.execute()


if __name__ == '__main__':
    main()
