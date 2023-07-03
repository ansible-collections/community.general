# -*- coding: utf-8 -*-
# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):
    # Common parameters for Proxmox VE modules
    DOCUMENTATION = r'''
options:
  api_host:
    description:
      - Specify the target host of the Proxmox VE cluster.
    type: str
    required: true
  api_user:
    description:
      - Specify the user to authenticate with.
    type: str
    required: true
  api_password:
    description:
      - Specify the password to authenticate with.
      - You can use E(PROXMOX_PASSWORD) environment variable.
    type: str
  api_token_id:
    description:
      - Specify the token ID.
      - Requires C(proxmoxer>=1.1.0) to work.
    type: str
    version_added: 1.3.0
  api_token_secret:
    description:
      - Specify the token secret.
      - Requires C(proxmoxer>=1.1.0) to work.
    type: str
    version_added: 1.3.0
  validate_certs:
    description:
      - If V(false), SSL certificates will not be validated.
      - This should only be used on personally controlled sites using self-signed certificates.
    type: bool
    default: false
requirements: [ "proxmoxer", "requests" ]
'''

    SELECTION = r'''
options:
  vmid:
    description:
      - Specifies the instance ID.
      - If not set the next available ID will be fetched from ProxmoxAPI.
    type: int
  node:
    description:
      - Proxmox VE node on which to operate.
      - Only required for O(state=present).
      - For every other states it will be autodiscovered.
    type: str
  pool:
    description:
      - Add the new VM to the specified pool.
    type: str
'''
