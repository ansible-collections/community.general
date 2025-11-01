# Copyright (c) 2018, Yanis Guenane <yanis+ansible@guenane.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


class ModuleDocFragment:
    # Standard documentation fragment
    DOCUMENTATION = r"""
options:
  api_token:
    description:
      - Scaleway OAuth token.
    type: str
    required: true
    aliases: [oauth_token]
  api_url:
    description:
      - Scaleway API URL.
    type: str
    default: https://api.scaleway.com
    aliases: [base_url]
  api_timeout:
    description:
      - HTTP timeout to Scaleway API in seconds.
    type: int
    default: 30
    aliases: [timeout]
  query_parameters:
    description:
      - List of parameters passed to the query string.
    type: dict
    default: {}
  validate_certs:
    description:
      - Validate SSL certs of the Scaleway API.
    type: bool
    default: true
notes:
  - Also see the API documentation on U(https://developer.scaleway.com/).
  - If O(api_token) is not set within the module, the following environment variables can be used in decreasing order of precedence
    E(SCW_TOKEN), E(SCW_API_KEY), E(SCW_OAUTH_TOKEN) or E(SCW_API_TOKEN).
  - If one wants to use a different O(api_url) one can also set the E(SCW_API_URL) environment variable.
"""

    ACTIONGROUP_SCALEWAY = r"""
options: {}
attributes:
  action_group:
    description: Use C(group/community.general.scaleway) in C(module_defaults) to set defaults for this module.
    support: full
    membership:
      - community.general.scaleway
"""
