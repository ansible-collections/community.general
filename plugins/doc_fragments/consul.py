# -*- coding: utf-8 -*-
# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ModuleDocFragment:
    # Common parameters for Consul modules
    DOCUMENTATION = r"""
options:
  host:
    description:
      - Host of the consul agent, defaults to V(localhost).
    default: localhost
    type: str
  port:
    type: int
    description:
      - The port on which the consul agent is running.
    default: 8500
  scheme:
    description:
      - The protocol scheme on which the consul agent is running.
        Defaults to V(http) and can be set to V(https) for secure connections.
    default: http
    type: str
  validate_certs:
    type: bool
    description:
      - Whether to verify the TLS certificate of the consul agent.
    default: true
  ca_path:
    description:
      - The CA bundle to use for https connections
    type: str
"""

    TOKEN = r"""
options:
  token:
    description:
      - The token to use for authorization.
    type: str
"""

    ACTIONGROUP_CONSUL = r"""
options: {}
attributes:
  action_group:
    description: Use C(group/community.general.consul) in C(module_defaults) to set defaults for this module.
    support: full
    membership:
      - community.general.consul
    version_added: 8.3.0
"""
