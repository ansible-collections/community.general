#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2015, Adam Števko <adam.stevko@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: dladm_etherstub
short_description: Manage etherstubs on Solaris/illumos systems.
description:
    - Create or delete etherstubs on Solaris/illumos systems.
author: Adam Števko (@xen0l)
options:
    name:
        description:
            - Etherstub name.
        required: true
    temporary:
        description:
            - Specifies that the etherstub is temporary. Temporary etherstubs
              do not persist across reboots.
        required: false
        default: false
        type: bool
    state:
        description:
            - Create or delete Solaris/illumos etherstub.
        required: false
        default: "present"
        choices: [ "present", "absent" ]
'''

EXAMPLES = '''
# Create 'stub0' etherstub
- dladm_etherstub:
    name: stub0
    state: present

# Remove 'stub0 etherstub
- dladm_etherstub:
    name: stub0
    state: absent
'''

RETURN = '''
name:
    description: etherstub name
    returned: always
    type: str
    sample: "switch0"
state:
    description: state of the target
    returned: always
    type: str
    sample: "present"
temporary:
    description: etherstub's persistence
    returned: always
    type: bool
    sample: "True"
'''
from ansible.module_utils.basic import AnsibleModule


class Etherstub(object):

    def __init__(self, module):
        self.module = module

        self.name = module.params['name']
        self.temporary = module.params['temporary']
        self.state = module.params['state']

    def etherstub_exists(self):
        cmd = [self.module.get_bin_path('dladm', True)]

        cmd.append('show-etherstub')
        cmd.append(self.name)

        (rc, _, _) = self.module.run_command(cmd)

        if rc == 0:
            return True
        else:
            return False

    def create_etherstub(self):
        cmd = [self.module.get_bin_path('dladm', True)]

        cmd.append('create-etherstub')

        if self.temporary:
            cmd.append('-t')
        cmd.append(self.name)

        return self.module.run_command(cmd)

    def delete_etherstub(self):
        cmd = [self.module.get_bin_path('dladm', True)]

        cmd.append('delete-etherstub')

        if self.temporary:
            cmd.append('-t')
        cmd.append(self.name)

        return self.module.run_command(cmd)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            temporary=dict(default=False, type='bool'),
            state=dict(default='present', choices=['absent', 'present']),
        ),
        supports_check_mode=True
    )

    etherstub = Etherstub(module)

    rc = None
    out = ''
    err = ''
    result = {}
    result['name'] = etherstub.name
    result['state'] = etherstub.state
    result['temporary'] = etherstub.temporary

    if etherstub.state == 'absent':
        if etherstub.etherstub_exists():
            if module.check_mode:
                module.exit_json(changed=True)
            (rc, out, err) = etherstub.delete_etherstub()
            if rc != 0:
                module.fail_json(name=etherstub.name, msg=err, rc=rc)
    elif etherstub.state == 'present':
        if not etherstub.etherstub_exists():
            if module.check_mode:
                module.exit_json(changed=True)
            (rc, out, err) = etherstub.create_etherstub()

        if rc is not None and rc != 0:
            module.fail_json(name=etherstub.name, msg=err, rc=rc)

    if rc is None:
        result['changed'] = False
    else:
        result['changed'] = True

    if out:
        result['stdout'] = out
    if err:
        result['stderr'] = err

    module.exit_json(**result)


if __name__ == '__main__':
    main()
