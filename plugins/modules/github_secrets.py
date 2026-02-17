#!/usr/bin/python

# Copyright (c) 2026, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""An Ansible module to manage GitHub repository or organization serets."""

# ruff: noqa: E402,EXE001,PLR0913,RUF059

from __future__ import annotations

DOCUMENTATION = r"""
module: github_secrets
short_description: Manage GitHub repository or organization secrets
description:
  - Create, update, or delete secrets in a GitHub repository or organization.
author:
  - Thomas Sjögren (@konstruktoid)
version_added: '12.4.0'
requirements:
  - pynacl
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
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
    required: false
    type: str
    aliases: ["repo"]
  key:
    description:
      - The name of the secret.
    type: str
    required: false
  value:
    description:
      - The value of the secret. Required when O(state=present).
    type: str
    required: false
  visibility:
    description:
      - The visibility of the secret when set at the organization level.
      - Required when O(state=present) and O(repository) is not set.
    type: str
    choices: ["all", "private", "selected"]
  state:
    description:
      - The desired state of the secret.
    type: str
    choices: ["present", "absent"]
    default: "present"
  list_only:
    description:
      - If C(true), the module will only list available secrets.
    type: bool
    default: false
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
- name: Add Github secret
  github_secrets:
    token: "{{ lookup('env', 'GITHUB_TOKEN') }}"
    repository: "ansible"
    organization: "ansible"
    key: "TEST_SECRET"
    value: "bob"
    state: "present"

- name: List Github secrets
  github_secrets:
    token: "{{ lookup('env', 'GITHUB_TOKEN') }}"
    repository: "ansible"
    organization: "ansible"
    list_only: true

- name: Delete Github secret
  github_secrets:
    token: "{{ lookup('env', 'GITHUB_TOKEN') }}"
    repository: "ansible"
    organization: "ansible"
    key: "TEST_SECRET"
    state: "absent"
"""

RETURN = r"""
result:
  description: The result of the module.
  type: dict
  returned: always
  sample: {
    "changed": true,
    "failed": false,
    "result": {
      "msg": "OK (2 bytes)",
      "response": "Secret created",
      "status": 201
    }
  }
"""

import json
from typing import Any

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.urls import fetch_url

try:
    from nacl import encoding, public

    HAS_PYNACL = True
except ImportError:
    HAS_PYNACL = False


def get_public_key(
    module: AnsibleModule,
    api_url: str,
    headers: dict[str, str],
    organization: str,
    repository: str,
) -> tuple[str, str]:
    """Retrieve the GitHub Actions public key used to encrypt secrets."""
    if repository:
        url = f"{api_url}/repos/{organization}/{repository}/actions/secrets/public-key"
    else:
        url = f"{api_url}/orgs/{organization}/actions/secrets/public-key"

    response, info = fetch_url(module, url, headers=headers)

    ok_status_code = 200
    if info["status"] != ok_status_code:
        module.fail_json(msg=f"Failed to get public key: {info}")

    data = json.loads(response.read())
    return data["key_id"], data["key"]


