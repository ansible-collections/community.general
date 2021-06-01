# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Erinn Looney-Triggs
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):
    # Common parameters for GitHub
    DOCUMENTATION = '''
description:
- Authentication can be done with a I(token).
options:
  token:
    description:
    - Access Token used for authentication to GitHub.
    type: str
    required: true
'''
