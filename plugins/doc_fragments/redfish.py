# -*- coding: utf-8 -*-

# Copyright (c) 2025 Ansible community
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):

    # Use together with the community.general.redfish module utils' REDFISH_COMMON_ARGUMENT_SPEC
    DOCUMENTATION = r"""
options:
  validate_certs:
    description:
      - If V(false), TLS/SSL certificates are not validated.
      - Set this to V(true) to enable certificate checking. Should be used together with O(ca_path).
    type: bool
    default: false
  ca_path:
    description:
      - PEM formatted file that contains a CA certificate to be used for validation.
      - Only used if O(validate_certs=true).
    type: path
  ciphers:
    required: false
    description:
      - TLS/SSL Ciphers to use for the request.
      - When a list is provided, all ciphers are joined in order with V(:).
      - See the L(OpenSSL Cipher List Format,https://www.openssl.org/docs/manmaster/man1/openssl-ciphers.html#CIPHER-LIST-FORMAT)
        for more details.
      - The available ciphers is dependent on the Python and OpenSSL/LibreSSL versions.
    type: list
    elements: str
"""
