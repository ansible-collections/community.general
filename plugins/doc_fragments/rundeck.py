# Copyright (c) 2021, Phillipe Smith <phsmithcc@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


class ModuleDocFragment:
    # Standard files documentation fragment
    DOCUMENTATION = r"""
options:
  url:
    type: str
    description:
      - Rundeck instance URL.
    required: true
  api_version:
    type: int
    description:
      - Rundeck API version to be used.
      - API version must be at least 14.
    default: 39
  api_token:
    type: str
    description:
      - Rundeck User API Token.
    required: true
"""
