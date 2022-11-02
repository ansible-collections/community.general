#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2013, Jimmy Tang <jcftang@gmail.com>
# Based on okpg (Patrick Pelletier <pp.pelletier@gmail.com>), pacman
# (Afterburn) and pkgin (Shaun Zinck) modules
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: macports
author: "Jimmy Tang (@jcftang)"
short_description: Package manager for MacPorts
description:
    - Manages MacPorts packages (ports)
options:
    name:
        description:
            - A list of port names.
        aliases: ['port']
        type: list
        elements: str
    selfupdate:
        description:
            - Update Macports and the ports tree, either prior to installing ports or as a separate step.
            - Equivalent to running C(port selfupdate).
        aliases: ['update_cache', 'update_ports']
        default: false
        type: bool
    state:
        description:
            - Indicates the desired state of the port.
        choices: [ 'present', 'absent', 'active', 'inactive', 'installed', 'removed']
        default: present
        type: str
    upgrade:
        description:
            - Upgrade all outdated ports, either prior to installing ports or as a separate step.
            - Equivalent to running C(port upgrade outdated).
        default: false
        type: bool
    variant:
        description:
            - A port variant specification.
            - 'C(variant) is only supported with state: I(installed)/I(present).'
        aliases: ['variants']
        type: str
'''
EXAMPLES = '''
- name: Install the foo port
  community.general.macports:
    name: foo

- name: Install the universal, x11 variant of the foo port
  community.general.macports:
    name: foo
    variant: +universal+x11

- name: Install a list of ports
  community.general.macports:
    name: "{{ ports }}"
  vars:
    ports:
    - foo
    - foo-tools

- name: Update Macports and the ports tree, then upgrade all outdated ports
  community.general.macports:
    selfupdate: true
    upgrade: true

- name: Update Macports and the ports tree, then install the foo port
  community.general.macports:
    name: foo
    selfupdate: true

- name: Remove the foo port
  community.general.macports:
    name: foo
    state: absent

- name: Activate the foo port
  community.general.macports:
    name: foo
    state: active

- name: Deactivate the foo port
  community.general.macports:
    name: foo
    state: inactive
