
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


class ModuleDocFragment(object):
    DOCUMENTATION = r"""
options:
  auth_token:
    description:
      - Authenticating API token provided by 1&1. Overrides the E(ONEANDONE_AUTH_TOKEN) environment variable.
    type: str
    required: true
  api_url:
    description:
      - Custom API URL. Overrides the E(ONEANDONE_API_URL) environment variable.
    type: str
"""
