#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# Copyright: (c) 2018, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = """
---
module: github_webhook
short_description: Manage GitHub webhooks
description:
  - "Create and delete GitHub webhooks"
requirements:
  - "PyGithub >= 1.3.5"
options:
  repository:
    description:
      - Full name of the repository to configure a hook for
    required: true
    aliases:
      - repo
    type: str
  url:
    description:
      - URL to which payloads will be delivered
    required: true
    type: str
  content_type:
    description:
      - The media type used to serialize the payloads
    required: false
    choices: [ form, json ]
    default: form
    type: str
  secret:
    description:
      - The shared secret between GitHub and the payload URL.
    required: false
    type: str
  insecure_ssl:
    description:
      - >
        Flag to indicate that GitHub should skip SSL verification when calling
        the hook.
    required: false
    type: bool
    default: false
  events:
    description:
      - >
        A list of GitHub events the hook is triggered for. Events are listed at
        U(https://developer.github.com/v3/activity/events/types/). Required
        unless C(state) is C(absent)
    required: false
    type: list
    elements: str
  active:
    description:
      - Whether or not the hook is active
    required: false
    type: bool
    default: true
  state:
    description:
      - Whether the hook should be present or absent
    required: false
    choices: [ absent, present ]
    default: present
    type: str

extends_documentation_fragment: community.general.github
author:
  - "Chris St. Pierre (@stpierre)"
"""

EXAMPLES = """
- name:  create a new webhook that triggers on push (password auth)
  github_webhook:
    repository: ansible/ansible
    url: https://www.example.com/hooks/
    events:
      - push
    user: "{{ github_user }}"
    password: "{{ github_password }}"

- name: create a new webhook in a github enterprise installation with multiple event triggers (token auth)
  github_webhook:
    repository: myorg/myrepo
    url: https://jenkins.example.com/ghprbhook/
    content_type: json
    secret: "{{ github_shared_secret }}"
    insecure_ssl: True
    events:
      - issue_comment
      - pull_request
    user: "{{ github_user }}"
    token: "{{ github_user_api_token }}"
    github_url: https://github.example.com

- name: delete a webhook (password auth)
  github_webhook:
    repository: ansible/ansible
    url: https://www.example.com/hooks/
    state: absent
    user: "{{ github_user }}"
    password: "{{ github_password }}"
"""

RETURN = """
---
hook_id:
  description: The GitHub ID of the hook created/updated
  returned: when state is 'present'
  type: int
  sample: 6206
"""

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils._text import to_native
from ansible_collections.community.general.plugins.module_utils import (
    github as github_utils,
)


class GithubWebHook(github_utils.GitHubBase):
    def __init__(self, module):
        self.module = module
        self.webhook_url = module.params["url"]
        self.content_type = module.params["content_type"]
        self.secret = module.params["secret"]
        self.insecure_ssl = module.params["insecure_ssl"]
        self.events = module.params["events"]
        self.active = module.params["active"]
        self.state = module.params["state"]

        super(GithubWebHook, self).__init__(
            username=module.params["user"],
            password=module.params["password"],
            token=module.params["token"],
            server=module.params["github_url"],
            repo=module.params["repository"],
        )

        self.auth()

        self.webhook_config = self._webhook_config()
        self.webhook = self._get_hook()

    def _webhook_config(self):
        return dict(
            url=self.webhook_url,
            content_type=self.content_type,
            secret=self.content_type,
            insecure_ssl="1" if self.insecure_ssl else "0",
        )

    def _get_hook(self):
        try:
            for hook in self.repository.get_hooks():
                if hook.config.get("url") == self.webhook_url:
                    return hook
            return None
        except github_utils.GithubError as err:
            self.module.fail_json(
                "Unable to get hooks from repository {0}: {1}".format(
                    self.module.params["repository"], to_native(err)
                )
            )

    def create_hook(self):
        try:
            hook = self.repository.create_hook(
                name="web",
                config=self.webhook_config,
                events=self.events,
                active=self.active,
            )
        except github_utils.GithubError as err:
            self.module.fail_json(
                msg="Unable to create hook for repository %s: %s"
                % (self.repository.full_name, to_native(err))
            )

        data = {"hook_id": hook.id}
        return True, data

    def update_hook(self):
        try:
            self.webhook.edit(
                name="web",
                config=self.webhook_config,
                events=self.events,
                active=self.events,
            )
        except github_utils.GithubError as err:
            self.module.fail_json(
                msg="Unable to modify hook for repository %s: %s"
                % (self.repository.full_name, to_native(err))
            )

        data = {"hook_id": self.webhook.id}
        return True, data


def main():
    argument_spec = github_utils.github_common_argument_spec()
    argument_spec.update(
        dict(
            repository=dict(type="str", required=True, aliases=["repo"]),
            url=dict(type="str", required=True),
            content_type=dict(
                type="str", choices=("json", "form"), required=False, default="form"
            ),
            secret=dict(type="str", required=False, no_log=True),
            insecure_ssl=dict(type="bool", required=False, default=False),
            events=dict(type="list", elements="str", required=False),
            active=dict(type="bool", required=False, default=True),
            state=dict(
                type="str",
                required=False,
                choices=("absent", "present"),
                default="present",
            ),
        )
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=(("password", "token"),),
        required_one_of=(("password", "token"),),
        required_if=(("state", "present", ("events",)),),
    )

    if not github_utils.HAS_GITHUB:
        module.fail_json(
            msg=missing_required_lib("PyGithub"), exception=github_utils.GITHUB_IMP_ERR
        )

    github_webhook = GithubWebHook(module)

    changed = False
    data = {}
    if github_webhook.webhook is None and module.params["state"] == "present":
        changed, data = github_webhook.create_hook()
    elif github_webhook.webhook is not None and module.params["state"] == "absent":
        try:
            github_webhook.webhook.delete()
        except github_utils.GithubException as err:
            module.fail_json(
                msg="Unable to delete hook from repository %s: %s"
                % (github_webhook.repository.full_name, to_native(err))
            )
        else:
            changed = True
    elif github_webhook.webhook is not None and module.params["state"] == "present":
        changed, data = github_webhook.update_hook()
    # else, there is no hook and we want there to be no hook

    module.exit_json(changed=changed, **data)


if __name__ == "__main__":
    main()
