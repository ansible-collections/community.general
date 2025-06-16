# -*- coding: utf-8 -*-

# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):

    # Standard documentation fragment
    DOCUMENTATION = r"""
options: {}
attributes:
  check_mode:
    description: Can run in C(check_mode) and return changed status prediction without modifying target.
  diff_mode:
    description: Will return details on what has changed (or possibly needs changing in C(check_mode)), when in diff mode.
"""

    PLATFORM = r"""
options: {}
attributes:
  platform:
    description: Target OS/families that can be operated against.
    support: N/A
"""

    # Should be used together with the standard fragment
    INFO_MODULE = r'''
options: {}
attributes:
  check_mode:
    support: full
    details:
      - This action does not modify state.
  diff_mode:
    support: N/A
    details:
      - This action does not modify state.
'''

    CONN = r"""
options: {}
attributes:
  become:
    description: Is usable alongside C(become) keywords.
  connection:
    description: Uses the target's configured connection information to execute code on it.
  delegation:
    description: Can be used in conjunction with C(delegate_to) and related keywords.
"""

    FACTS = r"""
options: {}
attributes:
  facts:
    description: Action returns an C(ansible_facts) dictionary that will update existing host facts.
"""

    # Should be used together with the standard fragment and the FACTS fragment
    FACTS_MODULE = r'''
options: {}
attributes:
  check_mode:
    support: full
    details:
      - This action does not modify state.
  diff_mode:
    support: N/A
    details:
      - This action does not modify state.
  facts:
    support: full
'''

    FILES = r"""
options: {}
attributes:
  safe_file_operations:
    description: Uses Ansible's strict file operation functions to ensure proper permissions and avoid data corruption.
"""

    FLOW = r"""
options: {}
attributes:
  action:
    description: Indicates this has a corresponding action plugin so some parts of the options can be executed on the controller.
  async:
    description: Supports being used with the C(async) keyword.
"""
