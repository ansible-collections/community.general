#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2013, Andrew Dunham <andrew@du.nham.ca>
# Copyright (c) 2013, Daniel Jaouen <dcj24@cornell.edu>
# Copyright (c) 2015, Indrajit Raychaudhuri <irc+code@indrajit.com>
# Copyright (c) 2024, Kit Ham <kitizz.devside@gmail.com>
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: homebrew_services
author:
    - "Kit Ham (@kitizz)"
requirements:
    - homebrew must already be installed on the target system
short_description: Services manager for Homebrew
version_added: 9.3.0
description:
    - Manages daemons and services via Homebrew.
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
            - An installed homebrew package whose service is to be updated.
        aliases: [ 'formula' ]
        type: str
        required: true
    path:
        description:
            - "A V(:) separated list of paths to search for C(brew) executable.
              Since a package (I(formula) in homebrew parlance) location is prefixed relative to the actual path of C(brew) command,
              providing an alternative C(brew) path enables managing different set of packages in an alternative location in the system."
        default: '/usr/local/bin:/opt/homebrew/bin:/home/linuxbrew/.linuxbrew/bin'
        type: path
    state:
        description:
            - State of the package's service.
        choices: [ 'present', 'absent', 'restarted' ]
        default: present
        type: str
"""

EXAMPLES = """
- name: Install foo package
  community.general.homebrew:
    name: foo
    state: present

- name: Start the foo service (equivalent to `brew services start foo`)
  community.general.homebrew_services:
    name: foo
    state: present

- name: Restart the foo service (equivalent to `brew services restart foo`)
  community.general.homebrew_services:
    name: foo
    state: restarted

- name: Remove the foo service (equivalent to `brew services stop foo`)
  community.general.homebrew_services:
    name: foo
    service_state: absent
"""

RETURN = """
pid:
    description:
      - If the service is now running, this is the PID of the service, otherwise -1.
    returned: success
    type: int
    sample: 1234
running:
    description:
      - Whether the service is running after running this command.
    returned: success
    type: bool
    sample: true
"""

import json
import sys

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.homebrew import (
    HomebrewValidate,
    parse_brew_path,
)

if sys.version_info < (3, 5):
    from collections import namedtuple

    # Stores validated arguments for an instance of an action.
    # See DOCUMENTATION string for argument-specific information.
    HomebrewServiceArgs = namedtuple(
        "HomebrewServiceArgs", ["name", "state", "brew_path"]
    )

    # Stores the state of a Homebrew service.
    HomebrewServiceState = namedtuple("HomebrewServiceState", ["running", "pid"])

else:
    from typing import NamedTuple, Optional

    # Stores validated arguments for an instance of an action.
    # See DOCUMENTATION string for argument-specific information.
    HomebrewServiceArgs = NamedTuple(
        "HomebrewServiceArgs", [("name", str), ("state", str), ("brew_path", str)]
    )

    # Stores the state of a Homebrew service.
    HomebrewServiceState = NamedTuple(
        "HomebrewServiceState", [("running", bool), ("pid", Optional[int])]
    )


def _brew_service_state(args, module):
    # type: (HomebrewServiceArgs, AnsibleModule) -> HomebrewServiceState
    cmd = [args.brew_path, "services", "info", args.name, "--json"]
    rc, stdout, stderr = module.run_command(cmd, check_rc=True)

    try:
        data = json.loads(stdout)[0]
    except json.JSONDecodeError:
        module.fail_json(msg="Failed to parse JSON output:\n{0}".format(stdout))

    return HomebrewServiceState(running=data["status"] == "started", pid=data["pid"])


def _exit_with_state(args, module, changed=False, message=None):
    # type: (HomebrewServiceArgs, AnsibleModule, bool, Optional[str]) -> None
    state = _brew_service_state(args, module)
    if message is None:
        message = (
            "Running: {state.running}, Changed: {changed}, PID: {state.pid}".format(
                state=state, changed=changed
            )
        )
    module.exit_json(msg=message, pid=state.pid, running=state.running, changed=changed)


def validate_and_load_arguments(module):
    # type: (AnsibleModule) -> HomebrewServiceArgs
    """Reuse the Homebrew module's validation logic to validate these arguments."""
    package = module.params["name"]  # type: ignore
    if not HomebrewValidate.valid_package(package):
        module.fail_json(msg="Invalid package name: {0}".format(package))

    state = module.params["state"]  # type: ignore
    if state not in ["present", "absent", "restarted"]:
        module.fail_json(msg="Invalid state: {0}".format(state))

    brew_path = parse_brew_path(module)

    return HomebrewServiceArgs(name=package, state=state, brew_path=brew_path)


def start_service(args, module):
    # type: (HomebrewServiceArgs, AnsibleModule) -> None
    """Start the requested brew service if it is not already running."""
    state = _brew_service_state(args, module)
    if state.running:
        # Nothing to do, return early.
        _exit_with_state(args, module, changed=False, message="Service already running")

    if module.check_mode:
        _exit_with_state(args, module, changed=True, message="Service would be started")

    start_cmd = [args.brew_path, "services", "start", args.name]
    rc, stdout, stderr = module.run_command(start_cmd, check_rc=True)

    _exit_with_state(args, module, changed=True)


def stop_service(args, module):
    # type: (HomebrewServiceArgs, AnsibleModule) -> None
    """Stop the requested brew service if it is running."""
    state = _brew_service_state(args, module)
    if not state.running:
        # Nothing to do, return early.
        _exit_with_state(args, module, changed=False, message="Service already stopped")

    if module.check_mode:
        _exit_with_state(args, module, changed=True, message="Service would be stopped")

    stop_cmd = [args.brew_path, "services", "stop", args.name]
    rc, stdout, stderr = module.run_command(stop_cmd, check_rc=True)

    _exit_with_state(args, module, changed=True)


def restart_service(args, module):
    # type: (HomebrewServiceArgs, AnsibleModule) -> None
    """Restart the requested brew service. This always results in a change."""
    if module.check_mode:
        _exit_with_state(
            args, module, changed=True, message="Service would be restarted"
        )

    restart_cmd = [args.brew_path, "services", "restart", args.name]
    rc, stdout, stderr = module.run_command(restart_cmd, check_rc=True)

    _exit_with_state(args, module, changed=True)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(
                aliases=["formula"],
                required=True,
                type="str",
            ),
            state=dict(
                choices=["present", "absent", "restarted"],
                default="present",
            ),
            path=dict(
                default="/usr/local/bin:/opt/homebrew/bin:/home/linuxbrew/.linuxbrew/bin",
                type="path",
            ),
        ),
        supports_check_mode=True,
    )

    module.run_command_environ_update = dict(
        LANG="C", LC_ALL="C", LC_MESSAGES="C", LC_CTYPE="C"
    )

    # Pre-validate arguments.
    service_args = validate_and_load_arguments(module)

    # Choose logic based on the desired state.
    if service_args.state == "present":
        start_service(service_args, module)
    elif service_args.state == "absent":
        stop_service(service_args, module)
    elif service_args.state == "restarted":
        restart_service(service_args, module)


if __name__ == "__main__":
    main()
