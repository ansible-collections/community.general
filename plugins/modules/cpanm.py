#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2012, Franck Cuny <franck@lumberjaph.net>
# Copyright (c) 2021, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r"""
module: cpanm
short_description: Manages Perl library dependencies
description:
  - Manage Perl library dependencies using cpanminus.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options:
  name:
    type: str
    description:
      - The Perl library to install. Valid values change according to the O(mode), see notes for more details.
      - Note that for installing from a local path the parameter O(from_path) should be used.
    aliases: [pkg]
  from_path:
    type: path
    description:
      - The local directory or C(tar.gz) file to install from.
  notest:
    description:
      - Do not run unit tests.
    type: bool
    default: false
  locallib:
    description:
      - Specify the install base to install modules.
    type: path
  mirror:
    description:
      - Specifies the base URL for the CPAN mirror to use.
    type: str
  mirror_only:
    description:
      - Use the mirror's index file instead of the CPAN Meta DB.
    type: bool
    default: false
  installdeps:
    description:
      - Only install dependencies.
    type: bool
    default: false
  install_recommendations:
    description:
      - If V(true), installs dependencies declared as recommends per META spec.
      - If V(false), it ensures the dependencies declared as recommends are not installed, overriding any decision made earlier
        in E(PERL_CPANM_OPT).
      - If parameter is not set, C(cpanm) uses its existing defaults.
      - When these dependencies fail to install, cpanm continues the installation, since they are just recommendation.
    type: bool
    version_added: 10.3.0
  install_suggestions:
    description:
      - If V(true), installs dependencies declared as suggests per META spec.
      - If V(false), it ensures the dependencies declared as suggests are not installed, overriding any decision made earlier
        in E(PERL_CPANM_OPT).
      - If parameter is not set, C(cpanm) uses its existing defaults.
      - When these dependencies fail to install, cpanm continues the installation, since they are just suggestion.
    type: bool
    version_added: 10.3.0
  version:
    description:
      - Version specification for the perl module. When O(mode) is V(new), C(cpanm) version operators are accepted.
    type: str
  executable:
    description:
      - Override the path to the cpanm executable.
    type: path
  mode:
    description:
      - Controls the module behavior. See notes below for more details.
      - The default changed from V(compatibility) to V(new) in community.general 9.0.0.
      - 'O(mode=new): The O(name) parameter may refer to a module name, a distribution file, a HTTP URL or a git repository
        URL as described in C(cpanminus) documentation. C(cpanm) version specifiers are recognized. This is the default mode
        from community.general 9.0.0 onwards.'
      - 'O(mode=compatibility): This was the default mode before community.general 9.0.0. O(name) must be either a module
        name or a distribution file. If the perl module given by O(name) is installed (at the exact O(version) when specified),
        then nothing happens. Otherwise, it is installed using the C(cpanm) executable. O(name) cannot be an URL, or a git
        URL. C(cpanm) version specifiers do not work in this mode.'
      - 'B(ATTENTION): V(compatibility) mode is deprecated and will be removed in community.general 13.0.0.'
    type: str
    choices: [compatibility, new]
    default: new
    version_added: 3.0.0
  name_check:
    description:
      - When O(mode=new), this parameter can be used to check if there is a module O(name) installed (at O(version), when
        specified).
    type: str
    version_added: 3.0.0
