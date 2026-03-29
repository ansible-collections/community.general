#!/usr/bin/python

# Copyright (c) 2025, John Westcott IV (@john-westcott-iv)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: github_branch_protection
short_description: Manage branch protection rules on Github repositories
version_added: NEXT_PATCH
description:
  - Manage branch protection rules on Github repositories using the PyGithub library.
  - Authentication can be done with O(access_token) or with O(username) and O(password).
  - When O(state=present), the protection settings are applied as a complete replacement.
    Any sub-options not specified will be disabled or set to their defaults.
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
  branch:
    description:
      - Branch name to protect.
    type: str
    required: true
  state:
    description:
      - Whether branch protection should exist or not.
    type: str
    default: present
    choices: [absent, present]
  required_status_checks:
    description:
      - Require status checks to pass before merging.
      - Set to V(null) to disable.
    type: dict
    suboptions:
      strict:
        description:
          - Require branches to be up to date before merging.
        type: bool
        default: false
      contexts:
        description:
          - The list of status checks to require in order to merge into this branch.
        type: list
        elements: str
        default: []
  enforce_admins:
    description:
      - Enforce all configured restrictions for administrators.
    type: bool
    default: false
  required_pull_request_reviews:
    description:
      - Require pull request reviews before merging.
      - Set to V(null) to disable.
    type: dict
    suboptions:
      dismiss_stale_reviews:
        description:
          - Dismiss approving reviews when someone pushes a new commit.
        type: bool
        default: false
      require_code_owner_reviews:
        description:
          - Require an approved review from code owners.
        type: bool
        default: false
      required_approving_review_count:
        description:
          - The number of approving reviews that are required.
        type: int
        default: 1
      dismissal_users:
        description:
          - List of user logins that can dismiss pull request reviews.
        type: list
        elements: str
        default: []
      dismissal_teams:
        description:
          - List of team slugs that can dismiss pull request reviews.
        type: list
        elements: str
        default: []
      require_last_push_approval:
        description:
          - Whether the most recent push must be approved by someone other than the person who pushed it.
        type: bool
        default: false
  restrictions:
    description:
      - Restrict who can push to the protected branch.
      - Only available for organization-owned repositories.
      - Set to V(null) to disable.
    type: dict
    suboptions:
      users:
        description:
          - List of user logins with push access.
        type: list
        elements: str
        default: []
      teams:
        description:
          - List of team slugs with push access.
        type: list
        elements: str
        default: []
  allow_force_pushes:
    description:
      - Permits force pushes to the protected branch.
    type: bool
    default: false
  allow_deletions:
    description:
      - Allows deletion of the protected branch.
    type: bool
    default: false
  required_linear_history:
    description:
      - Enforces a linear commit history by preventing merge commits.
    type: bool
    default: false
  required_conversation_resolution:
    description:
      - Requires all conversations on code to be resolved before a pull request can be merged.
    type: bool
    default: false
  lock_branch:
    description:
      - Lock the branch, making it read-only.
    type: bool
    default: false
  allow_fork_syncing:
    description:
      - Whether users can pull changes from upstream when the branch is locked.
    type: bool
    default: false
  block_creations:
    description:
      - Block creation of the branch if it matches the protection pattern.
    type: bool
    default: false
  required_signatures:
    description:
      - Require signed commits on the protected branch.
    type: bool
    default: false
requirements:
  - PyGithub>=1.54
notes:
  - For Python 3, PyGithub>=1.54 should be used.
  - "B(Important): When O(state=present), this module replaces all protection settings. Any settings not explicitly provided
    will be disabled or set to defaults. This is how the GitHub API works. Always specify the complete desired protection state."
author:
  - John Westcott IV (@john-westcott-iv)
"""

EXAMPLES = r"""
- name: Set basic branch protection
  community.general.github_branch_protection:
    access_token: mytoken
    organization: MyOrganization
    repo: myrepo
    branch: main
    enforce_admins: true
    required_pull_request_reviews:
      required_approving_review_count: 2
      dismiss_stale_reviews: true
    required_status_checks:
      strict: true
      contexts:
        - ci/build
        - ci/test
    state: present

- name: Protect branch with restrictions
  community.general.github_branch_protection:
    access_token: mytoken
    organization: MyOrganization
    repo: myrepo
    branch: main
    enforce_admins: true
    restrictions:
      users:
        - octocat
      teams:
        - release-team
    state: present

- name: Remove branch protection
  community.general.github_branch_protection:
    access_token: mytoken
    organization: MyOrganization
    repo: myrepo
    branch: main
    state: absent
"""

RETURN = r"""
protection:
  description: Branch protection configuration as returned by GitHub.
  returned: success and O(state=present)
  type: dict
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


