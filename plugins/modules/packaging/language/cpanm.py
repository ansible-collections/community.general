#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2012, Franck Cuny <franck@lumberjaph.net>
# Copyright (c) 2021, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: cpanm
short_description: Manages Perl library dependencies.
description:
  - Manage Perl library dependencies using cpanminus.
options:
  name:
    type: str
    description:
      - The Perl library to install. Valid values change according to the I(mode), see notes for more details.
      - Note that for installing from a local path the parameter I(from_path) should be used.
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
  version:
    description:
      - Version specification for the perl module. When I(mode) is C(new), C(cpanm) version operators are accepted.
    type: str
  executable:
    description:
      - Override the path to the cpanm executable.
    type: path
  mode:
    description:
      - Controls the module behavior. See notes below for more details.
    type: str
    choices: [compatibility, new]
    default: compatibility
    version_added: 3.0.0
  name_check:
    description:
      - When in C(new) mode, this parameter can be used to check if there is a module I(name) installed (at I(version), when specified).
    type: str
    version_added: 3.0.0
notes:
  - Please note that U(http://search.cpan.org/dist/App-cpanminus/bin/cpanm, cpanm) must be installed on the remote host.
  - "This module now comes with a choice of execution I(mode): C(compatibility) or C(new)."
  - "C(compatibility) mode:"
  - When using C(compatibility) mode, the module will keep backward compatibility. This is the default mode.
  - I(name) must be either a module name or a distribution file.
  - >
    If the perl module given by I(name) is installed (at the exact I(version) when specified), then nothing happens.
    Otherwise, it will be installed using the C(cpanm) executable.
  - I(name) cannot be an URL, or a git URL.
  - C(cpanm) version specifiers do not work in this mode.
  - "C(new) mode:"
  - "When using C(new) mode, the module will behave differently"
  - >
    The I(name) parameter may refer to a module name, a distribution file,
    a HTTP URL or a git repository URL as described in C(cpanminus) documentation.
  - C(cpanm) version specifiers are recognized.
author:
  - "Franck Cuny (@fcuny)"
  - "Alexei Znamensky (@russoz)"
'''

EXAMPLES = '''
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
'''

import os

from ansible_collections.community.general.plugins.module_utils.module_helper import (
    ModuleHelper, CmdMixin, ArgFormat
)


class CPANMinus(CmdMixin, ModuleHelper):
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
            executable=dict(type='path'),
            mode=dict(type='str', choices=['compatibility', 'new'], default='compatibility'),
            name_check=dict(type='str')
        ),
        required_one_of=[('name', 'from_path')],

    )
    command = 'cpanm'
    command_args_formats = dict(
        notest=dict(fmt="--notest", style=ArgFormat.BOOLEAN),
        locallib=dict(fmt=('--local-lib', '{0}'),),
        mirror=dict(fmt=('--mirror', '{0}'),),
        mirror_only=dict(fmt="--mirror-only", style=ArgFormat.BOOLEAN),
        installdeps=dict(fmt="--installdeps", style=ArgFormat.BOOLEAN),
    )
    check_rc = True

    def __init_module__(self):
        v = self.vars
        if v.mode == "compatibility":
            if v.name_check:
                self.do_raise("Parameter name_check can only be used with mode=new")
        else:
            if v.name and v.from_path:
                self.do_raise("Parameters 'name' and 'from_path' are mutually exclusive when 'mode=new'")

        self.command = self.module.get_bin_path(v.executable if v.executable else self.command)
        self.vars.set("binary", self.command)

    def _is_package_installed(self, name, locallib, version):
        if name is None or name.endswith('.tar.gz'):
            return False
        version = "" if version is None else " " + version

        env = {"PERL5LIB": "%s/lib/perl5" % locallib} if locallib else {}
        cmd = ['perl', '-le', 'use %s%s;' % (name, version)]
        rc, out, err = self.module.run_command(cmd, check_rc=False, environ_update=env)

        return rc == 0

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
        v = self.vars
        pkg_param = 'from_path' if v.from_path else 'name'

        if v.mode == 'compatibility':
            if self._is_package_installed(v.name, v.locallib, v.version):
                return
            pkg_spec = v[pkg_param]
            self.changed = self.run_command(
                params=['notest', 'locallib', 'mirror', 'mirror_only', 'installdeps', {'name': pkg_spec}],
            )
        else:
            installed = self._is_package_installed(v.name_check, v.locallib, v.version) if v.name_check else False
            if installed:
                return
            pkg_spec = self.sanitize_pkg_spec_version(v[pkg_param], v.version)
            self.changed = self.run_command(
                params=['notest', 'locallib', 'mirror', 'mirror_only', 'installdeps', {'name': pkg_spec}],
            )

    def process_command_output(self, rc, out, err):
        if self.vars.mode == "compatibility" and rc != 0:
            self.do_raise(msg=err, cmd=self.vars.cmd_args)
        return 'is up to date' not in err and 'is up to date' not in out


def main():
    CPANMinus.execute()


if __name__ == '__main__':
    main()
