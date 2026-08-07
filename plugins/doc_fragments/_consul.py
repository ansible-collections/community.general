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
  addr:
    description:
      - The address of the Consul agent, in the V(host:port) or V(scheme://host:port) form. The scheme and the port are
        optional, the host is not.
      - O(host), O(port) and O(scheme) take precedence over the components of this option.
      - If unset, the value of the E(CONSUL_HTTP_ADDR) environment variable is used when set. An address these modules
        cannot use, a C(unix://) socket for example, makes the module fail, unless O(host), O(port) and O(scheme) are all
        set, in which case the address is not consulted at all.
    type: str
    version_added: 13.3.0
  host:
    description:
      - Host of the Consul agent.
      - If unset, the host component of O(addr) is used, and V(localhost) when O(addr) is not set either.
    type: str
  port:
    type: int
    description:
      - The port on which the consul agent is running.
      - If unset, the port component of O(addr) is used, and V(8500) when that does not specify one either.
  scheme:
    description:
      - The protocol scheme on which the Consul agent is running.
      - If unset, a C(true) value in the E(CONSUL_HTTP_SSL) environment variable selects V(https), otherwise the scheme
        component of O(addr) is used, and V(http) when that does not specify one either. A C(false) E(CONSUL_HTTP_SSL) does
        not downgrade an V(https) O(addr).
    type: str
  validate_certs:
    type: bool
    description:
      - Whether to verify the TLS certificate of the Consul agent.
      - If unset, the value of the E(CONSUL_HTTP_SSL_VERIFY) environment variable is used when set.
        This is supported since community.general 13.3.0.
    default: true
  ca_path:
    description:
      - The CA bundle to use for https connections.
      - If unset, the value of the E(CONSUL_CACERT) environment variable is used when set.
        This is supported since community.general 13.3.0.
    type: str
"""

    TOKEN = r"""
options:
  token:
    description:
      - The token to use for authorization.
      - If unset, the value of the E(CONSUL_HTTP_TOKEN) environment variable is used.
        This is supported since community.general 13.3.0.
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
