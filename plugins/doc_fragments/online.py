# -*- coding: utf-8 -*-
# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):

    # Standard documentation fragment
    DOCUMENTATION = r'''
options:
  api_token:
    description:
      - Online OAuth token.
    type: str
    required: true
    aliases: [ oauth_token ]
  api_url:
    description:
      - Online API URL
    type: str
    default: 'https://api.online.net'
    aliases: [ base_url ]
  api_timeout:
    description:
      - HTTP timeout to Online API in seconds.
    type: int
    default: 30
    aliases: [ timeout ]
  validate_certs:
    description:
      - Validate SSL certs of the Online API.
    type: bool
    default: true
notes:
  - Also see the API documentation on U(https://console.online.net/en/api/)
  - If C(api_token) is not set within the module, the following
    environment variables can be used in decreasing order of precedence
    C(ONLINE_TOKEN), C(ONLINE_API_KEY), C(ONLINE_OAUTH_TOKEN), C(ONLINE_API_TOKEN)
  - If one wants to use a different C(api_url) one can also set the C(ONLINE_API_URL)
    environment variable.
'''
