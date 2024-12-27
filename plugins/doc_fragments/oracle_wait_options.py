# -*- coding: utf-8 -*-
# Copyright (c) 2018, Oracle and/or its affiliates.
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = r"""
options:
  wait:
    description: Whether to wait for create or delete operation to complete.
    default: true
    type: bool
  wait_timeout:
    description: Time, in seconds, to wait when O(wait=true).
    default: 1200
    type: int
  wait_until:
    description: The lifecycle state to wait for the resource to transition into when O(wait=true). By default, when O(wait=true),
      we wait for the resource to get into ACTIVE/ATTACHED/AVAILABLE/PROVISIONED/ RUNNING applicable lifecycle state during
      create operation and to get into DELETED/DETACHED/ TERMINATED lifecycle state during delete operation.
    type: str
"""
