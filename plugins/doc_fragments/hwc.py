# Copyright (c) 2018, Huawei Inc.
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


class ModuleDocFragment:
    # HWC doc fragment.
    DOCUMENTATION = r"""
options:
  identity_endpoint:
    description:
      - The Identity authentication URL.
    type: str
    required: true
  user:
    description:
      - The user name to login with.
      - Currently only user names are supported, and not user IDs.
    type: str
    required: true
  password:
    description:
      - The password to login with.
    type: str
    required: true
  domain:
    description:
      - The name of the Domain to scope to (Identity v3).
      - Currently only domain names are supported, and not domain IDs.
    type: str
    required: true
  project:
    description:
      - The name of the Tenant (Identity v2) or Project (Identity v3).
      - Currently only project names are supported, and not project IDs.
    type: str
    required: true
  region:
    description:
      - The region to which the project belongs.
    type: str
  id:
    description:
      - The ID of resource to be managed.
    type: str
notes:
  - For authentication, you can set identity_endpoint using the E(ANSIBLE_HWC_IDENTITY_ENDPOINT) environment variable.
  - For authentication, you can set user using the E(ANSIBLE_HWC_USER) environment variable.
  - For authentication, you can set password using the E(ANSIBLE_HWC_PASSWORD) environment variable.
  - For authentication, you can set domain using the E(ANSIBLE_HWC_DOMAIN) environment variable.
  - For authentication, you can set project using the E(ANSIBLE_HWC_PROJECT) environment variable.
  - For authentication, you can set region using the E(ANSIBLE_HWC_REGION) environment variable.
  - Environment variables values are only used when the playbook values are not set.
"""
