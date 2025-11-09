#!/usr/bin/python
#
# Copyright (c) 2018, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: github_webhook
short_description: Manage GitHub webhooks
description:
  - Create and delete GitHub webhooks.
requirements:
  - "PyGithub >= 1.3.5"
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options:
  repository:
    description:
      - Full name of the repository to configure a hook for.
    type: str
    required: true
    aliases:
      - repo
  url:
    description:
      - URL to which payloads are delivered.
    type: str
    required: true
  content_type:
    description:
      - The media type used to serialize the payloads.
    type: str
    choices: [form, json]
    default: form
  secret:
    description:
      - The shared secret between GitHub and the payload URL.
    type: str
  insecure_ssl:
    description:
      - Flag to indicate that GitHub should skip SSL verification when calling the hook.
    type: bool
    default: false
  events:
    description:
      - A list of GitHub events the hook is triggered for. Events are listed at U(https://developer.github.com/v3/activity/events/types/).
        Required unless O(state=absent).
    type: list
    elements: str
  active:
    description:
      - Whether or not the hook is active.
    type: bool
    default: true
  state:
    description:
      - Whether the hook should be present or absent.
    type: str
    choices: [absent, present]
    default: present
  user:
    description:
      - User to authenticate to GitHub as.
    type: str
    required: true
  password:
    description:
      - Password to authenticate to GitHub with.
    type: str
  token:
    description:
      - Token to authenticate to GitHub with.
    type: str
  github_url:
    description:
      - Base URL of the GitHub API.
    type: str
    default: https://api.github.com

author:
  - "Chris St. Pierre (@stpierre)"
"""

EXAMPLES = r"""
- name: Create a new webhook that triggers on push (password auth)
  community.general.github_webhook:
    repository: ansible/ansible
    url: https://www.example.com/hooks/
    events:
      - push
    user: "{{ github_user }}"
    password: "{{ github_password }}"

- name: Create a new webhook in a github enterprise installation with multiple event triggers (token auth)
  community.general.github_webhook:
    repository: myorg/myrepo
    url: https://jenkins.example.com/ghprbhook/
    content_type: json
    secret: "{{ github_shared_secret }}"
    insecure_ssl: true
    events:
      - issue_comment
      - pull_request
    user: "{{ github_user }}"
    token: "{{ github_user_api_token }}"
    github_url: https://github.example.com

- name: Delete a webhook (password auth)
  community.general.github_webhook:
    repository: ansible/ansible
    url: https://www.example.com/hooks/
    state: absent
    user: "{{ github_user }}"
    password: "{{ github_password }}"
"""

RETURN = r"""
hook_id:
  description: The GitHub ID of the hook created/updated.
  returned: when state is 'present'
  type: int
  sample: 6206
"""

import traceback

GITHUB_IMP_ERR = None
try:
    import github

    HAS_GITHUB = True
except ImportError:
    GITHUB_IMP_ERR = traceback.format_exc()
    HAS_GITHUB = False

from ansible.module_utils.basic import AnsibleModule, missing_required_lib


def _create_hook_config(module):
    hook_config = {
        "url": module.params["url"],
        "content_type": module.params["content_type"],
        "insecure_ssl": "1" if module.params["insecure_ssl"] else "0",
    }

    secret = module.params.get("secret")
    if secret:
        hook_config["secret"] = secret

    return hook_config


def create_hook(repo, module):
    config = _create_hook_config(module)
    try:
        hook = repo.create_hook(
            name="web", config=config, events=module.params["events"], active=module.params["active"]
        )
    except github.GithubException as err:
        module.fail_json(msg=f"Unable to create hook for repository {repo.full_name}: {err}")

    data = {"hook_id": hook.id}
    return True, data


def update_hook(repo, hook, module):
    config = _create_hook_config(module)
    try:
        hook.update()
        hook.edit(name="web", config=config, events=module.params["events"], active=module.params["active"])

        changed = hook.update()
    except github.GithubException as err:
        module.fail_json(msg=f"Unable to modify hook for repository {repo.full_name}: {err}")

    data = {"hook_id": hook.id}
    return changed, data


def main():
    module = AnsibleModule(
        argument_spec=dict(
            repository=dict(type="str", required=True, aliases=["repo"]),
            url=dict(type="str", required=True),
            content_type=dict(type="str", choices=("json", "form"), default="form"),
            secret=dict(type="str", no_log=True),
            insecure_ssl=dict(type="bool", default=False),
            events=dict(
                type="list",
                elements="str",
            ),
            active=dict(type="bool", default=True),
            state=dict(type="str", choices=("absent", "present"), default="present"),
            user=dict(type="str", required=True),
            password=dict(type="str", no_log=True),
            token=dict(type="str", no_log=True),
            github_url=dict(type="str", default="https://api.github.com"),
        ),
        mutually_exclusive=(("password", "token"),),
        required_one_of=(("password", "token"),),
        required_if=(("state", "present", ("events",)),),
    )

    if not HAS_GITHUB:
        module.fail_json(msg=missing_required_lib("PyGithub"), exception=GITHUB_IMP_ERR)

    try:
        github_conn = github.Github(
            module.params["user"],
            module.params.get("password") or module.params.get("token"),
            base_url=module.params["github_url"],
        )
    except github.GithubException as err:
        module.fail_json(msg=f"Could not connect to GitHub at {module.params['github_url']}: {err}")

    try:
        repo = github_conn.get_repo(module.params["repository"])
    except github.BadCredentialsException as err:
        module.fail_json(msg=f"Could not authenticate to GitHub at {module.params['github_url']}: {err}")
    except github.UnknownObjectException as err:
        module.fail_json(
            msg=f"Could not find repository {module.params['repository']} in GitHub at {module.params['github_url']}: {err}"
        )
    except Exception as err:
        module.fail_json(
            msg=f"Could not fetch repository {module.params['repository']} from GitHub at {module.params['github_url']}: {err}",
            exception=traceback.format_exc(),
        )

    hook = None
    try:
        for hook in repo.get_hooks():
            if hook.config.get("url") == module.params["url"]:
                break
        else:
            hook = None
    except github.GithubException as err:
        module.fail_json(msg=f"Unable to get hooks from repository {module.params['repository']}: {err}")

    changed = False
    data = {}
    if hook is None and module.params["state"] == "present":
        changed, data = create_hook(repo, module)
    elif hook is not None and module.params["state"] == "absent":
        try:
            hook.delete()
        except github.GithubException as err:
            module.fail_json(msg=f"Unable to delete hook from repository {repo.full_name}: {err}")
        else:
            changed = True
    elif hook is not None and module.params["state"] == "present":
        changed, data = update_hook(repo, hook, module)
    # else, there is no hook and we want there to be no hook

    module.exit_json(changed=changed, **data)


if __name__ == "__main__":
    main()
