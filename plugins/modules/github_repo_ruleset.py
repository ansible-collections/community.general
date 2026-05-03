#!/usr/bin/python

# Copyright (c) 2025, John Westcott IV (@john-westcott-iv)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: github_repo_ruleset
short_description: Manage repository rulesets on Github
version_added: NEXT_PATCH
description:
  - Create, update, and delete repository rulesets on Github.
  - Rulesets are the modern alternative to branch protection rules, offering more flexibility and granularity.
  - Uses the GitHub REST API directly via C(fetch_url) since PyGithub does not support rulesets.
  - Authentication can be done with O(access_token) or with O(username) and O(password).
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  username:
    description:
      - Username used for authentication.
      - This is only needed when not using O(access_token).
    type: str
  password:
    description:
      - Password used for authentication.
      - This is only needed when not using O(access_token).
    type: str
  access_token:
    description:
      - Token parameter for authentication.
      - This is only needed when not using O(username) and O(password).
    type: str
  api_url:
    description:
      - URL to the GitHub API if not using github.com but your own instance.
    type: str
    default: 'https://api.github.com'
  organization:
    description:
      - Repository owner (user or organization).
    type: str
    required: true
  repo:
    description:
      - Repository name.
    type: str
    required: true
  name:
    description:
      - Ruleset name.
      - Used for matching existing rulesets for idempotency.
      - B(Note) that GitHub allows duplicate ruleset names. If multiple rulesets share the same name, this module will fail
        with an error. Ensure ruleset names are unique.
    type: str
    required: true
  state:
    description:
      - Whether the ruleset should exist or not.
    type: str
    default: present
    choices: [absent, present]
  target:
    description:
      - The target of the ruleset.
    type: str
    default: branch
    choices: [branch, tag]
  enforcement:
    description:
      - The enforcement level of the ruleset.
      - V(active) means rules are enforced.
      - V(evaluate) means rules are not enforced but violations are reported.
      - V(disabled) means rules are not enforced or reported.
    type: str
    default: active
    choices: [active, evaluate, disabled]
  conditions:
    description:
      - Conditions for ref names that the ruleset applies to.
    type: dict
    suboptions:
      ref_name:
        description:
          - Ref name conditions.
        type: dict
        required: true
        suboptions:
          include:
            description:
              - List of ref name patterns to include.
              - Use V(~DEFAULT_BRANCH) for the default branch, V(~ALL) for all branches/tags.
            type: list
            elements: str
            default: []
          exclude:
            description:
              - List of ref name patterns to exclude.
            type: list
            elements: str
            default: []
  bypass_actors:
    description:
      - List of actors that can bypass the ruleset.
    type: list
    elements: dict
    default: []
    suboptions:
      actor_id:
        description:
          - The ID of the actor. For repository roles, use 1=Read, 2=Triage, 3=Write, 4=Maintain, 5=Admin.
        type: int
        required: true
      actor_type:
        description:
          - The type of actor.
        type: str
        required: true
        choices: [RepositoryRole, Team, Integration, OrganizationAdmin]
      bypass_mode:
        description:
          - When the actor can bypass the ruleset.
        type: str
        default: always
        choices: [always, pull_request]
  rules:
    description:
      - List of rules to enforce.
      - Each rule is a dictionary matching the GitHub API schema with a C(type) field and optional C(parameters).
      - "Rule types include: V(creation), V(update), V(deletion), V(required_linear_history), V(required_signatures),
        V(pull_request), V(required_status_checks), V(non_fast_forward), V(required_deployments), V(commit_message_pattern),
        V(commit_author_email_pattern), V(committer_email_pattern), V(branch_name_pattern), V(tag_name_pattern), and more."
    type: list
    elements: dict
    default: []
requirements: []
notes:
  - This module uses C(fetch_url) instead of PyGithub because PyGithub does not support the rulesets API.
author:
  - John Westcott IV (@john-westcott-iv)
"""

EXAMPLES = r"""
- name: Create a basic branch ruleset
  community.general.github_repo_ruleset:
    access_token: mytoken
    organization: MyOrganization
    repo: myrepo
    name: main-protection
    target: branch
    enforcement: active
    conditions:
      ref_name:
        include:
          - "~DEFAULT_BRANCH"
        exclude: []
    rules:
      - type: pull_request
        parameters:
          required_approving_review_count: 2
          dismiss_stale_reviews_on_push: true
          require_code_owner_review: true
      - type: required_status_checks
        parameters:
          required_status_checks:
            - context: ci/build
            - context: ci/test
          strict_required_status_checks_policy: true
      - type: required_linear_history
    state: present

- name: Create a ruleset with bypass actors
  community.general.github_repo_ruleset:
    access_token: mytoken
    organization: MyOrganization
    repo: myrepo
    name: release-protection
    enforcement: active
    conditions:
      ref_name:
        include:
          - "refs/heads/release-*"
        exclude: []
    bypass_actors:
      - actor_id: 5
        actor_type: RepositoryRole
        bypass_mode: always
    rules:
      - type: deletion
      - type: non_fast_forward
      - type: required_signatures
    state: present

- name: Delete a ruleset
  community.general.github_repo_ruleset:
    access_token: mytoken
    organization: MyOrganization
    repo: myrepo
    name: main-protection
    state: absent
"""

RETURN = r"""
ruleset:
  description: Ruleset information as returned by the GitHub API.
  returned: success and O(state=present)
  type: dict
