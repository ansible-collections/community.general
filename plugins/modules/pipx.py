#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2021, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r"""
module: pipx
short_description: Manages applications installed with pipx
version_added: 3.8.0
description:
  - Manage Python applications installed in isolated virtualenvs using pipx.
extends_documentation_fragment:
  - community.general.attributes
  - community.general.pipx
attributes:
  check_mode:
    support: full
  diff_mode:
    support: full
options:
  state:
    type: str
    choices:
      - present
      - absent
      - install
      - install_all
      - uninstall
      - uninstall_all
      - inject
      - uninject
      - upgrade
      - upgrade_shared
      - upgrade_all
      - reinstall
      - reinstall_all
      - latest
      - pin
      - unpin
    default: install
    description:
      - Desired state for the application.
      - The states V(present) and V(absent) are aliases to V(install) and V(uninstall), respectively.
      - The state V(latest) is equivalent to executing the task twice, with state V(install) and then V(upgrade). It was added
        in community.general 5.5.0.
      - The states V(install_all), V(uninject), V(upgrade_shared), V(pin) and V(unpin) are only available in C(pipx>=1.6.0),
        make sure to have a compatible version when using this option. These states have been added in community.general 9.4.0.
  name:
    type: str
    description:
      - The name of the application and also the name of the Python package being installed.
      - In C(pipx) documentation it is also referred to as the name of the virtual environment where the application is installed.
      - If O(name) is a simple package name without version specifiers, then that name is used as the Python package name
        to be installed.
      - Starting in community.general 10.7.0, you can use package specifiers when O(state=present) or O(state=install). For
        example, O(name=tox<4.0.0) or O(name=tox>3.0.27).
      - Please note that when you use O(state=present) and O(name) with version specifiers, contrary to the behavior of C(pipx),
        this module honors the version specifier and installs a version of the application that satisfies it. If you want
        to ensure the reinstallation of the application even when the version specifier is met, then you must use O(force=true),
        or perhaps use O(state=upgrade) instead.
      - Use O(source) for installing from URLs or directories.
  source:
    type: str
    description:
      - Source for the package. This option is used when O(state=install) or O(state=latest), and it is ignored with other
        states.
      - Use O(source) when installing a Python package with version specifier, or from a local path, from a VCS URL or compressed
        file.
      - The value of this option is passed as-is to C(pipx).
      - O(name) is still required when using O(source) to establish the application name without fetching the package from
        a remote source.
      - The module is not idempotent when using O(source).
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
      - The module is not idempotent when O(force=true).
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
  suffix:
    description:
      - Optional suffix for virtual environment and executable names.
      - B(Warning:) C(pipx) documentation states this is an B(experimental) feature subject to change.
    type: str
    version_added: 9.3.0
  global:
    version_added: 9.4.0
  spec_metadata:
    description:
      - Spec metadata file for O(state=install_all).
      - This content of the file is usually generated with C(pipx list --json), and it can be obtained with M(community.general.pipx_info)
        with O(community.general.pipx_info#module:include_raw=true) and obtaining the content from the RV(community.general.pipx_info#module:raw_output).
    type: path
    version_added: 9.4.0
requirements:
  - When using O(name) with version specifiers, the Python package C(packaging) is required.
  - If the package C(packaging) is at a version lesser than C(22.0.0), it fails silently when processing invalid specifiers,
    like C(tox<<<<4.0).
author:
  - "Alexei Znamensky (@russoz)"
"""

EXAMPLES = r"""
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

- name: Install or upgrade tox with extra 'docs'
  community.general.pipx:
    name: tox
    source: tox[docs]
    state: latest

- name: Reinstall black with specific Python version
  community.general.pipx:
    name: black
    state: reinstall
    python: 3.7

- name: Uninstall pycowsay
  community.general.pipx:
    name: pycowsay
    state: absent

- name: Install multiple packages from list
  vars:
    pipx_packages:
      - pycowsay
      - black
      - tox
  community.general.pipx:
    name: "{{ item }}"
    state: latest
  with_items: "{{ pipx_packages }}"
"""

RETURN = r"""
version:
  description: Version of pipx.
  type: str
  returned: always
  sample: "1.7.1"
  version_added: 10.1.0
"""


from ansible_collections.community.general.plugins.module_utils.module_helper import StateModuleHelper
from ansible_collections.community.general.plugins.module_utils.pipx import pipx_runner, pipx_common_argspec, make_process_dict
from ansible_collections.community.general.plugins.module_utils.pkg_req import PackageRequirement

from ansible.module_utils.facts.compat import ansible_facts


def _make_name(name, suffix):
    return name if suffix is None else "{0}{1}".format(name, suffix)


class PipX(StateModuleHelper):
    output_params = ['name', 'source', 'index_url', 'force', 'installdeps']
    argument_spec = dict(
        state=dict(type='str', default='install',
                   choices=[
                       'present', 'absent', 'install', 'install_all', 'uninstall', 'uninstall_all', 'inject', 'uninject',
                       'upgrade', 'upgrade_shared', 'upgrade_all', 'reinstall', 'reinstall_all', 'latest', 'pin', 'unpin',
                   ]),
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
        editable=dict(type='bool', default=False),
        pip_args=dict(type='str'),
        suffix=dict(type='str'),
        spec_metadata=dict(type='path'),
    )
    argument_spec.update(pipx_common_argspec)

    module = dict(
        argument_spec=argument_spec,
        required_if=[
            ('state', 'present', ['name']),
            ('state', 'install', ['name']),
            ('state', 'install_all', ['spec_metadata']),
            ('state', 'absent', ['name']),
            ('state', 'uninstall', ['name']),
            ('state', 'upgrade', ['name']),
            ('state', 'reinstall', ['name']),
            ('state', 'latest', ['name']),
            ('state', 'inject', ['name', 'inject_packages']),
            ('state', 'pin', ['name']),
            ('state', 'unpin', ['name']),
        ],
        required_by=dict(
            suffix="name",
        ),
        supports_check_mode=True,
    )
    use_old_vardict = False

    def _retrieve_installed(self):
        output_process = make_process_dict(include_injected=True)
        installed, dummy = self.runner('_list global', output_process=output_process).run()

        if self.app_name is None:
            return installed

        return {k: v for k, v in installed.items() if k == self.app_name}

    def __init_module__(self):
        if self.vars.executable:
            self.command = [self.vars.executable]
        else:
            facts = ansible_facts(self.module, gather_subset=['python'])
            self.command = [facts['python']['executable'], '-m', 'pipx']
        self.runner = pipx_runner(self.module, self.command)

        pkg_req = PackageRequirement(self.module, self.vars.name)
        self.parsed_name = pkg_req.parsed_name
        self.parsed_req = pkg_req.requirement
        self.app_name = _make_name(self.parsed_name, self.vars.suffix)

        self.vars.set('application', self._retrieve_installed(), change=True, diff=True)

        with self.runner("version") as ctx:
            rc, out, err = ctx.run()
            self.vars.version = out.strip()

    def __quit_module__(self):
        self.vars.application = self._retrieve_installed()

    def _capture_results(self, ctx):
        self.vars.stdout = ctx.results_out
        self.vars.stderr = ctx.results_err
        self.vars.cmd = ctx.cmd
        self.vars.set('run_info', ctx.run_info, verbosity=4)

    def state_install(self):
        # If we have a version spec and no source, use the version spec as source
        if self.parsed_req and not self.vars.source:
            self.vars.source = self.vars.name

        if self.vars.application.get(self.app_name):
            is_installed = True
            version_match = self.vars.application[self.app_name]['version'] in self.parsed_req.specifier if self.parsed_req else True
            force = self.vars.force or (not version_match)
        else:
            is_installed = False
            version_match = False
            force = self.vars.force

        if is_installed and version_match and not force:
            return

        self.changed = True
        args_order = 'state global index_url install_deps force python system_site_packages editable pip_args suffix name_source'
        with self.runner(args_order, check_mode_skip=True) as ctx:
            ctx.run(name_source=[self.parsed_name, self.vars.source], force=force)
            self._capture_results(ctx)

    state_present = state_install

    def state_install_all(self):
        self.changed = True
        with self.runner('state global index_url force python system_site_packages editable pip_args spec_metadata', check_mode_skip=True) as ctx:
            ctx.run()
            self._capture_results(ctx)

    def state_upgrade(self):
        name = _make_name(self.vars.name, self.vars.suffix)
        if not self.vars.application:
            self.do_raise("Trying to upgrade a non-existent application: {0}".format(name))
        if self.vars.force:
            self.changed = True

        with self.runner('state global include_injected index_url force editable pip_args name', check_mode_skip=True) as ctx:
            ctx.run(name=name)
            self._capture_results(ctx)

    def state_uninstall(self):
        if self.vars.application:
            name = _make_name(self.vars.name, self.vars.suffix)
            with self.runner('state global name', check_mode_skip=True) as ctx:
                ctx.run(name=name)
                self._capture_results(ctx)

    state_absent = state_uninstall

    def state_reinstall(self):
        name = _make_name(self.vars.name, self.vars.suffix)
        if not self.vars.application:
            self.do_raise("Trying to reinstall a non-existent application: {0}".format(name))
        self.changed = True
        with self.runner('state global name python', check_mode_skip=True) as ctx:
            ctx.run(name=name)
            self._capture_results(ctx)

    def state_inject(self):
        name = _make_name(self.vars.name, self.vars.suffix)
        if not self.vars.application:
            self.do_raise("Trying to inject packages into a non-existent application: {0}".format(name))
        if self.vars.force:
            self.changed = True
        with self.runner('state global index_url install_apps install_deps force editable pip_args name inject_packages', check_mode_skip=True) as ctx:
            ctx.run(name=name)
            self._capture_results(ctx)

    def state_uninject(self):
        name = _make_name(self.vars.name, self.vars.suffix)
        if not self.vars.application:
            self.do_raise("Trying to uninject packages into a non-existent application: {0}".format(name))
        with self.runner('state global name inject_packages', check_mode_skip=True) as ctx:
            ctx.run(name=name)
            self._capture_results(ctx)

    def state_uninstall_all(self):
        with self.runner('state global', check_mode_skip=True) as ctx:
            ctx.run()
            self._capture_results(ctx)

    def state_reinstall_all(self):
        with self.runner('state global python', check_mode_skip=True) as ctx:
            ctx.run()
            self._capture_results(ctx)

    def state_upgrade_all(self):
        if self.vars.force:
            self.changed = True
        with self.runner('state global include_injected force', check_mode_skip=True) as ctx:
            ctx.run()
            self._capture_results(ctx)

    def state_upgrade_shared(self):
        with self.runner('state global pip_args', check_mode_skip=True) as ctx:
            ctx.run()
            self._capture_results(ctx)

    def state_latest(self):
        if not self.vars.application or self.vars.force:
            self.changed = True
            args_order = 'state global index_url install_deps force python system_site_packages editable pip_args suffix name_source'
            with self.runner(args_order, check_mode_skip=True) as ctx:
                ctx.run(state='install', name_source=[self.vars.name, self.vars.source])
                self._capture_results(ctx)

        with self.runner('state global include_injected index_url force editable pip_args name', check_mode_skip=True) as ctx:
            ctx.run(state='upgrade')
            self._capture_results(ctx)

    def state_pin(self):
        with self.runner('state global name', check_mode_skip=True) as ctx:
            ctx.run()
            self._capture_results(ctx)

    def state_unpin(self):
        with self.runner('state global name', check_mode_skip=True) as ctx:
            ctx.run()
            self._capture_results(ctx)


def main():
    PipX.execute()


if __name__ == '__main__':
    main()
