#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2023, Florian Paul Azim Hoberg @gyptazy <gyptazy@gyptazy.ch>
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: pf
version_added: 6.3.0
short_description: Manage BSD Packet Filter (pf)
description:
    - This module manages the BSD Packet Filter (pf).
options:
  config:
    description:
      - Path to a pf rule set.
    type: path
    required: true
  filter:
    description:
      - If state is C(ignore), filters are ignored.
      - If state is C(filter), only filter rules will be loaded.
      - If state is C(nat), only nat rules will be loaded.
      - If state is C(options), only options rules will be loaded.
    choices: [ 'ignore', 'filter', 'nat', 'options' ]
    type: str
    default: ignore
  state:
    description:
      - If state is C(started), packet filter will be started.
      - If state is C(stopped), packet filter will be stopped.
      - If state is C(restarted), packet filter will be restarted.
      - If state is C(reloaded), packet filter will be reloaded/flushed.
    choices: [ 'started', 'stopped', 'restarted', 'reloaded' ]
    type: str
    default: reload
  dry_run:
    description:
      - Run C(pfctl) with dry-run option and provides it in meta output.
    type: bool
    default: False
notes:
  - Supports only BSD
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
requirements:
  - pf
author:
    - Florian Paul Azim Hoberg (@gyptazy)
'''

EXAMPLES = r'''
- name: Test pf rule set
  community.general.pf:
    config: /etc/pf.conf
    state: reloaded
    dry_run: true

- name: Reload pf rule set
  community.general.pf:
    config: /etc/pf.conf
    state: reloaded
'''

RETURN = r'''
state:
    description: An output of the desired state.
    returned: success
    type: str
    sample: started
filter:
    description: An output of the defined rule set filter.
    returned: success
    type: str
    sample: nat
rule_set:
    description: An output of the active rule set (only dry-run).
    returned: success
    type: str
    sample: pass in all flags S/SA keep state
