#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2016, Andrew Gaffney <andrew@agaffney.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: openwrt_init
author:
  - "Andrew Gaffney (@agaffney)"
short_description: Manage services on OpenWrt
description:
  - Controls OpenWrt services on remote hosts.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  name:
    type: str
    description:
      - Name of the service.
    required: true
    aliases: ['service']
  state:
    type: str
    description:
      - V(started)/V(stopped) are idempotent actions that will not run commands unless necessary.
      - V(restarted) will always bounce the service.
      - V(reloaded) will always reload.
    choices: ['started', 'stopped', 'restarted', 'reloaded']
  enabled:
    description:
      - Whether the service should start on boot. B(At least one of state and enabled are required).
    type: bool
  pattern:
    type: str
    description:
      - If the service does not respond to the 'running' command, name a substring to look for as would be found in the output
        of the C(ps) command as a stand-in for a 'running' result. If the string is found, the service will be assumed to
        be running.
notes:
  - One option other than O(name) is required.
requirements:
  - An OpenWrt system (with python)
"""

EXAMPLES = r"""
- name: Start service httpd, if not running
  community.general.openwrt_init:
    state: started
    name: httpd

- name: Stop service cron, if running
  community.general.openwrt_init:
    name: cron
    state: stopped

- name: Reload service httpd, in all cases
  community.general.openwrt_init:
    name: httpd
    state: reloaded

- name: Enable service httpd
  community.general.openwrt_init:
    name: httpd
    enabled: true
"""

RETURN = r"""
"""

import os
from ansible.module_utils.basic import AnsibleModule

module = None
init_script = None


# ===============================
# Check if service is enabled
def is_enabled():
    rc, dummy, dummy = module.run_command([init_script, 'enabled'])
    return rc == 0


# ===========================================
# Main control flow
def main():
    global module, init_script
    # init
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True, type='str', aliases=['service']),
            state=dict(type='str', choices=['started', 'stopped', 'restarted', 'reloaded']),
            enabled=dict(type='bool'),
            pattern=dict(type='str'),
        ),
        supports_check_mode=True,
        required_one_of=[('state', 'enabled')],
    )

    # initialize
    service = module.params['name']
    init_script = '/etc/init.d/' + service
    result = {
        'name': service,
        'changed': False,
    }
    # check if service exists
    if not os.path.exists(init_script):
        module.fail_json(msg='service %s does not exist' % service)

    # Enable/disable service startup at boot if requested
    if module.params['enabled'] is not None:
        # do we need to enable the service?
        enabled = is_enabled()

        # default to current state
        result['enabled'] = enabled

        # Change enable/disable if needed
        if enabled != module.params['enabled']:
            result['changed'] = True
            action = 'enable' if module.params['enabled'] else 'disable'

            if not module.check_mode:
                rc, dummy, err = module.run_command([init_script, action])
                # openwrt init scripts can return a non-zero exit code on a successful 'enable'
                # command if the init script doesn't contain a STOP value, so we ignore the exit
                # code and explicitly check if the service is now in the desired state
                if is_enabled() != module.params['enabled']:
                    module.fail_json(msg="Unable to %s service %s: %s" % (action, service, err))

            result['enabled'] = not enabled

    if module.params['state'] is not None:
        running = False

        # check if service is currently running
        if module.params['pattern']:
            # Find ps binary
            psbin = module.get_bin_path('ps', True)

            # this should be busybox ps, so we only want/need to the 'w' option
            rc, psout, dummy = module.run_command([psbin, 'w'])
            # If rc is 0, set running as appropriate
            if rc == 0:
                lines = psout.split("\n")
                running = any((module.params['pattern'] in line and "pattern=" not in line) for line in lines)
        else:
            rc, dummy, dummy = module.run_command([init_script, 'running'])
            if rc == 0:
                running = True

        # default to desired state
        result['state'] = module.params['state']

        # determine action, if any
        action = None
        if module.params['state'] == 'started':
            if not running:
                action = 'start'
                result['changed'] = True
        elif module.params['state'] == 'stopped':
            if running:
                action = 'stop'
                result['changed'] = True
        else:
            action = module.params['state'][:-2]  # remove 'ed' from restarted/reloaded
            result['state'] = 'started'
            result['changed'] = True

        if action:
            if not module.check_mode:
                rc, dummy, err = module.run_command([init_script, action])
                if rc != 0:
                    module.fail_json(msg="Unable to %s service %s: %s" % (action, service, err))

    module.exit_json(**result)


if __name__ == '__main__':
    main()
