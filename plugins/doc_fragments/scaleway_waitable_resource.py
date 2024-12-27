# -*- coding: utf-8 -*-

# Copyright (c) 2022, Guillaume MARTINEZ <lunik@tiwabbit.fr>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):

    # Standard documentation fragment
    DOCUMENTATION = r"""
options:
  wait:
    description:
      - Wait for the resource to reach its desired state before returning.
    type: bool
    default: true
  wait_timeout:
    type: int
    description:
      - Time to wait for the resource to reach the expected state.
    required: false
    default: 300
  wait_sleep_time:
    type: int
    description:
      - Time to wait before every attempt to check the state of the resource.
    required: false
    default: 3
"""
