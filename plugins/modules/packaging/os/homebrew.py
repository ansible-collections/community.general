#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2013, Andrew Dunham <andrew@du.nham.ca>
# (c) 2013, Daniel Jaouen <dcj24@cornell.edu>
# (c) 2015, Indrajit Raychaudhuri <irc+code@indrajit.com>
#
# Based on macports (Jimmy Tang <jcftang@gmail.com>)
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: homebrew
author:
    - "Indrajit Raychaudhuri (@indrajitr)"
    - "Daniel Jaouen (@danieljaouen)"
    - "Andrew Dunham (@andrew-d)"
requirements:
   - "python >= 2.6"
   - homebrew must already be installed on the target system
short_description: Package manager for Homebrew
description:
    - Manages Homebrew packages
options:
    name:
        description:
            - A list of names of packages to install/remove.
        aliases: [ 'formula', 'package', 'pkg' ]
        type: list
        elements: str
    path:
        description:
            - "A ':' separated list of paths to search for 'brew' executable.
              Since a package (I(formula) in homebrew parlance) location is prefixed relative to the actual path of I(brew) command,
              providing an alternative I(brew) path enables managing different set of packages in an alternative location in the system."
        default: '/usr/local/bin:/opt/homebrew/bin'
        type: path
    state:
        description:
            - state of the package.
        choices: [ 'absent', 'head', 'installed', 'latest', 'linked', 'present', 'removed', 'uninstalled', 'unlinked', 'upgraded' ]
        default: present
        type: str
    update_homebrew:
        description:
            - update homebrew itself first.
        type: bool
        default: no
    upgrade_all:
        description:
            - upgrade all homebrew packages.
        type: bool
        default: no
        aliases: ['upgrade']
    install_options:
        description:
            - options flags to install a package.
        aliases: ['options']
        type: list
        elements: str
    upgrade_options:
        description:
            - Option flags to upgrade.
        type: list
        elements: str
        version_added: '0.2.0'
notes:
  - When used with a `loop:` each package will be processed individually,
    it is much more efficient to pass the list directly to the `name` option.
'''

EXAMPLES = '''
# Install formula foo with 'brew' in default path
- community.general.homebrew:
    name: foo
    state: present

# Install formula foo with 'brew' in alternate path C(/my/other/location/bin)
- community.general.homebrew:
    name: foo
    path: /my/other/location/bin
    state: present

# Update homebrew first and install formula foo with 'brew' in default path
- community.general.homebrew:
    name: foo
    state: present
    update_homebrew: yes

# Update homebrew first and upgrade formula foo to latest available with 'brew' in default path
- community.general.homebrew:
    name: foo
    state: latest
    update_homebrew: yes

# Update homebrew and upgrade all packages
- community.general.homebrew:
    update_homebrew: yes
    upgrade_all: yes

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
    upgrade_all: yes
    upgrade_options: ignore-pinned
'''

RETURN = '''
msg:
    description: if the cache was updated or not
    returned: always
    type: str
    sample: "Changed: 0, Unchanged: 2"
unchanged_pkgs:
    description:
    - List of package names which are unchanged after module run
    returned: success
    type: list
    sample: ["awscli", "ag"]
    version_added: '0.2.0'
changed_pkgs:
    description:
    - List of package names which are changed after module run
    returned: success
    type: list
    sample: ['git', 'git-cola']
    version_added: '0.2.0'
