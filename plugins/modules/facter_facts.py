#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2023, Alexei Znamensky
# Copyright (c) 2012, Michael DeHaan <michael.dehaan@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: facter_facts
short_description: Runs the discovery program C(facter) on the remote system and return Ansible facts
version_added: 8.0.0
description:
    - Runs the C(facter) discovery program
      (U(https://github.com/puppetlabs/facter)) on the remote system, returning Ansible facts from the
      JSON data that can be useful for inventory purposes.
extends_documentation_fragment:
    - community.general.attributes
    - community.general.attributes.facts
    - community.general.attributes.facts_module
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
'''

EXAMPLES = '''
- name: Execute facter no arguments
  community.general.facter_facts:

- name: Execute facter with arguments
  community.general.facter_facts:
    arguments:
        - -p
        - system_uptime
        - timezone
        - is_virtual
'''

RETURN = r'''
ansible_facts:
  description: Dictionary with one key C(facter).
  returned: always
  type: dict
  contains:
    facter:
      description: Dictionary containing facts discovered in the remote system.
      returned: always
      type: dict
'''

import json

from ansible.module_utils.basic import AnsibleModule


def main():
    module = AnsibleModule(
        argument_spec=dict(
            arguments=dict(type='list', elements='str'),
        ),
        supports_check_mode=True,
    )

    facter_path = module.get_bin_path(
        'facter',
        opt_dirs=['/opt/puppetlabs/bin'])

    cmd = [facter_path, "--json"]
    if module.params['arguments']:
        cmd += module.params['arguments']

    rc, out, err = module.run_command(cmd, check_rc=True)
    module.exit_json(ansible_facts=dict(facter=json.loads(out)))


if __name__ == '__main__':
    main()
