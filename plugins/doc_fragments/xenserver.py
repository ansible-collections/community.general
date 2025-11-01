# Copyright (c) 2018, Bojan Vitnik <bvitnik@mainstream.rs>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


class ModuleDocFragment:
    # Common parameters for XenServer modules
    DOCUMENTATION = r"""
options:
  hostname:
    description:
      - The hostname or IP address of the XenServer host or XenServer pool master.
      - If the value is not specified in the task, the value of environment variable E(XENSERVER_HOST) is used instead.
    type: str
    default: localhost
    aliases: [host, pool]
  username:
    description:
      - The username to use for connecting to XenServer.
      - If the value is not specified in the task, the value of environment variable E(XENSERVER_USER) is used instead.
    type: str
    default: root
    aliases: [admin, user]
  password:
    description:
      - The password to use for connecting to XenServer.
      - If the value is not specified in the task, the value of environment variable E(XENSERVER_PASSWORD) is used instead.
    type: str
    aliases: [pass, pwd]
  validate_certs:
    description:
      - Allows connection when SSL certificates are not valid. Set to V(false) when certificates are not trusted.
      - If the value is not specified in the task, the value of environment variable E(XENSERVER_VALIDATE_CERTS) is used instead.
    type: bool
    default: true
"""
