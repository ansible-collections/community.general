#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, William L Thomson Jr
# Copyright (c) 2013, Yap Sok Ann
# Written by Yap Sok Ann <sokann@gmail.com>
# Modified by William L. Thomson Jr. <wlt@o-sinc.com>
# Based on apt module written by Matthew Williams <matthew@flowroute.com>
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: portage
short_description: Package manager for Gentoo
description:
  - Manages Gentoo packages

options:
  package:
    description:
      - Package atom or set, e.g. C(sys-apps/foo) or C(>foo-2.13) or C(@world)
    aliases: [name]
    type: list
    elements: str

  state:
    description:
      - State of the package atom
    default: "present"
    choices: [ "present", "installed", "emerged", "absent", "removed", "unmerged", "latest" ]
    type: str

  update:
    description:
      - Update packages to the best version available (--update)
    type: bool
    default: false

  backtrack:
    description:
      - Set backtrack value (C(--backtrack)).
    type: int
    version_added: 5.8.0

  deep:
    description:
      - Consider the entire dependency tree of packages (--deep)
    type: bool
    default: false

  newuse:
    description:
      - Include installed packages where USE flags have changed (--newuse)
    type: bool
    default: false

  changed_use:
    description:
      - Include installed packages where USE flags have changed, except when
      - flags that the user has not enabled are added or removed
      - (--changed-use)
    type: bool
    default: false

  oneshot:
    description:
      - Do not add the packages to the world file (--oneshot)
    type: bool
    default: false

  noreplace:
    description:
      - Do not re-emerge installed packages (--noreplace)
    type: bool
    default: true

  nodeps:
    description:
      - Only merge packages but not their dependencies (--nodeps)
    type: bool
    default: false

  onlydeps:
    description:
      - Only merge packages' dependencies but not the packages (--onlydeps)
    type: bool
    default: false

  depclean:
    description:
      - Remove packages not needed by explicitly merged packages (--depclean)
      - If no package is specified, clean up the world's dependencies
      - Otherwise, --depclean serves as a dependency aware version of --unmerge
    type: bool
    default: false

  quiet:
    description:
      - Run emerge in quiet mode (--quiet)
    type: bool
    default: false

  verbose:
    description:
      - Run emerge in verbose mode (--verbose)
    type: bool
    default: false

  sync:
    description:
      - Sync package repositories first
      - If C(yes), perform "emerge --sync"
      - If C(web), perform "emerge-webrsync"
    choices: [ "web", "yes", "no" ]
    type: str

  getbinpkgonly:
    description:
      - Merge only packages specified at C(PORTAGE_BINHOST) in C(make.conf).
    type: bool
    default: false
    version_added: 1.3.0

  getbinpkg:
    description:
      - Prefer packages specified at C(PORTAGE_BINHOST) in C(make.conf).
    type: bool
    default: false

  usepkgonly:
    description:
      - Merge only binaries (no compiling).
    type: bool
    default: false

  usepkg:
    description:
      - Tries to use the binary package(s) in the locally available packages directory.
    type: bool
    default: false

  keepgoing:
    description:
      - Continue as much as possible after an error.
    type: bool
    default: false

  jobs:
    description:
      - Specifies the number of packages to build simultaneously.
      - "Since version 2.6: Value of 0 or False resets any previously added"
      - --jobs setting values
    type: int

  loadavg:
    description:
      - Specifies that no new builds should be started if there are
      - other builds running and the load average is at least LOAD
      - "Since version 2.6: Value of 0 or False resets any previously added"
      - --load-average setting values
    type: float

  withbdeps:
    description:
      - Specifies that build time dependencies should be installed.
    type: bool
    version_added: 5.8.0

  quietbuild:
    description:
      - Redirect all build output to logs alone, and do not display it
      - on stdout (--quiet-build)
    type: bool
    default: false

  quietfail:
    description:
      - Suppresses display of the build log on stdout (--quiet-fail)
      - Only the die message and the path of the build log will be
      - displayed on stdout.
    type: bool
    default: false

author:
    - "William L Thomson Jr (@wltjr)"
    - "Yap Sok Ann (@sayap)"
    - "Andrew Udvare (@Tatsh)"
'''

EXAMPLES = '''
- name: Make sure package foo is installed
  community.general.portage:
    package: foo
    state: present

- name: Make sure package foo is not installed
  community.general.portage:
    package: foo
    state: absent

- name: Update package foo to the latest version (os specific alternative to latest)
  community.general.portage:
    package: foo
    update: true

- name: Install package foo using PORTAGE_BINHOST setup
  community.general.portage:
    package: foo
    getbinpkg: true

- name: Re-install world from binary packages only and do not allow any compiling
  community.general.portage:
    package: '@world'
    usepkgonly: true

- name: Sync repositories and update world
  community.general.portage:
    package: '@world'
    update: true
    deep: true
    sync: true

- name: Remove unneeded packages
  community.general.portage:
    depclean: true

- name: Remove package foo if it is not explicitly needed
  community.general.portage:
    package: foo
    state: absent
    depclean: true
