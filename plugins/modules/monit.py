#!/usr/bin/python

# Copyright (c) 2013, Darryl Stoflet <stoflet@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: monit
short_description: Manage the state of a program monitored using Monit
description:
  - Manage the state of a program monitored using Monit.
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
      - The name of the C(monit) program/process to manage.
    required: true
    type: str
  state:
    description:
      - The state of service.
    required: true
    choices: ["present", "started", "stopped", "restarted", "monitored", "unmonitored", "reloaded"]
    type: str
  timeout:
    description:
      - If there are pending actions for the service monitored by monit, then it checks for up to this many seconds to verify
        the requested action has been performed. The module sleeps for five seconds between each check.
    default: 300
    type: int
author:
  - Darryl Stoflet (@dstoflet)
  - Simon Kelly (@snopoke)
"""

EXAMPLES = r"""
- name: Manage the state of program httpd to be in started state
  community.general.monit:
    name: httpd
    state: started
"""

import re
import time
from enum import Enum

from ansible.module_utils.basic import AnsibleModule

STATE_COMMAND_MAP = {
    "stopped": "stop",
    "started": "start",
    "monitored": "monitor",
    "unmonitored": "unmonitor",
    "restarted": "restart",
}

MONIT_SERVICES = ["Process", "File", "Fifo", "Filesystem", "Directory", "Remote host", "System", "Program", "Network"]


class StatusValue(Enum):
    MISSING = "missing"
    OK = "ok"
    NOT_MONITORED = "not_monitored"
    INITIALIZING = "initializing"
    DOES_NOT_EXIST = "does_not_exist"
    EXECUTION_FAILED = "execution_failed"


class Status:
    """Represents a monit status with optional pending state."""

    def __init__(self, status_val: str | StatusValue, is_pending: bool = False):
        if isinstance(status_val, StatusValue):
            self.state = status_val
        else:
            self.state = getattr(StatusValue, status_val)
        self.is_pending = is_pending

    @property
    def value(self):
        return self.state.value

    def pending(self):
        """Return a new Status instance with is_pending=True."""
        return Status(self.state, is_pending=True)

    def __getattr__(self, item):
        if item.startswith("is_"):
            status_name = item[3:].upper()
            if hasattr(StatusValue, status_name):
                return self.value == getattr(StatusValue, status_name).value
        raise AttributeError(item)

    def __eq__(self, other):
        if not isinstance(other, Status):
            return False
        return self.state == other.state and self.is_pending == other.is_pending

    def __str__(self):
        return f"{self.value}{' (pending)' if self.is_pending else ''}"

    def __repr__(self):
        return f"<{self}>"


# Initialize convenience class attributes


class Monit:
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
        rc, out, err = self.module.run_command([self.monit_bin_path, "-V"], check_rc=True)
        version_line = out.split("\n")[0]
        raw_version = re.search(r"([0-9]+\.){1,2}([0-9]+)?", version_line).group()
        return raw_version, tuple(map(int, raw_version.split(".")))

    def exit_fail(self, msg, status=None, **kwargs):
        kwargs.update(
            {
                "msg": msg,
                "monit_version": self._raw_version,
                "process_status": str(status) if status else None,
            }
        )
        self.module.fail_json(**kwargs)

    def exit_success(self, state):
        self.module.exit_json(
            changed=True,
            name=self.process_name,
            monit_version=self._raw_version,
            state=state,
        )

    @property
    def command_args(self):
        return ["-B"] if self.monit_version() > (5, 18) else []

    def get_status(self, validate=False) -> Status:
        """Return the status of the process in monit.

        :@param validate: Force monit to re-check the status of the process
        """
        monit_command = "validate" if validate else "status"
        check_rc = not validate  # 'validate' always has rc = 1
        command = [self.monit_bin_path, monit_command] + self.command_args + [self.process_name]
        rc, out, err = self.module.run_command(command, check_rc=check_rc)
        return self._parse_status(out, err)

    def _parse_status(self, output, err) -> Status:
        escaped_monit_services = "|".join([re.escape(x) for x in MONIT_SERVICES])
        pattern = f"({escaped_monit_services}) '{re.escape(self.process_name)}'"
        if not re.search(pattern, output, re.IGNORECASE):
            return Status("MISSING")

        status_val_find = re.findall(r"^\s*status\s*([\w\- ]+)", output, re.MULTILINE)
        if not status_val_find:
            self.exit_fail("Unable to find process status", stdout=output, stderr=err)

        status_val = status_val_find[0].strip().upper()
        if " | " in status_val:
            status_val = status_val.split(" | ")[0]
        if " - " not in status_val:
            status_val = status_val.replace(" ", "_")
            # Normalize RUNNING to OK (monit reports both, they mean the same thing)
            if status_val == "RUNNING":
                status_val = "OK"
            try:
                return Status(status_val)
            except AttributeError:
                self.module.warn(f"Unknown monit status '{status_val}', treating as execution failed")
                return Status("EXECUTION_FAILED")
        else:
            status_val, substatus = status_val.split(" - ")
            action, state = substatus.split()
            if action in ["START", "INITIALIZING", "RESTART", "MONITOR"]:
                status = Status("OK")
            else:
                status = Status("NOT_MONITORED")

            if state == "PENDING":
                status = status.pending()
            return status

    def is_process_present(self):
        command = [self.monit_bin_path, "summary"] + self.command_args
        rc, out, err = self.module.run_command(command, check_rc=True)
        return bool(re.findall(rf"\b{self.process_name}\b", out))

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
                self.exit_fail("waited too long for monit to change state", running_status)

            loop_count += 1
            time.sleep(0.5)
            validate = loop_count % 2 == 0  # force recheck of status every second try
            running_status = self.get_status(validate)
        return running_status

    def wait_for_monit_to_stop_pending(self, current_status=None):
        """Fails this run if there is no status or it is pending/initializing for timeout"""
        timeout_time = time.time() + self.timeout

        if not current_status:
            current_status = self.get_status()
        waiting_status = [
            StatusValue.MISSING,
            StatusValue.INITIALIZING,
            StatusValue.DOES_NOT_EXIST,
        ]
        while current_status.is_pending or (current_status.state in waiting_status):
            if time.time() >= timeout_time:
                self.exit_fail('waited too long for "pending", or "initiating" status to go away', current_status)

            time.sleep(5)
            current_status = self.get_status(validate=True)
        return current_status

    def reload(self):
        rc, out, err = self.module.run_command([self.monit_bin_path, "reload"])
        if rc != 0:
            self.exit_fail("monit reload failed", stdout=out, stderr=err)
        self.exit_success(state="reloaded")

    def present(self):
        self.run_command("reload")

        timeout_time = time.time() + self.timeout
        while not self.is_process_present():
            if time.time() >= timeout_time:
                self.exit_fail('waited too long for process to become "present"')

            time.sleep(5)

        self.exit_success(state="present")

    def change_state(self, state: str, expected_status: StatusValue, invert_expected: bool | None = None):
        current_status = self.get_status()
        self.run_command(STATE_COMMAND_MAP[state])
        # Give monit daemon a moment to process the command before checking status
        # to avoid race condition where HTTP interface may be temporarily unresponsive
        time.sleep(0.5)
        status = self.wait_for_status_change(current_status)
        status = self.wait_for_monit_to_stop_pending(status)
        status_match = status.state == expected_status
        if invert_expected:
            status_match = not status_match
        if status_match:
            self.exit_success(state=state)
        self.exit_fail(f"{self.process_name} process not {state}", status)

    def stop(self):
        self.change_state("stopped", expected_status=StatusValue.NOT_MONITORED)

    def unmonitor(self):
        self.change_state("unmonitored", expected_status=StatusValue.NOT_MONITORED)

    def restart(self):
        self.change_state("restarted", expected_status=StatusValue.OK)

    def start(self):
        self.change_state("started", expected_status=StatusValue.OK)

    def monitor(self):
        self.change_state("monitored", expected_status=StatusValue.NOT_MONITORED, invert_expected=True)


def main():
    arg_spec = dict(
        name=dict(required=True),
        timeout=dict(default=300, type="int"),
        state=dict(
            required=True,
            choices=["present", "started", "restarted", "stopped", "monitored", "unmonitored", "reloaded"],
        ),
    )

    module = AnsibleModule(argument_spec=arg_spec, supports_check_mode=True)

    name = module.params["name"]
    state = module.params["state"]
    timeout = module.params["timeout"]

    monit = Monit(module, module.get_bin_path("monit", True), name, timeout)

    def exit_if_check_mode():
        if module.check_mode:
            module.exit_json(changed=True)

    if state == "reloaded":
        exit_if_check_mode()
        monit.reload()

    present = monit.is_process_present()

    if not present and state != "present":
        module.fail_json(msg=f"{name} process not presently configured with monit", name=name)

    if state == "present":
        if present:
            module.exit_json(changed=False, name=name, state=state)
        exit_if_check_mode()
        monit.present()

    monit.wait_for_monit_to_stop_pending()
    running = monit.is_process_running()

    if running and state in ["started", "monitored"]:
        module.exit_json(changed=False, name=name, state=state)

    if running and state == "stopped":
        exit_if_check_mode()
        monit.stop()

    if running and state == "unmonitored":
        exit_if_check_mode()
        monit.unmonitor()

    elif state == "restarted":
        exit_if_check_mode()
        monit.restart()

    elif not running and state == "started":
        exit_if_check_mode()
        monit.start()

    elif not running and state == "monitored":
        exit_if_check_mode()
        monit.monitor()

    module.exit_json(changed=False, name=name, state=state)


if __name__ == "__main__":
    main()
