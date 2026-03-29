#!/usr/bin/python

# Copyright (c) 2025, John Westcott IV (@john-westcott-iv)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: github_team_members
short_description: Manage team membership on Github organizations
version_added: NEXT_PATCH
description:
  - Manage the members of a team in a Github organization using the PyGithub library.
  - Supports adding, removing, and synchronizing team members with three state modes.
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
      - The GitHub organization that owns the team.
    type: str
    required: true
  team:
    description:
      - Team name or slug.
    type: str
    required: true
  members:
    description:
      - List of team members to manage.
      - Each entry can be a bare string (username with default role V(member)) or a dictionary with O(members[].username) and O(members[].role).
    type: list
    elements: raw
    required: true
  state:
    description:
      - How to manage the membership list.
      - V(present) ensures all listed members are on the team with the specified role. Does not remove unlisted members.
      - V(absent) ensures all listed members are NOT on the team. Removes them if present.
      - V(exact) makes the team membership exactly match the provided list.
        Members not in the list are removed, missing members are added, and roles are corrected.
    type: str
    default: present
    choices: [present, absent, exact]
requirements:
  - PyGithub>=1.54
notes:
  - For Python 3, PyGithub>=1.54 should be used.
  - Requires the authenticated user to have C(admin:org) scope on their token.
  - This module only works with organizations, not personal accounts.
author:
  - John Westcott IV (@john-westcott-iv)
"""

EXAMPLES = r"""
- name: Add members to a team
  community.general.github_team_members:
    access_token: mytoken
    organization: MyOrganization
    team: my-team
    members:
      - alice
      - bob
      - username: carol
        role: maintainer
    state: present

- name: Remove members from a team
  community.general.github_team_members:
    access_token: mytoken
    organization: MyOrganization
    team: my-team
    members:
      - alice
      - bob
    state: absent

- name: Set exact team membership
  community.general.github_team_members:
    access_token: mytoken
    organization: MyOrganization
    team: my-team
    members:
      - username: alice
        role: maintainer
      - bob
    state: exact
"""

RETURN = r"""
added:
  description: List of usernames that were added to the team.
  returned: success
  type: list
  elements: str
removed:
  description: List of usernames that were removed from the team.
  returned: success
  type: list
  elements: str
updated:
  description: List of usernames whose role was changed.
  returned: success
  type: list
  elements: str
members:
  description: Final list of team members with their roles.
  returned: success
  type: list
  elements: dict
  contains:
    username:
      description: The member's GitHub username.
      type: str
    role:
      description: The member's team role.
      type: str
"""

import traceback

from ansible.module_utils.basic import AnsibleModule, missing_required_lib

GITHUB_IMP_ERR = None
try:
    from github import Github, GithubException
    from github.GithubException import UnknownObjectException

    HAS_GITHUB_PACKAGE = True
except Exception:
    GITHUB_IMP_ERR = traceback.format_exc()
    HAS_GITHUB_PACKAGE = False


def authenticate(username=None, password=None, access_token=None, api_url=None):
    if access_token:
        return Github(base_url=api_url, login_or_token=access_token)
    else:
        return Github(base_url=api_url, login_or_token=username, password=password)


def normalize_member(entry):
    """Normalize a member entry to a dict with username and role."""
    if isinstance(entry, str):
        return {"username": entry, "role": "member"}
    return {"username": entry["username"], "role": entry.get("role", "member")}


def get_current_members(team):
    """Get current team members with their roles."""
    members = {}
    for member in team.get_members(role="member"):
        members[member.login] = "member"
    for member in team.get_members(role="maintainer"):
        members[member.login] = "maintainer"
    return members


def run_module(params, check_mode=False):
    gh = authenticate(
        username=params["username"],
        password=params["password"],
        access_token=params["access_token"],
        api_url=params["api_url"],
    )

    org = gh.get_organization(params["organization"])

    try:
        team = org.get_team_by_slug(params["team"])
    except UnknownObjectException as e:
        raise ValueError(f"Team '{params['team']}' not found in organization '{params['organization']}'") from e

    desired_members = [normalize_member(m) for m in params["members"]]
    desired_map = {m["username"]: m["role"] for m in desired_members}
    state = params["state"]

    current_members = get_current_members(team)

    added = []
    removed = []
    updated = []

    if state == "present":
        for username, role in desired_map.items():
            if username not in current_members:
                if not check_mode:
                    user = gh.get_user(username)
                    team.add_membership(user, role=role)
                added.append(username)
            elif current_members[username] != role:
                if not check_mode:
                    user = gh.get_user(username)
                    team.add_membership(user, role=role)
                updated.append(username)

    elif state == "absent":
        for username in desired_map:
            if username in current_members:
                if not check_mode:
                    user = gh.get_user(username)
                    team.remove_membership(user)
                removed.append(username)

    elif state == "exact":
        # Add missing and update roles
        for username, role in desired_map.items():
            if username not in current_members:
                if not check_mode:
                    user = gh.get_user(username)
                    team.add_membership(user, role=role)
                added.append(username)
            elif current_members[username] != role:
                if not check_mode:
                    user = gh.get_user(username)
                    team.add_membership(user, role=role)
                updated.append(username)

        # Remove members not in desired list
        for username in current_members:
            if username not in desired_map:
                if not check_mode:
                    user = gh.get_user(username)
                    team.remove_membership(user)
                removed.append(username)

    # Build final members list
    final_members = dict(current_members)
    for u in added:
        final_members[u] = desired_map[u]
    for u in updated:
        final_members[u] = desired_map[u]
    for u in removed:
        final_members.pop(u, None)

    result = dict(
        changed=bool(added or removed or updated),
        added=added,
        removed=removed,
        updated=updated,
        members=[{"username": u, "role": r} for u, r in sorted(final_members.items())],
    )
    return result


def main():
    module_args = dict(
        username=dict(type="str"),
        password=dict(type="str", no_log=True),
        access_token=dict(type="str", no_log=True),
        api_url=dict(type="str", default="https://api.github.com"),
        organization=dict(type="str", required=True),
        team=dict(type="str", required=True),
        members=dict(type="list", elements="raw", required=True),
        state=dict(type="str", default="present", choices=["present", "absent", "exact"]),
    )
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_together=[("username", "password")],
        required_one_of=[("username", "access_token")],
        mutually_exclusive=[("username", "access_token")],
    )

    if not HAS_GITHUB_PACKAGE:
        module.fail_json(msg=missing_required_lib("PyGithub"), exception=GITHUB_IMP_ERR)

    try:
        result = run_module(module.params, module.check_mode)
        module.exit_json(**result)
    except GithubException as e:
        module.fail_json(msg=f"Github error. {e}")
    except Exception as e:
        module.fail_json(msg=f"Unexpected error. {e}")


if __name__ == "__main__":
    main()