'''

from ansible.module_utils.basic import AnsibleModule


def main():
    """ start main program to manage packet filter (pf) """
    module = AnsibleModule(
        argument_spec=dict(
            config=dict(required=True, type='path'),
            filter=dict(default='ignore', choices=['ignore', 'filter', 'nat', 'options']),
            state=dict(default='reloaded', choices=['started', 'stopped', 'restarted', 'reloaded']),
            dry_run=dict(default=False, type='bool')
        ),
        supports_check_mode=True
    )

    config = module.params['config']
    filter = module.params['filter']
    state = module.params['state']
    dry_run = module.params['dry_run']
    changed = False
    out = "No information available for this state."

    # Validate for a supported OS
    validate(module, config)
    # Get current status of packet filter (pf)
    active_pf = status_pf(module)

    # Perform user defined and desired state
    # Start packet filter (pf) only if it is currently not running
    if state == 'started':
        if not active_pf:
            start_pf(module, active_pf)
            changed = True

    # Stop packet filter (pf) only it is currently running
    if state == 'stopped':
        if active_pf:
            stop_pf(module, active_pf)
            changed = True

    # Restart of packet filter (pf) can always be performed
    if state == 'restarted':
        restart_pf(module, active_pf)
        changed = True

    # Reload/Flush the defined rule set for packet filter (pf)
    # Note: May optionally run in dry run mode and print out
    #       the rule set in Ansible meta output
    if state == 'reloaded':
        out = reload_pf(module, config, dry_run, filter)
        # Dry run will not modify the system
        if not dry_run:
            changed = True

    module.exit_json(
        changed=changed,
        meta={
            "state": state,
            "filter": filter,
            "rule_set": out
        }
    )


def validate(module, config):
    """ Run basic validations """
    _validate_os(module)
    _validate_pf(module)
    _validate_pf_config(module, config)


def _validate_os(module):
    """ Validate the operating system """
    rc, out, err = module.run_command(['cat', '/etc/os-release'])

    # Validate for a BSD string in output
    if 'BSD' not in out:
        msg_err = 'Error: Unsupported OS. This can only be used on BSD systems.'
        module.fail_json(msg=msg_err)


def _validate_pf(module):
    """ Validate packet filter (pf) """
    rc, out, err = module.run_command(['ls', '/sbin/pfctl'])

    # Validate exit code
    if rc != 0:
        msg_err = 'Error: Unable to find pfctl binary.'
        module.fail_json(msg=msg_err)


def _validate_pf_config(module, config):
    """ Validate if the defined config is present """
    rc, out, err = module.run_command(['ls', config])

    # Fail if no config file is present
    if rc != 0:
        msg_err = f'Error: Config file does not exist: {config}'
        module.fail_json(msg=msg_err)


def status_pf(module):
    """ Current status of pf """
    rc, out, err = module.run_command(['service', 'pf', 'status'])

    # Obtain current status of pf
    if 'Enabled' in out:
        return True
    else:
        return False


def start_pf(module, active_pf):
    """ Start packet filter (pf) if not already running """
    exec_opt = 'start'
    error = False

    rc, out, err = module.run_command(['service', 'pf', exec_opt])

    # Validate exit code
    if rc != 0:
        error = True

    # Validate for status change to make sure the desired
    # state has been reached
    new_active_pf = status_pf(module)
    if new_active_pf == active_pf:
        error = True

    # Exit module on failure of change
    if error:
        msg_err = f'Error: Could not {exec_opt} pf.'
        module.fail_json(msg=msg_err)


def stop_pf(module, active_pf):
    """ Stop packet filter (pf) if not already stopped """
    exec_opt = 'stop'
    error = False

    rc, out, err = module.run_command(['service', 'pf', exec_opt])

    # Validate exit code
    if rc != 0:
        error = True

    # Validate for status change to make sure the desired
    # state has been reached
    new_active_pf = status_pf(module)
    if new_active_pf == active_pf:
        error = True

    # Exit module on failure of change
    if error:
        msg_err = f'Error: Could not {exec_opt} pf.'
        module.fail_json(msg=msg_err)


def restart_pf(module, active_pf):
    """ Restart packet filter (pf) """
    exec_opt = 'restart'
    error = False

    rc, out, err = module.run_command(['service', 'pf', exec_opt])

    # Validate exit code
    if rc != 0:
        error = True

    # Validate for status change to make sure the desired
    # state has been reached
    new_active_pf = status_pf(module)
    if new_active_pf != active_pf:
        error = True

    # Exit module on failure of change
    if error:
        msg_err = f'Error: Could not {exec_opt} pf.'
        module.fail_json(msg=msg_err)


def reload_pf(module, config, dry_run, filter):
    """ Restart packet filter (pf) """
    error = False

    # Create filter object
    filter = _set_filter_type(filter)

    # We need to create a switch case for filter to avoid
    # failing with an empty option param when invoked by
    # ansible run_command
    if dry_run:
        # Dry run with verbose output
        if filter != 'ignore':
            rc, out, err = module.run_command(['pfctl', filter, '-vnf', config])
        else:
            rc, out, err = module.run_command(['pfctl', '-vnf', config])
    else:
        # Flush rule set and apply new rule set
        if filter != 'ignore':
            rc, out, err = module.run_command(['pfctl', filter, '-f', config])
        else:
            rc, out, err = module.run_command(['pfctl', '-f', config])

    # Validate exit code
    if rc != 0:
        error = True

    # Exit module on failures
    if error:
        msg_err = 'Error: Could not reload pf.'
        module.fail_json(msg=msg_err)

    return out


def _set_filter_type(filter):
    """ Remap and set the defined filter type for the rule set """
    if filter == 'nat':
        return '-N'
    if filter == 'options':
        return '-O'
    if filter == 'filter':
        return '-R'


if __name__ == '__main__':
    main()
