#!/usr/bin/python

# Copyright (c) 2012, Matt Wright <matt@nobien.net>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: supervisorctl
short_description: Manage the state of a program or group of programs managed by C(supervisord)
description:
  - Manage the state of a program or group of programs managed by C(supervisord).
extends_documentation_fragment:
  - community.general._attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  name:
    type: str
    description:
      - The name of the supervisord program or group to manage.
      - The name is taken as group name when it ends with a colon V(:).
      - If O(name=all), all programs and program groups are managed.
    required: true
  config:
    type: path
    description:
      - The supervisor configuration file path.
  server_url:
    type: str
    description:
      - URL on which supervisord server is listening.
  username:
    type: str
    description:
      - Username to use for authentication.
  password:
    type: str
    description:
      - Password to use for authentication.
  state:
    type: str
    description:
      - The desired state of program/group.
    required: true
    choices: ["present", "started", "stopped", "restarted", "absent", "signalled"]
  stop_before_removing:
    type: bool
    description:
      - Use O(stop_before_removing=true) to stop the program/group before removing it.
    default: false
    version_added: 7.5.0
  signal:
    type: str
    description:
      - The signal to send to the program/group, when combined with the V(signalled) state. Required when l(state=signalled).
  supervisorctl_path:
    type: path
    description:
      - Path to C(supervisorctl) executable.
  wait:
    type: bool
    description:
      - When O(state=started) or O(state=restarted), wait while the programs are in the C(STARTING) or C(BACKOFF) states,
        and fail if any of them does not reach the C(RUNNING) state.
      - This includes programs that were already in the C(STARTING) or C(BACKOFF) states, for example after being added
        with O(state=present) and C(autostart=true).
      - When a program fails to start but C(supervisord) is still retrying it (see C(startretries) in the C(supervisord)
        configuration), the module keeps waiting instead of failing.
      - Depending on the C(startsecs) and C(startretries) settings of the programs, the wait may take a long time.
      - This option is ignored in check mode.
    default: false
    version_added: 14.0.0
notes:
  - When O(state=present), the module calls C(supervisorctl reread) then C(supervisorctl add) if the program/group does not
    exist.
  - When O(state=restarted), the module calls C(supervisorctl update) then calls C(supervisorctl restart).
  - When O(state=absent), the module calls C(supervisorctl reread) then C(supervisorctl remove) to remove the target program/group.
    If the program/group is still running, the action fails. If you want to stop the program/group before removing, use O(stop_before_removing=true).
requirements: ["supervisorctl"]
author:
  - "Matt Wright (@mattupstate)"
  - "Aaron Wang (@inetfuture) <inetfuture@gmail.com>"
"""

EXAMPLES = r"""
- name: Manage the state of program to be in started state
  community.general.supervisorctl:
    name: my_app
    state: started

- name: Manage the state of program group to be in started state
  community.general.supervisorctl:
    name: 'my_apps:'
    state: started

- name: Restart my_app, reading supervisorctl configuration from a specified file
  community.general.supervisorctl:
    name: my_app
    state: restarted
    config: /var/opt/my_project/supervisord.conf

- name: Restart my_app, connecting to supervisord with credentials and server URL
  community.general.supervisorctl:
    name: my_app
    state: restarted
    username: test
    password: testpass
    server_url: http://localhost:9001

- name: Send a signal to my_app via supervisorctl
  community.general.supervisorctl:
    name: my_app
    state: signalled
    signal: USR1

- name: Restart all programs and program groups
  community.general.supervisorctl:
    name: all
    state: restarted

- name: Start my_app and fail unless it reaches the RUNNING state
  community.general.supervisorctl:
    name: my_app
    state: started
    wait: true
