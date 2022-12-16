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

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves import shlex_quote


def update_package_db(module, opkg_path):
    """ Updates packages list. """

    rc, out, err = module.run_command([opkg_path, "update"])

    if rc != 0:
        module.fail_json(msg="could not update package db")


def query_package(module, opkg_path, name, version=None, state="present"):
    """ Returns whether a package is installed or not. """

    if state == "present":
        rc, out, err = module.run_command([opkg_path, "list-installed", name])
        if rc != 0:
            return False
        # variable out is one line if the package is installed:
        # "NAME - VERSION - DESCRIPTION"
        if version is not None:
            if not out.startswith("%s - %s " % (name, version)):
                return False
        else:
            if not out.startswith(name + " "):
                return False
        return True
    else:
        raise NotImplementedError()


def split_name_and_version(module, package):
    """ Split the name and the version when using the NAME=VERSION syntax """
    splitted = package.split('=', 1)
    if len(splitted) == 1:
        return splitted[0], None
    else:
        return splitted[0], splitted[1]


def remove_packages(module, opkg_path, packages):
    """ Uninstalls one or more packages if installed. """

    p = module.params
    force = p["force"]
    if force:
        force = "--force-%s" % force

    remove_c = 0
    # Using a for loop in case of error, we can report the package that failed
    for package in packages:
        package, version = split_name_and_version(module, package)

        # Query the package first, to see if we even need to remove
        if not query_package(module, opkg_path, package):
            continue

        if force:
            rc, out, err = module.run_command([opkg_path, "remove", force, package])
        else:
            rc, out, err = module.run_command([opkg_path, "remove", package])

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
        package, version = split_name_and_version(module, package)

        if query_package(module, opkg_path, package, version) and (force != '--force-reinstall'):
            continue

        if version is not None:
            version_str = "=%s" % version
        else:
            version_str = ""

        if force:
            rc, out, err = module.run_command([opkg_path, "install", force, package + version_str])
        else:
            rc, out, err = module.run_command([opkg_path, "install", package + version_str])

        if not query_package(module, opkg_path, package, version):
            module.fail_json(msg="failed to install %s%s: %s" % (package, version_str, out))

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
        )
    )

    opkg_path = module.get_bin_path('opkg', True, ['/bin'])

    p = module.params

    if p["update_cache"]:
        update_package_db(module, opkg_path)

    pkgs = p["name"]

    if p["state"] in ["present", "installed"]:
        install_packages(module, opkg_path, pkgs)

    elif p["state"] in ["absent", "removed"]:
        remove_packages(module, opkg_path, pkgs)


if __name__ == '__main__':
    main()
