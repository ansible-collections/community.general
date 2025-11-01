# Copyright (c) 2021, Andreas Botzner <andreas at botzner dot com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


class ModuleDocFragment:
    # Common parameters for Redis modules
    DOCUMENTATION = r"""
options:
  login_host:
    description:
      - Specify the target host running the database.
    default: localhost
    type: str
  login_port:
    description:
      - Specify the port to connect to.
    default: 6379
    type: int
  login_user:
    description:
      - Specify the user to authenticate with.
      - Requires L(redis,https://pypi.org/project/redis) >= 3.4.0.
    type: str
  login_password:
    description:
      - Specify the password to authenticate with.
      - Usually not used when target is localhost.
    type: str
  tls:
    description:
      - Specify whether or not to use TLS for the connection.
    type: bool
    default: true
  validate_certs:
    description:
      - Specify whether or not to validate TLS certificates.
      - This should only be turned off for personally controlled sites or with C(localhost) as target.
    type: bool
    default: true
  ca_certs:
    description:
      - Path to root certificates file. If not set and O(tls) is set to V(true), certifi's CA certificates are used.
    type: str
  client_cert_file:
    description:
      - Path to the client certificate file.
    type: str
    version_added: 9.3.0
  client_key_file:
    description:
      - Path to the client private key file.
    type: str
    version_added: 9.3.0
requirements: ["redis", "certifi"]

notes:
  - Requires the C(redis) Python package on the remote host. You can install it with pip (C(pip install redis)) or with a
    package manager. Information on the library can be found at U(https://github.com/andymccurdy/redis-py).
"""