"""

import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url


def github_request(module, url, method="GET", data=None):
    """Make a request to the GitHub API."""
    headers = {"Accept": "application/json"}

    if module.params.get("access_token"):
        headers["Authorization"] = f"Bearer {module.params['access_token']}"
    elif module.params.get("username"):
        module.params["url_username"] = module.params["username"]
        module.params["url_password"] = module.params["password"]
        module.params["force_basic_auth"] = True

    if data is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(data)

    resp, info = fetch_url(module, url, data=data, headers=headers, method=method, timeout=30)

    status = info["status"]
    body = None
    if resp:
        body = json.loads(resp.read())

    return status, body, info


def find_ruleset_by_name(module, base_url, name):
    """Find a ruleset by name. Returns (ruleset_id, ruleset_data) or (None, None)."""
    url = f"{base_url}"
    status, body, info = github_request(module, url, method="GET")

    if status != 200:
        module.fail_json(msg=f"Failed to list rulesets: {info.get('msg', 'Unknown error')}", http_status_code=status)

    matches = [r for r in body if r["name"] == name]
    if len(matches) > 1:
        module.fail_json(msg=f"Multiple rulesets found with name '{name}'. Ensure ruleset names are unique.")
    if len(matches) == 1:
        # Fetch full details
        ruleset_id = matches[0]["id"]
        detail_url = f"{base_url}/{ruleset_id}"
        status, detail, info = github_request(module, detail_url, method="GET")
        if status != 200:
            module.fail_json(
                msg=f"Failed to get ruleset details: {info.get('msg', 'Unknown error')}", http_status_code=status
            )
        return ruleset_id, detail

    return None, None


def build_ruleset_body(params):
    """Build the API request body from module params."""
    body = {
        "name": params["name"],
        "target": params["target"],
        "enforcement": params["enforcement"],
    }

    if params["conditions"] is not None:
        body["conditions"] = params["conditions"]
    else:
        body["conditions"] = {"ref_name": {"include": ["~ALL"], "exclude": []}}

    body["bypass_actors"] = params["bypass_actors"] or []
    body["rules"] = params["rules"] or []

    return body


def normalize_for_comparison(data):
    """Normalize ruleset data for comparison by extracting the relevant fields."""
    return {
        "name": data.get("name"),
        "target": data.get("target"),
        "enforcement": data.get("enforcement"),
        "conditions": data.get("conditions"),
        "bypass_actors": sorted(
            data.get("bypass_actors", []), key=lambda x: (x.get("actor_type", ""), x.get("actor_id", 0))
        ),
        "rules": sorted(data.get("rules", []), key=lambda x: x.get("type", "")),
    }


def run_module(module):
    params = module.params
    api_url = params["api_url"].rstrip("/")
    base_url = f"{api_url}/repos/{params['organization']}/{params['repo']}/rulesets"

    state = params["state"]
    name = params["name"]
    check_mode = module.check_mode

    result = dict(changed=False)

    ruleset_id, existing = find_ruleset_by_name(module, base_url, name)

    if state == "absent":
        if ruleset_id is not None:
            if not check_mode:
                status, _, info = github_request(module, f"{base_url}/{ruleset_id}", method="DELETE")
                if status not in (200, 204):
                    module.fail_json(
                        msg=f"Failed to delete ruleset: {info.get('msg', 'Unknown error')}", http_status_code=status
                    )
            result["changed"] = True
        return result

    # state == present
    desired_body = build_ruleset_body(params)

    if existing is not None:
        desired_normalized = normalize_for_comparison(desired_body)
        existing_normalized = normalize_for_comparison(existing)

        if desired_normalized == existing_normalized:
            result["ruleset"] = existing
            return result

        if not check_mode:
            status, body, info = github_request(module, f"{base_url}/{ruleset_id}", method="PUT", data=desired_body)
            if status != 200:
                module.fail_json(
                    msg=f"Failed to update ruleset: {info.get('msg', 'Unknown error')}", http_status_code=status
                )
            result["ruleset"] = body
        else:
            result["ruleset"] = desired_body
        result["changed"] = True
    else:
        if not check_mode:
            status, body, info = github_request(module, base_url, method="POST", data=desired_body)
            if status not in (200, 201):
                module.fail_json(
                    msg=f"Failed to create ruleset: {info.get('msg', 'Unknown error')}", http_status_code=status
                )
            result["ruleset"] = body
        else:
            result["ruleset"] = desired_body
        result["changed"] = True

    return result


def main():
    module_args = dict(
        username=dict(type="str"),
        password=dict(type="str", no_log=True),
        access_token=dict(type="str", no_log=True),
        api_url=dict(type="str", default="https://api.github.com"),
        organization=dict(type="str", required=True),
        repo=dict(type="str", required=True),
        name=dict(type="str", required=True),
        state=dict(type="str", default="present", choices=["present", "absent"]),
        target=dict(type="str", default="branch", choices=["branch", "tag"]),
        enforcement=dict(type="str", default="active", choices=["active", "evaluate", "disabled"]),
        conditions=dict(
            type="dict",
            options=dict(
                ref_name=dict(
                    type="dict",
                    required=True,
                    options=dict(
                        include=dict(type="list", elements="str", default=[]),
                        exclude=dict(type="list", elements="str", default=[]),
                    ),
                ),
            ),
        ),
        bypass_actors=dict(
            type="list",
            elements="dict",
            default=[],
            options=dict(
                actor_id=dict(type="int", required=True),
                actor_type=dict(
                    type="str", required=True, choices=["RepositoryRole", "Team", "Integration", "OrganizationAdmin"]
                ),
                bypass_mode=dict(type="str", default="always", choices=["always", "pull_request"]),
            ),
        ),
        rules=dict(type="list", elements="dict", default=[]),
    )
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_together=[("username", "password")],
        required_one_of=[("username", "access_token")],
        mutually_exclusive=[("username", "access_token")],
    )

    try:
        result = run_module(module)
        module.exit_json(**result)
    except Exception as e:
        module.fail_json(msg=f"Unexpected error. {e}")


if __name__ == "__main__":
    main()
