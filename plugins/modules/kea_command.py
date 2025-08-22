#!/usr/bin/python
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

# Copyright © Thorsten Glaser <tglaser@b1-systems.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

# note: this module has not been tested with Python, as the switch from ISC DHCPD to KEA occurs at a time where distros only ship Python3 instead.
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = r"""
---
module: kea_command
short_description: Submits generic command to ISC KEA server on target
description:
- Submits a command to the JSON API of an ISC KEA server running on the target and obtains the result.
- This module supports sending arbitrary commands and returns the server response unchecked;
  while it would be possible to write individual modules for specific KEA service commands,
  that approach would not scale, as the FOSS hooks alone provide dozens of commands.
- Between sending the command and parsing the result status, changed will register as true if an error occurs,
  to err on the safe side.
version_added: '11.3.0'
author: Thorsten Glaser (@mirabilos)
options:
  command:
    description:
    - The name of the command to send, for example C(status-get).
    required: true
    type: str
  arguments:
    description:
    - The arguments sent along with the command, if any.
    - Use V({}) to send an empty JSONObject instead of omitting.
    type: dict
  rv_unchanged:
    description:
    - A list of C(result) codes to indicate success but unchanged system state.
    - Set this to V([0]) for most acquisition commands.
    - Use V([3]) for C(lease4-del) and similar which have a separate code for this.
    - Any C(result) codes not listed in either O(rv_unchanged) or O(rv_changed) are interpreted as indicating an error result.
    - O(rv_unchanged) has precedence over O(rv_changed) if a result code is in both lists.
    type: list
    elements: int
    default: []
  rv_changed:
    description:
    - A list of C(result) codes to indicate success and changed system state.
    - Omit this for most acquisition commands.
    - Set it to V([0]) for C(lease4-del) and similar which return changed system state that way.
    - Any C(result) codes not listed in either O(rv_unchanged) or O(rv_changed) are interpreted as indicating an error result.
    - O(rv_unchanged) has precedence over O(rv_changed) if a result code is in both lists.
    type: list
    elements: int
    default: []
  socket:
    description:
    - The full pathname of the Unix Domain Socket to connect to.
    - The default value is suitable for C(kea-dhcp4-server) on Debian trixie.
    - This module directly interfacees via UDS; the HTTP wrappers are not supported.
    type: path
    default: /run/kea/kea4-ctrl-socket
extends_documentation_fragment:
- action_common_attributes
attributes:
  check_mode:
    details: Neither return codes nor the server response are available during check mode, and in fact not returned by the module in check mode.
    support: partial
  diff_mode:
    support: none
  platform:
    support: full
    platforms: posix
"""

EXAMPLES = r"""
vars:
  ipaddr: "192.168.123.45"
  hwaddr: "00:00:5E:00:53:00"
tasks:
# an example for a request acquiring information
- name: Get KEA DHCP6 status
  kea_command:
    command: status-get
    rv_unchanged: [0]
    socket: /run/kea/kea6-ctrl-socket
  register: kea6_status
- name: Display registered status result
  ansible.builtin.debug:
    msg: KEA DHCP6 running on PID {{ kea6_status.response.arguments.pid }}
# an example for requests modifying state
- name: Remove existing leases for {{ ipaddr }}, if any
  kea_command:
    command: lease4-del
    arguments:
      ip-address: "{{ ipaddr }}"
    rv_changed: [0]
    rv_unchanged: [3]
- name: Add DHCP lease for {{ ipaddr }}
  kea_command:
    command: lease4-add
    arguments:
      ip-address: "{{ ipaddr }}"
      hw-address: "{{ hwaddr }}"
    rv_changed: [0]
"""

RETURN = r"""
response:
  description: The server JSON response.
  returned: if available and not check mode
  type: dict
msg:
  description: An error message.
  returned: failure
  type: str
"""

import json
import os
import socket

from ansible.module_utils.basic import AnsibleModule


def _parse_constant(s):
    raise ValueError('Invalid JSON: "%s"' % s)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            command=dict(type='str', required=True),
            arguments=dict(type='dict'),
            rv_unchanged=dict(type='list', elements='int', default=[]),
            rv_changed=dict(type='list', elements='int', default=[]),
            socket=dict(type='path', default='/run/kea/kea4-ctrl-socket'),
        ),
        supports_check_mode=True,
    )

    cmd = {}
    cmd['command'] = module.params['command']
    if module.params['arguments'] is not None:
        cmd['arguments'] = module.params['arguments']
    cmdstr = json.dumps(cmd, ensure_ascii=True, allow_nan=False, indent=None, separators=(',', ':'), sort_keys=True)
    rvok = module.params['rv_unchanged']
    rvch = module.params['rv_changed']
    sockfn = module.params['socket']

    r = {
        'changed': False
    }
    rsp = b''

    if not os.path.exists(sockfn):
        module.fail_json(msg='socket (%s) does not exist' % sockfn, **r)
    if module.check_mode:
        module.exit_json(**r)

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        try:
            sock.connect(sockfn)
        except OSError as ex:
            module.fail_json(msg='could not connect to socket (%s)' % sockfn, exception=ex, **r)
        # better safe in case anything fails…
        r['changed'] = True
        try:
            sock.sendall(cmdstr.encode('ASCII'))
        except OSError as ex:
            module.fail_json(msg='could not write to socket (%s)' % sockfn, exception=ex, **r)

        try:
            while True:
                rspnew = sock.recv(8192)
                if len(rspnew) == 0:
                    break
                rsp += rspnew
        except OSError as ex:
            module.fail_json(msg='error reading from socket (%s)' % sockfn, exception=ex, **r)

    if len(rsp) < 15:
        module.fail_json(msg='unrealistically short response ' + repr(rsp), **r)

    try:
        r['response'] = json.loads(rsp, parse_constant=_parse_constant)
    except ValueError as ex:
        module.fail_json(msg='error parsing JSON response', exception=ex, **r)
    if not isinstance(r['response'], dict):
        module.fail_json(**r, msg='bogus JSON response (JSONObject expected)')
    if 'result' not in r['response']:
        module.fail_json(**r, msg='bogus JSON response (missing result)')
    res = r['response']['result']
    if not isinstance(res, int):
        module.fail_json(**r, msg='bogus JSON response (nōn-integer result)')

    if res in rvok:
        r['changed'] = False
    elif res not in rvch:
        module.fail_json(msg='failure result (code %d)' % res, **r)

    module.exit_json(**r)


if __name__ == '__main__':
    main()