'''

import re

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves import shlex_quote


def selfupdate(module, port_path):
    """ Update Macports and the ports tree. """

    rc, out, err = module.run_command("%s -v selfupdate" % port_path)

    if rc == 0:
        updated = any(
            re.search(r'Total number of ports parsed:\s+[^0]', s.strip()) or
            re.search(r'Installing new Macports release', s.strip())
            for s in out.split('\n')
            if s
        )
        if updated:
            changed = True
            msg = "Macports updated successfully"
        else:
            changed = False
            msg = "Macports already up-to-date"

        return (changed, msg, out, err)
    else:
        module.fail_json(msg="Failed to update Macports", stdout=out, stderr=err)


def upgrade(module, port_path):
    """ Upgrade outdated ports. """

    rc, out, err = module.run_command("%s upgrade outdated" % port_path)

    # rc is 1 when nothing to upgrade so check stdout first.
    if out.strip() == "Nothing to upgrade.":
        changed = False
        msg = "Ports already upgraded"
        return (changed, msg, out, err)
    elif rc == 0:
        changed = True
        msg = "Outdated ports upgraded successfully"
        return (changed, msg, out, err)
    else:
        module.fail_json(msg="Failed to upgrade outdated ports", stdout=out, stderr=err)


def query_port(module, port_path, name, state="present"):
    """ Returns whether a port is installed or not. """

    if state == "present":

        rc, out, err = module.run_command([port_path, "-q", "installed", name])

        if rc == 0 and out.strip().startswith(name + " "):
            return True

        return False

    elif state == "active":

        rc, out, err = module.run_command([port_path, "-q", "installed", name])

        if rc == 0 and "(active)" in out:
            return True

        return False


def remove_ports(module, port_path, ports, stdout, stderr):
    """ Uninstalls one or more ports if installed. """

    remove_c = 0
    # Using a for loop in case of error, we can report the port that failed
    for port in ports:
        # Query the port first, to see if we even need to remove
        if not query_port(module, port_path, port):
            continue

        rc, out, err = module.run_command("%s uninstall %s" % (port_path, port))
        stdout += out
        stderr += err
        if query_port(module, port_path, port):
            module.fail_json(msg="Failed to remove %s: %s" % (port, err), stdout=stdout, stderr=stderr)

        remove_c += 1

    if remove_c > 0:

        module.exit_json(changed=True, msg="Removed %s port(s)" % remove_c, stdout=stdout, stderr=stderr)

    module.exit_json(changed=False, msg="Port(s) already absent", stdout=stdout, stderr=stderr)


def install_ports(module, port_path, ports, variant, stdout, stderr):
    """ Installs one or more ports if not already installed. """

    install_c = 0

    for port in ports:
        if query_port(module, port_path, port):
            continue

        rc, out, err = module.run_command("%s install %s %s" % (port_path, port, variant))
        stdout += out
        stderr += err
        if not query_port(module, port_path, port):
            module.fail_json(msg="Failed to install %s: %s" % (port, err), stdout=stdout, stderr=stderr)

        install_c += 1

    if install_c > 0:
        module.exit_json(changed=True, msg="Installed %s port(s)" % (install_c), stdout=stdout, stderr=stderr)

    module.exit_json(changed=False, msg="Port(s) already present", stdout=stdout, stderr=stderr)


def activate_ports(module, port_path, ports, stdout, stderr):
    """ Activate a port if it's inactive. """

    activate_c = 0

    for port in ports:
        if not query_port(module, port_path, port):
            module.fail_json(msg="Failed to activate %s, port(s) not present" % (port), stdout=stdout, stderr=stderr)

        if query_port(module, port_path, port, state="active"):
            continue

        rc, out, err = module.run_command("%s activate %s" % (port_path, port))
        stdout += out
        stderr += err

        if not query_port(module, port_path, port, state="active"):
            module.fail_json(msg="Failed to activate %s: %s" % (port, err), stdout=stdout, stderr=stderr)

        activate_c += 1

    if activate_c > 0:
        module.exit_json(changed=True, msg="Activated %s port(s)" % (activate_c), stdout=stdout, stderr=stderr)

    module.exit_json(changed=False, msg="Port(s) already active", stdout=stdout, stderr=stderr)


def deactivate_ports(module, port_path, ports, stdout, stderr):
    """ Deactivate a port if it's active. """

    deactivated_c = 0

    for port in ports:
        if not query_port(module, port_path, port):
            module.fail_json(msg="Failed to deactivate %s, port(s) not present" % (port), stdout=stdout, stderr=stderr)

        if not query_port(module, port_path, port, state="active"):
            continue

        rc, out, err = module.run_command("%s deactivate %s" % (port_path, port))
        stdout += out
        stderr += err
        if query_port(module, port_path, port, state="active"):
            module.fail_json(msg="Failed to deactivate %s: %s" % (port, err), stdout=stdout, stderr=stderr)

        deactivated_c += 1

    if deactivated_c > 0:
        module.exit_json(changed=True, msg="Deactivated %s port(s)" % (deactivated_c), stdout=stdout, stderr=stderr)

    module.exit_json(changed=False, msg="Port(s) already inactive", stdout=stdout, stderr=stderr)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='list', elements='str', aliases=["port"]),
            selfupdate=dict(aliases=["update_cache", "update_ports"], default=False, type='bool'),
            state=dict(default="present", choices=["present", "installed", "absent", "removed", "active", "inactive"]),
            upgrade=dict(default=False, type='bool'),
            variant=dict(aliases=["variants"], default=None, type='str')
        )
    )

    stdout = ""
    stderr = ""

    port_path = module.get_bin_path('port', True, ['/opt/local/bin'])

    p = module.params

    if p["selfupdate"]:
        (changed, msg, out, err) = selfupdate(module, port_path)
        stdout += out
        stderr += err
        if not (p["name"] or p["upgrade"]):
            module.exit_json(changed=changed, msg=msg, stdout=stdout, stderr=stderr)

    if p["upgrade"]:
        (changed, msg, out, err) = upgrade(module, port_path)
        stdout += out
        stderr += err
        if not p["name"]:
            module.exit_json(changed=changed, msg=msg, stdout=stdout, stderr=stderr)

    pkgs = p["name"]

    variant = p["variant"]

    if p["state"] in ["present", "installed"]:
        install_ports(module, port_path, pkgs, variant, stdout, stderr)

    elif p["state"] in ["absent", "removed"]:
        remove_ports(module, port_path, pkgs, stdout, stderr)

    elif p["state"] == "active":
        activate_ports(module, port_path, pkgs, stdout, stderr)

    elif p["state"] == "inactive":
        deactivate_ports(module, port_path, pkgs, stdout, stderr)


if __name__ == '__main__':
    main()