notes:
  - Please note that U(http://search.cpan.org/dist/App-cpanminus/bin/cpanm, cpanm) must be installed on the remote host.
seealso:
  - name: C(cpanm) command manual page
    description: Manual page for the command.
    link: https://metacpan.org/dist/App-cpanminus/view/bin/cpanm
author:
  - "Franck Cuny (@fcuny)"
  - "Alexei Znamensky (@russoz)"
"""

EXAMPLES = r"""
- name: Install Dancer perl package
  community.general.cpanm:
    name: Dancer

- name: Install version 0.99_05 of the Plack perl package
  community.general.cpanm:
    name: MIYAGAWA/Plack-0.99_05.tar.gz

- name: Install Dancer into the specified locallib
  community.general.cpanm:
    name: Dancer
    locallib: /srv/webapps/my_app/extlib

- name: Install perl dependencies from local directory
  community.general.cpanm:
    from_path: /srv/webapps/my_app/src/

- name: Install Dancer perl package without running the unit tests in indicated locallib
  community.general.cpanm:
    name: Dancer
    notest: true
    locallib: /srv/webapps/my_app/extlib

- name: Install Dancer perl package from a specific mirror
  community.general.cpanm:
    name: Dancer
    mirror: 'http://cpan.cpantesters.org/'

- name: Install Dancer perl package into the system root path
  become: true
  community.general.cpanm:
    name: Dancer

- name: Install Dancer if it is not already installed OR the installed version is older than version 1.0
  community.general.cpanm:
    name: Dancer
    version: '1.0'
"""

RETURN = r"""
cpanm_version:
  description: Version of CPANMinus.
  type: str
  returned: always
  sample: "1.7047"
  version_added: 10.0.0
"""


import os
import re

from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, cmd_runner_fmt
from ansible_collections.community.general.plugins.module_utils.module_helper import ModuleHelper


class CPANMinus(ModuleHelper):
    output_params = ['name', 'version']
    module = dict(
        argument_spec=dict(
            name=dict(type='str', aliases=['pkg']),
            version=dict(type='str'),
            from_path=dict(type='path'),
            notest=dict(type='bool', default=False),
            locallib=dict(type='path'),
            mirror=dict(type='str'),
            mirror_only=dict(type='bool', default=False),
            installdeps=dict(type='bool', default=False),
            install_recommendations=dict(type='bool'),
            install_suggestions=dict(type='bool'),
            executable=dict(type='path'),
            mode=dict(type='str', default='new', choices=['compatibility', 'new']),
            name_check=dict(type='str')
        ),
        required_one_of=[('name', 'from_path')],

    )
    command = 'cpanm'
    command_args_formats = dict(
        notest=cmd_runner_fmt.as_bool("--notest"),
        locallib=cmd_runner_fmt.as_opt_val('--local-lib'),
        mirror=cmd_runner_fmt.as_opt_val('--mirror'),
        mirror_only=cmd_runner_fmt.as_bool("--mirror-only"),
        installdeps=cmd_runner_fmt.as_bool("--installdeps"),
        install_recommendations=cmd_runner_fmt.as_bool("--with-recommends", "--without-recommends", ignore_none=True),
        install_suggestions=cmd_runner_fmt.as_bool("--with-suggests", "--without-suggests", ignore_none=True),
        pkg_spec=cmd_runner_fmt.as_list(),
        cpanm_version=cmd_runner_fmt.as_fixed("--version"),
    )

    def __init_module__(self):
        v = self.vars
        if v.mode == "compatibility":
            if v.name_check:
                self.do_raise("Parameter name_check can only be used with mode=new")
            self.deprecate("'mode=compatibility' is deprecated, use 'mode=new' instead", version='13.0.0', collection_name="community.general")
        else:
            if v.name and v.from_path:
                self.do_raise("Parameters 'name' and 'from_path' are mutually exclusive when 'mode=new'")

        self.command = v.executable if v.executable else self.command
        self.runner = CmdRunner(self.module, self.command, self.command_args_formats, check_rc=True)
        self.vars.binary = self.runner.binary

        with self.runner("cpanm_version") as ctx:
            rc, out, err = ctx.run()
            line = out.split('\n')[0]
            match = re.search(r"version\s+([\d\.]+)\s+", line)
            if not match:
                self.do_raise("Failed to determine version number. First line of output: {0}".format(line))
            self.vars.cpanm_version = match.group(1)

    def _is_package_installed(self, name, locallib, version):
        def process(rc, out, err):
            return rc == 0

        if name is None or name.endswith('.tar.gz'):
            return False
        version = "" if version is None else " " + version

        env = {"PERL5LIB": "%s/lib/perl5" % locallib} if locallib else {}
        runner = CmdRunner(self.module, ["perl", "-le"], {"mod": cmd_runner_fmt.as_list()}, check_rc=False, environ_update=env)
        with runner("mod", output_process=process) as ctx:
            return ctx.run(mod='use %s%s;' % (name, version))

    def sanitize_pkg_spec_version(self, pkg_spec, version):
        if version is None:
            return pkg_spec
        if pkg_spec.endswith('.tar.gz'):
            self.do_raise(msg="parameter 'version' must not be used when installing from a file")
        if os.path.isdir(pkg_spec):
            self.do_raise(msg="parameter 'version' must not be used when installing from a directory")
        if pkg_spec.endswith('.git'):
            if version.startswith('~'):
                self.do_raise(msg="operator '~' not allowed in version parameter when installing from git repository")
            version = version if version.startswith('@') else '@' + version
        elif version[0] not in ('@', '~'):
            version = '~' + version
        return pkg_spec + version

    def __run__(self):
        def process(rc, out, err):
            if self.vars.mode == "compatibility" and rc != 0:
                self.do_raise(msg=err, cmd=self.vars.cmd_args)
            return 'is up to date' not in err and 'is up to date' not in out

        v = self.vars
        pkg_param = 'from_path' if v.from_path else 'name'

        if v.mode == 'compatibility':
            if self._is_package_installed(v.name, v.locallib, v.version):
                return
            pkg_spec = v[pkg_param]
        else:
            installed = self._is_package_installed(v.name_check, v.locallib, v.version) if v.name_check else False
            if installed:
                return
            pkg_spec = self.sanitize_pkg_spec_version(v[pkg_param], v.version)

        with self.runner([
            'notest',
            'locallib',
            'mirror',
            'mirror_only',
            'installdeps',
            'install_recommendations',
            'install_suggestions',
            'pkg_spec'
        ], output_process=process) as ctx:
            self.changed = ctx.run(pkg_spec=pkg_spec)


def main():
    CPANMinus.execute()


if __name__ == '__main__':
    main()