def protection_to_dict(branch):
    """Extract protection settings into a comparable dict."""
    try:
        protection = branch.get_protection()
    except UnknownObjectException:
        return None

    result = {
        "enforce_admins": False,
        "required_status_checks": None,
        "required_pull_request_reviews": None,
        "restrictions": None,
        "allow_force_pushes": False,
        "allow_deletions": False,
        "required_linear_history": False,
        "required_conversation_resolution": False,
        "lock_branch": False,
        "allow_fork_syncing": False,
        "block_creations": False,
        "required_signatures": False,
    }

    try:
        admin = branch.get_admin_enforcement()
        result["enforce_admins"] = admin if isinstance(admin, bool) else bool(admin)
    except (UnknownObjectException, GithubException):
        pass

    try:
        rsc = branch.get_required_status_checks()
        result["required_status_checks"] = {
            "strict": rsc.strict,
            "contexts": sorted(rsc.contexts),
        }
    except (UnknownObjectException, GithubException):
        pass

    try:
        rpr = branch.get_required_pull_request_reviews()
        dismissal_users = []
        dismissal_teams = []
        if rpr.dismissal_users:
            dismissal_users = sorted([u.login for u in rpr.dismissal_users])
        if rpr.dismissal_teams:
            dismissal_teams = sorted([t.slug for t in rpr.dismissal_teams])
        result["required_pull_request_reviews"] = {
            "dismiss_stale_reviews": rpr.dismiss_stale_reviews,
            "require_code_owner_reviews": rpr.require_code_owner_reviews,
            "required_approving_review_count": rpr.required_approving_review_count,
            "dismissal_users": dismissal_users,
            "dismissal_teams": dismissal_teams,
            "require_last_push_approval": getattr(rpr, "require_last_push_approval", False),
        }
    except (UnknownObjectException, GithubException):
        pass

    try:
        user_restrictions = sorted([u.login for u in branch.get_user_push_restrictions()])
        team_restrictions = sorted([t.slug for t in branch.get_team_push_restrictions()])
        result["restrictions"] = {
            "users": user_restrictions,
            "teams": team_restrictions,
        }
    except (UnknownObjectException, GithubException):
        pass

    try:
        result["allow_force_pushes"] = bool(protection.allow_force_pushes)
    except Exception:
        pass

    try:
        result["allow_deletions"] = bool(branch.get_allow_deletions())
    except (UnknownObjectException, GithubException):
        pass

    try:
        result["required_linear_history"] = bool(protection.required_linear_history)
    except Exception:
        pass

    try:
        result["required_conversation_resolution"] = bool(protection.required_conversation_resolution)
    except Exception:
        pass

    try:
        result["lock_branch"] = bool(protection.lock_branch)
    except Exception:
        pass

    try:
        result["allow_fork_syncing"] = bool(protection.allow_fork_syncing)
    except Exception:
        pass

    try:
        result["block_creations"] = bool(protection.block_creations)
    except Exception:
        pass

    try:
        result["required_signatures"] = bool(branch.get_required_signatures())
    except (UnknownObjectException, GithubException):
        pass

    return result


def build_desired_state(params):
    """Build desired protection state from module params."""
    desired = {
        "enforce_admins": params["enforce_admins"],
        "allow_force_pushes": params["allow_force_pushes"],
        "allow_deletions": params["allow_deletions"],
        "required_linear_history": params["required_linear_history"],
        "required_conversation_resolution": params["required_conversation_resolution"],
        "lock_branch": params["lock_branch"],
        "allow_fork_syncing": params["allow_fork_syncing"],
        "block_creations": params["block_creations"],
        "required_signatures": params["required_signatures"],
    }

    if params["required_status_checks"] is not None:
        rsc = params["required_status_checks"]
        desired["required_status_checks"] = {
            "strict": rsc.get("strict", False),
            "contexts": sorted(rsc.get("contexts", [])),
        }
    else:
        desired["required_status_checks"] = None

    if params["required_pull_request_reviews"] is not None:
        rpr = params["required_pull_request_reviews"]
        desired["required_pull_request_reviews"] = {
            "dismiss_stale_reviews": rpr.get("dismiss_stale_reviews", False),
            "require_code_owner_reviews": rpr.get("require_code_owner_reviews", False),
            "required_approving_review_count": rpr.get("required_approving_review_count", 1),
            "dismissal_users": sorted(rpr.get("dismissal_users", [])),
            "dismissal_teams": sorted(rpr.get("dismissal_teams", [])),
            "require_last_push_approval": rpr.get("require_last_push_approval", False),
        }
    else:
        desired["required_pull_request_reviews"] = None

    if params["restrictions"] is not None:
        rest = params["restrictions"]
        desired["restrictions"] = {
            "users": sorted(rest.get("users", [])),
            "teams": sorted(rest.get("teams", [])),
        }
    else:
        desired["restrictions"] = None

    return desired


