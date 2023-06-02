#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017-18, Abhijeet Kasurde <akasurde@redhat.com>
#
#  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
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
author:
    - Abhijeet Kasurde (@Akasurde)
'''

RETURN = '''
issue_status:
    description: State of the GitHub issue
    type: str
    returned: success
    sample: open, closed
'''

EXAMPLES = '''
- name: Check if GitHub issue is closed or not
  community.general.github_issue:
    organization: ansible
    repo: ansible
    issue: 23642
    action: get_status
  register: r

- name: Take action depending upon issue status
  ansible.builtin.debug:
    msg: Do something when issue 23642 is open
  when: r.issue_status == 'open'
'''

import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url


def main():
    module = AnsibleModule(
        argument_spec=dict(
            organization=dict(required=True),
            repo=dict(required=True),
            issue=dict(type='int', required=True),
            action=dict(choices=['get_status'], default='get_status'),
        ),
        supports_check_mode=True,
    )

    organization = module.params['organization']
    repo = module.params['repo']
    issue = module.params['issue']
    action = module.params['action']

    result = dict()

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/vnd.github.v3+json',
    }

    url = "https://api.github.com/repos/%s/%s/issues/%s" % (organization, repo, issue)

    response, info = fetch_url(module, url, headers=headers)
    if not (200 <= info['status'] < 400):
        if info['status'] == 404:
            module.fail_json(msg="Failed to find issue %s" % issue)
        module.fail_json(msg="Failed to send request to %s: %s" % (url, info['msg']))

    gh_obj = json.loads(response.read())

    if action == 'get_status' or action is None:
        if module.check_mode:
            result.update(changed=True)
        else:
            result.update(changed=True, issue_status=gh_obj['state'])

    module.exit_json(**result)


if __name__ == '__main__':
    main()
