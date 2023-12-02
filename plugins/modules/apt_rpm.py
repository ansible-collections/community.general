#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2013, Evgenii Terechkov
# Written by Evgenii Terechkov <evg@altlinux.org>
# Based on urpmi module written by Philippe Makowski <philippem@mageia.org>

# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: apt_rpm
short_description: APT-RPM package manager
description:
  - Manages packages with C(apt-rpm). Both low-level (C(rpm)) and high-level (C(apt-get)) package manager binaries required.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options:
  package:
    description:
      - List of packages to install, upgrade, or remove.
      - Since community.general 8.0.0, may include paths to local C(.rpm) files
        if O(state=installed) or O(state=present), requires C(rpm) python
        module.
    aliases: [ name, pkg ]
    type: list
    elements: str
  state:
    description:
      - Indicates the desired package state.
    choices: [ absent, present, installed, removed ]
    default: present
    type: str
  update_cache:
    description:
      - Run the equivalent of C(apt-get update) before the operation. Can be run as part of the package installation or as a separate step.
      - Default is not to update the cache.
    type: bool
    default: false
  clean:
    description:
      - Run the equivalent of C(apt-get clean) to clear out the local repository of retrieved package files. It removes everything but
        the lock file from C(/var/cache/apt/archives/) and C(/var/cache/apt/archives/partial/).
      - Can be run as part of the package installation (clean runs before install) or as a separate step.
    type: bool
    default: false
    version_added: 6.5.0
  dist_upgrade:
    description:
      - If true performs an C(apt-get dist-upgrade) to upgrade system.
    type: bool
    default: false
    version_added: 6.5.0
  update_kernel:
    description:
      - If true performs an C(update-kernel) to upgrade kernel packages.
    type: bool
    default: false
    version_added: 6.5.0
requirements:
  - C(rpm) python package (rpm bindings), optional. Required if O(package)
    option includes local files.
author:
- Evgenii Terechkov (@evgkrsk)
'''

EXAMPLES = '''
- name: Install package foo
  community.general.apt_rpm:
    pkg: foo
    state: present

- name: Install packages foo and bar
  community.general.apt_rpm:
    pkg:
      - foo
      - bar
    state: present

- name: Remove package foo
  community.general.apt_rpm:
    pkg: foo
    state: absent

- name: Remove packages foo and bar
  community.general.apt_rpm:
    pkg: foo,bar
    state: absent

# bar will be the updated if a newer version exists
- name: Update the package database and install bar
  community.general.apt_rpm:
    name: bar
    state: present
    update_cache: true

- name: Run the equivalent of "apt-get clean" as a separate step
  community.general.apt_rpm:
    clean: true

- name: Perform cache update and complete system upgrade (includes kernel)
  community.general.apt_rpm:
    update_cache: true
    dist_upgrade: true
    update_kernel: true
