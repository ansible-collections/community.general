#!/usr/bin/python

# Copyright (c) 2024, Ryan Cook <rcook@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt
# or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
---
module: bootc_manage
version_added: 9.3.0
author:
- Ryan Cook (@cooktheryan)
short_description: Bootc Switch and Upgrade
description:
    - This module manages the switching and upgrading of C(bootc).
options:
    state:
        description:
            - 'Control to apply the latest image or switch the image.'
            - 'B(Note:) This will not reboot the system.'
            - 'Please use M(ansible.builtin.reboot) to reboot the system.'
        required: true
        type: str
        choices: ['switch', 'latest']
    image:
        description:
            - 'The image to switch to.'
            - 'This is required when O(state=switch).'
        required: false
        type: str

'''

EXAMPLES = '''
# Switch to a different image
- name: Provide image to switch to a different image and retain the current running image
  community.general.bootc_manage:
    state: switch
    image: "example.com/image:latest"

# Apply updates of the current running image
- name: Apply updates of the current running image
  community.general.bootc_manage:
    state: latest
'''

RETURN = '''
'''


from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.locale import get_best_parsable_locale


def main():
    argument_spec = dict(
        state=dict(type='str', required=True, choices=['switch', 'latest']),
        image=dict(type='str', required=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=[
            ('state', 'switch', ['image']),
        ],
    )

    state = module.params['state']
    image = module.params['image']

    if state == 'switch':
        command = ['bootc', 'switch', image, '--retain']
    elif state == 'latest':
        command = ['bootc', 'upgrade']

    locale = get_best_parsable_locale(module)
    module.run_command_environ_update = dict(LANG=locale, LC_ALL=locale, LC_MESSAGES=locale, LC_CTYPE=locale, LANGUAGE=locale)
    rc, stdout, err = module.run_command(command, check_rc=True)

    if 'Queued for next boot: ' in stdout:
        result = {'changed': True, 'stdout': stdout}
        module.exit_json(**result)
    elif 'No changes in ' in stdout or 'Image specification is unchanged.' in stdout:
        result = {'changed': False, 'stdout': stdout}
        module.exit_json(**result)
    else:
        result = {'changed': False, 'stderr': err}
        module.fail_json(msg='ERROR: Command execution failed.', **result)


if __name__ == '__main__':
    main()
