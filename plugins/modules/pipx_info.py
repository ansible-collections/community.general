#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2021, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r"""
module: pipx_info
short_description: Rretrieves information about applications installed with pipx
version_added: 5.6.0
description:
  - Retrieve details about Python applications installed in isolated virtualenvs using pipx.
extends_documentation_fragment:
  - community.general.attributes
  - community.general.attributes.info_module
  - community.general.pipx
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
      - The raw output is not affected by O(include_deps) or O(include_injected).
    type: bool
    default: false
  global:
    version_added: 9.3.0
author:
  - "Alexei Znamensky (@russoz)"
"""

EXAMPLES = r"""
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
"""

RETURN = r"""
application:
  description: The list of installed applications.
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
      description: The dependencies of the installed application, when O(include_deps=true).
      returned: success
      type: list
      elements: str
      sample: ["virtualenv"]
    injected:
      description: The injected packages for the installed application, when O(include_injected=true).
      returned: success
      type: dict
      sample:
        licenses: "0.6.1"
    pinned:
      description:
        - Whether the installed application is pinned or not.
        - When using C(pipx<=1.6.0), this returns C(null).
      returned: success
      type: bool
      sample:
        pinned: true
      version_added: 10.0.0

raw_output:
  description: The raw output of the C(pipx list) command, when O(include_raw=true). Used for debugging.
  returned: success
  type: dict

cmd:
  description: Command executed to obtain the list of installed applications.
  returned: success
  type: list
  elements: str
  sample:
    [
      "/usr/bin/python3.10",
      "-m",
      "pipx",
      "list",
      "--include-injected",
      "--json"
    ]

version:
  description: Version of pipx.
  type: str
  returned: always
  sample: "1.7.1"
  version_added: 10.1.0
"""

from ansible_collections.community.general.plugins.module_utils.module_helper import ModuleHelper
from ansible_collections.community.general.plugins.module_utils.pipx import pipx_runner, pipx_common_argspec, make_process_dict

from ansible.module_utils.facts.compat import ansible_facts


class PipXInfo(ModuleHelper):
    output_params = ['name']
    argument_spec = dict(
        name=dict(type='str'),
        include_deps=dict(type='bool', default=False),
        include_injected=dict(type='bool', default=False),
        include_raw=dict(type='bool', default=False),
    )
    argument_spec.update(pipx_common_argspec)
    module = dict(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    use_old_vardict = False

    def __init_module__(self):
        if self.vars.executable:
            self.command = [self.vars.executable]
        else:
            facts = ansible_facts(self.module, gather_subset=['python'])
            self.command = [facts['python']['executable'], '-m', 'pipx']
        self.runner = pipx_runner(self.module, self.command)
        with self.runner("version") as ctx:
            rc, out, err = ctx.run()
            self.vars.version = out.strip()

    def __run__(self):
        output_process = make_process_dict(self.vars.include_injected, self.vars.include_deps)
        with self.runner('_list global', output_process=output_process) as ctx:
            applications, raw_data = ctx.run()
            if self.vars.include_raw:
                self.vars.raw_output = raw_data

            if self.vars.name:
                self.vars.application = [
                    v
                    for k, v in applications.items()
                    if k == self.vars.name
                ]
            else:
                self.vars.application = list(applications.values())
            self._capture_results(ctx)

    def _capture_results(self, ctx):
        self.vars.cmd = ctx.cmd
        if self.verbosity >= 4:
            self.vars.run_info = ctx.run_info


def main():
    PipXInfo.execute()


if __name__ == '__main__':
    main()
