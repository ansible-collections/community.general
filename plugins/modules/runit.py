#!/usr/bin/python

# Copyright (c) 2015, Brian Coca <bcoca@ansible.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: runit
author:
  - James Sumners (@jsumners)
short_description: Manage runit services
description:
  - Controls runit services on remote hosts using the sv utility.
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
      - Name of the service to manage.
    type: str
    required: true
  state:
    description:
      - V(started)/V(stopped) are idempotent actions that do not run commands unless necessary.
      - V(restarted) always bounces the service (sv restart) and V(killed) always bounces the service (sv force-stop).
      - V(reloaded) always sends a HUP (sv reload).
      - V(once) runs a normally downed sv once (sv once), not really an idempotent operation.
    type: str
    choices: [killed, once, reloaded, restarted, started, stopped]
  enabled:
    description:
      - Whether the service is enabled or not, if disabled it also implies stopped.
    type: bool
  service_dir:
    description:
      - Directory runsv watches for services.
    type: str
    default: /var/service
  service_src:
    description:
      - Directory where services are defined, the source of symlinks to O(service_dir).
    type: str
    default: /etc/sv
"""

EXAMPLES = r"""
- name: Start sv dnscache, if not running
  community.general.runit:
    name: dnscache
    state: started

- name: Stop sv dnscache, if running
  community.general.runit:
    name: dnscache
    state: stopped

- name: Kill sv dnscache, in all cases
  community.general.runit:
    name: dnscache
    state: killed

- name: Restart sv dnscache, in all cases
  community.general.runit:
    name: dnscache
    state: restarted

- name: Reload sv dnscache, in all cases
  community.general.runit:
    name: dnscache
    state: reloaded

- name: Use alternative sv directory location
  community.general.runit:
    name: dnscache
    state: reloaded
    service_dir: /run/service
"""

import os
import re

from ansible.module_utils.basic import AnsibleModule


class Sv:
    """
    Main class that handles daemontools, can be subclassed and overridden in case
    we want to use a 'derivative' like encore, s6, etc
    """

    def __init__(self, module):
        self.extra_paths = []
        self.report_vars = ["state", "enabled", "svc_full", "src_full", "pid", "duration", "full_state"]

        self.module = module

        self.name = module.params["name"]
        self.service_dir = module.params["service_dir"]
        self.service_src = module.params["service_src"]
        self.enabled = None
        self.full_state = None
        self.state = None
        self.pid = None
        self.duration = None

        self.svc_cmd = module.get_bin_path("sv", opt_dirs=self.extra_paths, required=True)
        self.svstat_cmd = module.get_bin_path("sv", opt_dirs=self.extra_paths)
        self.svc_full = f"{self.service_dir}/{self.name}"
        self.src_full = f"{self.service_src}/{self.name}"

        self.enabled = os.path.lexists(self.svc_full)
        if self.enabled:
            self.get_status()
        else:
            self.state = "stopped"

    def enable(self):
        if os.path.exists(self.src_full):
            try:
                os.symlink(self.src_full, self.svc_full)
            except OSError as e:
                self.module.fail_json(path=self.src_full, msg=f"Error while linking: {e}")
        else:
            self.module.fail_json(msg=f"Could not find source for service to enable ({self.src_full}).")

    def disable(self):
        self.execute_command([self.svc_cmd, "force-stop", self.src_full])
        try:
            os.unlink(self.svc_full)
        except OSError as e:
            self.module.fail_json(path=self.svc_full, msg=f"Error while unlinking: {e}")

    def get_status(self):
        (rc, out, err) = self.execute_command([self.svstat_cmd, "status", self.svc_full])

        if err is not None and err:
            self.full_state = self.state = err
        else:
            self.full_state = out
            # full_state *may* contain information about the logger:
            # "down: /etc/service/service-without-logger: 1s, normally up\n"
            # "down: /etc/service/updater: 127s, normally up; run: log: (pid 364) 263439s\n"
            full_state_no_logger = self.full_state.split("; ")[0]

            m = re.search(r"\(pid (\d+)\)", full_state_no_logger)
            if m:
                self.pid = m.group(1)

            m = re.search(r" (\d+)s", full_state_no_logger)
            if m:
                self.duration = m.group(1)

            if re.search(r"^run:", full_state_no_logger):
                self.state = "started"
            elif re.search(r"^down:", full_state_no_logger):
                self.state = "stopped"
            else:
                self.state = "unknown"
                return

    def started(self):
        return self.start()

    def start(self):
        return self.execute_command([self.svc_cmd, "start", self.svc_full])

    def stopped(self):
        return self.stop()

    def stop(self):
        return self.execute_command([self.svc_cmd, "stop", self.svc_full])

    def once(self):
        return self.execute_command([self.svc_cmd, "once", self.svc_full])

    def reloaded(self):
        return self.reload()

    def reload(self):
        return self.execute_command([self.svc_cmd, "reload", self.svc_full])

    def restarted(self):
        return self.restart()

    def restart(self):
        return self.execute_command([self.svc_cmd, "restart", self.svc_full])

    def killed(self):
        return self.kill()

    def kill(self):
        return self.execute_command([self.svc_cmd, "force-stop", self.svc_full])

    def execute_command(self, cmd):
        try:
            (rc, out, err) = self.module.run_command(cmd)
        except Exception as e:
            self.module.fail_json(msg=f"failed to execute: {e}")
        return rc, out, err

    def report(self):
        self.get_status()
        states = {}
        for k in self.report_vars:
            states[k] = self.__dict__[k]
        return states


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type="str", required=True),
            state=dict(type="str", choices=["killed", "once", "reloaded", "restarted", "started", "stopped"]),
            enabled=dict(type="bool"),
            service_dir=dict(type="str", default="/var/service"),
            service_src=dict(type="str", default="/etc/sv"),
        ),
        supports_check_mode=True,
    )

    module.run_command_environ_update = dict(LANG="C", LC_ALL="C", LC_MESSAGES="C", LC_CTYPE="C")

    state = module.params["state"]
    enabled = module.params["enabled"]

    sv = Sv(module)
    changed = False

    if enabled is not None and enabled != sv.enabled:
        changed = True
        if not module.check_mode:
            try:
                if enabled:
                    sv.enable()
                else:
                    sv.disable()
            except (OSError, IOError) as e:
                module.fail_json(msg=f"Could not change service link: {e}")

    if state is not None and state != sv.state:
        changed = True
        if not module.check_mode:
            getattr(sv, state)()

    module.exit_json(changed=changed, sv=sv.report())


if __name__ == "__main__":
    main()