def run_module(params, check_mode=False):
    gh = authenticate(
        username=params["username"],
        password=params["password"],
        access_token=params["access_token"],
        api_url=params["api_url"],
    )

    repo = gh.get_repo(f"{params['organization']}/{params['repo']}")
    branch = repo.get_branch(params["branch"])

    state = params["state"]
    result = dict(changed=False)

    if state == "absent":
        if branch.protected:
            if not check_mode:
                branch.remove_protection()
            result["changed"] = True
        return result

    # state == present
    desired = build_desired_state(params)
    current = protection_to_dict(branch) if branch.protected else None

    if current == desired:
        result["protection"] = current
        return result

    if not check_mode:
        # Build edit_protection kwargs
        kwargs = {
            "enforce_admins": desired["enforce_admins"],
            "allow_force_pushes": desired["allow_force_pushes"],
            "allow_deletions": desired["allow_deletions"],
            "required_linear_history": desired["required_linear_history"],
            "required_conversation_resolution": desired["required_conversation_resolution"],
            "lock_branch": desired["lock_branch"],
            "allow_fork_syncing": desired["allow_fork_syncing"],
            "block_creations": desired["block_creations"],
        }

        if desired["required_status_checks"] is not None:
            kwargs["strict"] = desired["required_status_checks"]["strict"]
            kwargs["contexts"] = desired["required_status_checks"]["contexts"]
        else:
            kwargs["strict"] = GithubObject.NotSet
            kwargs["contexts"] = GithubObject.NotSet

        if desired["required_pull_request_reviews"] is not None:
            rpr = desired["required_pull_request_reviews"]
            kwargs["dismiss_stale_reviews"] = rpr["dismiss_stale_reviews"]
            kwargs["require_code_owner_reviews"] = rpr["require_code_owner_reviews"]
            kwargs["required_approving_review_count"] = rpr["required_approving_review_count"]
            kwargs["dismissal_users"] = rpr["dismissal_users"]
            kwargs["dismissal_teams"] = rpr["dismissal_teams"]
            kwargs["require_last_push_approval"] = rpr["require_last_push_approval"]
        else:
            kwargs["dismiss_stale_reviews"] = GithubObject.NotSet
            kwargs["require_code_owner_reviews"] = GithubObject.NotSet
            kwargs["required_approving_review_count"] = GithubObject.NotSet

        if desired["restrictions"] is not None:
            kwargs["user_push_restrictions"] = desired["restrictions"]["users"]
            kwargs["team_push_restrictions"] = desired["restrictions"]["teams"]
        else:
            kwargs["user_push_restrictions"] = GithubObject.NotSet
            kwargs["team_push_restrictions"] = GithubObject.NotSet

        branch.edit_protection(**kwargs)

        # Handle required_signatures separately
        if desired["required_signatures"]:
            branch.add_required_signatures()
        else:
            try:
                branch.remove_required_signatures()
            except (UnknownObjectException, GithubException):
                pass

        result["protection"] = protection_to_dict(branch)
    else:
        result["protection"] = desired

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
        branch=dict(type="str", required=True),
        state=dict(type="str", default="present", choices=["present", "absent"]),
        required_status_checks=dict(
            type="dict",
            options=dict(
                strict=dict(type="bool", default=False),
                contexts=dict(type="list", elements="str", default=[]),
            ),
        ),
        enforce_admins=dict(type="bool", default=False),
        required_pull_request_reviews=dict(
            type="dict",
            options=dict(
                dismiss_stale_reviews=dict(type="bool", default=False),
                require_code_owner_reviews=dict(type="bool", default=False),
                required_approving_review_count=dict(type="int", default=1),
                dismissal_users=dict(type="list", elements="str", default=[]),
                dismissal_teams=dict(type="list", elements="str", default=[]),
                require_last_push_approval=dict(type="bool", default=False),
            ),
        ),
        restrictions=dict(
            type="dict",
            options=dict(
                users=dict(type="list", elements="str", default=[]),
                teams=dict(type="list", elements="str", default=[]),
            ),
        ),
        allow_force_pushes=dict(type="bool", default=False),
        allow_deletions=dict(type="bool", default=False),
        required_linear_history=dict(type="bool", default=False),
        required_conversation_resolution=dict(type="bool", default=False),
        lock_branch=dict(type="bool", default=False),
        allow_fork_syncing=dict(type="bool", default=False),
        block_creations=dict(type="bool", default=False),
        required_signatures=dict(type="bool", default=False),
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
