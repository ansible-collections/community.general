# -*- coding: utf-8 -*-

# Copyright (c) 2025, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = r"""
options:
  subscription_user:
    description:
      - The ProfitBricks username. Overrides the E(PB_SUBSCRIPTION_ID) environment variable.
    type: str
    required: true
  subscription_password:
    description:
      - The ProfitBricks password. Overrides the E(PB_PASSWORD) environment variable.
    type: str
    required: true
  wait:
    description:
      - Wait for the operation to complete before returning.
    default: true
    type: bool
  wait_timeout:
    description:
      - How long before wait gives up, in seconds.
    type: int
    default: 600

requirements:
  - "profitbricks"
"""

    ACTIONGROUP_PROFITBRICKS = r"""
options: {}
attributes:
  action_group:
    description: Use C(group/community.general.profitbricks) in C(module_defaults) to set defaults for this module.
    support: full
    membership:
      - community.general.profitbricks
"""
