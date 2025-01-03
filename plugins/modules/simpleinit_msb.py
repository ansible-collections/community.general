#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2016-2023, Vlad Glagolev <scm@vaygr.net>
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: simpleinit_msb
short_description: Manage services on Source Mage GNU/Linux
version_added: 7.5.0
description:
  - Controls services on remote hosts using C(simpleinit-msb).
notes:
  - This module needs ansible-core 2.15.5 or newer. Older versions have a broken and insufficient daemonize functionality.
author: "Vlad Glagolev (@vaygr)"
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
    required: false
    choices: [running, started, stopped, restarted, reloaded]
    description:
      - V(started)/V(stopped) are idempotent actions that do not run commands unless necessary. V(restarted) always bounces
        the service. V(reloaded) always reloads.
      - At least one of O(state) and O(enabled) are required.
      - Note that V(reloaded) starts the service if it is not already started, even if your chosen init system would not normally.
  enabled:
    type: bool
    required: false
    description:
      - Whether the service should start on boot.
      - At least one of O(state) and O(enabled) are required.
"""

EXAMPLES = r"""
- name: Example action to start service httpd, if not running
  community.general.simpleinit_msb:
    name: httpd
    state: started

- name: Example action to stop service httpd, if running
  community.general.simpleinit_msb:
    name: httpd
    state: stopped

- name: Example action to restart service httpd, in all cases
  community.general.simpleinit_msb:
    name: httpd
    state: restarted

- name: Example action to reload service httpd, in all cases
  community.general.simpleinit_msb:
    name: httpd
    state: reloaded

- name: Example action to enable service httpd, and not touch the running state
  community.general.simpleinit_msb:
    name: httpd
    enabled: true
