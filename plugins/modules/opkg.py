#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2013, Patrick Pelletier <pp.pelletier@gmail.com>
# Based on pacman (Afterburn) and pkgin (Shaun Zinck) modules
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: opkg
author: "Patrick Pelletier (@skinp)"
short_description: Package manager for OpenWrt
description:
    - Manages OpenWrt packages
options:
    name:
        description:
            - Name of package(s) to install/remove.
            - C(NAME=VERSION) syntax is also supported to install a package
              in a certain version. See the examples. This is supported since
              community.general 6.2.0.
        aliases: [pkg]
        required: true
        type: list
        elements: str
    state:
        description:
            - State of the package.
        choices: [ 'present', 'absent', 'installed', 'removed' ]
        default: present
        type: str
    force:
        description:
            - The C(opkg --force) parameter used.
        choices:
            - ""
            - "depends"
            - "maintainer"
            - "reinstall"
            - "overwrite"
            - "downgrade"
            - "space"
            - "postinstall"
            - "remove"
            - "checksum"
            - "removal-of-dependent-packages"
        default: ""
        type: str
    update_cache:
        description:
            - Update the package DB first.
        default: false
        type: bool
requirements:
    - opkg
    - python
'''
EXAMPLES = '''
- name: Install foo
  community.general.opkg:
    name: foo
    state: present

- name: Install foo in version 1.2
  community.general.opkg:
    name: foo=1.2
    state: present

- name: Update cache and install foo
  community.general.opkg:
    name: foo
    state: present
    update_cache: true

- name: Remove foo
  community.general.opkg:
    name: foo
    state: absent

- name: Remove foo and bar
  community.general.opkg:
    name:
      - foo
      - bar
    state: absent

- name: Install foo using overwrite option forcibly
  community.general.opkg:
    name: foo
    state: present
    force: overwrite
'''

from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, cmd_runner_fmt
from ansible_collections.community.general.plugins.module_utils.module_helper import StateModuleHelper


def update_package_db(module, opkg_path):
    """ Updates packages list. """

    rc, out, err = module.run_command("%s update" % opkg_path)

    if rc != 0:
        module.fail_json(msg="could not update package db")


def query_package(module, opkg_path, name, state="present"):
    """ Returns whether a package is installed or not. """

    if state == "present":

        rc, out, err = module.run_command("%s list-installed | grep -q \"^%s \"" % (shlex_quote(opkg_path), shlex_quote(name)), use_unsafe_shell=True)
        if rc == 0:
            return True

        return False


def remove_packages(module, opkg_path, packages):
    """ Uninstalls one or more packages if installed. """

    p = module.params
    force = p["force"]
    if force:
        force = "--force-%s" % force

    remove_c = 0
    # Using a for loop in case of error, we can report the package that failed
    for package in packages:
        # Query the package first, to see if we even need to remove
        if not query_package(module, opkg_path, package):
            continue

        rc, out, err = module.run_command("%s remove %s %s" % (opkg_path, force, package))

        if query_package(module, opkg_path, package):
            module.fail_json(msg="failed to remove %s: %s" % (package, out))

        remove_c += 1

    if remove_c > 0:

        module.exit_json(changed=True, msg="removed %s package(s)" % remove_c)

    module.exit_json(changed=False, msg="package(s) already absent")


def install_packages(module, opkg_path, packages):
    """ Installs one or more packages if not already installed. """

    p = module.params
    force = p["force"]
    if force:
        force = "--force-%s" % force

    install_c = 0

    for package in packages:
        if query_package(module, opkg_path, package) and (force != '--force-reinstall'):
            continue

        rc, out, err = module.run_command("%s install %s %s" % (opkg_path, force, package))

        if not query_package(module, opkg_path, package):
            module.fail_json(msg="failed to install %s: %s" % (package, out))

        install_c += 1

    if install_c > 0:
        module.exit_json(changed=True, msg="installed %s package(s)" % (install_c))

    module.exit_json(changed=False, msg="package(s) already present")


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(aliases=["pkg"], required=True, type="list", elements="str"),
            state=dict(default="present", choices=["present", "installed", "absent", "removed"]),
            force=dict(default="", choices=["", "depends", "maintainer", "reinstall", "overwrite", "downgrade", "space", "postinstall", "remove",
                                            "checksum", "removal-of-dependent-packages"]),
            update_cache=dict(default=False, type='bool'),
        ),
    )

    def __init_module__(self):
        self.vars.set("install_c", 0, output=False, change=True)
        self.vars.set("remove_c", 0, output=False, change=True)

        state_map = dict(
            query="list-installed",
            present="install",
            installed="install",
            absent="remove",
            removed="remove",
        )

        def _force(value):
            if value == "":
                value = None
            return cmd_runner_fmt.as_optval("--force-")(value)

        self.runner = CmdRunner(
            self.module,
            command="opkg",
            arg_formats=dict(
                package=cmd_runner_fmt.as_list(),
                state=cmd_runner_fmt.as_map(state_map),
                force=cmd_runner_fmt.as_func(_force),
                update_cache=cmd_runner_fmt.as_bool("update")
            ),
            check_rc=True,
        )

    def _package_in_desired_state(self, name, desired_installed):
        dummy, out, dummy = self.runner("state package").run(state="query", package=name)

        has_package = out.startswith(name + " ")
        return desired_installed == has_package

    def state_present(self):
        if self.vars.update_cache:
            self.runner("update_cache").run()
        with self.runner("state force package") as ctx:
            for package in self.vars.name:
                if not self._package_in_desired_state(package, desired_installed=True) or self.vars.force == "reinstall":
                    ctx.run(package=package)
                    if not self._package_in_desired_state(package, desired_installed=True):
                        self.do_raise("failed to install %s" % package)
                    self.vars.install_c += 1

    def state_absent(self):
        if self.vars.update_cache:
            self.runner("update_cache").run()
        with self.runner("state package") as ctx:
            for package in self.vars.name:
                if not self._package_in_desired_state(package, desired_installed=False):
                    ctx.run(package=package)
                    if not self._package_in_desired_state(package, desired_installed=False):
                        self.do_raise("failed to remove %s" % package)
                    self.vars.remove_c += 1

    state_installed = state_present
    state_removed = state_absent


def main():
    Opkg.execute()


if __name__ == '__main__':
    main()