'''

import os.path
import re

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
# /utils ------------------------------------------------------------------ }}}


class Homebrew(object):
    '''A class to manage Homebrew packages.'''

    # class regexes ------------------------------------------------ {{{
    VALID_PATH_CHARS = r'''
        \w                  # alphanumeric characters (i.e., [a-zA-Z0-9_])
        \s                  # spaces
        :                   # colons
        {sep}               # the OS-specific path separator
        .                   # dots
        \-                  # dashes
    '''.format(sep=os.path.sep)

    VALID_BREW_PATH_CHARS = r'''
        \w                  # alphanumeric characters (i.e., [a-zA-Z0-9_])
        \s                  # spaces
        {sep}               # the OS-specific path separator
        .                   # dots
        \-                  # dashes
    '''.format(sep=os.path.sep)

    VALID_PACKAGE_CHARS = r'''
        \w                  # alphanumeric characters (i.e., [a-zA-Z0-9_])
        .                   # dots
        /                   # slash (for taps)
        \+                  # plusses
        \-                  # dashes
        :                   # colons (for URLs)
        @                   # at-sign
    '''

    INVALID_PATH_REGEX = _create_regex_group_complement(VALID_PATH_CHARS)
    INVALID_BREW_PATH_REGEX = _create_regex_group_complement(VALID_BREW_PATH_CHARS)
    INVALID_PACKAGE_REGEX = _create_regex_group_complement(VALID_PACKAGE_CHARS)
    # /class regexes ----------------------------------------------- }}}

    # class validations -------------------------------------------- {{{
    @classmethod
    def valid_path(cls, path):
        '''
        `path` must be one of:
         - list of paths
         - a string containing only:
             - alphanumeric characters
             - dashes
             - dots
             - spaces
             - colons
             - os.path.sep
        '''

        if isinstance(path, string_types):
            return not cls.INVALID_PATH_REGEX.search(path)

        try:
            iter(path)
        except TypeError:
            return False
        else:
            paths = path
            return all(cls.valid_brew_path(path_) for path_ in paths)

    @classmethod
    def valid_brew_path(cls, brew_path):
        '''
        `brew_path` must be one of:
         - None
         - a string containing only:
             - alphanumeric characters
             - dashes
             - dots
             - spaces
             - os.path.sep
        '''

        if brew_path is None:
            return True

        return (
            isinstance(brew_path, string_types)
            and not cls.INVALID_BREW_PATH_REGEX.search(brew_path)
        )

    @classmethod
    def valid_package(cls, package):
        '''A valid package is either None or alphanumeric.'''

        if package is None:
            return True

        return (
            isinstance(package, string_types)
            and not cls.INVALID_PACKAGE_REGEX.search(package)
        )

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
        if not self.valid_path(path):
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
        if not self.valid_brew_path(brew_path):
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

    @property
    def current_package(self):
        return self._current_package

    @current_package.setter
    def current_package(self, package):
        if not self.valid_package(package):
            self._current_package = None
            self.failed = True
            self.message = 'Invalid package: {0}.'.format(package)
            raise HomebrewException(self.message)

        else:
            self._current_package = package
            return package
    # /class properties -------------------------------------------- }}}

    def __init__(self, module, path, packages=None, state=None,
                 update_homebrew=False, upgrade_all=False,
                 install_options=None, upgrade_options=None):
        if not install_options:
            install_options = list()
        if not upgrade_options:
            upgrade_options = list()
        self._setup_status_vars()
        self._setup_instance_vars(module=module, path=path, packages=packages,
                                  state=state, update_homebrew=update_homebrew,
                                  upgrade_all=upgrade_all,
                                  install_options=install_options,
                                  upgrade_options=upgrade_options,)

        self._prep()

    # prep --------------------------------------------------------- {{{
    def _setup_status_vars(self):
        self.failed = False
        self.changed = False
        self.changed_count = 0
        self.unchanged_count = 0
        self.changed_pkgs = []
        self.unchanged_pkgs = []
        self.message = ''

    def _setup_instance_vars(self, **kwargs):
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

    def _status(self):
        return (self.failed, self.changed, self.message)
    # /prep -------------------------------------------------------- }}}

    def run(self):
        try:
            self._run()
        except HomebrewException:
            pass

        if not self.failed and (self.changed_count + self.unchanged_count > 1):
            self.message = "Changed: %d, Unchanged: %d" % (
                self.changed_count,
                self.unchanged_count,
            )
        (failed, changed, message) = self._status()

        return (failed, changed, message)

    # checks ------------------------------------------------------- {{{
    def _current_package_is_installed(self):
        if not self.valid_package(self.current_package):
            self.failed = True
            self.message = 'Invalid package: {0}.'.format(self.current_package)
            raise HomebrewException(self.message)

        cmd = [
            "{brew_path}".format(brew_path=self.brew_path),
            "info",
            self.current_package,
        ]
        rc, out, err = self.module.run_command(cmd)
        for line in out.split('\n'):
            if (
                re.search(r'Built from source', line)
                or re.search(r'Poured from bottle', line)
            ):
                return True

        return False

    def _current_package_is_outdated(self):
        if not self.valid_package(self.current_package):
            return False

        rc, out, err = self.module.run_command([
            self.brew_path,
            'outdated',
            self.current_package,
        ])

        return rc != 0

    def _current_package_is_installed_from_head(self):
        if not Homebrew.valid_package(self.current_package):
            return False
        elif not self._current_package_is_installed():
            return False

        rc, out, err = self.module.run_command([
            self.brew_path,
            'info',
            self.current_package,
        ])

        try:
            version_info = [line for line in out.split('\n') if line][0]
        except IndexError:
            return False

        return version_info.split(' ')[-1] == 'HEAD'
    # /checks ------------------------------------------------------ }}}

    # commands ----------------------------------------------------- {{{
    def _run(self):
        if self.update_homebrew:
            self._update_homebrew()

        if self.upgrade_all:
            self._upgrade_all()

        if self.packages:
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
    def _install_current_package(self):
        if not self.valid_package(self.current_package):
            self.failed = True
            self.message = 'Invalid package: {0}.'.format(self.current_package)
            raise HomebrewException(self.message)

        if self._current_package_is_installed():
            self.unchanged_count += 1
            self.unchanged_pkgs.append(self.current_package)
            self.message = 'Package already installed: {0}'.format(
                self.current_package,
            )
            return True

        if self.module.check_mode:
            self.changed = True
            self.message = 'Package would be installed: {0}'.format(
                self.current_package
            )
            raise HomebrewException(self.message)

        if self.state == 'head':
            head = '--HEAD'
        else:
            head = None

        opts = (
            [self.brew_path, 'install']
            + self.install_options
            + [self.current_package, head]
        )
        cmd = [opt for opt in opts if opt]
        rc, out, err = self.module.run_command(cmd)

        if self._current_package_is_installed():
            self.changed_count += 1
            self.changed_pkgs.append(self.current_package)
            self.changed = True
            self.message = 'Package installed: {0}'.format(self.current_package)
            return True
        else:
            self.failed = True
            self.message = err.strip()
            raise HomebrewException(self.message)

    def _install_packages(self):
        for package in self.packages:
            self.current_package = package
            self._install_current_package()

        return True
    # /installed ----------------------------- }}}

    # upgraded ------------------------------- {{{
    def _upgrade_current_package(self):
        command = 'upgrade'

        if not self.valid_package(self.current_package):
            self.failed = True
            self.message = 'Invalid package: {0}.'.format(self.current_package)
            raise HomebrewException(self.message)

        if not self._current_package_is_installed():
            command = 'install'

        if self._current_package_is_installed() and not self._current_package_is_outdated():
            self.message = 'Package is already upgraded: {0}'.format(
                self.current_package,
            )
            self.unchanged_count += 1
            self.unchanged_pkgs.append(self.current_package)
            return True

        if self.module.check_mode:
            self.changed = True
            self.message = 'Package would be upgraded: {0}'.format(
                self.current_package
            )
            raise HomebrewException(self.message)

        opts = (
            [self.brew_path, command]
            + self.install_options
            + [self.current_package]
        )
        cmd = [opt for opt in opts if opt]
        rc, out, err = self.module.run_command(cmd)

        if self._current_package_is_installed() and not self._current_package_is_outdated():
            self.changed_count += 1
            self.changed_pkgs.append(self.current_package)
            self.changed = True
            self.message = 'Package upgraded: {0}'.format(self.current_package)
            return True
        else:
            self.failed = True
            self.message = err.strip()
            raise HomebrewException(self.message)

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
            for package in self.packages:
                self.current_package = package
                self._upgrade_current_package()
            return True
    # /upgraded ------------------------------ }}}

    # uninstalled ---------------------------- {{{
    def _uninstall_current_package(self):
        if not self.valid_package(self.current_package):
            self.failed = True
            self.message = 'Invalid package: {0}.'.format(self.current_package)
            raise HomebrewException(self.message)

        if not self._current_package_is_installed():
            self.unchanged_count += 1
            self.unchanged_pkgs.append(self.current_package)
            self.message = 'Package already uninstalled: {0}'.format(
                self.current_package,
            )
            return True

        if self.module.check_mode:
            self.changed = True
            self.message = 'Package would be uninstalled: {0}'.format(
                self.current_package
            )
            raise HomebrewException(self.message)

        opts = (
            [self.brew_path, 'uninstall', '--force']
            + self.install_options
            + [self.current_package]
        )
        cmd = [opt for opt in opts if opt]
        rc, out, err = self.module.run_command(cmd)

        if not self._current_package_is_installed():
            self.changed_count += 1
            self.changed_pkgs.append(self.current_package)
            self.changed = True
            self.message = 'Package uninstalled: {0}'.format(self.current_package)
            return True
        else:
            self.failed = True
            self.message = err.strip()
            raise HomebrewException(self.message)

    def _uninstall_packages(self):
        for package in self.packages:
            self.current_package = package
            self._uninstall_current_package()

        return True
    # /uninstalled ----------------------------- }}}

    # linked --------------------------------- {{{
    def _link_current_package(self):
        if not self.valid_package(self.current_package):
            self.failed = True
            self.message = 'Invalid package: {0}.'.format(self.current_package)
            raise HomebrewException(self.message)

        if not self._current_package_is_installed():
            self.failed = True
            self.message = 'Package not installed: {0}.'.format(self.current_package)
            raise HomebrewException(self.message)

        if self.module.check_mode:
            self.changed = True
            self.message = 'Package would be linked: {0}'.format(
                self.current_package
            )
            raise HomebrewException(self.message)

        opts = (
            [self.brew_path, 'link']
            + self.install_options
            + [self.current_package]
        )
        cmd = [opt for opt in opts if opt]
        rc, out, err = self.module.run_command(cmd)

        if rc == 0:
            self.changed_count += 1
            self.changed_pkgs.append(self.current_package)
            self.changed = True
            self.message = 'Package linked: {0}'.format(self.current_package)

            return True
        else:
            self.failed = True
            self.message = 'Package could not be linked: {0}.'.format(self.current_package)
            raise HomebrewException(self.message)

    def _link_packages(self):
        for package in self.packages:
            self.current_package = package
            self._link_current_package()

        return True
    # /linked -------------------------------- }}}

    # unlinked ------------------------------- {{{
    def _unlink_current_package(self):
        if not self.valid_package(self.current_package):
            self.failed = True
            self.message = 'Invalid package: {0}.'.format(self.current_package)
            raise HomebrewException(self.message)

        if not self._current_package_is_installed():
            self.failed = True
            self.message = 'Package not installed: {0}.'.format(self.current_package)
            raise HomebrewException(self.message)

        if self.module.check_mode:
            self.changed = True
            self.message = 'Package would be unlinked: {0}'.format(
                self.current_package
            )
            raise HomebrewException(self.message)

        opts = (
            [self.brew_path, 'unlink']
            + self.install_options
            + [self.current_package]
        )
        cmd = [opt for opt in opts if opt]
        rc, out, err = self.module.run_command(cmd)

        if rc == 0:
            self.changed_count += 1
            self.changed_pkgs.append(self.current_package)
            self.changed = True
            self.message = 'Package unlinked: {0}'.format(self.current_package)

            return True
        else:
            self.failed = True
            self.message = 'Package could not be unlinked: {0}.'.format(self.current_package)
            raise HomebrewException(self.message)

    def _unlink_packages(self):
        for package in self.packages:
            self.current_package = package
            self._unlink_current_package()

        return True
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
                default="/usr/local/bin:/opt/homebrew/bin",
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
            )
        ),
        supports_check_mode=True,
    )

    module.run_command_environ_update = dict(LANG='C', LC_ALL='C', LC_MESSAGES='C', LC_CTYPE='C')

    p = module.params

    if p['name']:
        packages = p['name']
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
                    upgrade_options=upgrade_options)
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
