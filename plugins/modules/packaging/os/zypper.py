#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2013, Patrick Callahan <pmc@patrickcallahan.com>
# based on
#     openbsd_pkg
#         (c) 2013
#         Patrik Lundin <patrik.lundin.swe@gmail.com>
#
#     yum
#         (c) 2012, Red Hat, Inc
#         Written by Seth Vidal <skvidal at fedoraproject.org>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: zypper
author:
    - "Patrick Callahan (@dirtyharrycallahan)"
    - "Alexander Gubin (@alxgu)"
    - "Thomas O'Donnell (@andytom)"
    - "Robin Roth (@robinro)"
    - "Andrii Radyk (@AnderEnder)"
short_description: Manage packages on SUSE and openSUSE
description:
    - Manage packages on SUSE and openSUSE using the zypper and rpm tools.
    - Also supports transactional updates, by running zypper inside C(/sbin/transactional-update --continue --drop-if-no-change --quiet run).
options:
    name:
        description:
        - Package name C(name) or package specifier or a list of either.
        - Can include a version like C(name=1.0), C(name>3.4) or C(name<=2.7). If a version is given, C(oldpackage) is implied and zypper is allowed to
          update the package within the version range given.
        - You can also pass a url or a local path to a rpm file.
        - When using state=latest, this can be '*', which updates all installed packages.
        required: true
        aliases: [ 'pkg' ]
        type: list
        elements: str
    state:
        description:
          - C(present) will make sure the package is installed.
            C(latest)  will make sure the latest version of the package is installed.
            C(absent)  will make sure the specified package is not installed.
            C(dist-upgrade) will make sure the latest version of all installed packages from all enabled repositories is installed.
          - When using C(dist-upgrade), I(name) should be C('*').
        required: false
        choices: [ present, latest, absent, dist-upgrade, installed, removed ]
        default: "present"
        type: str
    type:
        description:
          - The type of package to be operated on.
        required: false
        choices: [ package, patch, pattern, product, srcpackage, application ]
        default: "package"
        type: str
    extra_args_precommand:
       required: false
       description:
         - Add additional global target options to C(zypper).
         - Options should be supplied in a single line as if given in the command line.
       type: str
    disable_gpg_check:
        description:
          - Whether to disable to GPG signature checking of the package
            signature being installed. Has an effect only if state is
            I(present) or I(latest).
        required: false
        default: "no"
        type: bool
    disable_recommends:
        description:
          - Corresponds to the C(--no-recommends) option for I(zypper). Default behavior (C(yes)) modifies zypper's default behavior; C(no) does
            install recommended packages.
        required: false
        default: "yes"
        type: bool
    force:
        description:
          - Adds C(--force) option to I(zypper). Allows to downgrade packages and change vendor or architecture.
        required: false
        default: "no"
        type: bool
    force_resolution:
        description:
          - Adds C(--force-resolution) option to I(zypper). Allows to (un)install packages with conflicting requirements (resolver will choose a solution).
        required: false
        default: "no"
        type: bool
        version_added: '0.2.0'
    update_cache:
        description:
          - Run the equivalent of C(zypper refresh) before the operation. Disabled in check mode.
        required: false
        default: "no"
        type: bool
        aliases: [ "refresh" ]
    oldpackage:
        description:
          - Adds C(--oldpackage) option to I(zypper). Allows to downgrade packages with less side-effects than force. This is implied as soon as a
            version is specified as part of the package name.
        required: false
        default: "no"
        type: bool
    extra_args:
        required: false
        description:
          - Add additional options to C(zypper) command.
          - Options should be supplied in a single line as if given in the command line.
        type: str
    allow_vendor_change:
        type: bool
        required: false
        default: false
        description:
          - Adds C(--allow_vendor_change) option to I(zypper) dist-upgrade command.
        version_added: '0.2.0'
    replacefiles:
        type: bool
        required: false
        default: false
        description:
          - Adds C(--replacefiles) option to I(zypper) install/update command.
        version_added: '0.2.0'
    clean_deps:
        type: bool
        required: false
        default: false
        description:
          - Adds C(--clean-deps) option to I(zypper) remove command.
        version_added: '4.6.0'
notes:
  - When used with a `loop:` each package will be processed individually,
    it is much more efficient to pass the list directly to the `name` option.
# informational: requirements for nodes
requirements:
    - "zypper >= 1.0  # included in openSUSE >= 11.1 or SUSE Linux Enterprise Server/Desktop >= 11.0"
    - python-xml
    - rpm
'''

EXAMPLES = '''
- name: Install nmap
  community.general.zypper:
    name: nmap
    state: present

- name: Install apache2 with recommended packages
  community.general.zypper:
    name: apache2
    state: present
    disable_recommends: no

