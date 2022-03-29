# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

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
      - You can use C(PROXMOX_PASSWORD) environment variable.
    type: str
  api_token_id:
    description:
      - Specify the token ID.
    type: str
    version_added: 1.3.0
  api_token_secret:
    description:
      - Specify the token secret.
    type: str
    version_added: 1.3.0
  validate_certs:
    description:
      - If C(no), SSL certificates will not be validated.
      - This should only be used on personally controlled sites using self-signed certificates.
    type: bool
    default: no
requirements: [ "proxmoxer", "requests" ]
'''
