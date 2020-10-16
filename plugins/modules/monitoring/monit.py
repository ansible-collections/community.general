#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2013, Darryl Stoflet <stoflet@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: monit
short_description: Manage the state of a program monitored via Monit
description:
     - Manage the state of a program monitored via I(Monit)
options:
  name:
    description:
      - The name of the I(monit) program/process to manage
    required: true
  state:
    description:
      - The state of service
    required: true
    choices: [ "present", "started", "stopped", "restarted", "monitored", "unmonitored", "reloaded" ]
  timeout:
    description:
      - If there are pending actions for the service monitored by monit, then Ansible will check
        for up to this many seconds to verify the requested action has been performed.
        Ansible will sleep for five seconds between each check.
    default: 300
author: "Darryl Stoflet (@dstoflet)"
'''

EXAMPLES = '''
- name: Manage the state of program httpd to be in started state
  community.general.monit:
    name: httpd
    state: started
'''

import time
import re

from collections import namedtuple

from ansible.module_utils.basic import AnsibleModule

STATE_COMMAND_MAP = {
    'stopped': 'stop',
    'started': 'start',
    'monitored': 'monitor',
    'unmonitored': 'unmonitor',
    'restarted': 'restart'
}

MIN_VERSION = (5, 21)


class StatusValue(namedtuple("Status", "value, is_pending")):
    MISSING = 'missing'
    OK = 'ok'
    NOT_MONITORED = 'not_monitored'
    INITIALIZING = 'initializing'
    DOES_NOT_EXIST = 'does_not_exist'
    ALL_STATUS = [
        MISSING, OK, NOT_MONITORED, INITIALIZING, DOES_NOT_EXIST
    ]

    def __new__(cls, value, is_pending=False):
        return super(StatusValue, cls).__new__(cls, value, is_pending)

    def pending(self):
        return StatusValue(self.value, True)

    def __getattr__(self, item):
        if item in ('is_%s' % status for status in self.ALL_STATUS):
            return self.value == getattr(self, item[3:].upper())
        raise AttributeError(item)


class Status(object):
    MISSING = StatusValue(StatusValue.MISSING)
    OK = StatusValue(StatusValue.OK)
    NOT_MONITORED = StatusValue(StatusValue.NOT_MONITORED)
    INITIALIZING = StatusValue(StatusValue.INITIALIZING)
    DOES_NOT_EXIST = StatusValue(StatusValue.DOES_NOT_EXIST)


class Monit(object):
    def __init__(self, module, monit_bin_path, service_name, timeout):
        self.module = module
        self.monit_bin_path = monit_bin_path
        self.process_name = service_name
        self.timeout = timeout

        self._monit_version = None
        self._sleep_time = 5

    def monit_version(self):
        if self._monit_version is None:
            rc, out, err = self.module.run_command('%s -V' % self.monit_bin_path, check_rc=True)
            version_line = out.split('\n')[0]
            version = re.search(r"[0-9]+\.[0-9]+", version_line).group().split('.')
            # Use only major and minor even if there are more these should be enough
            self._monit_version = int(version[0]), int(version[1])
        return self._monit_version

    def check_version(self):
        if self.monit_version() < MIN_VERSION:
            min_version = '.'.join(str(v) for v in MIN_VERSION)
            self.module.fail_json(msg='Monit version not compatible with module. Install version >= %s' % min_version)

    def get_status(self):
        """Return the status of the process in monit."""
        command = '%s status %s -B' % (self.monit_bin_path, self.process_name)
        rc, out, err = self.module.run_command(command, check_rc=True)
        return self._parse_status(out)

    def _parse_status(self, output):
        if "Process '%s'" % self.process_name not in output:
            return Status.MISSING

        status_val = re.findall(r"^\s*status\s*([\w\- ]+)", output, re.MULTILINE)
        if not status_val:
            self.module.fail_json(msg="Unable to find process status")

        status_val = status_val[0].strip().upper()
        if ' - ' not in status_val:
            status_val = status_val.replace(' ', '_')
            return getattr(Status, status_val)
        else:
            status_val, substatus = status_val.split(' - ')
            action, state = substatus.split()
            if action in ['START', 'INITIALIZING', 'RESTART', 'MONITOR']:
                status = Status.OK
            else:
                status = Status.NOT_MONITORED

            if state == 'pending':
                status = status.pending()
            return status

    def is_process_present(self):
        rc, out, err = self.module.run_command('%s summary -B' % (self.monit_bin_path), check_rc=True)
        return bool(re.findall(r'\b%s\b' % self.process_name, out))

    def is_process_running(self):
        return self.get_status().is_ok

    def run_command(self, command):
        """Runs a monit command, and returns the new status."""
        return self.module.run_command('%s %s %s' % (self.monit_bin_path, command, self.process_name), check_rc=True)

    def wait_for_monit_to_stop_pending(self, state):
        """Fails this run if there is no status or it's pending/initializing for timeout"""
        timeout_time = time.time() + self.timeout

        running_status = self.get_status()
        waiting_status = [
            StatusValue.MISSING,
            StatusValue.INITIALIZING,
            StatusValue.DOES_NOT_EXIST,
        ]
        while running_status.is_pending or (running_status.value in waiting_status):
            if time.time() >= timeout_time:
                self.module.fail_json(
                    msg='waited too long for "pending", or "initiating" status to go away ({0})'.format(
                        running_status
                    ),
                    state=state
                )

            if self._sleep_time:
                time.sleep(self._sleep_time)
            running_status = self.get_status()

    def reload(self):
        rc, out, err = self.module.run_command('%s reload' % self.monit_bin_path)
        if rc != 0:
            self.module.fail_json(msg='monit reload failed', stdout=out, stderr=err)
        self.wait_for_monit_to_stop_pending('reloaded')
        self.module.exit_json(changed=True, name=self.process_name, state='reloaded')

    def present(self):
        self.run_command('reload')
        if not self.is_process_present():
            self.wait_for_monit_to_stop_pending('present')
        self.module.exit_json(changed=True, name=self.process_name, state='present')

    def change_state(self, state, expected_status, invert_expected=None):
        self.run_command(STATE_COMMAND_MAP[state])
        status = self.get_status()
        status_match = status.value == expected_status.value
        if invert_expected:
            status_match = not status_match
        if status_match:
            self.module.exit_json(changed=True, name=self.process_name, state=state)
        self.module.fail_json(msg='%s process not %s' % (self.process_name, state), status=repr(status))

    def stop(self):
        self.change_state('stopped', Status.NOT_MONITORED)

    def unmonitor(self):
        self.change_state('unmonitored', Status.NOT_MONITORED)

    def restart(self):
        self.change_state('restarted', Status.OK)

    def start(self):
        self.change_state('started', Status.OK)

    def monitor(self):
        self.change_state('monitored', Status.NOT_MONITORED, invert_expected=True)


def main():
    arg_spec = dict(
        name=dict(required=True),
        timeout=dict(default=300, type='int'),
        state=dict(required=True, choices=['present', 'started', 'restarted', 'stopped', 'monitored', 'unmonitored', 'reloaded'])
    )

    module = AnsibleModule(argument_spec=arg_spec, supports_check_mode=True)

    name = module.params['name']
    state = module.params['state']
    timeout = module.params['timeout']

    monit = Monit(module, module.get_bin_path('monit', True), name, timeout)
    monit.check_version()

    def exit_if_check_mode():
        if module.check_mode:
            module.exit_json(changed=True)

    if state == 'reloaded':
        exit_if_check_mode()
        monit.reload()

    present = monit.is_process_present()

    if not present and not state == 'present':
        module.fail_json(msg='%s process not presently configured with monit' % name, name=name, state=state)

    if state == 'present':
        if present:
            module.exit_json(changed=False, name=name, state=state)
        exit_if_check_mode()
        monit.present()

    monit.wait_for_monit_to_stop_pending(state)
    running = monit.is_process_running()

    if running and state in ['started', 'monitored']:
        module.exit_json(changed=False, name=name, state=state)

    if running and state == 'stopped':
        exit_if_check_mode()
        monit.stop()

    if running and state == 'unmonitored':
        exit_if_check_mode()
        monit.unmonitor()

    elif state == 'restarted':
        exit_if_check_mode()
        monit.restart()

    elif not running and state == 'started':
        exit_if_check_mode()
        monit.start()

    elif not running and state == 'monitored':
        exit_if_check_mode()
        monit.monitor()

    module.exit_json(changed=False, name=name, state=state)


if __name__ == '__main__':
    main()
