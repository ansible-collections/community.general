#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2013, Andrew Dunham <andrew@du.nham.ca>
# Copyright (c) 2013, Daniel Jaouen <dcj24@cornell.edu>
# Copyright (c) 2015, Indrajit Raychaudhuri <irc+code@indrajit.com>
#
# Based on macports (Jimmy Tang <jcftang@gmail.com>)
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r"""
module: homebrew
author:
  - "Indrajit Raychaudhuri (@indrajitr)"
  - "Daniel Jaouen (@danieljaouen)"
  - "Andrew Dunham (@andrew-d)"
requirements:
  - homebrew must already be installed on the target system
short_description: Package manager for Homebrew
description:
  - Manages Homebrew packages.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  name:
    description:
      - A list of names of packages to install/remove.
    aliases: ['formula', 'package', 'pkg']
    type: list
    elements: str
  path:
    description:
      - A V(:) separated list of paths to search for C(brew) executable. Since a package (I(formula) in homebrew parlance)
        location is prefixed relative to the actual path of C(brew) command, providing an alternative C(brew) path enables
        managing different set of packages in an alternative location in the system.
    default: '/usr/local/bin:/opt/homebrew/bin:/home/linuxbrew/.linuxbrew/bin'
    type: path
  state:
    description:
      - State of the package.
    choices: ['absent', 'head', 'installed', 'latest', 'linked', 'present', 'removed', 'uninstalled', 'unlinked', 'upgraded']
    default: present
    type: str
  update_homebrew:
    description:
      - Update homebrew itself first.
    type: bool
    default: false
  upgrade_all:
    description:
      - Upgrade all homebrew packages.
    type: bool
    default: false
    aliases: ['upgrade']
  install_options:
    description:
      - Options flags to install a package.
    aliases: ['options']
    type: list
    elements: str
  upgrade_options:
    description:
      - Option flags to upgrade.
    type: list
    elements: str
    version_added: '0.2.0'
  force_formula:
    description:
      - Force the package(s) to be treated as a formula (equivalent to C(brew --formula)).
      - To install a cask, use the M(community.general.homebrew_cask) module.
    type: bool
    default: false
    version_added: 9.0.0
notes:
  - When used with a C(loop:) each package is processed individually, it is much more efficient to pass the list directly
    to the O(name) option.
"""

EXAMPLES = r"""
# Install formula foo with 'brew' in default path
- community.general.homebrew:
    name: foo
    state: present

# Install formula foo with 'brew' in alternate path (/my/other/location/bin)
- community.general.homebrew:
    name: foo
    path: /my/other/location/bin
    state: present

# Update homebrew first and install formula foo with 'brew' in default path
- community.general.homebrew:
    name: foo
    state: present
    update_homebrew: true

# Update homebrew first and upgrade formula foo to latest available with 'brew' in default path
- community.general.homebrew:
    name: foo
    state: latest
    update_homebrew: true

# Update homebrew and upgrade all packages
- community.general.homebrew:
    update_homebrew: true
    upgrade_all: true

# Miscellaneous other examples
- community.general.homebrew:
    name: foo
    state: head

- community.general.homebrew:
    name: foo
    state: linked

- community.general.homebrew:
    name: foo
    state: absent

- community.general.homebrew:
    name: foo,bar
    state: absent

- community.general.homebrew:
    name: foo
    state: present
    install_options: with-baz,enable-debug

- name: Install formula foo with 'brew' from cask
  community.general.homebrew:
    name: homebrew/cask/foo
    state: present

- name: Use ignore-pinned option while upgrading all
  community.general.homebrew:
    upgrade_all: true
    upgrade_options: ignore-pinned

- name: Force installing a formula whose name is also a cask name
  community.general.homebrew:
    name: ambiguous_formula
    state: present
    force_formula: true
"""

RETURN = r"""
msg:
  description: If the cache was updated or not.
  returned: always
  type: str
  sample: "Changed: 0, Unchanged: 2"
unchanged_pkgs:
  description:
    - List of package names which are unchanged after module run.
  returned: success
  type: list
  sample: ["awscli", "ag"]
  version_added: '0.2.0'
changed_pkgs:
  description:
    - List of package names which are changed after module run.
  returned: success
  type: list
  sample: ["git", "git-cola"]
  version_added: '0.2.0'
"""

