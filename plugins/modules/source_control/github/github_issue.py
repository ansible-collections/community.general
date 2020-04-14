#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2017-18, Abhijeet Kasurde <akasurde@redhat.com>
# Copyright: (c) 2020, Andrea Tartaglia <andrea@braingap.uk>
#
#  GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}


DOCUMENTATION = r"""
module: github_issue
short_description: View GitHub issue.
description:
    - View GitHub issue for a given repository and organization.
options:
  repo:
    description:
      - Name of repository from which issue needs to be retrieved.
    required: true
    type: str
  organization:
    description:
      - Name of the GitHub organization in which the repository is hosted.
    required: true
    type: str
  issue:
    description:
      - Issue number for which information is required.
    required: true
    type: int
  action:
    description:
        - Get various details about issue depending upon action specified.
    default: 'get_status'
    choices:
        - 'get_status'
    type: str
extends_documentation_fragment: community.general.github
author:
    - Abhijeet Kasurde (@Akasurde)
"""

RETURN = r"""
get_status:
    description: State of the GitHub issue
    type: str
    returned: success
    sample: open, closed
"""

EXAMPLES = r"""
- name: Check if GitHub issue is closed or not
  community.general.github_issue:
    organization: ansible
    repo: ansible
    issue: 23642
    action: get_status
  register: r

- name: Take action depending upon issue status
  debug:
    msg: Do something when issue 23642 is open
  when: r.get_status == 'open'
"""

import json


from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible_collections.community.general.plugins.module_utils import (
    github as github_utils,
)
from ansible.module_utils._text import to_native

HAS_GITHUB = False
if github_utils.HAS_GITHUB:
    HAS_GITHUB = True
    from github import GithubException, BadCredentialsException, UnknownObjectException


class GitHubIssue(github_utils.GitHubBase):
    def __init__(self, module):
        self.issue = module.params["issue"]

        super(GitHubIssue, self).__init__(
            server=module.params["server"],
            repo=module.params["repo"],
            organization=module.params["organization"],
        )
        self.auth()

    def get_issue(self):
        try:
            return self.repository.get_issue(number=self.issue)
        except github_utils.GithubUnknownObjectError:
            return None
        except UnknownObjectException:
            return None


def main():
    argument_spec = github_utils.github_common_argument_spec()
    argument_spec.update(
        dict(
            organization=dict(required=True),
            repo=dict(required=True),
            issue=dict(type="int", required=True),
            action=dict(choices=["get_status"], default="get_status"),
        )
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True,)

    if not HAS_GITHUB:
        module.fail_json(
            msg=missing_required_lib("PyGithub >= 1.3.5"),
            exception=github_utils.GITHUB_IMP_ERR,
        )

    action = module.params["action"]

    if action == "get_status" or action is None:
        if module.check_mode:
            module.exit_json(changed=True)
        else:
            github_issue = GitHubIssue(module)
            github_issue_state = github_issue.get_issue()
            if github_issue_state is None:
                module.fail_json(
                    msg="Failed to find issue {0}".format(github_issue.issue)
                )
            module.exit_json(changed=True, get_status=github_issue_state.state)


if __name__ == "__main__":
    main()
