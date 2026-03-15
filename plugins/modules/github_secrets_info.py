#!/usr/bin/python

# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: github_secrets_info
short_description: List GitHub repository or organization secrets
description:
  - List secrets in a GitHub repository or organization.
author:
  - Thomas Sjögren (@konstruktoid)
version_added: '12.5.0'
extends_documentation_fragment:
  - community.general.attributes
  - community.general.attributes.info_module
options:
  organization:
    description:
      - The GitHub username or organization name.
    type: str
    required: true
    aliases: ["org", "username"]
  repository:
    description:
      - The name of the repository.
      - If not provided, the listing will be at organization level.
    type: str
    aliases: ["repo"]
  api_url:
    description:
      - The base URL for the GitHub API.
    type: str
    default: "https://api.github.com"
  token:
    description:
      - The GitHub token used for authentication.
    type: str
    required: true
"""

EXAMPLES = r"""
- name: List Github secret
  community.general.github_secrets_info:
    token: "{{ lookup('ansible.builtin.env', 'GITHUB_TOKEN') }}"
    repository: "ansible"
    organization: "ansible"
"""

RETURN = r"""
secrets:
  description: The list of currently existing secrets.
  type: list
  elements: dict
  returned: success
  sample: [
    {
      "created_at": "2026-01-11T23:19:00Z",
      "name": "ANSIBLE",
      "updated_at": "2026-02-15T22:18:16Z"
    },
  ]
  contains:
    name:
      description: The name of the secret.
      type: str
    created_at:
      description: The date and time when the secret was created.
      type: str
    updated_at:
      description: The date and time when the secret was last updated.
      type: str
"""

import json
import typing as t
from http import HTTPStatus

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url

from ansible_collections.community.general.plugins.module_utils import deps


def list_secrets(
    module: AnsibleModule,
    api_url: str,
    headers: dict[str, str],
    organization: str,
    repository: str,
) -> dict[str, list]:
    url = (
        f"{api_url}/repos/{organization}/{repository}/actions/secrets"
        if repository
        else f"{api_url}/orgs/{organization}/actions/secrets"
    )

    resp, info = fetch_url(module, url, headers=headers, method="GET")

    if info["status"] == HTTPStatus.OK:
        body = resp.read()
        return {"secrets": json.loads(body).get("secrets", [])}
    elif info["status"] == HTTPStatus.NOT_FOUND:
        return {
            "secrets": [],
        }
    else:
        module.fail_json(msg=f"Failed to list secrets: {info}")


def main() -> None:
    """Ansible module entry point."""
    argument_spec = {
        "organization": {
            "type": "str",
            "aliases": ["org", "username"],
            "required": True,
        },
        "repository": {"type": "str", "aliases": ["repo"]},
        "api_url": {"type": "str", "default": "https://api.github.com"},
        "token": {"type": "str", "required": True, "no_log": True},
    }

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    deps.validate(module)

    organization: str = module.params["organization"]
    repository: str = module.params["repository"]
    api_url: str = module.params["api_url"]
    token: str = module.params["token"]

    result: dict[str, t.Any] = {}

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    secrets = list_secrets(module, api_url, headers, organization, repository)

    result["changed"] = False
    result.update(
        secrets=secrets["secrets"],
    )

    module.exit_json(**result)


if __name__ == "__main__":
    main()