- name: Apply a given patch
  community.general.zypper:
    name: openSUSE-2016-128
    state: present
    type: patch

- name: Remove the nmap package
  community.general.zypper:
    name: nmap
    state: absent

- name: Install the nginx rpm from a remote repo
  community.general.zypper:
    name: 'http://nginx.org/packages/sles/12/x86_64/RPMS/nginx-1.8.0-1.sles12.ngx.x86_64.rpm'
    state: present

- name: Install local rpm file
  community.general.zypper:
    name: /tmp/fancy-software.rpm
    state: present

- name: Update all packages
  community.general.zypper:
    name: '*'
    state: latest

- name: Apply all available patches
  community.general.zypper:
    name: '*'
    state: latest
    type: patch

- name: Perform a dist-upgrade with additional arguments
  community.general.zypper:
    name: '*'
    state: dist-upgrade
    allow_vendor_change: true
    extra_args: '--allow-arch-change'

- name: Perform a installaion of nmap with the install option replacefiles
  community.general.zypper:
    name: 'nmap'
    state: latest
    replacefiles: true

- name: Refresh repositories and update package openssl
  community.general.zypper:
    name: openssl
    state: present
    update_cache: yes

- name: "Install specific version (possible comparisons: <, >, <=, >=, =)"
  community.general.zypper:
    name: 'docker>=1.10'
    state: present

- name: Wait 20 seconds to acquire the lock before failing
  community.general.zypper:
    name: mosh
    state: present
  environment:
    ZYPP_LOCK_TIMEOUT: 20
