# -*- coding: utf-8 -*-

# Copyright (c) 2015, Peter Sprygada <psprygada@ansible.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):

    # Standard files documentation fragment
    DOCUMENTATION = r"""
options:
  host:
    description:
      - Specifies the DNS host name or address for connecting to the remote device over the specified transport. The value
        of host is used as the destination address for the transport. Note this argument does not affect the SSH argument.
    type: str
  port:
    description:
      - Specifies the port to use when building the connection to the remote device. This value applies to either O(transport=cli)
        or O(transport=rest). The port value defaults to the appropriate transport common port if none is provided in the
        task. (cli=22, http=80, https=443). Note this argument does not affect the SSH transport.
    type: int
    default: 0 (use common port)
  username:
    description:
      - Configures the username to use to authenticate the connection to the remote device. This value is used to authenticate
        either the CLI login or the eAPI authentication depending on which transport is used. Note this argument does not
        affect the SSH transport. If the value is not specified in the task, the value of environment variable E(ANSIBLE_NET_USERNAME)
        is used instead.
    type: str
  password:
    description:
      - Specifies the password to use to authenticate the connection to the remote device. This is a common argument used
        for either O(transport=cli) or O(transport=rest). Note this argument does not affect the SSH transport. If the value
        is not specified in the task, the value of environment variable E(ANSIBLE_NET_PASSWORD) is used instead.
    type: str
  timeout:
    description:
      - Specifies the timeout in seconds for communicating with the network device for either connecting or sending commands.
        If the timeout is exceeded before the operation is completed, the module fails.
    type: int
    default: 10
  ssh_keyfile:
    description:
      - Specifies the SSH key to use to authenticate the connection to the remote device. This argument is only used for O(transport=cli).
        If the value is not specified in the task, the value of environment variable E(ANSIBLE_NET_SSH_KEYFILE) is used instead.
    type: path
  transport:
    description:
      - Configures the transport connection to use when connecting to the remote device. The transport argument supports connectivity
        to the device over SSH (V(ssh)), CLI (V(cli)), or REST (V(rest)).
    required: true
    type: str
    choices: [cli, rest, ssh]
    default: ssh
  use_ssl:
    description:
      - Configures the O(transport) to use SSL if set to V(true) only when the O(transport) argument is configured as rest.
        If the transport argument is not V(rest), this value is ignored.
    type: bool
    default: true
  provider:
    description:
      - Convenience method that allows all C(openswitch) arguments to be passed as a dict object. All constraints (required,
        choices, and so on) must be met either by individual arguments or values in this dict.
    type: dict
"""
