#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017, Joris Weijters <joris.weijters@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
author:
  - Joris Weijters (@molekuul)
module: aix_inittab
short_description: Manages the C(inittab) on AIX
description:
  - Manages the C(inittab) on AIX.
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
      - Name of the C(inittab) entry.
    type: str
    required: true
    aliases: [service]
  runlevel:
    description:
      - Runlevel of the entry.
    type: str
    required: true
  action:
    description:
      - Action what the init has to do with this entry.
    type: str
    choices:
      - boot
      - bootwait
      - hold
      - initdefault
      - 'off'
      - once
      - ondemand
      - powerfail
      - powerwait
      - respawn
      - sysinit
      - wait
  command:
    description:
      - What command has to run.
    type: str
    required: true
  insertafter:
    description:
      - After which inittabline should the new entry inserted.
    type: str
  state:
    description:
      - Whether the entry should be present or absent in the inittab file.
    type: str
    choices: [absent, present]
    default: present
notes:
  - The changes are persistent across reboots.
  - You need root rights to read or adjust the inittab with the C(lsitab), C(chitab), C(mkitab) or C(rmitab) commands.
  - Tested on AIX 7.1.
requirements:
  - itertools
"""

EXAMPLES = r"""
# Add service startmyservice to the inittab, directly after service existingservice.
- name: Add startmyservice to inittab
  community.general.aix_inittab:
    name: startmyservice
    runlevel: 4
    action: once
    command: echo hello
    insertafter: existingservice
    state: present
  become: true

# Change inittab entry startmyservice to runlevel "2" and processaction "wait".
- name: Change startmyservice to inittab
  community.general.aix_inittab:
    name: startmyservice
    runlevel: 2
    action: wait
    command: echo hello
    state: present
  become: true

- name: Remove startmyservice from inittab
  community.general.aix_inittab:
    name: startmyservice
    runlevel: 2
    action: wait
    command: echo hello
    state: absent
  become: true
"""

RETURN = r"""
name:
  description: Name of the adjusted C(inittab) entry.
  returned: always
  type: str
  sample: startmyservice
"""

# Import necessary libraries
try:
    # python 2
    from itertools import izip
except ImportError:
    izip = zip

from ansible.module_utils.basic import AnsibleModule

# end import modules
# start defining the functions


def check_current_entry(module):
    # Check if entry exists, if not return False in exists in return dict,
    # if true return True and the entry in return dict
    existsdict = {'exist': False}
    lsitab = module.get_bin_path('lsitab')
    (rc, out, err) = module.run_command([lsitab, module.params['name']])
    if rc == 0:
        keys = ('name', 'runlevel', 'action', 'command')
        values = out.split(":")
        # strip non readable characters as \n
        values = map(lambda s: s.strip(), values)
        existsdict = dict(izip(keys, values))
        existsdict.update({'exist': True})
    return existsdict


def main():
    # initialize
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True, aliases=['service']),
            runlevel=dict(type='str', required=True),
            action=dict(type='str', choices=[
                'boot',
                'bootwait',
                'hold',
                'initdefault',
                'off',
                'once',
                'ondemand',
                'powerfail',
                'powerwait',
                'respawn',
                'sysinit',
                'wait',
            ]),
            command=dict(type='str', required=True),
            insertafter=dict(type='str'),
            state=dict(type='str', default='present', choices=['absent', 'present']),
        ),
        supports_check_mode=True,
    )

    result = {
        'name': module.params['name'],
        'changed': False,
        'msg': ""
    }

    # Find commandline strings
    mkitab = module.get_bin_path('mkitab')
    rmitab = module.get_bin_path('rmitab')
    chitab = module.get_bin_path('chitab')
    rc = 0
    err = None

    # check if the new entry exists
    current_entry = check_current_entry(module)

    # if action is install or change,
    if module.params['state'] == 'present':

        # create new entry string
        new_entry = module.params['name'] + ":" + module.params['runlevel'] + \
            ":" + module.params['action'] + ":" + module.params['command']

        # If current entry exists or fields are different(if the entry does not
        # exists, then the entry will be created
        if (not current_entry['exist']) or (
                module.params['runlevel'] != current_entry['runlevel'] or
                module.params['action'] != current_entry['action'] or
                module.params['command'] != current_entry['command']):

            # If the entry does exist then change the entry
            if current_entry['exist']:
                if not module.check_mode:
                    (rc, out, err) = module.run_command([chitab, new_entry])
                if rc != 0:
                    module.fail_json(
                        msg="could not change inittab", rc=rc, err=err)
                result['msg'] = "changed inittab entry" + " " + current_entry['name']
                result['changed'] = True

            # If the entry does not exist create the entry
            elif not current_entry['exist']:
                if module.params['insertafter']:
                    if not module.check_mode:
                        (rc, out, err) = module.run_command(
                            [mkitab, '-i', module.params['insertafter'], new_entry])
                else:
                    if not module.check_mode:
                        (rc, out, err) = module.run_command(
                            [mkitab, new_entry])

                if rc != 0:
                    module.fail_json(msg="could not adjust inittab", rc=rc, err=err)
                result['msg'] = "add inittab entry" + " " + module.params['name']
                result['changed'] = True

    elif module.params['state'] == 'absent':
        # If the action is remove and the entry exists then remove the entry
        if current_entry['exist']:
            if not module.check_mode:
                (rc, out, err) = module.run_command(
                    [rmitab, module.params['name']])
                if rc != 0:
                    module.fail_json(
                        msg="could not remove entry from inittab)", rc=rc, err=err)
            result['msg'] = "removed inittab entry" + " " + current_entry['name']
            result['changed'] = True

    module.exit_json(**result)


if __name__ == '__main__':
    main()
