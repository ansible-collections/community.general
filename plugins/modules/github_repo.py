#!/usr/bin/python

# Copyright (c) 2021, Álvaro Torres Cogollo
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: github_repo
short_description: Manage your repositories on Github
version_added: 2.2.0
description:
  - Manages Github repositories using PyGithub library.
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
  name:
    description:
      - Repository name.
    type: str
    required: true
  description:
    description:
      - Description for the repository.
      - Defaults to empty if O(force_defaults=true), which is the default in this module.
      - Defaults to empty if O(force_defaults=false) when creating a new repository.
      - This is only used when O(state) is V(present).
    type: str
  private:
    description:
      - Whether the repository should be private or not.
      - Defaults to V(false) if O(force_defaults=true), which is the default in this module.
      - Defaults to V(false) if O(force_defaults=false) when creating a new repository.
      - This is only used when O(state=present).
    type: bool
  has_issues:
    description:
      - Whether to enable issues on the repository.
    type: bool
    version_added: NEXT_PATCH
  has_wiki:
    description:
      - Whether to enable the wiki on the repository.
    type: bool
    version_added: NEXT_PATCH
  has_projects:
    description:
      - Whether to enable projects on the repository.
    type: bool
    version_added: NEXT_PATCH
  has_discussions:
    description:
      - Whether to enable discussions on the repository.
    type: bool
    version_added: NEXT_PATCH
  allow_squash_merge:
    description:
      - Whether to allow squash merges for pull requests.
    type: bool
    version_added: NEXT_PATCH
  allow_merge_commit:
    description:
      - Whether to allow merge commits for pull requests.
    type: bool
    version_added: NEXT_PATCH
  allow_rebase_merge:
    description:
      - Whether to allow rebase merges for pull requests.
    type: bool
    version_added: NEXT_PATCH
  delete_branch_on_merge:
    description:
      - Whether to automatically delete head branches after pull requests are merged.
    type: bool
    version_added: NEXT_PATCH
  allow_auto_merge:
    description:
      - Whether to allow auto-merge on pull requests.
    type: bool
    version_added: NEXT_PATCH
  squash_merge_commit_title:
    description:
      - The default value for a squash merge commit title.
    type: str
    choices: [PR_TITLE, COMMIT_OR_PR_TITLE]
    version_added: NEXT_PATCH
  squash_merge_commit_message:
    description:
      - The default value for a squash merge commit message.
    type: str
    choices: [PR_BODY, COMMIT_MESSAGES, BLANK]
    version_added: NEXT_PATCH
  merge_commit_title:
    description:
      - The default value for a merge commit title.
    type: str
    choices: [PR_TITLE, MERGE_MESSAGE]
    version_added: NEXT_PATCH
  merge_commit_message:
    description:
      - The default value for a merge commit message.
    type: str
    choices: [PR_BODY, PR_TITLE, BLANK]
    version_added: NEXT_PATCH
  homepage:
    description:
      - A URL with more information about the repository.
    type: str
    version_added: NEXT_PATCH
  topics:
    description:
      - A list of topics to set on the repository.
      - This replaces all existing topics.
    type: list
    elements: str
    version_added: NEXT_PATCH
  state:
    description:
      - Whether the repository should exist or not.
    type: str
    default: present
    choices: [absent, present]
  organization:
    description:
      - Organization for the repository.
      - When O(state=present), the repository is created in the current user profile.
    type: str
  api_url:
    description:
      - URL to the GitHub API if not using github.com but you own instance.
    type: str
    default: 'https://api.github.com'
    version_added: "3.5.0"
  force_defaults:
    description:
      - If V(true), overwrite current O(description) and O(private) attributes with defaults.
      - V(true) is deprecated for this option and will not be allowed starting in community.general 13.0.0. V(false) will be the default value then.
    type: bool
    version_added: 4.1.0
requirements:
  - PyGithub>=1.54
notes:
  - For Python 3, PyGithub>=1.54 should be used.
author:
  - Álvaro Torres Cogollo (@atorrescogollo)
"""

EXAMPLES = r"""
- name: Create a Github repository
  community.general.github_repo:
    access_token: mytoken
    organization: MyOrganization
    name: myrepo
    description: "Just for fun"
    private: true
    state: present
    force_defaults: false
  register: result

- name: Update repository settings
  community.general.github_repo:
    access_token: mytoken
    organization: MyOrganization
    name: myrepo
    has_wiki: false
    has_issues: true
    has_projects: false
    has_discussions: true
    allow_squash_merge: true
    allow_merge_commit: false
    allow_rebase_merge: false
    delete_branch_on_merge: true
    allow_auto_merge: true
    squash_merge_commit_title: PR_TITLE
    squash_merge_commit_message: PR_BODY
    homepage: "https://example.com"
    topics:
      - ansible
      - automation
    state: present
    force_defaults: false
  register: result

- name: Delete the repository
  community.general.github_repo:
    username: octocat
    password: password
    organization: MyOrganization
    name: myrepo
    state: absent
  register: result