'''

import os
import re
import traceback

from ansible.module_utils.basic import (
    AnsibleModule,
    missing_required_lib,
)
from ansible.module_utils.common.text.converters import to_native

try:
    import rpm
except ImportError:
    HAS_RPM_PYTHON = False
    RPM_PYTHON_IMPORT_ERROR = traceback.format_exc()
else:
    HAS_RPM_PYTHON = True
    RPM_PYTHON_IMPORT_ERROR = None

APT_CACHE = "/usr/bin/apt-cache"
APT_PATH = "/usr/bin/apt-get"
RPM_PATH = "/usr/bin/rpm"
APT_GET_ZERO = "\n0 upgraded, 0 newly installed"
UPDATE_KERNEL_ZERO = "\nTry to install new kernel "


def local_rpm_package_name(path):
    """return package name of a local rpm passed in.
    Inspired by ansible.builtin.yum"""

    ts = rpm.TransactionSet()
    ts.setVSFlags(rpm._RPMVSF_NOSIGNATURES)
    fd = os.open(path, os.O_RDONLY)
    try:
        header = ts.hdrFromFdno(fd)
    except rpm.error as e:
        return None
    finally:
        os.close(fd)

    return to_native(header[rpm.RPMTAG_NAME])


def query_package(module, name):
    # rpm -q returns 0 if the package is installed,
    # 1 if it is not installed
    rc, out, err = module.run_command("%s -q %s" % (RPM_PATH, name))
    if rc == 0:
        return True
    else:
        return False


def check_package_version(module, name):
    # compare installed and candidate version
    # if newest version already installed return True
    # otherwise return False

    rc, out, err = module.run_command([APT_CACHE, "policy", name], environ_update={"LANG": "C"})
    installed = re.split("\n |: ", out)[2]
    candidate = re.split("\n |: ", out)[4]
    if installed >= candidate:
        return True
    return False


def query_package_provides(module, name):
    # rpm -q returns 0 if the package is installed,
    # 1 if it is not installed
    if name.endswith('.rpm'):
        # Likely a local RPM file
        if not HAS_RPM_PYTHON:
            module.fail_json(
                msg=missing_required_lib('rpm'),
                exception=RPM_PYTHON_IMPORT_ERROR,
            )

        name = local_rpm_package_name(name)

    rc, out, err = module.run_command("%s -q --provides %s" % (RPM_PATH, name))
    if rc == 0:
        if check_package_version(module, name):
            return True
    else:
        return False


def update_package_db(module):
    rc, update_out, err = module.run_command([APT_PATH, "update"], check_rc=True, environ_update={"LANG": "C"})
    return (False, update_out)


def dir_size(module, path):
    total_size = 0
    for path, dirs, files in os.walk(path):
        for f in files:
            total_size += os.path.getsize(os.path.join(path, f))
    return total_size


def clean(module):
    t = dir_size(module, "/var/cache/apt/archives")
    rc, out, err = module.run_command([APT_PATH, "clean"], check_rc=True)
    return (t != dir_size(module, "/var/cache/apt/archives"), out)


def dist_upgrade(module):
    rc, out, err = module.run_command([APT_PATH, "-y", "dist-upgrade"], check_rc=True, environ_update={"LANG": "C"})
    return (APT_GET_ZERO not in out, out)


def update_kernel(module):
    rc, out, err = module.run_command(["/usr/sbin/update-kernel", "-y"], check_rc=True, environ_update={"LANG": "C"})
    return (UPDATE_KERNEL_ZERO not in out, out)


def remove_packages(module, packages):

    if packages is None:
        return (False, "Empty package list")

    remove_c = 0
    # Using a for loop in case of error, we can report the package that failed
    for package in packages:
        # Query the package first, to see if we even need to remove
        if not query_package(module, package):
            continue

        rc, out, err = module.run_command("%s -y remove %s" % (APT_PATH, package), environ_update={"LANG": "C"})

        if rc != 0:
            module.fail_json(msg="failed to remove %s: %s" % (package, err))

        remove_c += 1

    if remove_c > 0:
        return (True, "removed %s package(s)" % remove_c)

    return (False, "package(s) already absent")


def install_packages(module, pkgspec):

    if pkgspec is None:
        return (False, "Empty package list")

    packages = ""
    for package in pkgspec:
        if not query_package_provides(module, package):
            packages += "'%s' " % package

    if len(packages) != 0:

        rc, out, err = module.run_command("%s -y install %s" % (APT_PATH, packages), environ_update={"LANG": "C"})

        installed = True
        for packages in pkgspec:
            if not query_package_provides(module, package):
                installed = False

        # apt-rpm always have 0 for exit code if --force is used
        if rc or not installed:
            module.fail_json(msg="'apt-get -y install %s' failed: %s" % (packages, err))
        else:
            return (True, "%s present(s)" % packages)
    else:
        return (False, "Nothing to install")


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str', default='present', choices=['absent', 'installed', 'present', 'removed']),
            update_cache=dict(type='bool', default=False),
            clean=dict(type='bool', default=False),
            dist_upgrade=dict(type='bool', default=False),
            update_kernel=dict(type='bool', default=False),
            package=dict(type='list', elements='str', aliases=['name', 'pkg']),
        ),
    )

    if not os.path.exists(APT_PATH) or not os.path.exists(RPM_PATH):
        module.fail_json(msg="cannot find /usr/bin/apt-get and/or /usr/bin/rpm")

    p = module.params
    modified = False
    output = ""

    if p['update_cache']:
        update_package_db(module)

    if p['clean']:
        (m, out) = clean(module)
        modified = modified or m

    if p['dist_upgrade']:
        (m, out) = dist_upgrade(module)
        modified = modified or m
        output += out

    if p['update_kernel']:
        (m, out) = update_kernel(module)
        modified = modified or m
        output += out

    packages = p['package']
    if p['state'] in ['installed', 'present']:
        (m, out) = install_packages(module, packages)
        modified = modified or m
        output += out

    if p['state'] in ['absent', 'removed']:
        (m, out) = remove_packages(module, packages)
        modified = modified or m
        output += out

    # Return total modification status and output of all commands
    module.exit_json(changed=modified, msg=output)


if __name__ == '__main__':
    main()
