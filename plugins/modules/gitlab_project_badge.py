#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2022, Guillaume MARTINEZ (lunik@tiwabbit.fr)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: gitlab_project_badge
short_description: Manage project badges on GitLab Server
version_added: 6.1.0
description:
  - This module allows to add and remove badges to/from a project.
author: Guillaume MARTINEZ (@Lunik)
requirements:
  - C(owner) or C(maintainer) rights to project on the GitLab server
extends_documentation_fragment:
  - community.general.auth_basic
  - community.general.gitlab
  - community.general.attributes

attributes:
  check_mode:
    support: full
  diff_mode:
    support: none

options:
  project:
    description:
      - The name (or full path) of the GitLab project the badge is added to/removed from.
    required: true
    type: str

  state:
    description:
      - State of the badge in the project.
      - On V(present), it adds a badge to a GitLab project.
      - On V(absent), it removes a badge from a GitLab project.
    choices: ['present', 'absent']
    default: 'present'
    type: str

  link_url:
    description:
      - The URL associated with the badge.
    required: true
    type: str

  image_url:
    description:
      - The image URL of the badge.
      - A badge is identified by this URL.
    required: true
    type: str
"""

EXAMPLES = r"""
- name: Add a badge to a GitLab Project
  community.general.gitlab_project_badge:
    api_url: 'https://example.gitlab.com'
    api_token: 'Your-Private-Token'
    project: projectname
    state: present
    link_url: 'https://example.gitlab.com/%{project_path}'
    image_url: 'https://example.gitlab.com/%{project_path}/badges/%{default_branch}/pipeline.svg'

- name: Remove a badge from a GitLab Project
  community.general.gitlab_project_badge:
    api_url: 'https://example.gitlab.com'
    api_token: 'Your-Private-Token'
    project: projectname
    state: absent
    link_url: 'https://example.gitlab.com/%{project_path}'
    image_url: 'https://example.gitlab.com/%{project_path}/badges/%{default_branch}/pipeline.svg'
"""

RETURN = r"""
badge:
  description: The badge information.
  returned: when O(state=present)
  type: dict
  sample:
    id: 1
    link_url: 'http://example.com/ci_status.svg?project=%{project_path}&ref=%{default_branch}'
    image_url: 'https://shields.io/my/badge'
    rendered_link_url: 'http://example.com/ci_status.svg?project=example-org/example-project&ref=master'
    rendered_image_url: 'https://shields.io/my/badge'
    kind: project
"""

from ansible.module_utils.api import basic_auth_argument_spec
from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.general.plugins.module_utils.gitlab import (
    auth_argument_spec, gitlab_authentication, find_project, list_all_kwargs
)


def present_strategy(module, gl, project, wished_badge):
    changed = False

    existing_badge = None
    for badge in project.badges.list(**list_all_kwargs):
        if badge.image_url == wished_badge["image_url"]:
            existing_badge = badge
            break

    if not existing_badge:
        changed = True
        if module.check_mode:
            return changed, {"status": "A project badge would be created."}

        badge = project.badges.create(wished_badge)
        return changed, badge.attributes

    if existing_badge.link_url != wished_badge["link_url"]:
        changed = True
        existing_badge.link_url = wished_badge["link_url"]

    if changed:
        if module.check_mode:
            return changed, {"status": "Project badge attributes would be changed."}

        existing_badge.save()

    return changed, existing_badge.attributes


def absent_strategy(module, gl, project, wished_badge):
    changed = False

    existing_badge = None
    for badge in project.badges.list(**list_all_kwargs):
        if badge.image_url == wished_badge["image_url"]:
            existing_badge = badge
            break

    if not existing_badge:
        return changed, None

    changed = True
    if module.check_mode:
        return changed, {"status": "Project badge would be destroyed."}

    existing_badge.delete()

    return changed, None


state_strategy = {
    "present": present_strategy,
    "absent": absent_strategy
}


def core(module):
    # check prerequisites and connect to gitlab server
    gl = gitlab_authentication(module)

    gitlab_project = module.params['project']
    state = module.params['state']

    project = find_project(gl, gitlab_project)
    # project doesn't exist
    if not project:
        module.fail_json(msg="project '%s' not found." % gitlab_project)

    wished_badge = {
        "link_url": module.params["link_url"],
        "image_url": module.params["image_url"],
    }

    changed, summary = state_strategy[state](module=module, gl=gl, project=project, wished_badge=wished_badge)

    module.exit_json(changed=changed, badge=summary)


def main():
    argument_spec = basic_auth_argument_spec()
    argument_spec.update(auth_argument_spec())
    argument_spec.update(dict(
        project=dict(type='str', required=True),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        link_url=dict(type='str', required=True),
        image_url=dict(type='str', required=True),
    ))

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[
            ['api_username', 'api_token'],
            ['api_username', 'api_oauth_token'],
            ['api_username', 'api_job_token'],
            ['api_token', 'api_oauth_token'],
            ['api_token', 'api_job_token'],
        ],
        required_together=[
            ['api_username', 'api_password'],
        ],
        required_one_of=[
            ['api_username', 'api_token', 'api_oauth_token', 'api_job_token'],
        ],
        supports_check_mode=True,
    )

    core(module)


if __name__ == '__main__':
    main()
