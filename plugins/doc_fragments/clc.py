# -*- coding: utf-8 -*-

# Copyright (c) 2024, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):

    # Standard documentation fragment
    DOCUMENTATION = r"""
options: {}
requirements:
  - requests >= 2.5.0
  - clc-sdk
notes:
  - To use this module, it is required to set the below environment variables which enables access to the Centurylink Cloud.
  - E(CLC_V2_API_USERNAME), the account login ID for the Centurylink Cloud.
  - E(CLC_V2_API_PASSWORD), the account password for the Centurylink Cloud.
  - Alternatively, the module accepts the API token and account alias. The API token can be generated using the CLC account
    login and password using the HTTP API call @ U(https://api.ctl.io/v2/authentication/login).
  - E(CLC_V2_API_TOKEN), the API token generated from U(https://api.ctl.io/v2/authentication/login).
  - E(CLC_ACCT_ALIAS), the account alias associated with the Centurylink Cloud.
  - Users can set E(CLC_V2_API_URL) to specify an endpoint for pointing to a different CLC environment.
"""
