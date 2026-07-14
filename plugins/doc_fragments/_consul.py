# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Note that this doc fragment is **PRIVATE** to the collection. It can have breaking changes at any time.
# Do not use this from other collections or standalone plugins/modules!

from __future__ import annotations


class ModuleDocFragment:
    # Common parameters for Consul modules
    DOCUMENTATION = r"""
options:
  host:
    description:
      - Host of the Consul agent.
      - If unset, the host component of the E(CONSUL_HTTP_ADDR) environment variable is used when set (since community.general
        13.2.0).
    default: localhost
    type: str
  port:
    type: int
    description:
      - The port on which the consul agent is running.
      - If unset, the port component of the E(CONSUL_HTTP_ADDR) environment variable is used when set (since community.general
        13.2.0).
    default: 8500
  scheme:
    description:
      - The protocol scheme on which the Consul agent is running. Defaults to V(http) and can be set to V(https) for secure
        connections.
      - If unset, a true value in the E(CONSUL_HTTP_SSL) environment variable selects V(https), otherwise the scheme component
        of E(CONSUL_HTTP_ADDR) is used when set (since community.general 13.2.0). A false E(CONSUL_HTTP_SSL) does not downgrade
        an V(https) scheme in E(CONSUL_HTTP_ADDR).
    default: http
    type: str
  validate_certs:
    type: bool
    description:
      - Whether to verify the TLS certificate of the Consul agent.
      - If unset, the value of the E(CONSUL_HTTP_SSL_VERIFY) environment variable is used when set (since community.general
        13.2.0).
    default: true
  ca_path:
    description:
      - The CA bundle to use for https connections.
      - If unset, the value of the E(CONSUL_CACERT) environment variable is used when set (since community.general 13.2.0).
    type: str
"""

    TOKEN = r"""
options:
  token:
    description:
      - The token to use for authorization.
      - If unset, the value of the E(CONSUL_HTTP_TOKEN) environment variable is used (since community.general 13.2.0).
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
"""
