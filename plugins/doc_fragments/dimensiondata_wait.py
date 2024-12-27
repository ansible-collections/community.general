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

    # Dimension Data ("wait-for-completion" parameters) doc fragment
    DOCUMENTATION = r"""
options:
  wait:
    description:
      - Should we wait for the task to complete before moving onto the next.
    type: bool
    default: false
  wait_time:
    description:
      - The maximum amount of time (in seconds) to wait for the task to complete.
      - Only applicable if O(wait=true).
    type: int
    default: 600
  wait_poll_interval:
    description:
      - The amount of time (in seconds) to wait between checks for task completion.
      - Only applicable if O(wait=true).
    type: int
    default: 2
"""
