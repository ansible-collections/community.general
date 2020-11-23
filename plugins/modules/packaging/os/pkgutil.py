#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2013, Alexander Winkler <mail () winkler-alexander.de>
# based on svr4pkg by
#  Boyd Adamson <boyd () boydadamson.com> (2012)
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: pkgutil
short_description: OpenCSW package management on Solaris
description:
- This module installs, updates and removes packages from the OpenCSW project for Solaris.
- Unlike the M(community.general.svr4pkg) module, it will resolve and download dependencies.
- See U(https://www.opencsw.org/) for more information about the project.
author:
- Alexander Winkler (@dermute)
- David Ponessa (@scathatheworm)
options:
  name:
    description:
    - The name of the package.
    - When using C(state=latest), this can be C('*'), which updates all installed packages managed by pkgutil.
    type: list
    required: true
    elements: str
    aliases: [ pkg ]
  site:
    description:
    - The repository path to install the package from.
    - Its global definition is in C(/etc/opt/csw/pkgutil.conf).
    required: false
    type: str
  state:
    description:
    - Whether to install (C(present)/C(installed)), or remove (C(absent)/C(removed)) packages.
    - The upgrade (C(latest)) operation will update/install the packages to the latest version available.
    type: str
    required: true
    choices: [ absent, installed, latest, present, removed ]
  update_catalog:
    description:
    - If you always want to refresh your catalog from the mirror, even when it's not stale, set this to C(yes).
    type: bool
    default: no
  force:
    description:
    - To allow the update process to downgrade packages to match what is present in the repository, set this to C(yes).
    - This is useful for rolling back to stable from testing, or similar operations.
    type: bool
    default: false
    version_added: 1.2.0
notes:
- In order to check the availability of packages, the catalog cache under C(/var/opt/csw/pkgutil) may be refreshed even in check mode.
'''

EXAMPLES = r'''
- name: Install a package
  community.general.pkgutil:
    name: CSWcommon
    state: present

- name: Install a package from a specific repository
  community.general.pkgutil:
    name: CSWnrpe
    site: ftp://myinternal.repo/opencsw/kiel
    state: latest

- name: Remove a package
  community.general.pkgutil:
    name: CSWtop
    state: absent

- name: Install several packages
  community.general.pkgutil:
    name:
    - CSWsudo
    - CSWtop
    state: present

- name: Update all packages
  community.general.pkgutil:
    name: '*'
    state: latest

- name: Update all packages and force versions to match latest in catalog
  community.general.pkgutil:
    name: '*'
    state: latest
    force: yes
'''

RETURN = r''' # '''

from ansible.module_utils.basic import AnsibleModule


def packages_not_installed(module, names):
    ''' Check if each package is installed and return list of the ones absent '''
    pkgs = []
    for pkg in names:
        rc, out, err = run_command(module, ['pkginfo', '-q', pkg])
        if rc != 0:
            pkgs.append(pkg)
    return pkgs


def packages_installed(module, names):
    ''' Check if each package is installed and return list of the ones present '''
    pkgs = []
    for pkg in names:
        if not pkg.startswith('CSW'):
            continue
        rc, out, err = run_command(module, ['pkginfo', '-q', pkg])
        if rc == 0:
            pkgs.append(pkg)
    return pkgs


def packages_not_latest(module, names, site, update_catalog):
    ''' Check status of each package and return list of the ones with an upgrade available '''
    cmd = ['pkgutil']
    if update_catalog:
        cmd.append('-U')
    cmd.append('-c')
    if site is not None:
        cmd.extend('-t', site)
    if names != ['*']:
        cmd.extend(names)
    rc, out, err = run_command(module, cmd)

    # Find packages in the catalog which are not up to date
    packages = []
    for line in out.split('\n')[1:-1]:
        if 'catalog' not in line and 'SAME' not in line:
            packages.append(line.split(' ')[0])

    # Remove duplicates
    return list(set(packages))


def run_command(module, cmd, **kwargs):
    progname = cmd[0]
    cmd[0] = module.get_bin_path(progname, True, ['/opt/csw/bin'])
    return module.run_command(cmd, **kwargs)


def package_install(module, state, pkgs, site, update_catalog, force):
    cmd = ['pkgutil']
    if module.check_mode:
        cmd.append('-n')
    cmd.append('-iy')
    if update_catalog:
        cmd.append('-U')
    if site is not None:
        cmd.extend('-t', site)
    if force:
        cmd.append('-f')
    cmd.extend(pkgs)
    return run_command(module, cmd)


def package_upgrade(module, pkgs, site, update_catalog, force):
    cmd = ['pkgutil']
    if module.check_mode:
        cmd.append('-n')
    cmd.append('-uy')
    if update_catalog:
        cmd.append('-U')
    if site is not None:
        cmd.extend('-t', site)
    if force:
        cmd.append('-f')
    cmd += pkgs
    return run_command(module, cmd)


def package_uninstall(module, pkgs):
    cmd = ['pkgutil']
    if module.check_mode:
        cmd.append('-n')
    cmd.append('-ry')
    cmd.extend(pkgs)
    return run_command(module, cmd)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='list', elements='str', required=True, aliases=['pkg']),
            state=dict(type='str', required=True, choices=['absent', 'installed', 'latest', 'present', 'removed']),
            site=dict(type='str'),
            update_catalog=dict(type='bool', default=False),
            force=dict(type='bool', default=False),
        ),
        supports_check_mode=True,
    )
    name = module.params['name']
    state = module.params['state']
    site = module.params['site']
    update_catalog = module.params['update_catalog']
    force = module.params['force']

    rc = None
    out = ''
    err = ''
    result = dict(
        name=name,
        state=state,
    )

    if state in ['installed', 'present']:
        # Fail with an explicit error when trying to "install" '*'
        if name == ['*']:
            module.fail_json(msg="Can not use 'state: present' with name: '*'")

        # Build list of packages that are actually not installed from the ones requested
        pkgs = packages_not_installed(module, name)

        # If the package list is empty then all packages are already present
        if pkgs == []:
            module.exit_json(changed=False)

        (rc, out, err) = package_install(module, state, pkgs, site, update_catalog, force)
        if rc != 0:
            module.fail_json(msg=(err or out))

    elif state in ['latest']:
        # When using latest for *
        if name == ['*']:
            # Check for packages that are actually outdated
            pkgs = packages_not_latest(module, name, site, update_catalog)

            # If the package list comes up empty, everything is already up to date
            if pkgs == []:
                module.exit_json(changed=False)

            # If there are packages to update, just empty the list and run the command without it
            # pkgutil logic is to update all when run without packages names
            pkgs = []
            (rc, out, err) = package_upgrade(module, pkgs, site, update_catalog, force)
            if rc != 0:
                module.fail_json(msg=(err or out))
        else:
            # Build list of packages that are either outdated or not installed
            pkgs = packages_not_installed(module, name)
            pkgs += packages_not_latest(module, name, site, update_catalog)

            # If the package list is empty that means all packages are installed and up to date
            if pkgs == []:
                module.exit_json(changed=False)

            (rc, out, err) = package_upgrade(module, pkgs, site, update_catalog, force)
            if rc != 0:
                module.fail_json(msg=(err or out))

    elif state in ['absent', 'removed']:
        # Build list of packages requested for removal that are actually present
        pkgs = packages_installed(module, name)

        # If the list is empty, no packages need to be removed
        if pkgs == []:
            module.exit_json(changed=False)

        (rc, out, err) = package_uninstall(module, pkgs)
        if rc != 0:
            module.fail_json(msg=(err or out))

    if rc is None:
        # pkgutil was not executed because the package was already present/absent/up to date
        result['changed'] = False
    elif rc == 0:
        result['changed'] = True
    else:
        result['changed'] = False
        result['failed'] = True

    if out:
        result['stdout'] = out
    if err:
        result['stderr'] = err

    module.exit_json(**result)


if __name__ == '__main__':
    main()
