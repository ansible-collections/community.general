#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: rax_identity
short_description: Load Rackspace Cloud Identity
description:
     - Verifies Rackspace Cloud credentials and returns identity information
options:
  state:
    type: str
    description:
      - Indicate desired state of the resource
    choices: ['present']
    default: present
    required: false
author:
    - "Christopher H. Laco (@claco)"
    - "Matt Martz (@sivel)"
extends_documentation_fragment:
- community.general.rackspace.openstack

'''

EXAMPLES = '''
- name: Load Rackspace Cloud Identity
  gather_facts: false
  hosts: local
  connection: local
  tasks:
    - name: Load Identity
      local_action:
        module: rax_identity
        credentials: ~/.raxpub
        region: DFW
      register: rackspace_identity
'''

try:
    import pyrax
    HAS_PYRAX = True
except ImportError:
    HAS_PYRAX = False

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.rax import (rax_argument_spec, rax_required_together, rax_to_dict,
                                                                            setup_rax_module)


def cloud_identity(module, state, identity):
    instance = dict(
        authenticated=identity.authenticated,
        credentials=identity._creds_file
    )
    changed = False

    instance.update(rax_to_dict(identity))
    instance['services'] = instance.get('services', {}).keys()

    if state == 'present':
        if not identity.authenticated:
            module.fail_json(msg='Credentials could not be verified!')

    module.exit_json(changed=changed, identity=instance)


def main():
    argument_spec = rax_argument_spec()
    argument_spec.update(
        dict(
            state=dict(default='present', choices=['present'])
        )
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_together=rax_required_together()
    )

    if not HAS_PYRAX:
        module.fail_json(msg='pyrax is required for this module')

    state = module.params.get('state')

    setup_rax_module(module, pyrax)

    if not pyrax.identity:
        module.fail_json(msg='Failed to instantiate client. This '
                             'typically indicates an invalid region or an '
                             'incorrectly capitalized region name.')

    cloud_identity(module, state, pyrax.identity)


if __name__ == '__main__':
    main()
