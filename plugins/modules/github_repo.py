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


def authenticate(username=None, password=None, access_token=None, api_url=None):
    if not api_url:
        return None

    if access_token:
        return Github(base_url=api_url, login_or_token=access_token)
    else:
        return Github(base_url=api_url, login_or_token=username, password=password)


def create_repo(gh, name, organization=None, private=None, description=None, check_mode=False):
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

    if changes:
        if not check_mode:
            repo.edit(**changes)

        result["repo"].update(
            {
                "private": repo._private.value if not check_mode else private,
                "description": repo._description.value if not check_mode else description,
            }
        )
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
        return create_repo(
            gh=gh,
            name=params["name"],
            organization=params["organization"],
            private=params["private"],
            description=params["description"],
            check_mode=check_mode,
        )


def main():
    module_args = dict(
        username=dict(type="str"),
        password=dict(type="str", no_log=True),
        access_token=dict(type="str", no_log=True),
        name=dict(type="str", required=True),
        state=dict(type="str", default="present", choices=["present", "absent"]),
        organization=dict(
            type="str",
        ),
        private=dict(type="bool"),
        description=dict(type="str"),
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
