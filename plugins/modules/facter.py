#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2012, Michael DeHaan <michael.dehaan@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: facter
short_description: Runs the discovery program C(facter) on the remote system
description:
  - Runs the C(facter) discovery program (U(https://github.com/puppetlabs/facter)) on the remote system, returning JSON data
    that can be useful for inventory purposes.
deprecated:
  removed_in: 12.0.0
  why: The module has been replaced by M(community.general.facter_facts).
  alternative: Use M(community.general.facter_facts) instead.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options:
  arguments:
    description:
      - Specifies arguments for facter.
    type: list
    elements: str
requirements:
  - facter
  - ruby-json
author:
  - Ansible Core Team
  - Michael DeHaan
"""

EXAMPLES = r"""
# Example command-line invocation
# ansible www.example.net -m facter

- name: Execute facter no arguments
  community.general.facter:

- name: Execute facter with arguments
  community.general.facter:
    arguments:
      - -p
      - system_uptime
      - timezone
      - is_virtual
"""
import json

from ansible.module_utils.basic import AnsibleModule


def main():
    module = AnsibleModule(
        argument_spec=dict(
            arguments=dict(type='list', elements='str')
        )
    )

    facter_path = module.get_bin_path(
        'facter',
        opt_dirs=['/opt/puppetlabs/bin'])

    cmd = [facter_path, "--json"]
    if module.params['arguments']:
        cmd += module.params['arguments']

    rc, out, err = module.run_command(cmd, check_rc=True)
    module.exit_json(**json.loads(out))


if __name__ == '__main__':
    main()
