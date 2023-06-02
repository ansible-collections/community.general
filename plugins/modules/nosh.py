#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017, Thomas Caravia <taca@kadisius.eu>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: nosh
author:
    - "Thomas Caravia (@tacatac)"
short_description: Manage services with nosh
description:
    - Control running and enabled state for system-wide or user services.
    - BSD and Linux systems are supported.
options:
    name:
        type: str
        required: true
        description:
            - Name of the service to manage.
    state:
        type: str
        required: false
        choices: [ started, stopped, reset, restarted, reloaded ]
        description:
            - C(started)/C(stopped) are idempotent actions that will not run
              commands unless necessary.
              C(restarted) will always bounce the service.
              C(reloaded) will send a SIGHUP or start the service.
              C(reset) will start or stop the service according to whether it is
              enabled or not.
    enabled:
        required: false
        type: bool
        description:
            - Enable or disable the service, independently of C(*.preset) file
              preference or running state. Mutually exclusive with I(preset). Will take
              effect prior to I(state=reset).
    preset:
        required: false
        type: bool
        description:
            - Enable or disable the service according to local preferences in C(*.preset) files.
              Mutually exclusive with I(enabled). Only has an effect if set to true. Will take
              effect prior to I(state=reset).
    user:
        required: false
        default: false
        type: bool
        description:
            - Run system-control talking to the calling user's service manager, rather than
              the system-wide service manager.
requirements:
    - A system with an active nosh service manager, see Notes for further information.
