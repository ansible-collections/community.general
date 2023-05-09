#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2023, Jonathan Kamens <jik@kamens.us>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# pylint: disable=missing-module-docstring

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: perlmod_install_info

short_description: Determine from where to install Perl modules

requirements:
    - C(apt-file) executable in search path on systems that use the apt package
      manager
    - C(dnf) or C(yum) executable in search path on systems that use the
      dnf/yum package manager
    - C(cpanm) executable in search path if you want to be able to search for
      packages using cpanm

version_added: "7.0.0"

description:
    - Searches dnf, yum, apt, and/or cpanm to determine the best source from
      which to install a Perl module.
    - Prefers the OS repositories over cpanm. Only returns modules from CPAN
      when it is searchable (I(try_cpan) is C(auto) or C(true) and the C(cpanm)
      executable is available) and the returned modules were not found
      in any other source.
    - Specify module names as you would specify them with the C(use) command in
      a Perl script.
    - Does not actually install modules. Instead, returns information about
      where they can be installed from, which can be supplied to subsequent
      tasks to do the actual installation.
    - Note that this module will not fail by default if it cannot locate a
      requested module. If you want that behavior, include a C(failed_when)
      which checks for C(missing) being defined as shown in the examples.

options:
    name:
        description: Specify one or more Perl modules to search for.
        required: true
        type: list
        elements: str
    try_installed:
        description: Specify whether to check if modules are already installed
          and not look elsewhere if they are.
        type: bool
        default: true
    try_dnf:
        description: Specify whether to check for modules using the dnf package
          manager. Defaults to C(true) if C(dnf) executable is available.
        type: str
        choices:
        - 'auto'
        - 'true'
        - 'false'
        default: 'auto'
    try_yum:
        description: Specify whether to check for modules using the dnf package
          manager. Defaults to C(true) if I(try_dnf=false) and C(yum) executable
          is available.
        type: str
        choices:
        - 'auto'
        - 'true'
        - 'false'
        default: 'auto'
    try_apt:
        description: Specify whether to check for modules using the apt package
          manager. Defaults to C(true) if C(apt-file) executable is available.
        type: str
        choices:
        - 'auto'
        - 'true'
        - 'false'
        default: 'auto'
    try_cpanm:
        description: Specify whether to check for modules using cpanm. Defaults
          to C(true) if C(cpanm) executable is available.
        type: str
        choices:
        - 'auto'
        - 'true'
        - 'false'
        default: 'auto'
    update:
        description: Specify whether to update package manager databases before
          searching.
        type: bool
        default: false

extends_documentation_fragment:
    - community.general.attributes
    - community.general.attributes.info_module

author:
    - Jonathan Kamens (@jikamens)
'''

EXAMPLES = r'''
# Search and fail if the package can't be found
- name: Search for Net::DNS if it is not already installed
  community.general.perlmod_install_info:
    name: Net::DNS
  register: perlmod_info
  failed_when: perlmod_info.missing is defined

- name: Search for two modules, even if they are already installed
  community.general.perlmod_install_info:
    name:
    - URI
    - WWW::Mechanize
  try_installed: false
  register: perlmod_info

- name: install dnf packages identified by perlmod_install_info
  dnf:
    name: "{{perlmod_info.dnf}}"
  when: perlmod_info.dnf is defined

- name: install yum packages identified by perlmod_install_info
  yum:
    name: "{{perlmod_info.yum}}"
  when: perlmod_info.yum is defined

- name: install yum packages identified by perlmod_install_info
  apt:
    name: "{{perlmod_info.apt}}"
  when: perlmod_info.apt is defined

- name: install cpanm packages identified by perlmod_install_info
  cpanm:
    name: "{{item}}"
  with_items: "{{perlmod_info.cpanm}}"
  when: perlmod_info.cpanm is defined
'''

RETURN = r'''
installed:
    description: List of modules that are already installed.
    type: list
    elements: str
    returned: when I(try_installed) is C(true) and installed modules were found
    sample: ['Net::DNS']
