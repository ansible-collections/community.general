#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2013, Daniel Jaouen <dcj24@cornell.edu>
# Copyright (c) 2016, Indrajit Raychaudhuri <irc+code@indrajit.com>
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: homebrew_cask
author:
  - "Indrajit Raychaudhuri (@indrajitr)"
  - "Daniel Jaouen (@danieljaouen)"
  - "Enric Lluelles (@enriclluelles)"
short_description: Install and uninstall homebrew casks
description:
  - Manages Homebrew casks.
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
    - Name of cask to install or remove.
    aliases: [ 'cask', 'package', 'pkg' ]
    type: list
    elements: str
  path:
    description:
    - "':' separated list of paths to search for 'brew' executable."
    default: '/usr/local/bin:/opt/homebrew/bin'
    type: path
  state:
    description:
    - State of the cask.
    choices: [ 'absent', 'installed', 'latest', 'present', 'removed', 'uninstalled', 'upgraded' ]
    default: present
    type: str
  sudo_password:
    description:
    - The sudo password to be passed to SUDO_ASKPASS.
    required: false
    type: str
  update_homebrew:
    description:
    - Update homebrew itself first.
    - Note that C(brew cask update) is a synonym for C(brew update).
    type: bool
    default: false
  install_options:
    description:
    - Options flags to install a package.
    aliases: [ 'options' ]
    type: list
    elements: str
  accept_external_apps:
    description:
    - Allow external apps.
    type: bool
    default: false
  upgrade_all:
    description:
    - Upgrade all casks.
    - Mutually exclusive with C(upgraded) state.
    type: bool
    default: false
    aliases: [ 'upgrade' ]
  greedy:
    description:
    - Upgrade casks that auto update.
    - Passes C(--greedy) to C(brew outdated --cask) when checking
      if an installed cask has a newer version available,
      or to C(brew upgrade --cask) when upgrading all casks.
    type: bool
    default: false
'''
EXAMPLES = '''
- name: Install cask
  community.general.homebrew_cask:
    name: alfred
    state: present

- name: Remove cask
  community.general.homebrew_cask:
    name: alfred
    state: absent

- name: Install cask with install options
  community.general.homebrew_cask:
    name: alfred
    state: present
    install_options: 'appdir=/Applications'

- name: Install cask with install options
  community.general.homebrew_cask:
    name: alfred
    state: present
    install_options: 'debug,appdir=/Applications'

- name: Install cask with force option
  community.general.homebrew_cask:
    name: alfred
    state: present
    install_options: force

- name: Allow external app
  community.general.homebrew_cask:
    name: alfred
    state: present
    accept_external_apps: true

- name: Remove cask with force option
  community.general.homebrew_cask:
    name: alfred
    state: absent
    install_options: force

- name: Upgrade all casks
  community.general.homebrew_cask:
    upgrade_all: true

- name: Upgrade all casks with greedy option
  community.general.homebrew_cask:
    upgrade_all: true
    greedy: true

- name: Upgrade given cask with force option
  community.general.homebrew_cask:
    name: alfred
    state: upgraded
    install_options: force

- name: Upgrade cask with greedy option
  community.general.homebrew_cask:
    name: 1password
    state: upgraded
    greedy: true

- name: Using sudo password for installing cask
  community.general.homebrew_cask:
    name: wireshark
    state: present
    sudo_password: "{{ ansible_become_pass }}"
