#!/usr/bin/python

# Copyright (c) 2013, Ivan Vanderbyl <ivan@app.io>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
module: logentries
author: "Ivan Vanderbyl (@ivanvanderbyl)"
short_description: Module for tracking logs using U(logentries.com)
description:
  - Sends logs to LogEntries in realtime.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  path:
    type: str
    description:
      - Path to a log file.
    required: true
  state:
    type: str
    description:
      - Following state of the log.
    choices: ['present', 'absent', 'followed', 'unfollowed']
    default: present
  name:
    type: str
    description:
      - Name of the log.
  logtype:
    type: str
    description:
      - Type of the log.
    aliases: [type]

notes:
  - Requires the LogEntries agent which can be installed following the instructions at U(logentries.com).
"""

EXAMPLES = r"""
- name: Track nginx logs
  community.general.logentries:
    path: /var/log/nginx/access.log
    state: present
    name: nginx-access-log

- name: Stop tracking nginx logs
  community.general.logentries:
    path: /var/log/nginx/error.log
    state: absent
"""

from ansible.module_utils.basic import AnsibleModule


def query_log_status(module, le_path, path, state="present"):
    """Returns whether a log is followed or not."""

    if state == "present":
        rc, out, err = module.run_command([le_path, "followed", path])
        if rc == 0:
            return True

        return False


def follow_log(module, le_path, logs, name=None, logtype=None):
    """Follows one or more logs if not already followed."""

    followed_count = 0

    for log in logs:
        if query_log_status(module, le_path, log):
            continue

        if module.check_mode:
            module.exit_json(changed=True)

        cmd = [le_path, "follow", log]
        if name:
            cmd.extend(["--name", name])
        if logtype:
            cmd.extend(["--type", logtype])
        rc, out, err = module.run_command(cmd)

        if not query_log_status(module, le_path, log):
            module.fail_json(msg=f"failed to follow '{log}': {err.strip()}")

        followed_count += 1

    if followed_count > 0:
        module.exit_json(changed=True, msg=f"followed {followed_count} log(s)")

    module.exit_json(changed=False, msg="logs(s) already followed")


def unfollow_log(module, le_path, logs):
    """Unfollows one or more logs if followed."""

    removed_count = 0

    # Using a for loop in case of error, we can report the package that failed
    for log in logs:
        # Query the log first, to see if we even need to remove.
        if not query_log_status(module, le_path, log):
            continue

        if module.check_mode:
            module.exit_json(changed=True)
        rc, out, err = module.run_command([le_path, "rm", log])

        if query_log_status(module, le_path, log):
            module.fail_json(msg=f"failed to remove '{log}': {err.strip()}")

        removed_count += 1

    if removed_count > 0:
        module.exit_json(changed=True, msg=f"removed {removed_count} package(s)")

    module.exit_json(changed=False, msg="logs(s) already unfollowed")


def main():
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(required=True),
            state=dict(default="present", choices=["present", "followed", "absent", "unfollowed"]),
            name=dict(type="str"),
            logtype=dict(type="str", aliases=["type"]),
        ),
        supports_check_mode=True,
    )

    le_path = module.get_bin_path("le", True, ["/usr/local/bin"])

    p = module.params

    # Handle multiple log files
    logs = p["path"].split(",")
    logs = [_f for _f in logs if _f]

    if p["state"] in ["present", "followed"]:
        follow_log(module, le_path, logs, name=p["name"], logtype=p["logtype"])

    elif p["state"] in ["absent", "unfollowed"]:
        unfollow_log(module, le_path, logs)


if __name__ == "__main__":
    main()
