#!/usr/bin/python

# Copyright (c) 2025, John Westcott IV (@john-westcott-iv)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: github_team
short_description: Manage teams on Github organizations
version_added: NEXT_PATCH
description:
  - Create, update, rename, and delete teams in Github organizations using the PyGithub library.
  - This module manages the team itself but not its members. Use M(community.general.github_team_members) for membership management.
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
  name:
    description:
      - Team name.
      - Used for matching existing teams by slug (GitHub auto-generates slugs from names).
    type: str
    required: true
  description:
    description:
      - Description for the team.
    type: str
  privacy:
    description:
      - The level of privacy this team should have.
      - V(closed) means visible to all members of the organization.
      - V(secret) means only visible to organization owners and team members.
    type: str
    choices: [closed, secret]
  permission:
    description:
      - The default permission for repositories added to this team.
    type: str
    choices: [pull, push, admin]
  parent_team:
    description:
      - The name (slug) of the parent team for nested teams.
      - Set to an empty string to remove the parent team.
    type: str
  notification_setting:
    description:
      - The notification setting for the team.
      - V(notifications_enabled) means all team members receive notifications.
      - V(notifications_disabled) means only those who are explicitly subscribed receive notifications.
    type: str
    choices: [notifications_enabled, notifications_disabled]
  new_name:
    description:
      - Rename the team to this value.
      - Only used when O(state=present) and the team already exists.
    type: str
  state:
    description:
      - Whether the team should exist or not.
    type: str
    default: present
    choices: [absent, present]
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
- name: Create a team
  community.general.github_team:
    access_token: mytoken
    organization: MyOrganization
    name: my-team
    description: "The best team"
    privacy: closed
    permission: push
    state: present

- name: Create a nested team
  community.general.github_team:
    access_token: mytoken
    organization: MyOrganization
    name: sub-team
    parent_team: my-team
    state: present

- name: Rename a team
  community.general.github_team:
    access_token: mytoken
    organization: MyOrganization
    name: my-team
    new_name: renamed-team
    state: present

- name: Delete a team
  community.general.github_team:
    access_token: mytoken
    organization: MyOrganization
    name: my-team
    state: absent
"""

RETURN = r"""
team:
  description: Team information as a dictionary.
  returned: success and O(state=present)
  type: dict
  contains:
    id:
      description: The team ID.
      type: int
      returned: success
    name:
      description: The team name.
      type: str
      returned: success
    slug:
      description: The team slug.
      type: str
      returned: success
    description:
      description: The team description.
      type: str
      returned: success
    privacy:
      description: The team privacy level.
      type: str
      returned: success
    permission:
      description: The default repository permission.
      type: str
      returned: success
    url:
      description: The API URL of the team.
      type: str
      returned: success
"""

import traceback

from ansible.module_utils.basic import AnsibleModule, missing_required_lib

GITHUB_IMP_ERR = None
try:
    from github import Github, GithubException, GithubObject
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


def team_to_dict(team):
    return {
        "id": team.id,
        "name": team.name,
        "slug": team.slug,
        "description": team.description or "",
        "privacy": team.privacy,
        "permission": team.permission,
        "url": team.url,
    }


def get_team(org, name):
    """Try to find a team by slug. Returns None if not found."""
    try:
        return org.get_team_by_slug(name)
    except UnknownObjectException:
        return None


def run_module(params, check_mode=False):
    gh = authenticate(
        username=params["username"],
        password=params["password"],
        access_token=params["access_token"],
        api_url=params["api_url"],
    )

    org = gh.get_organization(params["organization"])
    name = params["name"]
    state = params["state"]

    result = dict(changed=False)

    team = get_team(org, name)

    if state == "absent":
        if team is not None:
            if not check_mode:
                team.delete()
            result["changed"] = True
        return result

    # state == present
    if team is None:
        # Create new team
        create_kwargs = {}
        if params["description"] is not None:
            create_kwargs["description"] = params["description"]
        if params["privacy"] is not None:
            create_kwargs["privacy"] = params["privacy"]
        if params["permission"] is not None:
            create_kwargs["permission"] = params["permission"]
        if params["notification_setting"] is not None:
            create_kwargs["notification_setting"] = params["notification_setting"]
        if params["parent_team"] is not None and params["parent_team"] != "":
            parent = get_team(org, params["parent_team"])
            if parent is None:
                raise ValueError(f"Parent team '{params['parent_team']}' not found")
            create_kwargs["parent_team_id"] = parent.id

        if not check_mode:
            team = org.create_team(name=name, **create_kwargs)
            result["team"] = team_to_dict(team)
        else:
            result["team"] = {
                "id": 0,
                "name": name,
                "slug": name.lower().replace(" ", "-"),
                "description": params["description"] or "",
                "privacy": params["privacy"] or "secret",
                "permission": params["permission"] or "pull",
                "url": "",
            }
        result["changed"] = True
        return result

    # Team exists, check for changes
    edit_kwargs = {}
    target_name = params["new_name"] if params["new_name"] else team.name

    if target_name != team.name:
        edit_kwargs["name"] = target_name

    if params["description"] is not None and params["description"] != (team.description or ""):
        edit_kwargs["description"] = params["description"]

    if params["privacy"] is not None and params["privacy"] != team.privacy:
        edit_kwargs["privacy"] = params["privacy"]

    if params["permission"] is not None and params["permission"] != team.permission:
        edit_kwargs["permission"] = params["permission"]

    if params["notification_setting"] is not None and params["notification_setting"] != team.notification_setting:
        edit_kwargs["notification_setting"] = params["notification_setting"]

    if params["parent_team"] is not None:
        if params["parent_team"] == "":
            # Remove parent team
            current_parent_id = team.parent.id if team.parent else None
            if current_parent_id is not None:
                edit_kwargs["parent_team_id"] = GithubObject.NotSet
        else:
            parent = get_team(org, params["parent_team"])
            if parent is None:
                raise ValueError(f"Parent team '{params['parent_team']}' not found")
            current_parent_id = team.parent.id if team.parent else None
            if parent.id != current_parent_id:
                edit_kwargs["parent_team_id"] = parent.id

    if edit_kwargs:
        if "name" not in edit_kwargs:
            edit_kwargs["name"] = team.name
        if not check_mode:
            team.edit(**edit_kwargs)

        d = team_to_dict(team)
        d.update({k: v for k, v in edit_kwargs.items() if k != "parent_team_id"})
        result["team"] = d
        result["changed"] = True
    else:
        result["team"] = team_to_dict(team)

    return result


def main():
    module_args = dict(
        username=dict(type="str"),
        password=dict(type="str", no_log=True),
        access_token=dict(type="str", no_log=True),
        api_url=dict(type="str", default="https://api.github.com"),
        organization=dict(type="str", required=True),
        name=dict(type="str", required=True),
        description=dict(type="str"),
        privacy=dict(type="str", choices=["closed", "secret"]),
        permission=dict(type="str", choices=["pull", "push", "admin"]),
        parent_team=dict(type="str"),
        notification_setting=dict(type="str", choices=["notifications_enabled", "notifications_disabled"]),
        new_name=dict(type="str"),
        state=dict(type="str", default="present", choices=["present", "absent"]),
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