dnf:
    description:
      - List of dnf requirements that should be installed to provide at least
        some of the required Perl modules.
      - This value is returned when I(try_dnf) is C(true), or C(auto) and dnf
        is available, and at least some of the requested modules were found in
        dnf.
    type: list
    elements: str
    returned: when some of the requested modules were found in dnf
    sample: ['perl(Net::DNS)']
yum:
    description:
      - List of yum requirements that should be installed to provide at least
        some of the required Perl modules.
      - This value is returned when I(try_yum) is C(true), or C(auto) and yum
        is available, and at least some of the requested modules were found in
        yum.
    type: list
    elements: str
    returned: when some of the requested modules were found in yum
    sample: ['perl(Net::DNS)']
apt:
    description:
      - List of apt requirements that should be installed to provide at least
        some of the required Perl modules.
      - This value is returned when I(try_apt) is C(true), or C(auto) and apt
        is available, and at least some of the requested modules were found in
        apt.
    type: list
    elements: str
    returned: when some of the requested modules were found in apt
    sample: ['libnet-dns-perl']
cpanm:
    description:
      - List of modules that should be installed from CPAN to provide at least
        some of the required Perl modules.
      - This value is returned when I(try_cpanm) is C(true), or C(auto) and
        C(cpanm) is available, and at least some of the requested modules were
        found in CPAN.
      - OS repositories are preferred over CPAN, so a module is only returned
        here if it isn't in any of other options that were searched.
    type: list
    elements: str
    returned: when requested modules were found in CPAN
    sample: ['Net::DNS']
missing:
    description: List of Perl modules that could not be found.
    type: list
    elements: str
    returned: when there are missing modules
    sample: ['No::Such::Module']