'''

import os.path
import xml
import re
from xml.dom.minidom import parseString as parseXML
from ansible.module_utils.common.text.converters import to_native

# import module snippets
from ansible.module_utils.basic import AnsibleModule


class Package:
    def __init__(self, name, prefix, version):
        self.name = name
        self.prefix = prefix
        self.version = version
        self.shouldinstall = (prefix == '+')

    def __str__(self):
        return self.prefix + self.name + self.version


def split_name_version(name):
    """splits of the package name and desired version

    example formats:
        - docker>=1.10
        - apache=2.4

    Allowed version specifiers: <, >, <=, >=, =
    Allowed version format: [0-9.-]*

    Also allows a prefix indicating remove "-", "~" or install "+"
    """

    prefix = ''
    if name[0] in ['-', '~', '+']:
        prefix = name[0]
        name = name[1:]
    if prefix == '~':
        prefix = '-'

    version_check = re.compile('^(.*?)((?:<|>|<=|>=|=)[0-9.-]*)?$')
    try:
        reres = version_check.match(name)
        name, version = reres.groups()
        if version is None:
            version = ''
        return prefix, name, version
    except Exception:
        return prefix, name, ''


def get_want_state(names, remove=False):
    packages = []
    urls = []
    for name in names:
        if '://' in name or name.endswith('.rpm'):
            urls.append(name)
        else:
            prefix, pname, version = split_name_version(name)
            if prefix not in ['-', '+']:
                if remove:
                    prefix = '-'
                else:
                    prefix = '+'
            packages.append(Package(pname, prefix, version))
    return packages, urls


def get_installed_state(m, packages):
    "get installed state of packages"

    cmd = get_cmd(m, 'search')
    cmd.extend(['--match-exact', '--details', '--installed-only'])
    cmd.extend([p.name for p in packages])
    return parse_zypper_xml(m, cmd, fail_not_found=False)[0]


def parse_zypper_xml(m, cmd, fail_not_found=True, packages=None):
    rc, stdout, stderr = m.run_command(cmd, check_rc=False)

    try:
        dom = parseXML(stdout)
    except xml.parsers.expat.ExpatError as exc:
        m.fail_json(msg="Failed to parse zypper xml output: %s" % to_native(exc),
                    rc=rc, stdout=stdout, stderr=stderr, cmd=cmd)

    if rc == 104:
        # exit code 104 is ZYPPER_EXIT_INF_CAP_NOT_FOUND (no packages found)
        if fail_not_found:
            errmsg = dom.getElementsByTagName('message')[-1].childNodes[0].data
            m.fail_json(msg=errmsg, rc=rc, stdout=stdout, stderr=stderr, cmd=cmd)
        else:
            return {}, rc, stdout, stderr
    elif rc in [0, 106, 103]:
        # zypper exit codes
        # 0: success
        # 106: signature verification failed
        # 103: zypper was upgraded, run same command again
        if packages is None:
            firstrun = True
            packages = {}
        else:
            firstrun = False
        solvable_list = dom.getElementsByTagName('solvable')
        for solvable in solvable_list:
            name = solvable.getAttribute('name')
            packages[name] = {}
            packages[name]['version'] = solvable.getAttribute('edition')
            packages[name]['oldversion'] = solvable.getAttribute('edition-old')
            status = solvable.getAttribute('status')
            packages[name]['installed'] = status == "installed"
            packages[name]['group'] = solvable.parentNode.nodeName
        if rc == 103 and firstrun:
            # if this was the first run and it failed with 103
            # run zypper again with the same command to complete update
            return parse_zypper_xml(m, cmd, fail_not_found=fail_not_found, packages=packages)

        return packages, rc, stdout, stderr
    m.fail_json(msg='Zypper run command failed with return code %s.' % rc, rc=rc, stdout=stdout, stderr=stderr, cmd=cmd)


def get_cmd(m, subcommand):
    "puts together the basic zypper command arguments with those passed to the module"
    is_install = subcommand in ['install', 'update', 'patch', 'dist-upgrade']
    is_refresh = subcommand == 'refresh'
    cmd = [m.get_bin_path('zypper', required=True), '--quiet', '--non-interactive', '--xmlout']
    if transactional_updates():
        cmd = [m.get_bin_path('transactional-update', required=True), '--continue', '--drop-if-no-change', '--quiet', 'run'] + cmd
    if m.params['extra_args_precommand']:
        args_list = m.params['extra_args_precommand'].split()
        cmd.extend(args_list)
    # add global options before zypper command
    if (is_install or is_refresh) and m.params['disable_gpg_check']:
        cmd.append('--no-gpg-checks')

    if subcommand == 'search':
        cmd.append('--disable-repositories')

    cmd.append(subcommand)
    if subcommand not in ['patch', 'dist-upgrade'] and not is_refresh:
        cmd.extend(['--type', m.params['type']])
    if m.check_mode and subcommand != 'search':
        cmd.append('--dry-run')
    if is_install:
        cmd.append('--auto-agree-with-licenses')
        if m.params['disable_recommends']:
            cmd.append('--no-recommends')
        if m.params['force']:
            cmd.append('--force')
        if m.params['force_resolution']:
            cmd.append('--force-resolution')
        if m.params['oldpackage']:
            cmd.append('--oldpackage')
        if m.params['replacefiles']:
            cmd.append('--replacefiles')
    if subcommand == 'remove':
        if m.params['clean_deps']:
            cmd.append('--clean-deps')
    if subcommand == 'dist-upgrade' and m.params['allow_vendor_change']:
        cmd.append('--allow-vendor-change')
    if m.params['extra_args']:
        args_list = m.params['extra_args'].split(' ')
        cmd.extend(args_list)

    return cmd


def set_diff(m, retvals, result):
    # TODO: if there is only one package, set before/after to version numbers
    packages = {'installed': [], 'removed': [], 'upgraded': []}
    if result:
        for p in result:
            group = result[p]['group']
            if group == 'to-upgrade':
                versions = ' (' + result[p]['oldversion'] + ' => ' + result[p]['version'] + ')'
                packages['upgraded'].append(p + versions)
            elif group == 'to-install':
                packages['installed'].append(p)
            elif group == 'to-remove':
                packages['removed'].append(p)

    output = ''
    for state in packages:
        if packages[state]:
            output += state + ': ' + ', '.join(packages[state]) + '\n'
    if 'diff' not in retvals:
        retvals['diff'] = {}
    if 'prepared' not in retvals['diff']:
        retvals['diff']['prepared'] = output
    else:
        retvals['diff']['prepared'] += '\n' + output


def package_present(m, name, want_latest):
    "install and update (if want_latest) the packages in name_install, while removing the packages in name_remove"
    retvals = {'rc': 0, 'stdout': '', 'stderr': ''}
    packages, urls = get_want_state(name)

    # add oldpackage flag when a version is given to allow downgrades
    if any(p.version for p in packages):
        m.params['oldpackage'] = True

    if not want_latest:
        # for state=present: filter out already installed packages
        # if a version is given leave the package in to let zypper handle the version
        # resolution
        packageswithoutversion = [p for p in packages if not p.version]
        prerun_state = {}
        if packageswithoutversion:
            prerun_state = get_installed_state(m, packageswithoutversion)
        # generate lists of packages to install or remove
        packages = [p for p in packages if p.shouldinstall != (p.name in prerun_state)]

    if not packages and not urls:
        # nothing to install/remove and nothing to update
        return None, retvals

    # zypper install also updates packages
    cmd = get_cmd(m, 'install')
    cmd.append('--')
    cmd.extend(urls)
    # pass packages to zypper
    # allow for + or - prefixes in install/remove lists
    # also add version specifier if given
    # do this in one zypper run to allow for dependency-resolution
    # for example "-exim postfix" runs without removing packages depending on mailserver
    cmd.extend([str(p) for p in packages])

    retvals['cmd'] = cmd
    result, retvals['rc'], retvals['stdout'], retvals['stderr'] = parse_zypper_xml(m, cmd)

    return result, retvals


def package_update_all(m):
    "run update or patch on all available packages"

    retvals = {'rc': 0, 'stdout': '', 'stderr': ''}
    if m.params['type'] == 'patch':
        cmdname = 'patch'
    elif m.params['state'] == 'dist-upgrade':
        cmdname = 'dist-upgrade'
    else:
        cmdname = 'update'

    cmd = get_cmd(m, cmdname)
    retvals['cmd'] = cmd
    result, retvals['rc'], retvals['stdout'], retvals['stderr'] = parse_zypper_xml(m, cmd)
    return result, retvals


def package_absent(m, name):
    "remove the packages in name"
    retvals = {'rc': 0, 'stdout': '', 'stderr': ''}
    # Get package state
    packages, urls = get_want_state(name, remove=True)
    if any(p.prefix == '+' for p in packages):
        m.fail_json(msg="Can not combine '+' prefix with state=remove/absent.")
    if urls:
        m.fail_json(msg="Can not remove via URL.")
    if m.params['type'] == 'patch':
        m.fail_json(msg="Can not remove patches.")
    prerun_state = get_installed_state(m, packages)
    packages = [p for p in packages if p.name in prerun_state]

    if not packages:
        return None, retvals

    cmd = get_cmd(m, 'remove')
    cmd.extend([p.name + p.version for p in packages])

    retvals['cmd'] = cmd
    result, retvals['rc'], retvals['stdout'], retvals['stderr'] = parse_zypper_xml(m, cmd)
    return result, retvals


def repo_refresh(m):
    "update the repositories"
    retvals = {'rc': 0, 'stdout': '', 'stderr': ''}

    cmd = get_cmd(m, 'refresh')

    retvals['cmd'] = cmd
    result, retvals['rc'], retvals['stdout'], retvals['stderr'] = parse_zypper_xml(m, cmd)

    return retvals


def transactional_updates():
    return os.path.exists('/var/lib/misc/transactional-update.state')

# ===========================================
# Main control flow


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True, aliases=['pkg'], type='list', elements='str'),
            state=dict(required=False, default='present', choices=['absent', 'installed', 'latest', 'present', 'removed', 'dist-upgrade']),
            type=dict(required=False, default='package', choices=['package', 'patch', 'pattern', 'product', 'srcpackage', 'application']),
            extra_args_precommand=dict(required=False, default=None),
            disable_gpg_check=dict(required=False, default=False, type='bool'),
            disable_recommends=dict(required=False, default=True, type='bool'),
            force=dict(required=False, default=False, type='bool'),
            force_resolution=dict(required=False, default=False, type='bool'),
            update_cache=dict(required=False, aliases=['refresh'], default=False, type='bool'),
            oldpackage=dict(required=False, default=False, type='bool'),
            extra_args=dict(required=False, default=None),
            allow_vendor_change=dict(required=False, default=False, type='bool'),
            replacefiles=dict(required=False, default=False, type='bool'),
            clean_deps=dict(required=False, default=False, type='bool'),
        ),
        supports_check_mode=True
    )

    module.run_command_environ_update = dict(LANG='C', LC_ALL='C', LC_MESSAGES='C')

    name = module.params['name']
    state = module.params['state']
    update_cache = module.params['update_cache']

    # remove empty strings from package list
    name = list(filter(None, name))

    # Refresh repositories
    if update_cache and not module.check_mode:
        retvals = repo_refresh(module)

        if retvals['rc'] != 0:
            module.fail_json(msg="Zypper refresh run failed.", **retvals)

    # Perform requested action
    if name == ['*'] and state in ['latest', 'dist-upgrade']:
        packages_changed, retvals = package_update_all(module)
    elif name != ['*'] and state == 'dist-upgrade':
        module.fail_json(msg="Can not dist-upgrade specific packages.")
    else:
        if state in ['absent', 'removed']:
            packages_changed, retvals = package_absent(module, name)
        elif state in ['installed', 'present', 'latest']:
            packages_changed, retvals = package_present(module, name, state == 'latest')

    retvals['changed'] = retvals['rc'] == 0 and bool(packages_changed)

    if module._diff:
        set_diff(module, retvals, packages_changed)

    if retvals['rc'] != 0:
        module.fail_json(msg="Zypper run failed.", **retvals)

    if not retvals['changed']:
        del retvals['stdout']
        del retvals['stderr']

    module.exit_json(name=name, state=state, update_cache=update_cache, **retvals)


if __name__ == "__main__":
    main()
