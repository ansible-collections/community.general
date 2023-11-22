# -*- coding: utf-8 -*-
# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):

    # Standard files documentation fragment
    DOCUMENTATION = r'''
options:
  api_url:
    description:
      - The resolvable endpoint for the API.
    type: str
  api_username:
    description:
      - The username to use for authentication against the API.
    type: str
  api_password:
    description:
      - The password to use for authentication against the API.
    type: str
  validate_certs:
    description:
      - Whether or not to validate SSL certs when supplying a HTTPS endpoint.
    type: bool
    default: true
'''
