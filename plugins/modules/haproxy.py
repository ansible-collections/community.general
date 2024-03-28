#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2014, Ravi Bhure <ravibhure@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: haproxy
short_description: Enable, disable, and set weights for HAProxy backend servers using socket commands
author:
    - Ravi Bhure (@ravibhure)
description:
    - Enable, disable, drain and set weights for HAProxy backend servers using socket commands.
notes:
    - Enable, disable and drain commands are restricted and can only be issued on
      sockets configured for level 'admin'. For example, you can add the line
      'stats socket /var/run/haproxy.sock level admin' to the general section of
      haproxy.cfg. See U(http://haproxy.1wt.eu/download/1.5/doc/configuration.txt).
    - Depends on netcat (C(nc)) being available; you need to install the appropriate
      package for your operating system before this module can be used.
extends_documentation_fragment:
    - community.general.attributes
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options:
  backend:
    description:
      - Name of the HAProxy backend pool.
      - If this parameter is unset, it will be auto-detected.
    type: str
  drain:
    description:
      - Wait until the server has no active connections or until the timeout
        determined by wait_interval and wait_retries is reached.
      - Continue only after the status changes to C(MAINT).
      - This overrides the shutdown_sessions option.
    type: bool
    default: false
  host:
    description:
      - Name of the backend host to change.
    type: str
    required: true
  shutdown_sessions:
    description:
      - When disabling a server, immediately terminate all the sessions attached
        to the specified server.
      - This can be used to terminate long-running sessions after a server is put
        into maintenance mode. Overridden by the drain option.
    type: bool
    default: false
  socket:
    description:
      - Path to the HAProxy socket file.
    type: path
    default: /var/run/haproxy.sock
  state:
    description:
      - Desired state of the provided backend host.
      - Note that V(drain) state was added in version 2.4.
      - It is supported only by HAProxy version 1.5 or later,
      - When used on versions < 1.5, it will be ignored.
    type: str
    required: true
    choices: [ disabled, drain, enabled ]
  agent:
    description:
      - Disable/enable agent checks (depending on O(state) value).
    type: bool
    default: false
    version_added: 1.0.0
  health:
    description:
      - Disable/enable health checks (depending on O(state) value).
    type: bool
    default: false
    version_added: "1.0.0"
  fail_on_not_found:
    description:
      - Fail whenever trying to enable/disable a backend host that does not exist.
    type: bool
    default: false
  wait:
    description:
      - Wait until the server reports a status of C(UP) when O(state=enabled),
        status of C(MAINT) when O(state=disabled) or status of C(DRAIN) when O(state=drain).
    type: bool
    default: false
  wait_interval:
    description:
      - Number of seconds to wait between retries.
    type: int
    default: 5
  wait_retries:
    description:
      - Number of times to check for status after changing the state.
    type: int
    default: 25
  weight:
    description:
      - The value passed in argument.
      - If the value ends with the V(%) sign, then the new weight will be
        relative to the initially configured weight.
      - Relative weights are only permitted between 0 and 100% and absolute
        weights are permitted between 0 and 256.
    type: str
'''

EXAMPLES = r'''
- name: Disable server in 'www' backend pool
  community.general.haproxy:
    state: disabled
    host: '{{ inventory_hostname }}'
    backend: www

- name: Disable server in 'www' backend pool, also stop health/agent checks
  community.general.haproxy:
    state: disabled
    host: '{{ inventory_hostname }}'
    health: true
    agent: true

- name: Disable server without backend pool name (apply to all available backend pool)
  community.general.haproxy:
    state: disabled
    host: '{{ inventory_hostname }}'

- name: Disable server, provide socket file
  community.general.haproxy:
    state: disabled
    host: '{{ inventory_hostname }}'
    socket: /var/run/haproxy.sock
    backend: www

- name: Disable server, provide socket file, wait until status reports in maintenance
  community.general.haproxy:
    state: disabled
    host: '{{ inventory_hostname }}'
    socket: /var/run/haproxy.sock
    backend: www
    wait: true

# Place server in drain mode, providing a socket file.  Then check the server's
# status every minute to see if it changes to maintenance mode, continuing if it
# does in an hour and failing otherwise.
- community.general.haproxy:
    state: disabled
    host: '{{ inventory_hostname }}'
    socket: /var/run/haproxy.sock
    backend: www
    wait: true
    drain: true
    wait_interval: 60
    wait_retries: 60

- name: Disable backend server in 'www' backend pool and drop open sessions to it
  community.general.haproxy:
    state: disabled
    host: '{{ inventory_hostname }}'
    backend: www
    socket: /var/run/haproxy.sock
    shutdown_sessions: true

- name: Disable server without backend pool name (apply to all available backend pool) but fail when the backend host is not found
  community.general.haproxy:
    state: disabled
    host: '{{ inventory_hostname }}'
    fail_on_not_found: true

- name: Enable server in 'www' backend pool
  community.general.haproxy:
    state: enabled
    host: '{{ inventory_hostname }}'
    backend: www

- name: Enable server in 'www' backend pool wait until healthy
  community.general.haproxy:
    state: enabled
    host: '{{ inventory_hostname }}'
    backend: www
    wait: true

- name: Enable server in 'www' backend pool wait until healthy. Retry 10 times with intervals of 5 seconds to retrieve the health
  community.general.haproxy:
    state: enabled
    host: '{{ inventory_hostname }}'
    backend: www
    wait: true
    wait_retries: 10
    wait_interval: 5

- name: Enable server in 'www' backend pool with change server(s) weight
  community.general.haproxy:
    state: enabled
    host: '{{ inventory_hostname }}'
    socket: /var/run/haproxy.sock
    weight: 10
    backend: www

- name: Set the server in 'www' backend pool to drain mode
  community.general.haproxy:
    state: drain
    host: '{{ inventory_hostname }}'
    socket: /var/run/haproxy.sock
    backend: www
'''

import csv
import socket
import time
from string import Template

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_bytes, to_text


DEFAULT_SOCKET_LOCATION = "/var/run/haproxy.sock"
RECV_SIZE = 1024
ACTION_CHOICES = ['enabled', 'disabled', 'drain']
WAIT_RETRIES = 25
WAIT_INTERVAL = 5


######################################################################
class TimeoutException(Exception):
    pass


class HAProxy(object):
    """
    Used for communicating with HAProxy through its local UNIX socket interface.
    Perform common tasks in Haproxy related to enable server and
    disable server.

    The complete set of external commands Haproxy handles is documented
    on their website:

    http://haproxy.1wt.eu/download/1.5/doc/configuration.txt#Unix Socket commands
    """

    def __init__(self, module):
        self.module = module

        self.state = self.module.params['state']
        self.host = self.module.params['host']
        self.backend = self.module.params['backend']
        self.weight = self.module.params['weight']
        self.socket = self.module.params['socket']
        self.shutdown_sessions = self.module.params['shutdown_sessions']
        self.fail_on_not_found = self.module.params['fail_on_not_found']
        self.agent = self.module.params['agent']
        self.health = self.module.params['health']
        self.wait = self.module.params['wait']
        self.wait_retries = self.module.params['wait_retries']
        self.wait_interval = self.module.params['wait_interval']
        self._drain = self.module.params['drain']
        self.command_results = {}

    def execute(self, cmd, timeout=200, capture_output=True):
        """
        Executes a HAProxy command by sending a message to a HAProxy's local
        UNIX socket and waiting up to 'timeout' milliseconds for the response.
        """
        self.client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.client.connect(self.socket)
        self.client.sendall(to_bytes('%s\n' % cmd))

        result = b''
        buf = b''
        buf = self.client.recv(RECV_SIZE)
        while buf:
            result += buf
            buf = self.client.recv(RECV_SIZE)
        result = to_text(result, errors='surrogate_or_strict')

        if capture_output:
            self.capture_command_output(cmd, result.strip())
        self.client.close()
        return result

    def capture_command_output(self, cmd, output):
        """
        Capture the output for a command
        """
        if 'command' not in self.command_results:
            self.command_results['command'] = []
        self.command_results['command'].append(cmd)
        if 'output' not in self.command_results:
            self.command_results['output'] = []
        self.command_results['output'].append(output)

    def discover_all_backends(self):
        """
        Discover all entries with svname = 'BACKEND' and return a list of their corresponding
        pxnames
        """
        data = self.execute('show stat', 200, False).lstrip('# ')
        r = csv.DictReader(data.splitlines())
        return tuple(map(lambda d: d['pxname'], filter(lambda d: d['svname'] == 'BACKEND', r)))

    def discover_version(self):
        """
        Attempt to extract the haproxy version.
        Return a tuple containing major and minor version.
        """
        data = self.execute('show info', 200, False)
        lines = data.splitlines()
        line = [x for x in lines if 'Version:' in x]
        try:
            version_values = line[0].partition(':')[2].strip().split('.', 3)
            version = (int(version_values[0]), int(version_values[1]))
        except (ValueError, TypeError, IndexError):
            version = None

        return version

    def execute_for_backends(self, cmd, pxname, svname, wait_for_status=None):
        """
        Run some command on the specified backends. If no backends are provided they will
        be discovered automatically (all backends)
        """
        # Discover backends if none are given
        if pxname is None:
            backends = self.discover_all_backends()
        else:
            backends = [pxname]

        # Run the command for each requested backend
        for backend in backends:
            # Fail when backends were not found
            state = self.get_state_for(backend, svname)
            if (self.fail_on_not_found) and state is None:
                self.module.fail_json(
                    msg="The specified backend '%s/%s' was not found!" % (backend, svname))

            if state is not None:
                self.execute(Template(cmd).substitute(pxname=backend, svname=svname))
                if self.wait and not (wait_for_status == "DRAIN" and state == "DOWN"):
                    self.wait_until_status(backend, svname, wait_for_status)

    def get_state_for(self, pxname, svname):
        """
        Find the state of specific services. When pxname is not set, get all backends for a specific host.
        Returns a list of dictionaries containing the status and weight for those services.
        """
        data = self.execute('show stat', 200, False).lstrip('# ')
        r = csv.DictReader(data.splitlines())
        state = tuple(
            map(
                lambda d: {'status': d['status'], 'weight': d['weight'], 'scur': d['scur']},
                filter(lambda d: (pxname is None or d['pxname']
                                  == pxname) and d['svname'] == svname, r)
            )
        )
        return state or None

    def wait_until_status(self, pxname, svname, status):
        """
        Wait for a service to reach the specified status. Try RETRIES times
        with INTERVAL seconds of sleep in between. If the service has not reached
        the expected status in that time, the module will fail. If the service was
        not found, the module will fail.
        """
        for i in range(1, self.wait_retries):
            state = self.get_state_for(pxname, svname)

            # We can assume there will only be 1 element in state because both svname and pxname are always set when we get here
            # When using track we get a status like this: MAINT (via pxname/svname) so we need to do substring matching
            if status in state[0]['status']:
                if not self._drain or state[0]['scur'] == '0':
                    return True
            time.sleep(self.wait_interval)

        self.module.fail_json(msg="server %s/%s not status '%s' after %d retries. Aborting." %
                              (pxname, svname, status, self.wait_retries))

    def enabled(self, host, backend, weight):
        """
        Enabled action, marks server to UP and checks are re-enabled,
        also supports to get current weight for server (default) and
        set the weight for haproxy backend server when provides.
        """
        cmd = "get weight $pxname/$svname; enable server $pxname/$svname"
        if self.agent:
            cmd += "; enable agent $pxname/$svname"
        if self.health:
            cmd += "; enable health $pxname/$svname"
        if weight:
            cmd += "; set weight $pxname/$svname %s" % weight
        self.execute_for_backends(cmd, backend, host, 'UP')

    def disabled(self, host, backend, shutdown_sessions):
        """
        Disabled action, marks server to DOWN for maintenance. In this mode, no more checks will be
        performed on the server until it leaves maintenance,
        also it shutdown sessions while disabling backend host server.
        """
        cmd = "get weight $pxname/$svname"
        if self.agent:
            cmd += "; disable agent $pxname/$svname"
        if self.health:
            cmd += "; disable health $pxname/$svname"
        cmd += "; disable server $pxname/$svname"
        if shutdown_sessions:
            cmd += "; shutdown sessions server $pxname/$svname"
        self.execute_for_backends(cmd, backend, host, 'MAINT')

    def drain(self, host, backend, status='DRAIN'):
        """
        Drain action, sets the server to DRAIN mode.
        In this mode, the server will not accept any new connections
        other than those that are accepted via persistence.
        """
        haproxy_version = self.discover_version()

        # check if haproxy version supports DRAIN state (starting with 1.5)
        if haproxy_version and (1, 5) <= haproxy_version:
            cmd = "set server $pxname/$svname state drain"
            self.execute_for_backends(cmd, backend, host, "DRAIN")
            if status == "MAINT":
                self.disabled(host, backend, self.shutdown_sessions)

    def act(self):
        """
        Figure out what you want to do from ansible, and then do it.
        """
        # Get the state before the run
        self.command_results['state_before'] = self.get_state_for(self.backend, self.host)

        # toggle enable/disable server
        if self.state == 'enabled':
            self.enabled(self.host, self.backend, self.weight)
        elif self.state == 'disabled' and self._drain:
            self.drain(self.host, self.backend, status='MAINT')
        elif self.state == 'disabled':
            self.disabled(self.host, self.backend, self.shutdown_sessions)
        elif self.state == 'drain':
            self.drain(self.host, self.backend)
        else:
            self.module.fail_json(msg="unknown state specified: '%s'" % self.state)

        # Get the state after the run
        self.command_results['state_after'] = self.get_state_for(self.backend, self.host)

        # Report change status
        self.command_results['changed'] = (self.command_results['state_before'] != self.command_results['state_after'])

        self.module.exit_json(**self.command_results)


def main():

    # load ansible module object
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str', required=True, choices=ACTION_CHOICES),
            host=dict(type='str', required=True),
            backend=dict(type='str'),
            weight=dict(type='str'),
            socket=dict(type='path', default=DEFAULT_SOCKET_LOCATION),
            shutdown_sessions=dict(type='bool', default=False),
            fail_on_not_found=dict(type='bool', default=False),
            health=dict(type='bool', default=False),
            agent=dict(type='bool', default=False),
            wait=dict(type='bool', default=False),
            wait_retries=dict(type='int', default=WAIT_RETRIES),
            wait_interval=dict(type='int', default=WAIT_INTERVAL),
            drain=dict(type='bool', default=False),
        ),
    )

    if not socket:
        module.fail_json(msg="unable to locate haproxy socket")

    ansible_haproxy = HAProxy(module)
    ansible_haproxy.act()


if __name__ == '__main__':
    main()