'''

import os
import re
import tempfile

from ansible_collections.community.general.plugins.module_utils.version import LooseVersion

from ansible.module_utils.common.text.converters import to_bytes
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six import iteritems, string_types


# exceptions -------------------------------------------------------------- {{{
class HomebrewCaskException(Exception):
    pass
# /exceptions ------------------------------------------------------------- }}}


# utils ------------------------------------------------------------------- {{{
def _create_regex_group_complement(s):
    lines = (line.strip() for line in s.split('\n') if line.strip())
    chars = filter(None, (line.split('#')[0].strip() for line in lines))
    group = r'[^' + r''.join(chars) + r']'
    return re.compile(group)
# /utils ------------------------------------------------------------------ }}}


class HomebrewCask(object):
    '''A class to manage Homebrew casks.'''

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

    VALID_CASK_CHARS = r'''
        \w                  # alphanumeric characters (i.e., [a-zA-Z0-9_])
        .                   # dots
        /                   # slash (for taps)
        \-                  # dashes
        @                   # at symbol
    '''

    INVALID_PATH_REGEX = _create_regex_group_complement(VALID_PATH_CHARS)
    INVALID_BREW_PATH_REGEX = _create_regex_group_complement(VALID_BREW_PATH_CHARS)
    INVALID_CASK_REGEX = _create_regex_group_complement(VALID_CASK_CHARS)
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

        if isinstance(path, (string_types)):
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
    def valid_cask(cls, cask):
        '''A valid cask is either None or alphanumeric + backslashes.'''

        if cask is None:
            return True

        return (
            isinstance(cask, string_types)
            and not cls.INVALID_CASK_REGEX.search(cask)
        )

    @classmethod
    def valid_state(cls, state):
        '''
        A valid state is one of:
            - installed
            - absent
        '''

        if state is None:
            return True
        else:
            return (
                isinstance(state, string_types)
                and state.lower() in (
                    'installed',
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
            raise HomebrewCaskException(self.message)

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
            raise HomebrewCaskException(self.message)

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
            raise HomebrewCaskException(self.message)

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
    def current_cask(self):
        return self._current_cask

    @current_cask.setter
    def current_cask(self, cask):
        if not self.valid_cask(cask):
            self._current_cask = None
            self.failed = True
            self.message = 'Invalid cask: {0}.'.format(cask)
            raise HomebrewCaskException(self.message)

        else:
            self._current_cask = cask
            return cask

    @property
    def brew_version(self):
        try:
            return self._brew_version
        except AttributeError:
            return None

    @brew_version.setter
    def brew_version(self, brew_version):
        self._brew_version = brew_version

    # /class properties -------------------------------------------- }}}

    def __init__(self, module, path=path, casks=None, state=None,
                 sudo_password=None, update_homebrew=False,
                 install_options=None, accept_external_apps=False,
                 upgrade_all=False, greedy=False):
        if not install_options:
            install_options = list()
        self._setup_status_vars()
        self._setup_instance_vars(module=module, path=path, casks=casks,
                                  state=state, sudo_password=sudo_password,
                                  update_homebrew=update_homebrew,
                                  install_options=install_options,
                                  accept_external_apps=accept_external_apps,
                                  upgrade_all=upgrade_all,
                                  greedy=greedy, )

        self._prep()

    # prep --------------------------------------------------------- {{{
    def _setup_status_vars(self):
        self.failed = False
        self.changed = False
        self.changed_count = 0
        self.unchanged_count = 0
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
            raise HomebrewCaskException(self.message)

        self.brew_path = self.module.get_bin_path(
            'brew',
            required=True,
            opt_dirs=self.path,
        )
        if not self.brew_path:
            self.brew_path = None
            self.failed = True
            self.message = 'Unable to locate homebrew executable.'
            raise HomebrewCaskException('Unable to locate homebrew executable.')

        return self.brew_path

    def _status(self):
        return (self.failed, self.changed, self.message)
    # /prep -------------------------------------------------------- }}}

    def run(self):
        try:
            self._run()
        except HomebrewCaskException:
            pass

        if not self.failed and (self.changed_count + self.unchanged_count > 1):
            self.message = "Changed: %d, Unchanged: %d" % (
                self.changed_count,
                self.unchanged_count,
            )
        (failed, changed, message) = self._status()

        return (failed, changed, message)

    # checks ------------------------------------------------------- {{{
    def _current_cask_is_outdated(self):
        if not self.valid_cask(self.current_cask):
            return False

        if self._brew_cask_command_is_deprecated():
            base_opts = [self.brew_path, 'outdated', '--cask']
        else:
            base_opts = [self.brew_path, 'cask', 'outdated']

        cask_is_outdated_command = base_opts + (['--greedy'] if self.greedy else []) + [self.current_cask]

        rc, out, err = self.module.run_command(cask_is_outdated_command)

        return out != ""

    def _current_cask_is_installed(self):
        if not self.valid_cask(self.current_cask):
            self.failed = True
            self.message = 'Invalid cask: {0}.'.format(self.current_cask)
            raise HomebrewCaskException(self.message)

        if self._brew_cask_command_is_deprecated():
            base_opts = [self.brew_path, "list", "--cask"]
        else:
            base_opts = [self.brew_path, "cask", "list"]

        cmd = base_opts + [self.current_cask]
        rc, out, err = self.module.run_command(cmd)

        if rc == 0:
            return True
        else:
            return False

    def _get_brew_version(self):
        if self.brew_version:
            return self.brew_version

        cmd = [self.brew_path, '--version']

        rc, out, err = self.module.run_command(cmd, check_rc=True)

        # get version string from first line of "brew --version" output
        version = out.split('\n')[0].split(' ')[1]
        self.brew_version = version
        return self.brew_version

    def _brew_cask_command_is_deprecated(self):
        # The `brew cask` replacements were fully available in 2.6.0 (https://brew.sh/2020/12/01/homebrew-2.6.0/)
        return LooseVersion(self._get_brew_version()) >= LooseVersion('2.6.0')
    # /checks ------------------------------------------------------ }}}

    # commands ----------------------------------------------------- {{{
    def _run(self):
        if self.upgrade_all:
            return self._upgrade_all()

        if self.casks:
            if self.state == 'installed':
                return self._install_casks()
            elif self.state == 'upgraded':
                return self._upgrade_casks()
            elif self.state == 'absent':
                return self._uninstall_casks()

        self.failed = True
        self.message = "You must select a cask to install."
        raise HomebrewCaskException(self.message)

    # sudo_password fix ---------------------- {{{
    def _run_command_with_sudo_password(self, cmd):
        rc, out, err = '', '', ''

        with tempfile.NamedTemporaryFile() as sudo_askpass_file:
            sudo_askpass_file.write(b"#!/bin/sh\n\necho '%s'\n" % to_bytes(self.sudo_password))
            os.chmod(sudo_askpass_file.name, 0o700)
            sudo_askpass_file.file.close()

            rc, out, err = self.module.run_command(
                cmd,
                environ_update={'SUDO_ASKPASS': sudo_askpass_file.name}
            )

            self.module.add_cleanup_file(sudo_askpass_file.name)

        return (rc, out, err)
    # /sudo_password fix --------------------- }}}

    # updated -------------------------------- {{{
    def _update_homebrew(self):
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
            raise HomebrewCaskException(self.message)
    # /updated ------------------------------- }}}

    # _upgrade_all --------------------------- {{{
    def _upgrade_all(self):
        if self.module.check_mode:
            self.changed = True
            self.message = 'Casks would be upgraded.'
            raise HomebrewCaskException(self.message)

        if self._brew_cask_command_is_deprecated():
            cmd = [self.brew_path, 'upgrade', '--cask']
        else:
            cmd = [self.brew_path, 'cask', 'upgrade']

        if self.greedy:
            cmd = cmd + ['--greedy']

        rc, out, err = '', '', ''

        if self.sudo_password:
            rc, out, err = self._run_command_with_sudo_password(cmd)
        else:
            rc, out, err = self.module.run_command(cmd)

        if rc == 0:
            if re.search(r'==> No Casks to upgrade', out.strip(), re.IGNORECASE):
                self.message = 'Homebrew casks already upgraded.'

            else:
                self.changed = True
                self.message = 'Homebrew casks upgraded.'

            return True
        else:
            self.failed = True
            self.message = err.strip()
            raise HomebrewCaskException(self.message)
    # /_upgrade_all -------------------------- }}}

    # installed ------------------------------ {{{
    def _install_current_cask(self):
        if not self.valid_cask(self.current_cask):
            self.failed = True
            self.message = 'Invalid cask: {0}.'.format(self.current_cask)
            raise HomebrewCaskException(self.message)

        if '--force' not in self.install_options and self._current_cask_is_installed():
            self.unchanged_count += 1
            self.message = 'Cask already installed: {0}'.format(
                self.current_cask,
            )
            return True

        if self.module.check_mode:
            self.changed = True
            self.message = 'Cask would be installed: {0}'.format(
                self.current_cask
            )
            raise HomebrewCaskException(self.message)

        if self._brew_cask_command_is_deprecated():
            base_opts = [self.brew_path, 'install', '--cask']
        else:
            base_opts = [self.brew_path, 'cask', 'install']

        opts = base_opts + [self.current_cask] + self.install_options

        cmd = [opt for opt in opts if opt]

        rc, out, err = '', '', ''

        if self.sudo_password:
            rc, out, err = self._run_command_with_sudo_password(cmd)
        else:
            rc, out, err = self.module.run_command(cmd)

        if self._current_cask_is_installed():
            self.changed_count += 1
            self.changed = True
            self.message = 'Cask installed: {0}'.format(self.current_cask)
            return True
        elif self.accept_external_apps and re.search(r"Error: It seems there is already an App at", err):
            self.unchanged_count += 1
            self.message = 'Cask already installed: {0}'.format(
                self.current_cask,
            )
            return True
        else:
            self.failed = True
            self.message = err.strip()
            raise HomebrewCaskException(self.message)

    def _install_casks(self):
        for cask in self.casks:
            self.current_cask = cask
            self._install_current_cask()

        return True
    # /installed ----------------------------- }}}

    # upgraded ------------------------------- {{{
    def _upgrade_current_cask(self):
        command = 'upgrade'

        if not self.valid_cask(self.current_cask):
            self.failed = True
            self.message = 'Invalid cask: {0}.'.format(self.current_cask)
            raise HomebrewCaskException(self.message)

        if not self._current_cask_is_installed():
            command = 'install'

        if self._current_cask_is_installed() and not self._current_cask_is_outdated():
            self.message = 'Cask is already upgraded: {0}'.format(
                self.current_cask,
            )
            self.unchanged_count += 1
            return True

        if self.module.check_mode:
            self.changed = True
            self.message = 'Cask would be upgraded: {0}'.format(
                self.current_cask
            )
            raise HomebrewCaskException(self.message)

        if self._brew_cask_command_is_deprecated():
            base_opts = [self.brew_path, command, '--cask']
        else:
            base_opts = [self.brew_path, 'cask', command]

        opts = base_opts + self.install_options + [self.current_cask]

        cmd = [opt for opt in opts if opt]

        rc, out, err = '', '', ''

        if self.sudo_password:
            rc, out, err = self._run_command_with_sudo_password(cmd)
        else:
            rc, out, err = self.module.run_command(cmd)

        if self._current_cask_is_installed() and not self._current_cask_is_outdated():
            self.changed_count += 1
            self.changed = True
            self.message = 'Cask upgraded: {0}'.format(self.current_cask)
            return True
        else:
            self.failed = True
            self.message = err.strip()
            raise HomebrewCaskException(self.message)

    def _upgrade_casks(self):
        for cask in self.casks:
            self.current_cask = cask
            self._upgrade_current_cask()

        return True
    # /upgraded ------------------------------ }}}

    # uninstalled ---------------------------- {{{
    def _uninstall_current_cask(self):
        if not self.valid_cask(self.current_cask):
            self.failed = True
            self.message = 'Invalid cask: {0}.'.format(self.current_cask)
            raise HomebrewCaskException(self.message)

        if not self._current_cask_is_installed():
            self.unchanged_count += 1
            self.message = 'Cask already uninstalled: {0}'.format(
                self.current_cask,
            )
            return True

        if self.module.check_mode:
            self.changed = True
            self.message = 'Cask would be uninstalled: {0}'.format(
                self.current_cask
            )
            raise HomebrewCaskException(self.message)

        if self._brew_cask_command_is_deprecated():
            base_opts = [self.brew_path, 'uninstall', '--cask']
        else:
            base_opts = [self.brew_path, 'cask', 'uninstall']

        opts = base_opts + [self.current_cask] + self.install_options

        cmd = [opt for opt in opts if opt]

        rc, out, err = '', '', ''

        if self.sudo_password:
            rc, out, err = self._run_command_with_sudo_password(cmd)
        else:
            rc, out, err = self.module.run_command(cmd)

        if not self._current_cask_is_installed():
            self.changed_count += 1
            self.changed = True
            self.message = 'Cask uninstalled: {0}'.format(self.current_cask)
            return True
        else:
            self.failed = True
            self.message = err.strip()
            raise HomebrewCaskException(self.message)

    def _uninstall_casks(self):
        for cask in self.casks:
            self.current_cask = cask
            self._uninstall_current_cask()

        return True
    # /uninstalled --------------------------- }}}
    # /commands ---------------------------------------------------- }}}


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(
                aliases=["pkg", "package", "cask"],
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
                    "latest", "upgraded",
                    "absent", "removed", "uninstalled",
                ],
            ),
            sudo_password=dict(
                type="str",
                required=False,
                no_log=True,
            ),
            update_homebrew=dict(
                default=False,
                type='bool',
            ),
            install_options=dict(
                default=None,
                aliases=['options'],
                type='list',
                elements='str',
            ),
            accept_external_apps=dict(
                default=False,
                type='bool',
            ),
            upgrade_all=dict(
                default=False,
                aliases=["upgrade"],
                type='bool',
            ),
            greedy=dict(
                default=False,
                type='bool',
            ),
        ),
        supports_check_mode=True,
    )

    module.run_command_environ_update = dict(LANG='C', LC_ALL='C', LC_MESSAGES='C', LC_CTYPE='C')

    p = module.params

    if p['name']:
        casks = p['name']
    else:
        casks = None

    path = p['path']
    if path:
        path = path.split(':')

    state = p['state']
    if state in ('present', 'installed'):
        state = 'installed'
    if state in ('latest', 'upgraded'):
        state = 'upgraded'
    if state in ('absent', 'removed', 'uninstalled'):
        state = 'absent'

    sudo_password = p['sudo_password']

    update_homebrew = p['update_homebrew']
    upgrade_all = p['upgrade_all']
    greedy = p['greedy']
    p['install_options'] = p['install_options'] or []
    install_options = ['--{0}'.format(install_option)
                       for install_option in p['install_options']]

    accept_external_apps = p['accept_external_apps']

    brew_cask = HomebrewCask(module=module, path=path, casks=casks,
                             state=state, sudo_password=sudo_password,
                             update_homebrew=update_homebrew,
                             install_options=install_options,
                             accept_external_apps=accept_external_apps,
                             upgrade_all=upgrade_all,
                             greedy=greedy,
                             )
    (failed, changed, message) = brew_cask.run()
    if failed:
        module.fail_json(msg=message)
    else:
        module.exit_json(changed=changed, msg=message)


if __name__ == '__main__':
    main()
