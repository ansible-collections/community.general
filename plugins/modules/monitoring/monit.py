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
    - Manage the state of a program monitored via I(Monit).
options:
  name:
    description:
      - The name of the I(monit) program/process to manage.
    required: true
    type: str
  state:
    description:
      - The state of service.
    required: true
    choices: [ "present", "started", "stopped", "restarted", "monitored", "unmonitored", "reloaded" ]
    type: str
  timeout:
    description:
      - If there are pending actions for the service monitored by monit, then Ansible will check
        for up to this many seconds to verify the requested action has been performed.
        Ansible will sleep for five seconds between each check.
    default: 300
    type: int
author:
    - Darryl Stoflet (@dstoflet)
    - Simon Kelly (@snopoke)
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
from ansible.module_utils.six import python_2_unicode_compatible


STATE_COMMAND_MAP = {
    'stopped': 'stop',
    'started': 'start',
    'monitored': 'monitor',
    'unmonitored': 'unmonitor',
    'restarted': 'restart'
}

MONIT_SERVICES = ['Process', 'File', 'Fifo', 'Filesystem', 'Directory', 'Remote host', 'System', 'Program',
                  'Network']


@python_2_unicode_compatible
class StatusValue(namedtuple("Status", "value, is_pending")):
    MISSING = 'missing'
    OK = 'ok'
    NOT_MONITORED = 'not_monitored'
    INITIALIZING = 'initializing'
    DOES_NOT_EXIST = 'does_not_exist'
    EXECUTION_FAILED = 'execution_failed'
    ALL_STATUS = [
        MISSING, OK, NOT_MONITORED, INITIALIZING, DOES_NOT_EXIST, EXECUTION_FAILED
    ]

    def __new__(cls, value, is_pending=False):
        return super(StatusValue, cls).__new__(cls, value, is_pending)

    def pending(self):
        return StatusValue(self.value, True)

    def __getattr__(self, item):
        if item in ('is_%s' % status for status in self.ALL_STATUS):
            return self.value == getattr(self, item[3:].upper())
        raise AttributeError(item)

    def __str__(self):
        return "%s%s" % (self.value, " (pending)" if self.is_pending else "")


class Status(object):
    MISSING = StatusValue(StatusValue.MISSING)
    OK = StatusValue(StatusValue.OK)
    RUNNING = StatusValue(StatusValue.OK)
    NOT_MONITORED = StatusValue(StatusValue.NOT_MONITORED)
    INITIALIZING = StatusValue(StatusValue.INITIALIZING)
    DOES_NOT_EXIST = StatusValue(StatusValue.DOES_NOT_EXIST)
    EXECUTION_FAILED = StatusValue(StatusValue.EXECUTION_FAILED)


