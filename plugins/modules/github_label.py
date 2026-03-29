#!/usr/bin/python

# Copyright (c) 2025, John Westcott IV (@john-westcott-iv)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: github_label
short_description: Manage labels on Github repositories
version_added: NEXT_PATCH
description:
  - Create, update, rename, and delete labels on Github repositories using the PyGithub library.
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
      - Label name.
    type: str
    required: true
  color:
    description:
      - Hex color code for the label, without the leading C(#).
      - For example V(0e8a16) or V(ff0000).
      - Required when O(state=present) and the label does not already exist.
    type: str
  description:
    description:
      - A short description for the label.
    type: str
    default: ''
  new_name:
    description:
      - Rename the label to this value.
      - Only used when O(state=present) and the label already exists.
    type: str
  state:
    description:
      - Whether the label should exist or not.
    type: str
    default: present
    choices: [absent, present]
requirements:
  - PyGithub>=1.54
notes:
  - For Python 3, PyGithub>=1.54 should be used.
author:
  - John Westcott IV (@john-westcott-iv)
"""

EXAMPLES = r"""
- name: Create a label
  community.general.github_label:
    access_token: mytoken
    organization: MyOrganization
    repo: myrepo
    name: bug
    color: "d73a4a"
    description: "Something isn't working"
    state: present

- name: Update a label color
  community.general.github_label:
    access_token: mytoken
    organization: MyOrganization
    repo: myrepo
    name: bug
    color: "ff0000"
    state: present

- name: Rename a label
  community.general.github_label:
    access_token: mytoken
    organization: MyOrganization
    repo: myrepo
    name: bug
    new_name: defect
    color: "d73a4a"
    state: present

- name: Delete a label
  community.general.github_label:
    access_token: mytoken
    organization: MyOrganization
    repo: myrepo
    name: bug
    state: absent
"""

RETURN = r"""
label:
  description: Label information as a dictionary.
  returned: success and O(state=present)
  type: dict
  contains:
    name:
      description: The label name.
      type: str
      returned: success
    color:
      description: The label color (hex without C(#)).
      type: str
      returned: success
    description:
      description: The label description.
      type: str
      returned: success
    url:
      description: The API URL of the label.
      type: str
      returned: success
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


def label_to_dict(label):
    return {
        "name": label.name,
        "color": label.color,
        "description": label.description or "",
        "url": label.url,
    }


def run_module(params, check_mode=False):
    gh = authenticate(
        username=params["username"],
        password=params["password"],
        access_token=params["access_token"],
        api_url=params["api_url"],
    )

    repo = gh.get_repo(f"{params['organization']}/{params['repo']}")

    name = params["name"]
    state = params["state"]
    color = params["color"]
    description = params["description"]
    new_name = params["new_name"]

    result = dict(changed=False)

    try:
        label = repo.get_label(name)
    except UnknownObjectException:
        label = None

    if state == "absent":
        if label is not None:
            if not check_mode:
                label.delete()
            result["changed"] = True
        return result

    # state == present
    if label is None:
        if color is None:
            raise ValueError("Parameter 'color' is required when creating a new label")
        if not check_mode:
            label = repo.create_label(name=name, color=color, description=description)
            result["label"] = label_to_dict(label)
        else:
            result["label"] = {"name": name, "color": color, "description": description, "url": ""}
        result["changed"] = True
        return result

    # Label exists, check for changes
    changes = {}
    target_name = new_name if new_name else name
    target_color = color if color else label.color
    target_description = description if description is not None else (label.description or "")

    if target_name != label.name:
        changes["name"] = target_name
    if target_color != label.color:
        changes["color"] = target_color
    if target_description != (label.description or ""):
        changes["description"] = target_description

    if changes:
        if not check_mode:
            label.edit(
                name=target_name,
                color=target_color,
                description=target_description,
            )

        result["label"] = {
            "name": target_name,
            "color": target_color,
            "description": target_description,
            "url": label.url,
        }
        result["changed"] = True
    else:
        result["label"] = label_to_dict(label)

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
        color=dict(type="str"),
        description=dict(type="str", default=""),
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