"""

import os
import re

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.service import daemonize


class SimpleinitMSB(object):
    """
    Main simpleinit-msb service manipulation class
    """

    def __init__(self, module):
        self.module = module
        self.name = module.params['name']
        self.state = module.params['state']
        self.enable = module.params['enabled']
        self.changed = False
        self.running = None
        self.action = None
        self.telinit_cmd = None
        self.svc_change = False

    def execute_command(self, cmd, daemon=False):
        if not daemon:
            return self.module.run_command(cmd)
        else:
            return daemonize(self.module, cmd)

    def check_service_changed(self):
        if self.state and self.running is None:
            self.module.fail_json(msg="failed determining service state, possible typo of service name?")
        # Find out if state has changed
        if not self.running and self.state in ["started", "running", "reloaded"]:
            self.svc_change = True
        elif self.running and self.state in ["stopped", "reloaded"]:
            self.svc_change = True
        elif self.state == "restarted":
            self.svc_change = True
        if self.module.check_mode and self.svc_change:
            self.module.exit_json(changed=True, msg='service state changed')

    def modify_service_state(self):
        # Only do something if state will change
        if self.svc_change:
            # Control service
            if self.state in ['started', 'running']:
                self.action = "start"
            elif not self.running and self.state == 'reloaded':
                self.action = "start"
            elif self.state == 'stopped':
                self.action = "stop"
            elif self.state == 'reloaded':
                self.action = "reload"
            elif self.state == 'restarted':
                self.action = "restart"

            if self.module.check_mode:
                self.module.exit_json(changed=True, msg='changing service state')

            return self.service_control()
        else:
            # If nothing needs to change just say all is well
            rc = 0
            err = ''
            out = ''
            return rc, out, err

    def get_service_tools(self):
        paths = ['/sbin', '/usr/sbin', '/bin', '/usr/bin']
        binaries = ['telinit']
        location = dict()

        for binary in binaries:
            location[binary] = self.module.get_bin_path(binary, opt_dirs=paths)

        if location.get('telinit', False) and os.path.exists("/etc/init.d/smgl_init"):
            self.telinit_cmd = location['telinit']

        if self.telinit_cmd is None:
            self.module.fail_json(msg='cannot find telinit script for simpleinit-msb, aborting...')

    def get_service_status(self):
        self.action = "status"
        rc, status_stdout, status_stderr = self.service_control()

        if self.running is None and status_stdout.count('\n') <= 1:
            cleanout = status_stdout.lower().replace(self.name.lower(), '')

            if "is not running" in cleanout:
                self.running = False
            elif "is running" in cleanout:
                self.running = True

        return self.running

    def service_enable(self):
        # Check if the service is already enabled/disabled
        if not self.enable ^ self.service_enabled():
            return

        action = "boot" + ("enable" if self.enable else "disable")

        (rc, out, err) = self.execute_command("%s %s %s" % (self.telinit_cmd, action, self.name))

        self.changed = True

        for line in err.splitlines():
            if self.enable and line.find('already enabled') != -1:
                self.changed = False
                break
            if not self.enable and line.find('already disabled') != -1:
                self.changed = False
                break

        if not self.changed:
            return

        return (rc, out, err)

    def service_enabled(self):
        self.service_exists()

        (rc, out, err) = self.execute_command("%s %sd" % (self.telinit_cmd, self.enable))

        service_enabled = False if self.enable else True

        rex = re.compile(r'^%s$' % self.name)

        for line in out.splitlines():
            if rex.match(line):
                service_enabled = True if self.enable else False
                break

        return service_enabled

    def service_exists(self):
        (rc, out, err) = self.execute_command("%s list" % self.telinit_cmd)

        service_exists = False

        rex = re.compile(r'^\w+\s+%s$' % self.name)

        for line in out.splitlines():
            if rex.match(line):
                service_exists = True
                break

        if not service_exists:
            self.module.fail_json(msg='telinit could not find the requested service: %s' % self.name)

    def service_control(self):
        self.service_exists()

        svc_cmd = "%s run %s" % (self.telinit_cmd, self.name)

        rc_state, stdout, stderr = self.execute_command("%s %s" % (svc_cmd, self.action), daemon=True)

        return (rc_state, stdout, stderr)


def build_module():
    return AnsibleModule(
        argument_spec=dict(
            name=dict(required=True, aliases=['service']),
            state=dict(choices=['running', 'started', 'stopped', 'restarted', 'reloaded']),
            enabled=dict(type='bool'),
        ),
        supports_check_mode=True,
        required_one_of=[['state', 'enabled']],
    )


def main():
    module = build_module()

    service = SimpleinitMSB(module)

    rc = 0
    out = ''
    err = ''
    result = {}
    result['name'] = service.name

    # Find service management tools
    service.get_service_tools()

    # Enable/disable service startup at boot if requested
    if service.module.params['enabled'] is not None:
        service.service_enable()
        result['enabled'] = service.enable

    if module.params['state'] is None:
        # Not changing the running state, so bail out now.
        result['changed'] = service.changed
        module.exit_json(**result)

    result['state'] = service.state

    service.get_service_status()

    # Calculate if request will change service state
    service.check_service_changed()

    # Modify service state if necessary
    (rc, out, err) = service.modify_service_state()

    if rc != 0:
        if err:
            module.fail_json(msg=err)
        else:
            module.fail_json(msg=out)

    result['changed'] = service.changed | service.svc_change
    if service.module.params['enabled'] is not None:
        result['enabled'] = service.module.params['enabled']

    if not service.module.params['state']:
        status = service.get_service_status()
        if status is None:
            result['state'] = 'absent'
        elif status is False:
            result['state'] = 'started'
        else:
            result['state'] = 'stopped'
    else:
        # as we may have just bounced the service the service command may not
        # report accurate state at this moment so just show what we ran
        if service.module.params['state'] in ['started', 'restarted', 'running', 'reloaded']:
            result['state'] = 'started'
        else:
            result['state'] = 'stopped'

    module.exit_json(**result)


if __name__ == '__main__':
    main()