class Monit(object):
    def __init__(self, module, monit_bin_path, service_name, timeout):
        self.module = module
        self.monit_bin_path = monit_bin_path
        self.process_name = service_name
        self.timeout = timeout

        self._monit_version = None
        self._raw_version = None
        self._status_change_retry_count = 6

    def monit_version(self):
        if self._monit_version is None:
            self._raw_version, version = self._get_monit_version()
            # Use only major and minor even if there are more these should be enough
            self._monit_version = version[0], version[1]
        return self._monit_version

    def _get_monit_version(self):
        rc, out, err = self.module.run_command([self.monit_bin_path, '-V'], check_rc=True)
        version_line = out.split('\n')[0]
        raw_version = re.search(r"([0-9]+\.){1,2}([0-9]+)?", version_line).group()
        return raw_version, tuple(map(int, raw_version.split('.')))

    def exit_fail(self, msg, status=None, **kwargs):
        kwargs.update({
            'msg': msg,
            'monit_version': self._raw_version,
            'process_status': str(status) if status else None,
        })
        self.module.fail_json(**kwargs)

    def exit_success(self, state):
        self.module.exit_json(changed=True, name=self.process_name, state=state)

    @property
    def command_args(self):
        return ["-B"] if self.monit_version() > (5, 18) else []

    def get_status(self, validate=False):
        """Return the status of the process in monit.

        :@param validate: Force monit to re-check the status of the process
        """
        monit_command = "validate" if validate else "status"
        check_rc = False if validate else True  # 'validate' always has rc = 1
        command = [self.monit_bin_path, monit_command] + self.command_args + [self.process_name]
        rc, out, err = self.module.run_command(command, check_rc=check_rc)
        return self._parse_status(out, err)

    def _parse_status(self, output, err):
        escaped_monit_services = '|'.join([re.escape(x) for x in MONIT_SERVICES])
        pattern = "(%s) '%s'" % (escaped_monit_services, re.escape(self.process_name))
        if not re.search(pattern, output, re.IGNORECASE):
            return Status.MISSING

        status_val = re.findall(r"^\s*status\s*([\w\- ]+)", output, re.MULTILINE)
        if not status_val:
            self.exit_fail("Unable to find process status", stdout=output, stderr=err)

        status_val = status_val[0].strip().upper()
        if ' | ' in status_val:
            status_val = status_val.split(' | ')[0]
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
        command = [self.monit_bin_path, 'summary'] + self.command_args
        rc, out, err = self.module.run_command(command, check_rc=True)
        return bool(re.findall(r'\b%s\b' % self.process_name, out))

    def is_process_running(self):
        return self.get_status().is_ok

    def run_command(self, command):
        """Runs a monit command, and returns the new status."""
        return self.module.run_command([self.monit_bin_path, command, self.process_name], check_rc=True)

    def wait_for_status_change(self, current_status):
        running_status = self.get_status()
        if running_status.value != current_status.value or current_status.value == StatusValue.EXECUTION_FAILED:
            return running_status

        loop_count = 0
        while running_status.value == current_status.value:
            if loop_count >= self._status_change_retry_count:
                self.exit_fail('waited too long for monit to change state', running_status)

            loop_count += 1
            time.sleep(0.5)
            validate = loop_count % 2 == 0  # force recheck of status every second try
            running_status = self.get_status(validate)
        return running_status

    def wait_for_monit_to_stop_pending(self, current_status=None):
        """Fails this run if there is no status or it's pending/initializing for timeout"""
        timeout_time = time.time() + self.timeout

        if not current_status:
            current_status = self.get_status()
        waiting_status = [
            StatusValue.MISSING,
            StatusValue.INITIALIZING,
            StatusValue.DOES_NOT_EXIST,
        ]
        while current_status.is_pending or (current_status.value in waiting_status):
            if time.time() >= timeout_time:
                self.exit_fail('waited too long for "pending", or "initiating" status to go away', current_status)

            time.sleep(5)
            current_status = self.get_status(validate=True)
        return current_status

    def reload(self):
        rc, out, err = self.module.run_command([self.monit_bin_path, 'reload'])
        if rc != 0:
            self.exit_fail('monit reload failed', stdout=out, stderr=err)
        self.exit_success(state='reloaded')

    def present(self):
        self.run_command('reload')

        timeout_time = time.time() + self.timeout
        while not self.is_process_present():
            if time.time() >= timeout_time:
                self.exit_fail('waited too long for process to become "present"')

            time.sleep(5)

        self.exit_success(state='present')

    def change_state(self, state, expected_status, invert_expected=None):
        current_status = self.get_status()
        self.run_command(STATE_COMMAND_MAP[state])
        status = self.wait_for_status_change(current_status)
        status = self.wait_for_monit_to_stop_pending(status)
        status_match = status.value == expected_status.value
        if invert_expected:
            status_match = not status_match
        if status_match:
            self.exit_success(state=state)
        self.exit_fail('%s process not %s' % (self.process_name, state), status)

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

    def exit_if_check_mode():
        if module.check_mode:
            module.exit_json(changed=True)

    if state == 'reloaded':
        exit_if_check_mode()
        monit.reload()

    present = monit.is_process_present()

    if not present and not state == 'present':
        module.fail_json(msg='%s process not presently configured with monit' % name, name=name)

    if state == 'present':
        if present:
            module.exit_json(changed=False, name=name, state=state)
        exit_if_check_mode()
        monit.present()

    monit.wait_for_monit_to_stop_pending()
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