def encrypt_secret(public_key: str, secret_value: str) -> str:
    """Encrypt a secret value using GitHub's public key."""
    key = public.PublicKey(
        public_key.encode("utf-8"),
        encoding.Base64Encoder(),  # type: ignore [arg-type]
    )
    sealed_box = public.SealedBox(key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return encoding.Base64Encoder.encode(encrypted).decode("utf-8")


def upsert_secret(
    module: AnsibleModule,
    api_url: str,
    headers: dict[str, str],
    organization: str,
    repository: str,
    key: str,
    encrypted_value: str,
    key_id: str,
) -> dict[str, Any]:
    """Create or update a GitHub Actions secret."""
    url = (
        f"{api_url}/repos/{organization}/{repository}/actions/secrets/{key}"
        if repository
        else f"{api_url}/orgs/{organization}/actions/secrets/{key}"
    )

    payload = {
        "encrypted_value": encrypted_value,
        "key_id": key_id,
    }

    if not repository and module.params.get("visibility"):
        payload["visibility"] = module.params["visibility"]

    resp, info = fetch_url(
        module,
        url,
        headers=headers,
        data=json.dumps(payload).encode("utf-8"),
        method="PUT",
    )

    if info["status"] not in (201, 204):
        module.fail_json(msg=f"Failed to upsert secret: {info}")

    return info


def delete_secret(
    module: AnsibleModule,
    api_url: str,
    headers: dict[str, str],
    organization: str,
    repository: str,
    key: str,
) -> dict[str, Any]:
    """Delete a GitHub Actions secret."""
    url = (
        f"{api_url}/repos/{organization}/{repository}/actions/secrets/{key}"
        if repository
        else f"{api_url}/orgs/{organization}/actions/secrets/{key}"
    )

    resp, info = fetch_url(
        module,
        url,
        headers=headers,
        method="DELETE",
    )

    delete_response_code = 204
    if info["status"] != delete_response_code:
        module.fail_json(msg=f"Failed to delete secret: {info}")

    return info


def list_secrets(
    module: AnsibleModule,
    api_url: str,
    headers: dict[str, str],
    organization: str,
    repository: str,
) -> dict[str, Any]:
    """List GitHub Actions secrets."""
    url = (
        f"{api_url}/repos/{organization}/{repository}/actions/secrets"
        if repository
        else f"{api_url}/orgs/{organization}/actions/secrets"
    )

    resp, info = fetch_url(
        module,
        url,
        headers=headers,
        method="GET",
    )

    list_response_code = 200
    if info["status"] != list_response_code:
        module.fail_json(msg=f"Failed to list secrets: {info}")

    body = resp.read()
    return {
        "response": resp,
        "data": json.loads(body),
        "info": info,
    }


def main() -> None:
    """Ansible module entry point."""
    argument_spec = {
        "organization": {
            "type": "str",
            "aliases": ["org", "username"],
            "required": True,
        },
        "repository": {"type": "str", "aliases": ["repo"], "required": False},
        "key": {"type": "str", "required": False, "no_log": False},
        "value": {"type": "str", "required": False, "no_log": True},
        "visibility": {
            "type": "str",
            "choices": ["all", "private", "selected"],
            "required": False,
        },
        "state": {
            "type": "str",
            "choices": ["present", "absent"],
            "default": "present",
        },
        "list_only": {"type": "bool", "default": False},
        "api_url": {"type": "str", "default": "https://api.github.com"},
        "token": {"type": "str", "required": True, "no_log": True},
    }

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False,
    )

    if not HAS_PYNACL:
        module.fail_json(msg=missing_required_lib("PyNaCl"))

    organization: str = module.params["organization"]
    repository: str = module.params["repository"]
    key: str = module.params["key"]
    value: str = module.params["value"]
    visibility: str = module.params.get("visibility")
    state: str = module.params["state"]
    list_only: bool = module.params["list_only"]
    api_url: str = module.params["api_url"]
    token: str = module.params["token"]

    if value not in (None, "") and not key:
        module.fail_json(
            msg="Invalid parameters",
            details="When 'value' is provided, 'key' must also be set",
            params=module.params,
        )

    if state == "present" and not value and not list_only:
        module.fail_json(
            msg="Invalid parameters",
            details="When state is 'present', 'value' must be provided",
            params=module.params,
        )

    if state == "present" and not repository and not visibility and not list_only:
        module.fail_json(
            msg="Invalid parameters",
            details=("When state is 'present' and 'repository' is not set, 'visibility' must be provided"),
            params=module.params,
        )

    result: dict[str, Any] = {}

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    if list_only:
        secrets = list_secrets(
            module,
            api_url,
            headers,
            organization,
            repository,
        )

        result["changed"] = False
        result.update(
            result={
                "status": secrets["info"]["status"],
                "msg": secrets["data"]["secrets"],
                "response": "Secrets listed",
            },
        )

    if state == "present" and not list_only:
        key_id, public_key = get_public_key(
            module,
            api_url,
            headers,
            organization,
            repository,
        )

        encrypted_value = encrypt_secret(public_key, value) if value else None

        upsert = upsert_secret(
            module,
            api_url,
            headers,
            organization,
            repository,
            key,
            encrypted_value,
            key_id,
        )

        response_created = 201
        response_msg = "Secret created" if upsert["status"] == response_created else "Secret updated"

        result["changed"] = True
        result.update(
            result={
                "status": upsert["status"],
                "msg": upsert.get("msg"),
                "response": response_msg,
            },
        )

    if state == "absent" and not list_only:
        delete = delete_secret(
            module,
            api_url,
            headers,
            organization,
            repository,
            key,
        )

        result["changed"] = True
        result.update(
            result={
                "status": delete["status"],
                "msg": delete.get("msg"),
                "response": "Secret deleted",
            },
        )

    module.exit_json(**result)


if __name__ == "__main__":
    main()
