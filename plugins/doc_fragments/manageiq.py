# Copyright (c) 2017, Daniel Korn <korndaniel1@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


class ModuleDocFragment:
    # Standard ManageIQ documentation fragment
    DOCUMENTATION = r"""
options:
  manageiq_connection:
    description:
      - ManageIQ connection configuration information.
    required: false
    type: dict
    suboptions:
      url:
        description:
          - ManageIQ environment URL. E(MIQ_URL) environment variable if set. Otherwise, it is required to pass it.
        type: str
        required: false
      username:
        description:
          - ManageIQ username. E(MIQ_USERNAME) environment variable if set. Otherwise, required if no token is passed in.
        type: str
      password:
        description:
          - ManageIQ password. E(MIQ_PASSWORD) environment variable if set. Otherwise, required if no token is passed in.
        type: str
      token:
        description:
          - ManageIQ token. E(MIQ_TOKEN) environment variable if set. Otherwise, required if no username or password is passed
            in.
        type: str
      validate_certs:
        description:
          - Whether SSL certificates should be verified for HTTPS requests.
        type: bool
        default: true
        aliases: [verify_ssl]
      ca_cert:
        description:
          - The path to a CA bundle file or directory with certificates.
        type: str
        aliases: [ca_bundle_path]

requirements:
  - 'manageiq-client U(https://github.com/ManageIQ/manageiq-api-client-python/)'
"""
