#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2012, Franck Cuny <franck@lumberjaph.net>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

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
      - The name of the Perl library to install. You may use the "full distribution path", e.g. C(MIYAGAWA/Plack-0.99_05.tar.gz).
    aliases: [pkg, from_url]
  from_path:
    type: path
    description:
      - The local directory from where to install
    aliases: [from_dir]
  notest:
    description:
      - Do not run unit tests
    type: bool
    default: no
  locallib:
    description:
      - Specify the install base to install modules
    type: path
  mirror:
    description:
      - Specifies the base URL for the CPAN mirror to use
    type: str
  mirror_only:
    description:
      - Use the mirror's index file instead of the CPAN Meta DB
    type: bool
    default: no
  installdeps:
    description:
      - Only install dependencies
    type: bool
    default: no
  version:
    description:
      - minimum version of perl module to consider acceptable
    type: str
  system_lib:
    description:
      - Use this if you want to install modules to the system perl include path. You must be root or have "passwordless" sudo for this to work.
      - This uses the cpanm commandline option C(--sudo), which has nothing to do with ansible privilege escalation.
      - >
        This option is not recommended for use and it will be deprecated in the future. If you need to escalate privileges
        please consider using any of the multiple mechanisms available in Ansible.
    type: bool
    default: no
    aliases: ['use_sudo']
  executable:
    description:
      - Override the path to the cpanm executable
    type: path
notes:
  - Please note that U(http://search.cpan.org/dist/App-cpanminus/bin/cpanm, cpanm) must be installed on the remote host.
author: "Franck Cuny (@fcuny)"
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
    notest: True
    locallib: /srv/webapps/my_app/extlib

- name: Install Dancer perl package from a specific mirror
  community.general.cpanm:
    name: Dancer
    mirror: 'http://cpan.cpantesters.org/'

- name: Install Dancer perl package into the system root path
  community.general.cpanm:
    name: Dancer
    system_lib: yes

- name: Install Dancer if it is not already installed OR the installed version is older than version 1.0
  community.general.cpanm:
    name: Dancer
    version: '1.0'
'''

import os

from ansible_collections.community.general.plugins.module_utils.module_helper import (
    ModuleHelper, CmdMixin, ArgFormat, ModuleHelperException
)


class CPANMinus(CmdMixin, ModuleHelper):
    module = dict(
        argument_spec=dict(
            name=dict(type='str', aliases=['pkg', 'from_url']),
            version=dict(type='str'),
            from_path=dict(type='path', aliases=['from_dir']),
            notest=dict(default=False, type='bool'),
            locallib=dict(type='path'),
            mirror=dict(type='str'),
            mirror_only=dict(default=False, type='bool'),
            installdeps=dict(type='bool', default=False),
            system_lib=dict(type='bool', default=False, aliases=['use_sudo']),
            executable=dict(type='path'),
        ),
        required_one_of=[('name', 'from_path')],
        mutually_exclusive=[('name', 'from_path'), ('from_path', 'version')],
    )
    command = 'cpanm'
    command_args_formats = dict(
        notest=dict(fmt="--notest", style=ArgFormat.BOOLEAN),
        locallib=dict(fmt=('--local-lib', '{0}'),),
        mirror=dict(fmt=('--mirror', '{0}'),),
        mirror_only=dict(fmt="--mirror-only", style=ArgFormat.BOOLEAN),
        installdeps=dict(fmt="--installdeps", style=ArgFormat.BOOLEAN),
        system_lib=dict(fmt="--sudo", style=ArgFormat.BOOLEAN),
    )
    check_rc = True

    def sanitize_pkg_spec_version(self, pkg_spec):
        v = self.module.params['version']
        if v is None:
            return pkg_spec
        if pkg_spec.endswith('.tar.gz'):
            raise ModuleHelperException(msg="parameter 'version' must not be used when installing from a file")
        if os.path.isdir(pkg_spec):
            raise ModuleHelperException(msg="parameter 'version' must not be used when installing from a directory")
        if pkg_spec.endswith('.git'):
            if v.startswith('~'):
                raise ModuleHelperException(msg="operator '~' not allowed in version parameter when installing from git repository")
            v = v if v.startswith('@') else '@' + v
        elif v[0] not in ('@', '~'):
            v = '~' + v
        return pkg_spec + v

    def __run__(self):
        p = self.module.params

        if p['executable']:
            self.command = p['executable']
        self.vars.binary = self.command
        self.vars.name = p['name']

        pkg_param = 'from_path' if p['from_path'] else 'name'
        pkg_spec = self.sanitize_pkg_spec_version(p[pkg_param])

        self.run_command(params=['notest', 'locallib', 'mirror', 'mirror_only', 'installdeps', 'system_lib', {'name': pkg_spec}])

    def process_command_output(self, rc, out, err):
        self.changed = 'is up to date' not in err and 'is up to date' not in out


def main():
    cpanm = CPANMinus()
    cpanm.run()


if __name__ == '__main__':
    main()