"""


import os
import time

from ansible.module_utils.basic import AnsibleModule, is_executable


def _is_active(status):
    return status in ("RUNNING", "STARTING", "BACKOFF")


def _is_not_active(status):
    return not _is_active(status)


def _is_strictly_running(status):
    return status in ("RUNNING",)


def _always(_status):
    return True


def main():
    arg_spec = dict(
        name=dict(type="str", required=True),
        config=dict(type="path"),
        server_url=dict(type="str"),
        username=dict(type="str"),
        password=dict(type="str", no_log=True),
        supervisorctl_path=dict(type="path"),
        state=dict(
            type="str", required=True, choices=["present", "started", "restarted", "stopped", "absent", "signalled"]
        ),
        stop_before_removing=dict(type="bool", default=False),
        signal=dict(type="str"),
        wait=dict(type="bool", default=False),
    )

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True,
        required_if=[("state", "signalled", ["signal"])],
    )

    name = module.params["name"]
    is_group = False
    if name.endswith(":"):
        is_group = True
        name = name.rstrip(":")
    state = module.params["state"]
    stop_before_removing = module.params["stop_before_removing"]
    config = module.params["config"]
    server_url = module.params["server_url"]
    username = module.params["username"]
    password = module.params["password"]
    supervisorctl_path = module.params["supervisorctl_path"]
    signal = module.params["signal"]
    wait = module.params["wait"] and state in ("started", "restarted") and not module.check_mode

    # we check error message for a pattern, so we need to make sure that's in C locale
    module.run_command_environ_update = dict(LANGUAGE="C", LC_ALL="C")

    if supervisorctl_path:
        if os.path.exists(supervisorctl_path) and is_executable(supervisorctl_path):
            supervisorctl_args = [supervisorctl_path]
        else:
            module.fail_json(
                msg=f"Provided path to supervisorctl does not exist or isn't executable: {supervisorctl_path}"
            )
    else:
        supervisorctl_args = [module.get_bin_path("supervisorctl", True)]

    if config:
        supervisorctl_args.extend(["-c", config])
    if server_url:
        supervisorctl_args.extend(["-s", server_url])
    if username:
        supervisorctl_args.extend(["-u", username])
    if password:
        supervisorctl_args.extend(["-p", password])

    def run_supervisorctl(cmd, name=None, **kwargs):
        args = list(supervisorctl_args)  # copy the master args
        args.append(cmd)
        if name:
            args.append(name)
        return module.run_command(args, **kwargs)

    def get_matched_processes():
        matched = []
        rc, out, err = run_supervisorctl("status")
        for line in out.splitlines():
            # One status line may look like one of these two:
            # process not in group:
            #   echo_date_lonely RUNNING pid 7680, uptime 13:22:18
            # process in group:
            #   echo_date_group:echo_date_00 RUNNING pid 7681, uptime 13:22:18
            fields = [field for field in line.split(" ") if field != ""]
            process_name = fields[0]
            status = fields[1]

            if is_group:
                # If there is ':', this process must be in a group.
                if ":" in process_name:
                    group = process_name.split(":")[0]
                    if group != name:
                        continue
                else:
                    continue
            else:
                if process_name != name and name != "all":
                    continue

            matched.append((process_name, status))
        return matched

    def wait_for_running(processes, action_output=""):
        process_names = [process_name for process_name, status in processes]
        while True:
            statuses = [(p, s) for p, s in get_matched_processes() if p in process_names]
            if not any(s in ("STARTING", "BACKOFF") for p, s in statuses):
                break
            time.sleep(1)
        not_running = [f"{p} ({s})" for p, s in statuses if s != "RUNNING"]
        if not_running:
            module.fail_json(
                msg=f"Failed to reach the RUNNING state: {', '.join(not_running)}",
                name=name,
                state=state,
                stdout=action_output,
            )

    def take_action_on_processes(processes, status_filter, action, expected_result, exit_module=True):
        to_take_action_on = []
        for process_name, status in processes:
            if status_filter(status):
                to_take_action_on.append(process_name)

        if len(to_take_action_on) == 0:
            if not exit_module:
                return
            if wait:
                wait_for_running(processes)
            module.exit_json(changed=False, name=name, state=state)
        if module.check_mode:
            if not exit_module:
                return
            module.exit_json(changed=True)
        action_outputs = []
        for process_name in to_take_action_on:
            # with wait, a failed start is judged by the state reached after supervisord's retries
            rc, out, err = run_supervisorctl(action, process_name, check_rc=not wait)
            if not wait and f"{process_name}: {expected_result}" not in out:
                module.fail_json(msg=out)
            action_outputs.append(out)

        if wait:
            wait_for_running(processes, "".join(action_outputs))
        if exit_module:
            module.exit_json(changed=True, name=name, state=state, affected=to_take_action_on)

    if name == "all" and state in ("started", "stopped", "restarted"):
        if state == "restarted":
            run_supervisorctl("update", check_rc=True)
        processes = get_matched_processes()
        status_filters = {
            "started": _is_not_active,
            "stopped": _is_active,
            "restarted": _always,
        }
        to_act_on = [p for p, s in processes if status_filters[state](s)]
        if not to_act_on:
            if wait:
                wait_for_running(processes)
            module.exit_json(changed=False, name=name, state=state)
        if module.check_mode:
            module.exit_json(changed=True)
        actions = {"started": "start", "stopped": "stop", "restarted": "restart"}
        rc, out, err = run_supervisorctl(actions[state], "all", check_rc=not wait)
        if wait:
            wait_for_running(processes, out)
        module.exit_json(changed=True, name=name, state=state, affected=to_act_on)

    if state == "restarted":
        rc, out, err = run_supervisorctl("update", check_rc=True)
        processes = get_matched_processes()
        if len(processes) == 0:
            module.fail_json(name=name, msg="ERROR (no such process)")

        take_action_on_processes(processes, _always, "restart", "started")

    processes = get_matched_processes()

    if state == "absent":
        if len(processes) == 0:
            module.exit_json(changed=False, name=name, state=state)

        if stop_before_removing:
            take_action_on_processes(processes, _is_active, "stop", "stopped", exit_module=False)

        if module.check_mode:
            module.exit_json(changed=True)
        run_supervisorctl("reread", check_rc=True)
        rc, out, err = run_supervisorctl("remove", name)
        if f"{name}: removed process group" in out:
            module.exit_json(changed=True, name=name, state=state)
        else:
            module.fail_json(msg=out, name=name, state=state)

    if state == "present":
        if len(processes) > 0:
            module.exit_json(changed=False, name=name, state=state)

        if module.check_mode:
            module.exit_json(changed=True)
        run_supervisorctl("reread", check_rc=True)
        dummy, out, dummy = run_supervisorctl("add", name)
        if f"{name}: added process group" in out:
            module.exit_json(changed=True, name=name, state=state)
        else:
            module.fail_json(msg=out, name=name, state=state)

    # from this point onwards, if there are no matching processes, module cannot go on.
    if len(processes) == 0 and name != "all":
        module.fail_json(name=name, msg="ERROR (no such process)")

    if state == "started":
        take_action_on_processes(processes, _is_not_active, "start", "started")

    if state == "stopped":
        take_action_on_processes(processes, _is_active, "stop", "stopped")

    if state == "signalled":
        take_action_on_processes(processes, _is_strictly_running, f"signal {signal}", "signalled")


if __name__ == "__main__":
    main()
