# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Ansible Project
# Copyright: (c) 2020, Alexei Znamensky (russoz@gmail.com)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):
    # Extra parameters when using ModuleHelper classes
    DOCUMENTATION = r'''
options:
  ack_named_deprecations:
    description:
    - Acknowledge deprecations by name.
    - Deprecations listed here will not be triggered.
    type: list
    elements: str
'''