'''

import os
import re
import sys
import traceback

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.respawn import has_respawned, respawn_module
from ansible.module_utils.common.text.converters import to_native


try:
    from portage.dbapi import vartree
    from portage.exception import InvalidAtom
    HAS_PORTAGE = True
    PORTAGE_IMPORT_ERROR = None
except ImportError:
    HAS_PORTAGE = False
    PORTAGE_IMPORT_ERROR = traceback.format_exc()


def query_package(module, package, action):
    if package.startswith('@'):
        return query_set(module, package, action)
    return query_atom(module, package, action)


def query_atom(module, atom, action):
    vdb = vartree.vardbapi()
    try:
        exists = vdb.match(atom)
    except InvalidAtom:
        return False
    return bool(exists)


def query_set(module, set, action):
    system_sets = [
        '@live-rebuild',
        '@module-rebuild',
        '@preserved-rebuild',
        '@security',
        '@selected',
        '@system',
        '@world',
        '@x11-module-rebuild',
    ]

    if set in system_sets:
        if action == 'unmerge':
            module.fail_json(msg='set %s cannot be removed' % set)
        return False

    world_sets_path = '/var/lib/portage/world_sets'
    if not os.path.exists(world_sets_path):
        return False

    cmd = 'grep %s %s' % (set, world_sets_path)

    rc, out, err = module.run_command(cmd)
    return rc == 0


def sync_repositories(module, webrsync=False):
    if module.check_mode:
        module.exit_json(msg='check mode not supported by sync')

    if webrsync:
        webrsync_path = module.get_bin_path('emerge-webrsync', required=True)
        cmd = '%s --quiet' % webrsync_path
    else:
        cmd = '%s --sync --quiet --ask=n' % module.emerge_path

    rc, out, err = module.run_command(cmd)
    if rc != 0:
        module.fail_json(msg='could not sync package repositories')


# Note: In the 3 functions below, package querying is done one-by-one,
# but emerge is done in one go. If that is not desirable, split the
# packages into multiple tasks instead of joining them together with
# comma.


def emerge_packages(module, packages):
    """Run emerge command against given list of atoms."""
    p = module.params

    if p['noreplace'] and not (p['update'] or p['state'] == 'latest'):
        for package in packages:
            if p['noreplace'] and not query_package(module, package, 'emerge'):
                break
        else:
            module.exit_json(changed=False, msg='Packages already present.')
        if module.check_mode:
            module.exit_json(changed=True, msg='Packages would be installed.')

    args = []
    emerge_flags = {
        'update': '--update',
        'deep': '--deep',
        'newuse': '--newuse',
        'changed_use': '--changed-use',
        'oneshot': '--oneshot',
        'noreplace': '--noreplace',
        'nodeps': '--nodeps',
        'onlydeps': '--onlydeps',
        'quiet': '--quiet',
        'verbose': '--verbose',
        'getbinpkgonly': '--getbinpkgonly',
        'getbinpkg': '--getbinpkg',
        'usepkgonly': '--usepkgonly',
        'usepkg': '--usepkg',
        'keepgoing': '--keep-going',
        'quietbuild': '--quiet-build',
        'quietfail': '--quiet-fail',
    }
    for flag, arg in emerge_flags.items():
        if p[flag]:
            args.append(arg)

    if p['state'] and p['state'] == 'latest':
        args.append("--update")

    emerge_flags = {
        'jobs': '--jobs',
        'loadavg': '--load-average',
        'backtrack': '--backtrack',
        'withbdeps': '--with-bdeps',
    }

    for flag, arg in emerge_flags.items():
        flag_val = p[flag]

        if flag_val is None:
            """Fallback to default: don't use this argument at all."""
            continue

        if not flag_val:
            """If the value is 0 or 0.0: add the flag, but not the value."""
            args.append(arg)
            continue

        """Add the --flag=value pair."""
        if isinstance(p[flag], bool):
            args.extend((arg, to_native('y' if flag_val else 'n')))
        else:
            args.extend((arg, to_native(flag_val)))

    cmd, (rc, out, err) = run_emerge(module, packages, *args)
    if rc != 0:
        module.fail_json(
            cmd=cmd, rc=rc, stdout=out, stderr=err,
            msg='Packages not installed.',
        )

    # Check for SSH error with PORTAGE_BINHOST, since rc is still 0 despite
    #   this error
    if (p['usepkgonly'] or p['getbinpkg'] or p['getbinpkgonly']) \
            and 'Permission denied (publickey).' in err:
        module.fail_json(
            cmd=cmd, rc=rc, stdout=out, stderr=err,
            msg='Please check your PORTAGE_BINHOST configuration in make.conf '
                'and your SSH authorized_keys file',
        )

    changed = True
    for line in out.splitlines():
        if re.match(r'(?:>+) Emerging (?:binary )?\(1 of', line):
            msg = 'Packages installed.'
            break
        elif module.check_mode and re.match(r'\[(binary|ebuild)', line):
            msg = 'Packages would be installed.'
            break
    else:
        changed = False
        msg = 'No packages installed.'

    module.exit_json(
        changed=changed, cmd=cmd, rc=rc, stdout=out, stderr=err,
        msg=msg,
    )


def unmerge_packages(module, packages):
    p = module.params

    for package in packages:
        if query_package(module, package, 'unmerge'):
            break
    else:
        module.exit_json(changed=False, msg='Packages already absent.')

    args = ['--unmerge']

    for flag in ['quiet', 'verbose']:
        if p[flag]:
            args.append('--%s' % flag)

    cmd, (rc, out, err) = run_emerge(module, packages, *args)

    if rc != 0:
        module.fail_json(
            cmd=cmd, rc=rc, stdout=out, stderr=err,
            msg='Packages not removed.',
        )

    module.exit_json(
        changed=True, cmd=cmd, rc=rc, stdout=out, stderr=err,
        msg='Packages removed.',
    )


def cleanup_packages(module, packages):
    p = module.params

    if packages:
        for package in packages:
            if query_package(module, package, 'unmerge'):
                break
        else:
            module.exit_json(changed=False, msg='Packages already absent.')

    args = ['--depclean']

    for flag in ['quiet', 'verbose']:
        if p[flag]:
            args.append('--%s' % flag)

    cmd, (rc, out, err) = run_emerge(module, packages, *args)
    if rc != 0:
        module.fail_json(cmd=cmd, rc=rc, stdout=out, stderr=err)

    removed = 0
    for line in out.splitlines():
        if not line.startswith('Number removed:'):
            continue
        parts = line.split(':')
        removed = int(parts[1].strip())
    changed = removed > 0

    module.exit_json(
        changed=changed, cmd=cmd, rc=rc, stdout=out, stderr=err,
        msg='Depclean completed.',
    )


def run_emerge(module, packages, *args):
    args = list(args)

    args.append('--ask=n')
    if module.check_mode:
        args.append('--pretend')

    cmd = [module.emerge_path] + args + packages
    return cmd, module.run_command(cmd)


portage_present_states = ['present', 'emerged', 'installed', 'latest']
portage_absent_states = ['absent', 'unmerged', 'removed']


def main():
    module = AnsibleModule(
        argument_spec=dict(
            package=dict(type='list', elements='str', default=None, aliases=['name']),
            state=dict(
                default=portage_present_states[0],
                choices=portage_present_states + portage_absent_states,
            ),
            update=dict(default=False, type='bool'),
            backtrack=dict(default=None, type='int'),
            deep=dict(default=False, type='bool'),
            newuse=dict(default=False, type='bool'),
            changed_use=dict(default=False, type='bool'),
            oneshot=dict(default=False, type='bool'),
            noreplace=dict(default=True, type='bool'),
            nodeps=dict(default=False, type='bool'),
            onlydeps=dict(default=False, type='bool'),
            depclean=dict(default=False, type='bool'),
            quiet=dict(default=False, type='bool'),
            verbose=dict(default=False, type='bool'),
            sync=dict(default=None, choices=['yes', 'web', 'no']),
            getbinpkgonly=dict(default=False, type='bool'),
            getbinpkg=dict(default=False, type='bool'),
            usepkgonly=dict(default=False, type='bool'),
            usepkg=dict(default=False, type='bool'),
            keepgoing=dict(default=False, type='bool'),
            jobs=dict(default=None, type='int'),
            loadavg=dict(default=None, type='float'),
            withbdeps=dict(default=None, type='bool'),
            quietbuild=dict(default=False, type='bool'),
            quietfail=dict(default=False, type='bool'),
        ),
        required_one_of=[['package', 'sync', 'depclean']],
        mutually_exclusive=[
            ['nodeps', 'onlydeps'],
            ['quiet', 'verbose'],
            ['quietbuild', 'verbose'],
            ['quietfail', 'verbose'],
        ],
        supports_check_mode=True,
    )

    if not HAS_PORTAGE:
        if sys.executable != '/usr/bin/python' and not has_respawned():
            respawn_module('/usr/bin/python')
        else:
            module.fail_json(msg=missing_required_lib('portage'),
                             exception=PORTAGE_IMPORT_ERROR)

    module.emerge_path = module.get_bin_path('emerge', required=True)

    p = module.params

    if p['sync'] and p['sync'].strip() != 'no':
        sync_repositories(module, webrsync=(p['sync'] == 'web'))
        if not p['package']:
            module.exit_json(msg='Sync successfully finished.')

    packages = []
    if p['package']:
        packages.extend(p['package'])

    if p['depclean']:
        if packages and p['state'] not in portage_absent_states:
            module.fail_json(
                msg='Depclean can only be used with package when the state is '
                    'one of: %s' % portage_absent_states,
            )

        cleanup_packages(module, packages)

    elif p['state'] in portage_present_states:
        emerge_packages(module, packages)

    elif p['state'] in portage_absent_states:
        unmerge_packages(module, packages)


if __name__ == '__main__':
    main()
