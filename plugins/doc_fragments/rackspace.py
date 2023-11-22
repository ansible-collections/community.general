# -*- coding: utf-8 -*-

# Copyright (c) 2014, Matt Martz <matt@sivel.net>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):

    # Standard Rackspace only documentation fragment
    DOCUMENTATION = r'''
options:
  api_key:
    description:
      - Rackspace API key, overrides O(credentials).
    type: str
    aliases: [ password ]
  credentials:
    description:
      - File to find the Rackspace credentials in. Ignored if O(api_key) and
        O(username) are provided.
    type: path
    aliases: [ creds_file ]
  env:
    description:
      - Environment as configured in C(~/.pyrax.cfg),
        see U(https://github.com/rackspace/pyrax/blob/master/docs/getting_started.md#pyrax-configuration).
    type: str
  region:
    description:
      - Region to create an instance in.
    type: str
  username:
    description:
      - Rackspace username, overrides O(credentials).
    type: str
  validate_certs:
    description:
      - Whether or not to require SSL validation of API endpoints.
    type: bool
    aliases: [ verify_ssl ]
requirements:
  - pyrax
notes:
  - The following environment variables can be used, E(RAX_USERNAME),
    E(RAX_API_KEY), E(RAX_CREDS_FILE), E(RAX_CREDENTIALS), E(RAX_REGION).
  - E(RAX_CREDENTIALS) and E(RAX_CREDS_FILE) point to a credentials file
    appropriate for pyrax. See U(https://github.com/rackspace/pyrax/blob/master/docs/getting_started.md#authenticating).
  - E(RAX_USERNAME) and E(RAX_API_KEY) obviate the use of a credentials file.
  - E(RAX_REGION) defines a Rackspace Public Cloud region (DFW, ORD, LON, ...).
'''

    # Documentation fragment including attributes to enable communication
    # of other OpenStack clouds. Not all rax modules support this.
    OPENSTACK = r'''
options:
  api_key:
    type: str
    description:
      - Rackspace API key, overrides O(credentials).
    aliases: [ password ]
  auth_endpoint:
    type: str
    description:
      - The URI of the authentication service.
      - If not specified will be set to U(https://identity.api.rackspacecloud.com/v2.0/).
  credentials:
    type: path
    description:
      - File to find the Rackspace credentials in. Ignored if O(api_key) and
        O(username) are provided.
    aliases: [ creds_file ]
  env:
    type: str
    description:
      - Environment as configured in C(~/.pyrax.cfg),
        see U(https://github.com/rackspace/pyrax/blob/master/docs/getting_started.md#pyrax-configuration).
  identity_type:
    type: str
    description:
      - Authentication mechanism to use, such as rackspace or keystone.
    default: rackspace
  region:
    type: str
    description:
      - Region to create an instance in.
  tenant_id:
    type: str
    description:
      - The tenant ID used for authentication.
  tenant_name:
    type: str
    description:
      - The tenant name used for authentication.
  username:
    type: str
    description:
      - Rackspace username, overrides O(credentials).
  validate_certs:
    description:
      - Whether or not to require SSL validation of API endpoints.
    type: bool
    aliases: [ verify_ssl ]
deprecated:
  removed_in: 9.0.0
  why: This module relies on the deprecated package pyrax.
  alternative: Use the Openstack modules instead.
requirements:
  - pyrax
notes:
  - The following environment variables can be used, E(RAX_USERNAME),
    E(RAX_API_KEY), E(RAX_CREDS_FILE), E(RAX_CREDENTIALS), E(RAX_REGION).
  - E(RAX_CREDENTIALS) and E(RAX_CREDS_FILE) points to a credentials file
    appropriate for pyrax. See U(https://github.com/rackspace/pyrax/blob/master/docs/getting_started.md#authenticating).
  - E(RAX_USERNAME) and E(RAX_API_KEY) obviate the use of a credentials file.
  - E(RAX_REGION) defines a Rackspace Public Cloud region (DFW, ORD, LON, ...).
'''
