# -*- coding: utf-8 -*-

# Copyright (c) 2019, Evgeniy Krysanov <evgeniy.krysanov@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):

    # Standard documentation fragment
    DOCUMENTATION = r"""
options:
  client_id:
    description:
      - The OAuth consumer key.
      - If not set the environment variable E(BITBUCKET_CLIENT_ID) will be used.
    type: str
  client_secret:
    description:
      - The OAuth consumer secret.
      - If not set the environment variable E(BITBUCKET_CLIENT_SECRET) will be used.
    type: str
  user:
    description:
      - The username.
      - If not set the environment variable E(BITBUCKET_USERNAME) will be used.
      - O(ignore:username) is an alias of O(user) since community.general 6.0.0. It was an alias of O(workspace) before.
    type: str
    version_added: 4.0.0
    aliases: [username]
  password:
    description:
      - The App password.
      - If not set the environment variable E(BITBUCKET_PASSWORD) will be used.
    type: str
    version_added: 4.0.0
notes:
  - Bitbucket OAuth consumer key and secret can be obtained from Bitbucket profile -> Settings -> Access Management -> OAuth.
  - Bitbucket App password can be created from Bitbucket profile -> Personal Settings -> App passwords.
  - If both OAuth and Basic Auth credentials are passed, OAuth credentials take precedence.
"""
