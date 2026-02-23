#!/usr/bin/python

# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

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
    details: The module needs to interact with the GitHub API, which does not support check mode.
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
      - If not provided, the secret will be managed at the organization level.
    type: str
    aliases: ["repo"]
  key:
    description:
      - The name of the secret.
    type: str
  value:
    description:
      - The value of the secret. Required when O(state=present).
    type: str
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

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url

from ansible_collections.community.general.plugins.module_utils import deps

with deps.declare(
    "pynacl",
    reason="pynacl is a required dependency",
    url="https://pypi.org/project/PyNaCl/",
):
    from nacl import encoding, public

ok_status_code = 200
missing_status_code = 404

created_response_code = 201
delete_response_code = 204


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

    if info["status"] != delete_response_code and info["status"] != missing_status_code:
        module.fail_json(msg=f"Failed to delete secret: {info}")

    return info


def main() -> None:
    """Ansible module entry point."""
    argument_spec = {
        "organization": {
            "type": "str",
            "aliases": ["org", "username"],
            "required": True,
        },
        "repository": {"type": "str", "aliases": ["repo"]},
        "key": {"type": "str", "no_log": False},
        "value": {"type": "str", "no_log": True},
        "visibility": {"type": "str", "choices": ["all", "private", "selected"]},
        "state": {
            "type": "str",
            "choices": ["present", "absent"],
            "default": "present",
        },
        "api_url": {"type": "str", "default": "https://api.github.com"},
        "token": {"type": "str", "required": True, "no_log": True},
    }

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=[("state", "present", ["value"])],
        required_by={"value": "key"},
        supports_check_mode=False,
    )

    deps.validate(module)

    organization: str = module.params["organization"]
    repository: str = module.params["repository"]
    key: str = module.params["key"]
    value: str = module.params["value"]
    visibility: str = module.params.get("visibility")
    state: str = module.params["state"]
    api_url: str = module.params["api_url"]
    token: str = module.params["token"]

    if value is not None and not key:
        module.fail_json(
            msg="Invalid parameters",
            details="When 'value' is provided, 'key' must also be set",
            params=module.params,
        )

    if state == "present" and value is None:
        module.fail_json(
            msg="Invalid parameters",
            details="When 'state' is 'present', 'value' must be provided",
            params=module.params,
        )

    if state == "present" and not repository and not visibility:
        module.fail_json(
            msg="Invalid parameters",
            details=("When 'state' is 'present' and 'repository' is not set, 'visibility' must be provided"),
            params=module.params,
        )

    result: dict[str, Any] = {}

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    if state == "present":
        key_id, public_key = get_public_key(
            module,
            api_url,
            headers,
            organization,
            repository,
        )

        encrypted_value = encrypt_secret(public_key, value)

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

        response_msg = "Secret created" if upsert["status"] == created_response_code else "Secret updated"

        result["changed"] = True
        result.update(
            result={
                "status": upsert["status"],
                "msg": upsert.get("msg"),
                "response": response_msg,
            },
        )

    if state == "absent":
        delete = delete_secret(
            module,
            api_url,
            headers,
            organization,
            repository,
            key,
        )

        if delete["status"] == delete_response_code:
            result["changed"] = True
            result.update(
                result={
                    "status": delete["status"],
                    "msg": delete.get("msg"),
                    "response": "Secret deleted",
                },
            )

        if delete["status"] == missing_status_code:
            result["changed"] = False
            result.update(
                result={
                    "status": delete["status"],
                    "msg": delete.get("msg"),
                    "response": "Secret not found",
                },
            )

    module.exit_json(**result)


if __name__ == "__main__":
    main()