notes:
    - Information on the nosh utilities suite may be found at U(https://jdebp.eu/Softwares/nosh/).
'''

EXAMPLES = '''
- name: Start dnscache if not running
  community.general.nosh:
    name: dnscache
    state: started

- name: Stop mpd, if running
  community.general.nosh:
    name: mpd
    state: stopped

- name: Restart unbound or start it if not already running
  community.general.nosh:
    name: unbound
    state: restarted

- name: Reload fail2ban or start it if not already running
  community.general.nosh:
    name: fail2ban
    state: reloaded

- name: Disable nsd
  community.general.nosh:
    name: nsd
    enabled: false

- name: For package installers, set nginx running state according to local enable settings, preset and reset
  community.general.nosh:
    name: nginx
    preset: true
    state: reset

- name: Reboot the host if nosh is the system manager, would need a "wait_for*" task at least, not recommended as-is
  community.general.nosh:
    name: reboot
    state: started

- name: Using conditionals with the module facts
  tasks:
    - name: Obtain information on tinydns service
      community.general.nosh:
        name: tinydns
      register: result

    - name: Fail if service not loaded
      ansible.builtin.fail:
        msg: "The {{ result.name }} service is not loaded"
      when: not result.status

    - name: Fail if service is running
      ansible.builtin.fail:
        msg: "The {{ result.name }} service is running"
      when: result.status and result.status['DaemontoolsEncoreState'] == "running"
'''

RETURN = '''
name:
    description: name used to find the service
    returned: success
    type: str
    sample: "sshd"
service_path:
    description: resolved path for the service
    returned: success
    type: str
    sample: "/var/sv/sshd"
enabled:
    description: whether the service is enabled at system bootstrap
    returned: success
    type: bool
    sample: true
preset:
    description: whether the enabled status reflects the one set in the relevant C(*.preset) file
    returned: success
    type: bool
    sample: 'False'
state:
    description: service process run state, C(None) if the service is not loaded and will not be started
    returned: if state option is used
    type: str
    sample: "reloaded"
status:
    description: A dictionary with the key=value pairs returned by C(system-control show-json) or C(None) if the service is not loaded
    returned: success
    type: complex
    contains:
        After:
            description: []  # FIXME
            returned: success
            type: list
            sample: ["/etc/service-bundles/targets/basic","../sshdgenkeys", "log"]
        Before:
            description: []  # FIXME
            returned: success
            type: list
            sample: ["/etc/service-bundles/targets/shutdown"]
        Conflicts:
            description: []  # FIXME
            returned: success
            type: list
            sample: []
        DaemontoolsEncoreState:
            description: []  # FIXME
            returned: success
            type: str
            sample: "running"
        DaemontoolsState:
            description: []  # FIXME
            returned: success
            type: str
            sample: "up"
        Enabled:
            description: []  # FIXME
            returned: success
            type: bool
            sample: true
        LogService:
            description: []  # FIXME
            returned: success
            type: str
            sample: "../cyclog@sshd"
        MainPID:
            description: []  # FIXME
            returned: success
            type: int
            sample: 661
        Paused:
            description: []  # FIXME
            returned: success
            type: bool
            sample: 'False'
        ReadyAfterRun:
            description: []  # FIXME
            returned: success
            type: bool
            sample: 'False'
        RemainAfterExit:
            description: []  # FIXME
            returned: success
            type: bool
            sample: 'False'
        Required-By:
            description: []  # FIXME
            returned: success
            type: list
            sample: []
        RestartExitStatusCode:
            description: []  # FIXME
            returned: success
            type: int
            sample: '0'
        RestartExitStatusNumber:
            description: []  # FIXME
            returned: success
            type: int
            sample: '0'
        RestartTimestamp:
            description: []  # FIXME
            returned: success
            type: int
            sample: 4611686019935648081
        RestartUTCTimestamp:
            description: []  # FIXME
            returned: success
            type: int
            sample: 1508260140
        RunExitStatusCode:
            description: []  # FIXME
            returned: success
            type: int
            sample: '0'
        RunExitStatusNumber:
            description: []  # FIXME
            returned: success
            type: int
            sample: '0'
        RunTimestamp:
            description: []  # FIXME
            returned: success
            type: int
            sample: 4611686019935648081
        RunUTCTimestamp:
            description: []  # FIXME
            returned: success
            type: int
            sample: 1508260140
        StartExitStatusCode:
            description: []  # FIXME
            returned: success
            type: int
            sample: 1
        StartExitStatusNumber:
            description: []  # FIXME
            returned: success
            type: int
            sample: '0'
        StartTimestamp:
            description: []  # FIXME
            returned: success
            type: int
            sample: 4611686019935648081
        StartUTCTimestamp:
            description: []  # FIXME
            returned: success
            type: int
            sample: 1508260140
        StopExitStatusCode:
            description: []  # FIXME
            returned: success
            type: int
            sample: '0'
        StopExitStatusNumber:
            description: []  # FIXME
            returned: success
            type: int
            sample: '0'
        StopTimestamp:
            description: []  # FIXME
            returned: success
            type: int
            sample: 4611686019935648081
        StopUTCTimestamp:
            description: []  # FIXME
            returned: success
            type: int
            sample: 1508260140
        Stopped-By:
            description: []  # FIXME
            returned: success
            type: list
            sample: ["/etc/service-bundles/targets/shutdown"]
        Timestamp:
            description: []  # FIXME
            returned: success
            type: int
            sample: 4611686019935648081
        UTCTimestamp:
            description: []  # FIXME
            returned: success
            type: int
            sample: 1508260140
        Want:
            description: []  # FIXME
            returned: success
            type: str
            sample: "nothing"
        Wanted-By:
            description: []  # FIXME
            returned: success
            type: list
            sample: ["/etc/service-bundles/targets/server","/etc/service-bundles/targets/sockets"]
        Wants:
            description: []  # FIXME
            returned: success
            type: list
            sample: ["/etc/service-bundles/targets/basic","../sshdgenkeys"]
user:
    description: whether the user-level service manager is called
    returned: success
    type: bool
    sample: false
'''


import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.service import fail_if_missing
from ansible.module_utils.common.text.converters import to_native


def run_sys_ctl(module, args):
    sys_ctl = [module.get_bin_path('system-control', required=True)]
    if module.params['user']:
        sys_ctl = sys_ctl + ['--user']
    return module.run_command(sys_ctl + args)


def get_service_path(module, service):
    (rc, out, err) = run_sys_ctl(module, ['find', service])
    # fail if service not found
    if rc != 0:
        fail_if_missing(module, False, service, msg='host')
    else:
        return to_native(out).strip()


def service_is_enabled(module, service_path):
    (rc, out, err) = run_sys_ctl(module, ['is-enabled', service_path])
    return rc == 0


def service_is_preset_enabled(module, service_path):
    (rc, out, err) = run_sys_ctl(module, ['preset', '--dry-run', service_path])
    return to_native(out).strip().startswith("enable")


def service_is_loaded(module, service_path):
    (rc, out, err) = run_sys_ctl(module, ['is-loaded', service_path])
    return rc == 0


def get_service_status(module, service_path):
    (rc, out, err) = run_sys_ctl(module, ['show-json', service_path])
    # will fail if not service is not loaded
    if err is not None and err:
        module.fail_json(msg=err)
    else:
        json_out = json.loads(to_native(out).strip())
        status = json_out[service_path]  # descend past service path header
        return status


def service_is_running(service_status):
    return service_status['DaemontoolsEncoreState'] in set(['starting', 'started', 'running'])


def handle_enabled(module, result, service_path):
    """Enable or disable a service as needed.

    - 'preset' will set the enabled state according to available preset file settings.
    - 'enabled' will set the enabled state explicitly, independently of preset settings.

    These options are set to "mutually exclusive" but the explicit 'enabled' option will
    have priority if the check is bypassed.
    """

    # computed prior in control flow
    preset = result['preset']
    enabled = result['enabled']

    # preset, effect only if option set to true (no reverse preset)
    if module.params['preset']:
        action = 'preset'

        # run preset if needed
        if preset != module.params['preset']:
            result['changed'] = True
            if not module.check_mode:
                (rc, out, err) = run_sys_ctl(module, [action, service_path])
                if rc != 0:
                    module.fail_json(msg="Unable to %s service %s: %s" % (action, service_path, out + err))
            result['preset'] = not preset
            result['enabled'] = not enabled

    # enabled/disabled state
    if module.params['enabled'] is not None:
        if module.params['enabled']:
            action = 'enable'
        else:
            action = 'disable'

        # change enable/disable if needed
        if enabled != module.params['enabled']:
            result['changed'] = True
            if not module.check_mode:
                (rc, out, err) = run_sys_ctl(module, [action, service_path])
                if rc != 0:
                    module.fail_json(msg="Unable to %s service %s: %s" % (action, service_path, out + err))
            result['enabled'] = not enabled
            result['preset'] = not preset


def handle_state(module, result, service_path):
    """Set service running state as needed.

    Takes into account the fact that a service may not be loaded (no supervise directory) in
    which case it is 'stopped' as far as the service manager is concerned. No status information
    can be obtained and the service can only be 'started'.
    """
    # default to desired state, no action
    result['state'] = module.params['state']
    state = module.params['state']
    action = None

    # computed prior in control flow, possibly modified by handle_enabled()
    enabled = result['enabled']

    # service not loaded -> not started by manager, no status information
    if not service_is_loaded(module, service_path):
        if state in ['started', 'restarted', 'reloaded']:
            action = 'start'
            result['state'] = 'started'
        elif state == 'reset':
            if enabled:
                action = 'start'
                result['state'] = 'started'
            else:
                result['state'] = None
        else:
            result['state'] = None

    # service is loaded
    else:
        # get status information
        result['status'] = get_service_status(module, service_path)
        running = service_is_running(result['status'])

        if state == 'started':
            if not running:
                action = 'start'
        elif state == 'stopped':
            if running:
                action = 'stop'
        # reset = start/stop according to enabled status
        elif state == 'reset':
            if enabled is not running:
                if running:
                    action = 'stop'
                    result['state'] = 'stopped'
                else:
                    action = 'start'
                    result['state'] = 'started'
        # start if not running, 'service' module constraint
        elif state == 'restarted':
            if not running:
                action = 'start'
                result['state'] = 'started'
            else:
                action = 'condrestart'
        # start if not running, 'service' module constraint
        elif state == 'reloaded':
            if not running:
                action = 'start'
                result['state'] = 'started'
            else:
                action = 'hangup'

    # change state as needed
    if action:
        result['changed'] = True
        if not module.check_mode:
            (rc, out, err) = run_sys_ctl(module, [action, service_path])
            if rc != 0:
                module.fail_json(msg="Unable to %s service %s: %s" % (action, service_path, err))

# ===========================================
# Main control flow


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            state=dict(type='str', choices=['started', 'stopped', 'reset', 'restarted', 'reloaded']),
            enabled=dict(type='bool'),
            preset=dict(type='bool'),
            user=dict(type='bool', default=False),
        ),
        supports_check_mode=True,
        mutually_exclusive=[['enabled', 'preset']],
    )

    service = module.params['name']
    rc = 0
    out = err = ''
    result = {
        'name': service,
        'changed': False,
        'status': None,
    }

    # check service can be found (or fail) and get path
    service_path = get_service_path(module, service)

    # get preliminary service facts
    result['service_path'] = service_path
    result['user'] = module.params['user']
    result['enabled'] = service_is_enabled(module, service_path)
    result['preset'] = result['enabled'] is service_is_preset_enabled(module, service_path)

    # set enabled state, service need not be loaded
    if module.params['enabled'] is not None or module.params['preset']:
        handle_enabled(module, result, service_path)

    # set service running state
    if module.params['state'] is not None:
        handle_state(module, result, service_path)

    # get final service status if possible
    if service_is_loaded(module, service_path):
        result['status'] = get_service_status(module, service_path)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