'''

import re
import shutil
import tempfile

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.parsing.convert_bool import boolean


def check_installed(amodule, perlmod):
    """Returns True if perl can import the specified module."""
    (rc, dummy, dummy) = amodule.run_command(
        ["perl", "-e", "use %s" % (perlmod,)])
    return rc == 0


def dnf_or_yum(amodule, which_cmd, update, modules):
    """Returns two sets: dnf/yum found modules and the packages they're in."""
    want = ["perl(%s)" % (module,) for module in modules]
    cmd = [which_cmd]
    if update:
        cmd.append('--refresh')
    cmd.append('whatprovides')
    cmd.extend(want)
    (dummy, stdout, dummy) = amodule.run_command(cmd)
    packages = set()
    for line in stdout.split('\n'):
        line = re.split(r'\s+', line)
        # Provide : perl(module) = version is output format
        if len(line) > 2 and line[0] == 'Provide' and line[1] == ':' and \
           line[2] not in packages:
            packages.add(line[2])
    found = set(package[5:-1] for package in packages)
    return (found, packages)


def apt(amodule, update, modules):
    """Returns two sets: apt found modules and the packages they're in."""
    # Update database if requested
    if update:
        amodule.run_command(['apt-file', 'update'])

    # Get list of include paths from perl
    (dummy, stdout, dummy) = amodule.run_command(['perl', '-V'])
    in_inc = False
    perlpath = []
    for line in (r.strip() for r in stdout.split('\n')):
        if line == '@INC:':
            in_inc = True
            continue
        if not in_inc:
            continue
        if line.startswith('/'):
            perlpath.append(line)
            continue
        break

    found = set()
    packages = set()
    for name in modules:
        # Convert module name into tail end of a module path
        tail = '/' + name.replace('::', '/') + '.pm'
        # Search for it with apt-file
        (dummy, stdout, dummy) = amodule.run_command(
            ['apt-file', 'search', tail])
        for line in stdout.split('\n'):
            # package: path is output format
            match = re.match(r'^([^:]+): (/.*)', line)
            if not match:
                continue
            package = match.group(1)
            path = match.group(2)
            # Does the path end with our module path (eliminate accidental
            # matches in the middle of the path)
            if not path.endswith(tail):
                continue
            directory = path[:-len(tail)]
            if directory not in perlpath:
                continue
            # Eureka
            found.add(name)
            packages.add(package)
    return (found, packages)


def cpanm(amodule, modules):
    """Returns 2 sets: CPANM modules found and their recursive dependencies."""
    found = set()
    dependencies = set()
    for module in modules:
        # It would be better to use TemporaryDirectory rather htan mkdtemp,
        # but it's not supported in Python 2.7, which Ansible still needs to
        # support.
        tempdir = tempfile.mkdtemp()
        try:
            (rc, stdout, dummy) = amodule.run_command(
                ['cpanm', '--local-lib-contained',
                 tempdir, '--scandeps', module])
        finally:
            shutil.rmtree(tempdir, ignore_errors=True)
        if rc != 0:
            continue
        found.add(module)
        for line in stdout.split('\n'):
            match = re.search(r'Found dependencies: (.*)', line)
            if not match:
                continue
            dependencies |= set(m for m in match.group(1).split(', ')
                                if m not in modules)
    return (found, dependencies)


def find_modules(amodule, result, errors, names=None, update=None):
    """Stores results in `result`, returns set of missing modules."""
    params = amodule.params
    names = set(params['name'] if names is None else names)
    update = params['update'] if update is None else update

    try_installed = params['try_installed']
    try_dnf = amodule.get_bin_path('dnf') is not None \
        if params['try_dnf'] == 'auto' else boolean(params['try_dnf'])
    if not try_dnf:
        try_yum = amodule.get_bin_path('yum') is not None \
            if params['try_yum'] == 'auto' else boolean(params['try_yum'])
    try_apt = amodule.get_bin_path('apt-file') is not None \
        if params['try_apt'] == 'auto' else boolean(params['try_apt'])
    try_cpanm = amodule.get_bin_path('cpanm') is not None \
        if params['try_cpanm'] == 'auto' else boolean(params['try_cpanm'])

    found = set()

    if names and try_installed:
        this_found = set(n for n in names if check_installed(amodule, n))
        result['installed'] = result.get('installed', set()) | this_found
        found |= this_found
        names -= this_found

    if names and (try_dnf or try_yum):
        which_cmd = 'dnf' if try_dnf else 'yum'
        (this_found, packages) = dnf_or_yum(amodule, which_cmd, update, names)
        result[which_cmd] = result.get(which_cmd, set()) | packages
        found |= this_found
        names -= this_found

    if names and try_apt:
        (this_found, packages) = apt(amodule, update, names)
        result['apt'] = result.get('apt', set()) | packages
        found |= this_found
        names -= this_found

    if names and try_cpanm:
        (this_found, dependencies) = cpanm(amodule, names)
        result['cpanm'] = result.get('cpanm', set()) | this_found
        found |= this_found
        names -= this_found
        dependencies -= found
        names |= find_modules(amodule, result, errors, names=dependencies,
                              update=False)

    return names


def run_module():
    """Does all the work."""
    module_args = dict(
        name=dict(type='list', elements='str', required=True),
        try_installed=dict(type='bool', required=False, default=True),
        try_dnf=dict(type='str', required=False, default='auto',
                     choices=['auto', 'true', 'false']),
        try_yum=dict(type='str', required=False, default='auto',
                     choices=['auto', 'true', 'false']),
        try_apt=dict(type='str', required=False, default='auto',
                     choices=['auto', 'true', 'false']),
        try_cpanm=dict(type='str', required=False, default='auto',
                       choices=['auto', 'true', 'false']),
        update=dict(type='bool', required=False, default=False),
    )

    result = dict(
        changed=False,
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    errors = []
    missing = find_modules(module, result, errors)
    if missing:
        result['missing'] = missing

    if errors:
        module.fail_json(msg='\n'.join(errors))

    module.exit_json(**result)


def main():
    """Main entry point when called as script."""
    run_module()


if __name__ == '__main__':
    main()