"""

RETURN = r"""
repo:
  description: Repository information as JSON. See U(https://docs.github.com/en/rest/reference/repos#get-a-repository).
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

# Parameters that map directly to Repository.edit() kwargs
REPO_EDIT_PARAMS = [
    "has_issues",
    "has_wiki",
    "has_projects",
    "has_discussions",
    "allow_squash_merge",
    "allow_merge_commit",
    "allow_rebase_merge",
    "delete_branch_on_merge",
    "allow_auto_merge",
    "squash_merge_commit_title",
    "squash_merge_commit_message",
    "merge_commit_title",
    "merge_commit_message",
    "homepage",
]


def authenticate(username=None, password=None, access_token=None, api_url=None):
    if not api_url:
        return None

    if access_token:
        return Github(base_url=api_url, login_or_token=access_token)
    else:
        return Github(base_url=api_url, login_or_token=username, password=password)


def create_repo(gh, name, organization=None, private=None, description=None, check_mode=False, **extra_params):
    result = dict(changed=False, repo=dict())
    if organization:
        target = gh.get_organization(organization)
    else:
        target = gh.get_user()

    repo = None
    try:
        repo = target.get_repo(name=name)
        result["repo"] = repo.raw_data
    except UnknownObjectException:
        if not check_mode:
            repo = target.create_repo(
                name=name,
                private=GithubObject.NotSet if private is None else private,
                description=GithubObject.NotSet if description is None else description,
            )
            result["repo"] = repo.raw_data

        result["changed"] = True

    changes = {}
    if private is not None:
        if repo is None or repo.raw_data["private"] != private:
            changes["private"] = private
    if description is not None:
        if repo is None or repo.raw_data["description"] not in (description, description or None):
            changes["description"] = description

    for param in REPO_EDIT_PARAMS:
        value = extra_params.get(param)
        if value is not None:
            raw_key = param
            if repo is None or repo.raw_data.get(raw_key) != value:
                changes[param] = value

    if changes:
        if not check_mode:
            repo.edit(**changes)

        result["repo"].update(changes)
        result["changed"] = True

    # Handle topics separately (different API endpoint)
    topics = extra_params.get("topics")
    if topics is not None:
        current_topics = sorted(repo.get_topics()) if repo is not None and not check_mode else []
        if sorted(topics) != current_topics:
            if not check_mode:
                repo.replace_topics(topics)
                result["repo"]["topics"] = topics
            else:
                result["repo"]["topics"] = topics
            result["changed"] = True

    return result


def delete_repo(gh, name, organization=None, check_mode=False):
    result = dict(changed=False)
    if organization:
        target = gh.get_organization(organization)
    else:
        target = gh.get_user()
    try:
        repo = target.get_repo(name=name)
        if not check_mode:
            repo.delete()
        result["changed"] = True
    except UnknownObjectException:
        pass

    return result


def run_module(params, check_mode=False):
    if params["force_defaults"]:
        params["description"] = params["description"] or ""
        params["private"] = params["private"] or False

    gh = authenticate(
        username=params["username"],
        password=params["password"],
        access_token=params["access_token"],
        api_url=params["api_url"],
    )
    if params["state"] == "absent":
        return delete_repo(gh=gh, name=params["name"], organization=params["organization"], check_mode=check_mode)
    else:
        extra_params = {param: params[param] for param in REPO_EDIT_PARAMS if params.get(param) is not None}
        if params.get("topics") is not None:
            extra_params["topics"] = params["topics"]
        return create_repo(
            gh=gh,
            name=params["name"],
            organization=params["organization"],
            private=params["private"],
            description=params["description"],
            check_mode=check_mode,
            **extra_params,
        )


def main():
    module_args = dict(
        username=dict(type="str"),
        password=dict(type="str", no_log=True),
        access_token=dict(type="str", no_log=True),
        name=dict(type="str", required=True),
        state=dict(type="str", default="present", choices=["present", "absent"]),
        organization=dict(type="str"),
        private=dict(type="bool"),
        description=dict(type="str"),
        has_issues=dict(type="bool"),
        has_wiki=dict(type="bool"),
        has_projects=dict(type="bool"),
        has_discussions=dict(type="bool"),
        allow_squash_merge=dict(type="bool"),
        allow_merge_commit=dict(type="bool"),
        allow_rebase_merge=dict(type="bool"),
        delete_branch_on_merge=dict(type="bool"),
        allow_auto_merge=dict(type="bool"),
        squash_merge_commit_title=dict(type="str", choices=["PR_TITLE", "COMMIT_OR_PR_TITLE"]),
        squash_merge_commit_message=dict(type="str", choices=["PR_BODY", "COMMIT_MESSAGES", "BLANK"]),
        merge_commit_title=dict(type="str", choices=["PR_TITLE", "MERGE_MESSAGE"]),
        merge_commit_message=dict(type="str", choices=["PR_BODY", "PR_TITLE", "BLANK"]),
        homepage=dict(type="str"),
        topics=dict(type="list", elements="str"),
        api_url=dict(type="str", default="https://api.github.com"),
        force_defaults=dict(type="bool"),
    )
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_together=[("username", "password")],
        required_one_of=[("username", "access_token")],
        mutually_exclusive=[("username", "access_token")],
    )

    if module.params["force_defaults"] is None:
        module.deprecate(
            "'force_defaults=true' is deprecated and will not be allowed in community.general 13.0.0, use 'force_defaults=false' instead",
            version="13.0.0",
            collection_name="community.general",
        )
        module.params["force_defaults"] = True

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