import json
import re

from ansible_collections.community.general.plugins.module_utils.homebrew import HomebrewValidate

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six import iteritems, string_types


# exceptions -------------------------------------------------------------- {{{
class HomebrewException(Exception):
    pass
# /exceptions ------------------------------------------------------------- }}}


# utils ------------------------------------------------------------------- {{{
def _create_regex_group_complement(s):
    lines = (line.strip() for line in s.split('\n') if line.strip())
    chars = filter(None, (line.split('#')[0].strip() for line in lines))
    group = r'[^' + r''.join(chars) + r']'
    return re.compile(group)


def _check_package_in_json(json_output, package_type):
    return bool(json_output.get(package_type, []) and json_output[package_type][0].get("installed"))
# /utils ------------------------------------------------------------------ }}}


class Homebrew(object):
    '''A class to manage Homebrew packages.'''

    # class validations -------------------------------------------- {{{
    @classmethod
    def valid_state(cls, state):
        '''
        A valid state is one of:
            - None
            - installed
            - upgraded
            - head
            - linked
            - unlinked
            - absent
        '''

        if state is None:
            return True
        else:
            return (
                isinstance(state, string_types)
                and state.lower() in (
                    'installed',
                    'upgraded',
                    'head',
                    'linked',
                    'unlinked',
                    'absent',
                )
            )

    @classmethod
    def valid_module(cls, module):
        '''A valid module is an instance of AnsibleModule.'''

        return isinstance(module, AnsibleModule)

    # /class validations ------------------------------------------- }}}

    # class properties --------------------------------------------- {{{
    @property
    def module(self):
        return self._module

    @module.setter
    def module(self, module):
        if not self.valid_module(module):
            self._module = None
            self.failed = True
            self.message = 'Invalid module: {0}.'.format(module)
            raise HomebrewException(self.message)

        else:
            self._module = module
            return module

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        if not HomebrewValidate.valid_path(path):
            self._path = []
            self.failed = True
            self.message = 'Invalid path: {0}.'.format(path)
            raise HomebrewException(self.message)

        else:
            if isinstance(path, string_types):
                self._path = path.split(':')
            else:
                self._path = path

            return path

    @property
    def brew_path(self):
        return self._brew_path

    @brew_path.setter
    def brew_path(self, brew_path):
        if not HomebrewValidate.valid_brew_path(brew_path):
            self._brew_path = None
            self.failed = True
            self.message = 'Invalid brew_path: {0}.'.format(brew_path)
            raise HomebrewException(self.message)

        else:
            self._brew_path = brew_path
            return brew_path

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, params):
        self._params = self.module.params
        return self._params

    # /class properties -------------------------------------------- }}}

    def __init__(self, module, path, packages=None, state=None,
                 update_homebrew=False, upgrade_all=False,
                 install_options=None, upgrade_options=None,
                 force_formula=False):
        if not install_options:
            install_options = list()
        if not upgrade_options:
            upgrade_options = list()
        self._setup_status_vars()
        self._setup_instance_vars(module=module, path=path, packages=packages,
                                  state=state, update_homebrew=update_homebrew,
                                  upgrade_all=upgrade_all,
                                  install_options=install_options,
                                  upgrade_options=upgrade_options,
                                  force_formula=force_formula)

        self._prep()

    # prep --------------------------------------------------------- {{{
    def _setup_status_vars(self):
        self.failed = False
        self.changed = False
        self.changed_pkgs = []
        self.unchanged_pkgs = []
        self.message = ''

    def _setup_instance_vars(self, **kwargs):
        self.installed_packages = set()
        self.outdated_packages = set()
        for key, val in iteritems(kwargs):
            setattr(self, key, val)

    def _prep(self):
        self._prep_brew_path()

    def _prep_brew_path(self):
        if not self.module:
            self.brew_path = None
            self.failed = True
            self.message = 'AnsibleModule not set.'
            raise HomebrewException(self.message)

        self.brew_path = self.module.get_bin_path(
            'brew',
            required=True,
            opt_dirs=self.path,
        )
        if not self.brew_path:
            self.brew_path = None
            self.failed = True
            self.message = 'Unable to locate homebrew executable.'
            raise HomebrewException('Unable to locate homebrew executable.')

        return self.brew_path

    def _validate_packages_names(self):
        invalid_packages = []
        for package in self.packages:
            if not HomebrewValidate.valid_package(package):
                invalid_packages.append(package)

        if invalid_packages:
            self.failed = True
            self.message = 'Invalid package{0}: {1}'.format(
                "s" if len(invalid_packages) > 1 else "",
                ", ".join(invalid_packages),
            )
            raise HomebrewException(self.message)

    def _save_package_info(self, package_detail, package_name):
        if bool(package_detail.get("installed")):
            self.installed_packages.add(package_name)
        if bool(package_detail.get("outdated")):
            self.outdated_packages.add(package_name)

    def _extract_package_name(self, package_detail, is_cask):
        # "brew info" can lookup by name, full_name, token, full_token, or aliases
        # In addition, any name can be prefixed by the tap.
        # Any of these can be supplied by the user as the package name.  In case
        # of ambiguity, where a given name might match multiple packages,
        # formulae are preferred over casks. For all other ambiguities, the
        # results are an error.  Note that in the homebrew/core and
        # homebrew/cask taps, there are no "other" ambiguities.
        if is_cask:  # according to brew info
            name = package_detail["token"]
            full_name = package_detail["full_token"]
        else:
            name = package_detail["name"]
            full_name = package_detail["full_name"]

        # Issue https://github.com/ansible-collections/community.general/issues/9803:
        # name can include the tap as a prefix, in order to disambiguate,
        # e.g. casks from identically named formulae.
        #
        # Issue https://github.com/ansible-collections/community.general/issues/10012:
        # package_detail["tap"] is None if package is no longer available.
        tapped_name = [package_detail["tap"] + "/" + name] if package_detail["tap"] else []
        aliases = package_detail.get("aliases", [])
        package_names = set([name, full_name] + tapped_name + aliases)

        # Finally, identify which of all those package names was the one supplied by the user.
        package_names = package_names & set(self.packages)
        if len(package_names) != 1:
            self.failed = True
            self.message = "Package names are missing or ambiguous: " + ", ".join(str(p) for p in package_names)
            raise HomebrewException(self.message)

        # Then make sure the user provided name resurface.
        return package_names.pop()

    def _get_packages_info(self):
        cmd = [
            "{brew_path}".format(brew_path=self.brew_path),
            "info",
            "--json=v2",
        ]
        cmd.extend(self.packages)
        if self.force_formula:
            cmd.append("--formula")

        rc, out, err = self.module.run_command(cmd)
        if rc != 0:
            self.failed = True
            self.message = err.strip() or ("Unknown failure with exit code %d" % rc)
            raise HomebrewException(self.message)

        data = json.loads(out)
        for package_detail in data.get("formulae", []):
            package_name = self._extract_package_name(package_detail, is_cask=False)
            self._save_package_info(package_detail, package_name)

        for package_detail in data.get("casks", []):
            package_name = self._extract_package_name(package_detail, is_cask=True)
            self._save_package_info(package_detail, package_name)

    # /prep -------------------------------------------------------- }}}

    def run(self):
        try:
            self._run()
        except HomebrewException:
            pass

        changed_count = len(self.changed_pkgs)
        unchanged_count = len(self.unchanged_pkgs)
        if not self.failed and (changed_count + unchanged_count > 1):
            self.message = "Changed: %d, Unchanged: %d" % (
                changed_count,
                unchanged_count,
            )
        return (self.failed, self.changed, self.message)

    # commands ----------------------------------------------------- {{{
    def _run(self):
        if self.update_homebrew:
            self._update_homebrew()

        if self.upgrade_all:
            self._upgrade_all()

        if self.packages:
            self._validate_packages_names()
            self._get_packages_info()
            if self.state == 'installed':
                return self._install_packages()
            elif self.state == 'upgraded':
                return self._upgrade_packages()
            elif self.state == 'head':
                return self._install_packages()
            elif self.state == 'linked':
                return self._link_packages()
            elif self.state == 'unlinked':
                return self._unlink_packages()
            elif self.state == 'absent':
                return self._uninstall_packages()

    # updated -------------------------------- {{{
    def _update_homebrew(self):
        if self.module.check_mode:
            self.changed = True
            self.message = 'Homebrew would be updated.'
            raise HomebrewException(self.message)

        rc, out, err = self.module.run_command([
            self.brew_path,
            'update',
        ])
        if rc == 0:
            if out and isinstance(out, string_types):
                already_updated = any(
                    re.search(r'Already up-to-date.', s.strip(), re.IGNORECASE)
                    for s in out.split('\n')
                    if s
                )
                if not already_updated:
                    self.changed = True
                    self.message = 'Homebrew updated successfully.'
                else:
                    self.message = 'Homebrew already up-to-date.'

            return True
        else:
            self.failed = True
            self.message = err.strip()
            raise HomebrewException(self.message)
    # /updated ------------------------------- }}}

    # _upgrade_all --------------------------- {{{
    def _upgrade_all(self):
        if self.module.check_mode:
            self.changed = True
            self.message = 'Homebrew packages would be upgraded.'
            raise HomebrewException(self.message)
        cmd = [self.brew_path, 'upgrade'] + self.upgrade_options

        rc, out, err = self.module.run_command(cmd)
        if rc == 0:
            if not out:
                self.message = 'Homebrew packages already upgraded.'

            else:
                self.changed = True
                self.message = 'Homebrew upgraded.'

            return True
        else:
            self.failed = True
            self.message = err.strip()
            raise HomebrewException(self.message)
    # /_upgrade_all -------------------------- }}}

    # installed ------------------------------ {{{
    def _install_packages(self):
        packages_to_install = set(self.packages) - self.installed_packages

        if len(packages_to_install) == 0:
            self.unchanged_pkgs.extend(self.packages)
            self.message = 'Package{0} already installed: {1}'.format(
                "s" if len(self.packages) > 1 else "",
                ", ".join(self.packages),
            )
            return True

        if self.module.check_mode:
            self.changed = True
            self.message = 'Package{0} would be installed: {1}'.format(
                "s" if len(packages_to_install) > 1 else "",
                ", ".join(packages_to_install)
            )
            raise HomebrewException(self.message)

        if self.state == 'head':
            head = '--HEAD'
        else:
            head = None

        if self.force_formula:
            formula = '--formula'
        else:
            formula = None

        opts = (
            [self.brew_path, 'install']
            + self.install_options
            + list(packages_to_install)
            + [head, formula]
        )
        cmd = [opt for opt in opts if opt]
        rc, out, err = self.module.run_command(cmd)

        if rc == 0:
            self.changed_pkgs.extend(packages_to_install)
            self.unchanged_pkgs.extend(self.installed_packages)
            self.changed = True
            self.message = 'Package{0} installed: {1}'.format(
                "s" if len(packages_to_install) > 1 else "",
                ", ".join(packages_to_install)
            )
            return True
        else:
            self.failed = True
            self.message = err.strip()
            raise HomebrewException(self.message)
    # /installed ----------------------------- }}}

    # upgraded ------------------------------- {{{
    def _upgrade_all_packages(self):
        opts = (
            [self.brew_path, 'upgrade']
            + self.install_options
        )
        cmd = [opt for opt in opts if opt]
        rc, out, err = self.module.run_command(cmd)

        if rc == 0:
            self.changed = True
            self.message = 'All packages upgraded.'
            return True
        else:
            self.failed = True
            self.message = err.strip()
            raise HomebrewException(self.message)

    def _upgrade_packages(self):
        if not self.packages:
            self._upgrade_all_packages()
        else:
            # There are 3 action possible here depending on installed and outdated states:
            #   - not installed -> 'install'
            #   - installed and outdated -> 'upgrade'
            #   - installed and NOT outdated -> Nothing to do!
            packages_to_install = set(self.packages) - self.installed_packages
            packages_to_upgrade = self.installed_packages & self.outdated_packages
            packages_to_install_or_upgrade = packages_to_install | packages_to_upgrade

            if len(packages_to_install_or_upgrade) == 0:
                self.unchanged_pkgs.extend(self.packages)
                self.message = 'Package{0} already upgraded: {1}'.format(
                    "s" if len(self.packages) > 1 else "",
                    ", ".join(self.packages),
                )
                return True

            if self.module.check_mode:
                self.changed = True
                self.message = 'Package{0} would be upgraded: {1}'.format(
                    "s" if len(packages_to_install_or_upgrade) > 1 else "",
                    ", ".join(packages_to_install_or_upgrade)
                )
                raise HomebrewException(self.message)

            for command, packages in [
                ("install", packages_to_install),
                ("upgrade", packages_to_upgrade)
            ]:
                if not packages:
                    continue

                opts = (
                    [self.brew_path, command]
                    + self.install_options
                    + list(packages)
                )
                cmd = [opt for opt in opts if opt]
                rc, out, err = self.module.run_command(cmd)

                if rc != 0:
                    self.failed = True
                    self.message = err.strip()
                    raise HomebrewException(self.message)

            self.changed_pkgs.extend(packages_to_install_or_upgrade)
            self.unchanged_pkgs.extend(set(self.packages) - packages_to_install_or_upgrade)
            self.changed = True
            self.message = 'Package{0} upgraded: {1}'.format(
                "s" if len(packages_to_install_or_upgrade) > 1 else "",
                ", ".join(packages_to_install_or_upgrade),
            )
    # /upgraded ------------------------------ }}}

    # uninstalled ---------------------------- {{{
    def _uninstall_packages(self):
        packages_to_uninstall = self.installed_packages & set(self.packages)

        if len(packages_to_uninstall) == 0:
            self.unchanged_pkgs.extend(self.packages)
            self.message = 'Package{0} already uninstalled: {1}'.format(
                "s" if len(self.packages) > 1 else "",
                ", ".join(self.packages),
            )
            return True

        if self.module.check_mode:
            self.changed = True
            self.message = 'Package{0} would be uninstalled: {1}'.format(
                "s" if len(packages_to_uninstall) > 1 else "",
                ", ".join(packages_to_uninstall)
            )
            raise HomebrewException(self.message)

        opts = (
            [self.brew_path, 'uninstall', '--force']
            + self.install_options
            + list(packages_to_uninstall)
        )
        cmd = [opt for opt in opts if opt]
        rc, out, err = self.module.run_command(cmd)

        if rc == 0:
            self.changed_pkgs.extend(packages_to_uninstall)
            self.unchanged_pkgs.extend(set(self.packages) - self.installed_packages)
            self.changed = True
            self.message = 'Package{0} uninstalled: {1}'.format(
                "s" if len(packages_to_uninstall) > 1 else "",
                ", ".join(packages_to_uninstall)
            )
            return True
        else:
            self.failed = True
            self.message = err.strip()
            raise HomebrewException(self.message)
    # /uninstalled ----------------------------- }}}

    # linked --------------------------------- {{{
    def _link_packages(self):
        missing_packages = set(self.packages) - self.installed_packages
        if missing_packages:
            self.failed = True
            self.message = 'Package{0} not installed: {1}.'.format(
                "s" if len(missing_packages) > 1 else "",
                ", ".join(missing_packages),
            )
            raise HomebrewException(self.message)

        if self.module.check_mode:
            self.changed = True
            self.message = 'Package{0} would be linked: {1}'.format(
                "s" if len(self.packages) > 1 else "",
                ", ".join(self.packages)
            )
            raise HomebrewException(self.message)

        opts = (
            [self.brew_path, 'link']
            + self.install_options
            + self.packages
        )
        cmd = [opt for opt in opts if opt]
        rc, out, err = self.module.run_command(cmd)

        if rc == 0:
            self.changed_pkgs.extend(self.packages)
            self.changed = True
            self.message = 'Package{0} linked: {1}'.format(
                "s" if len(self.packages) > 1 else "",
                ", ".join(self.packages)
            )
            return True
        else:
            self.failed = True
            self.message = 'Package{0} could not be linked: {1}.'.format(
                "s" if len(self.packages) > 1 else "",
                ", ".join(self.packages)
            )
            raise HomebrewException(self.message)
    # /linked -------------------------------- }}}

    # unlinked ------------------------------- {{{
    def _unlink_packages(self):
        missing_packages = set(self.packages) - self.installed_packages
        if missing_packages:
            self.failed = True
            self.message = 'Package{0} not installed: {1}.'.format(
                "s" if len(missing_packages) > 1 else "",
                ", ".join(missing_packages),
            )
            raise HomebrewException(self.message)

        if self.module.check_mode:
            self.changed = True
            self.message = 'Package{0} would be unlinked: {1}'.format(
                "s" if len(self.packages) > 1 else "",
                ", ".join(self.packages)
            )
            raise HomebrewException(self.message)

        opts = (
            [self.brew_path, 'unlink']
            + self.install_options
            + self.packages
        )
        cmd = [opt for opt in opts if opt]
        rc, out, err = self.module.run_command(cmd)

        if rc == 0:
            self.changed_pkgs.extend(self.packages)
            self.changed = True
            self.message = 'Package{0} unlinked: {1}'.format(
                "s" if len(self.packages) > 1 else "",
                ", ".join(self.packages)
            )
            return True
        else:
            self.failed = True
            self.message = 'Package{0} could not be unlinked: {1}.'.format(
                "s" if len(self.packages) > 1 else "",
                ", ".join(self.packages)
            )
            raise HomebrewException(self.message)
    # /unlinked ------------------------------ }}}
    # /commands ---------------------------------------------------- }}}


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(
                aliases=["pkg", "package", "formula"],
                required=False,
                type='list',
                elements='str',
            ),
            path=dict(
                default="/usr/local/bin:/opt/homebrew/bin:/home/linuxbrew/.linuxbrew/bin",
                required=False,
                type='path',
            ),
            state=dict(
                default="present",
                choices=[
                    "present", "installed",
                    "latest", "upgraded", "head",
                    "linked", "unlinked",
                    "absent", "removed", "uninstalled",
                ],
            ),
            update_homebrew=dict(
                default=False,
                type='bool',
            ),
            upgrade_all=dict(
                default=False,
                aliases=["upgrade"],
                type='bool',
            ),
            install_options=dict(
                default=None,
                aliases=['options'],
                type='list',
                elements='str',
            ),
            upgrade_options=dict(
                default=None,
                type='list',
                elements='str',
            ),
            force_formula=dict(
                default=False,
                type='bool',
            ),
        ),
        supports_check_mode=True,
    )

    module.run_command_environ_update = dict(LANG='C', LC_ALL='C', LC_MESSAGES='C', LC_CTYPE='C')

    p = module.params

    if p['name']:
        packages = [package_name.lower() for package_name in p['name']]
    else:
        packages = None

    path = p['path']
    if path:
        path = path.split(':')

    state = p['state']
    if state in ('present', 'installed'):
        state = 'installed'
    if state in ('head', ):
        state = 'head'
    if state in ('latest', 'upgraded'):
        state = 'upgraded'
    if state == 'linked':
        state = 'linked'
    if state == 'unlinked':
        state = 'unlinked'
    if state in ('absent', 'removed', 'uninstalled'):
        state = 'absent'

    force_formula = p['force_formula']
    update_homebrew = p['update_homebrew']
    if not update_homebrew:
        module.run_command_environ_update.update(
            dict(HOMEBREW_NO_AUTO_UPDATE="True")
        )
    upgrade_all = p['upgrade_all']
    p['install_options'] = p['install_options'] or []
    install_options = ['--{0}'.format(install_option)
                       for install_option in p['install_options']]

    p['upgrade_options'] = p['upgrade_options'] or []
    upgrade_options = ['--{0}'.format(upgrade_option)
                       for upgrade_option in p['upgrade_options']]
    brew = Homebrew(module=module, path=path, packages=packages,
                    state=state, update_homebrew=update_homebrew,
                    upgrade_all=upgrade_all, install_options=install_options,
                    upgrade_options=upgrade_options, force_formula=force_formula)
    (failed, changed, message) = brew.run()
    changed_pkgs = brew.changed_pkgs
    unchanged_pkgs = brew.unchanged_pkgs

    if failed:
        module.fail_json(msg=message)
    module.exit_json(
        changed=changed,
        msg=message,
        unchanged_pkgs=unchanged_pkgs,
        changed_pkgs=changed_pkgs
    )


if __name__ == '__main__':
    main()
