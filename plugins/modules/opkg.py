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
short_description: Package manager for OpenWrt and Openembedded/Yocto based Linux distributions
description:
    - Manages ipk packages for OpenWrt and Openembedded/Yocto based Linux distributions
extends_documentation_fragment:
    - community.general.attributes
attributes:
    check_mode:
        support: none
    diff_mode:
        support: none
options:
    name:
        description:
            - Name of package(s) to install/remove.
            - C(NAME=VERSION) syntax is also supported to install a package
              in a certain version. See the examples. This only works on Yocto based
              Linux distributions (opkg>=0.3.2) and not for OpenWrt. This is
              supported since community.general 6.2.0.
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
            - Passing V("") as value and not passing any value at all have both
              the same effect of B(not) using any C(--force-) parameter.
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
        type: str
    update_cache:
        description:
            - Update the package DB first.
        default: false
        type: bool
    executable:
        description:
            - The executable location for C(opkg).
        type: path
        version_added: 7.2.0
requirements:
    - opkg
    - python
'''
EXAMPLES = '''
- name: Install foo
  community.general.opkg:
    name: foo
    state: present

- name: Install foo in version 1.2 (opkg>=0.3.2 on Yocto based Linux distributions)
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

import os
from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, cmd_runner_fmt
from ansible_collections.community.general.plugins.module_utils.module_helper import StateModuleHelper


class Opkg(StateModuleHelper):
    module = dict(
        argument_spec=dict(
            name=dict(aliases=["pkg"], required=True, type="list", elements="str"),
            state=dict(default="present", choices=["present", "installed", "absent", "removed"]),
            force=dict(choices=["", "depends", "maintainer", "reinstall", "overwrite", "downgrade", "space",
                                "postinstall", "remove", "checksum", "removal-of-dependent-packages"]),
            update_cache=dict(default=False, type='bool'),
            executable=dict(type="path"),
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
            return cmd_runner_fmt.as_optval("--force-")(value, ctx_ignore_none=True)

        dir, cmd = os.path.split(self.vars.executable) if self.vars.executable else (None, "opkg")

        self.runner = CmdRunner(
            self.module,
            command=cmd,
            arg_formats=dict(
                package=cmd_runner_fmt.as_list(),
                state=cmd_runner_fmt.as_map(state_map),
                force=cmd_runner_fmt.as_func(_force),
                update_cache=cmd_runner_fmt.as_bool("update"),
            ),
            path_prefix=dir,
        )

        if self.vars.update_cache:
            rc, dummy, dummy = self.runner("update_cache").run()
            if rc != 0:
                self.do_raise("could not update package db")

    @staticmethod
    def split_name_and_version(package):
        """ Split the name and the version when using the NAME=VERSION syntax """
        splitted = package.split('=', 1)
        if len(splitted) == 1:
            return splitted[0], None
        else:
            return splitted[0], splitted[1]

    def _package_in_desired_state(self, name, want_installed, version=None):
        dummy, out, dummy = self.runner("state package").run(state="query", package=name)

        has_package = out.startswith(name + " - %s" % ("" if not version else (version + " ")))
        return want_installed == has_package

    def state_present(self):
        with self.runner("state force package") as ctx:
            for package in self.vars.name:
                pkg_name, pkg_version = self.split_name_and_version(package)
                if not self._package_in_desired_state(pkg_name, want_installed=True, version=pkg_version) or self.vars.force == "reinstall":
                    ctx.run(package=package)
                    if not self._package_in_desired_state(pkg_name, want_installed=True, version=pkg_version):
                        self.do_raise("failed to install %s" % package)
                    self.vars.install_c += 1
            if self.verbosity >= 4:
                self.vars.run_info = ctx.run_info
        if self.vars.install_c > 0:
            self.vars.msg = "installed %s package(s)" % (self.vars.install_c)
        else:
            self.vars.msg = "package(s) already present"

    def state_absent(self):
        with self.runner("state force package") as ctx:
            for package in self.vars.name:
                package, dummy = self.split_name_and_version(package)
                if not self._package_in_desired_state(package, want_installed=False):
                    ctx.run(package=package)
                    if not self._package_in_desired_state(package, want_installed=False):
                        self.do_raise("failed to remove %s" % package)
                    self.vars.remove_c += 1
            if self.verbosity >= 4:
                self.vars.run_info = ctx.run_info
        if self.vars.remove_c > 0:
            self.vars.msg = "removed %s package(s)" % (self.vars.remove_c)
        else:
            self.vars.msg = "package(s) already absent"

    state_installed = state_present
    state_removed = state_absent


def main():
    Opkg.execute()


if __name__ == '__main__':
    main()
