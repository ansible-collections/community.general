# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


class ModuleDocFragment:
    # Standard files documentation fragment
    DOCUMENTATION = r"""
requirements:
  - requests (Python library U(https://pypi.org/project/requests/))

options:
  api_token:
    description:
      - GitLab access token with API permissions.
    type: str
  api_oauth_token:
    description:
      - GitLab OAuth token for logging in.
    type: str
    version_added: 4.2.0
  api_job_token:
    description:
      - GitLab CI job token for logging in.
    type: str
    version_added: 4.2.0
  ca_path:
    description:
      - The CA certificates bundle to use to verify GitLab server certificate.
    type: str
    version_added: 8.1.0
"""
