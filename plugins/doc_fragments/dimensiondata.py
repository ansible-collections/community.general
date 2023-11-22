# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Dimension Data
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

# Authors:
#   - Adam Friedman  <tintoy@tintoy.io>


class ModuleDocFragment(object):

    # Dimension Data doc fragment
    DOCUMENTATION = r'''

options:
  region:
    description:
      - The target region.
      - Regions are defined in Apache libcloud project [libcloud/common/dimensiondata.py].
      - They are also listed in U(https://libcloud.readthedocs.io/en/latest/compute/drivers/dimensiondata.html).
      - Note that the default value C(na) stands for "North America".
      - The module prepends C(dd-) to the region choice.
    type: str
    default: na
  mcp_user:
    description:
      - The username used to authenticate to the CloudControl API.
      - If not specified, will fall back to E(MCP_USER) from environment variable or C(~/.dimensiondata).
    type: str
  mcp_password:
    description:
      - The password used to authenticate to the CloudControl API.
      - If not specified, will fall back to E(MCP_PASSWORD) from environment variable or C(~/.dimensiondata).
      - Required if O(mcp_user) is specified.
    type: str
  location:
    description:
      - The target datacenter.
    type: str
    required: true
  validate_certs:
    description:
      - If V(false), SSL certificates will not be validated.
      - This should only be used on private instances of the CloudControl API that use self-signed certificates.
    type: bool
    default: true
'''
