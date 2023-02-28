#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2012, Boyd Adamson <boyd () boydadamson.com>
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: svr4pkg
short_description: Manage Solaris SVR4 packages
description:
    - Manages SVR4 packages on Solaris 10 and 11.
    - These were the native packages on Solaris <= 10 and are available
      as a legacy feature in Solaris 11.
    - Note that this is a very basic packaging system. It will not enforce
      dependencies on install or remove.
author: "Boyd Adamson (@brontitall)"
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
      - Package name, e.g. C(SUNWcsr)
    required: true
    type: str

  state:
    description:
      - Whether to install (C(present)), or remove (C(absent)) a package.
      - If the package is to be installed, then I(src) is required.
      - The SVR4 package system doesn't provide an upgrade operation. You need to uninstall the old, then install the new package.
    required: true
    choices: ["present", "absent"]
    type: str

  src:
    description:
      - Specifies the location to install the package from. Required when I(state=present).
      - "Can be any path acceptable to the C(pkgadd) command's C(-d) option. e.g.: C(somefile.pkg), C(/dir/with/pkgs), C(http:/server/mypkgs.pkg)."
      - If using a file or directory, they must already be accessible by the host. See the M(ansible.builtin.copy) module for a way to get them there.
    type: str
  proxy:
    description:
      - HTTP[s] proxy to be used if I(src) is a URL.
    type: str
  response_file:
    description:
      - Specifies the location of a response file to be used if package expects input on install. (added in Ansible 1.4)
    required: false
    type: str
  zone:
    description:
      - Whether to install the package only in the current zone, or install it into all zones.
      - The installation into all zones works only if you are working with the global zone.
    required: false
    default: "all"
    choices: ["current", "all"]
    type: str
  category:
    description:
      - Install/Remove category instead of a single package.
    required: false
    type: bool
    default: false
'''

EXAMPLES = '''
- name: Install a package from an already copied file
  community.general.svr4pkg:
    name: CSWcommon
    src: /tmp/cswpkgs.pkg
    state: present

- name: Install a package directly from an http site
  community.general.svr4pkg:
    name: CSWpkgutil
    src: 'http://get.opencsw.org/now'
    state: present
    zone: current

- name: Install a package with a response file
  community.general.svr4pkg:
    name: CSWggrep
    src: /tmp/third-party.pkg
    response_file: /tmp/ggrep.response
    state: present

- name: Ensure that a package is not installed
  community.general.svr4pkg:
    name: SUNWgnome-sound-recorder
    state: absent

- name: Ensure that a category is not installed
  community.general.svr4pkg:
    name: FIREFOX
    state: absent
    category: true
'''


import os
import tempfile

from ansible.module_utils.basic import AnsibleModule


def package_installed(module, name, category):
    cmd = [module.get_bin_path('pkginfo', True), '-q']
    if category:
        cmd.append('-c')
    cmd.append(name)
    rc, out, err = module.run_command(' '.join(cmd))
    if rc == 0:
        return True
    else:
        return False


def create_admin_file():
    (desc, filename) = tempfile.mkstemp(prefix='ansible_svr4pkg', text=True)
    fullauto = b'''
mail=
instance=unique
partial=nocheck
runlevel=quit
idepend=nocheck
rdepend=nocheck
space=quit
setuid=nocheck
conflict=nocheck
action=nocheck
networktimeout=60
networkretries=3
authentication=quit
keystore=/var/sadm/security
proxy=
basedir=default
'''
    os.write(desc, fullauto)
    os.close(desc)
    return filename


def run_command(module, cmd):
    progname = cmd[0]
    cmd[0] = module.get_bin_path(progname, True)
    return module.run_command(cmd)


def package_install(module, name, src, proxy, response_file, zone, category):
    adminfile = create_admin_file()
    cmd = ['pkgadd', '-n']
    if zone == 'current':
        cmd += ['-G']
    cmd += ['-a', adminfile, '-d', src]
    if proxy is not None:
        cmd += ['-x', proxy]
    if response_file is not None:
        cmd += ['-r', response_file]
    if category:
        cmd += ['-Y']
    cmd.append(name)
    (rc, out, err) = run_command(module, cmd)
    os.unlink(adminfile)
    return (rc, out, err)


def package_uninstall(module, name, src, category):
    adminfile = create_admin_file()
    if category:
        cmd = ['pkgrm', '-na', adminfile, '-Y', name]
    else:
        cmd = ['pkgrm', '-na', adminfile, name]
    (rc, out, err) = run_command(module, cmd)
    os.unlink(adminfile)
    return (rc, out, err)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            state=dict(required=True, choices=['present', 'absent']),
            src=dict(default=None),
            proxy=dict(default=None),
            response_file=dict(default=None),
            zone=dict(required=False, default='all', choices=['current', 'all']),
            category=dict(default=False, type='bool')
        ),
        supports_check_mode=True
    )
    state = module.params['state']
    name = module.params['name']
    src = module.params['src']
    proxy = module.params['proxy']
    response_file = module.params['response_file']
    zone = module.params['zone']
    category = module.params['category']
    rc = None
    out = ''
    err = ''
    result = {}
    result['name'] = name
    result['state'] = state

    if state == 'present':
        if src is None:
            module.fail_json(name=name,
                             msg="src is required when state=present")
        if not package_installed(module, name, category):
            if module.check_mode:
                module.exit_json(changed=True)
            (rc, out, err) = package_install(module, name, src, proxy, response_file, zone, category)
            # Stdout is normally empty but for some packages can be
            # very long and is not often useful
            if len(out) > 75:
                out = out[:75] + '...'

    elif state == 'absent':
        if package_installed(module, name, category):
            if module.check_mode:
                module.exit_json(changed=True)
            (rc, out, err) = package_uninstall(module, name, src, category)
            out = out[:75]

    # Returncodes as per pkgadd(1m)
    #    0 Successful completion
    #    1 Fatal error.
    #    2 Warning.
    #    3 Interruption.
    #    4 Administration.
    #    5 Administration. Interaction  is  required.  Do  not  use pkgadd -n.
    #   10 Reboot after installation of all packages.
    #   20 Reboot after installation of this package.
    #   99 (observed) pkgadd: ERROR: could not process datastream from </tmp/pkgutil.pkg>
    if rc in (0, 2, 3, 10, 20):
        result['changed'] = True
    # no install nor uninstall, or failed
    else:
        result['changed'] = False

    # rc will be none when the package already was installed and no action took place
    # Only return failed=False when the returncode is known to be good as there may be more
    # undocumented failure return codes
    if rc not in (None, 0, 2, 10, 20):
        result['failed'] = True
    else:
        result['failed'] = False

    if out:
        result['stdout'] = out
    if err:
        result['stderr'] = err

    module.exit_json(**result)


if __name__ == '__main__':
    main()
