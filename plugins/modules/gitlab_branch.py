#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2021, Werner Dijkerman (ikben@werner-dijkerman.nl)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: gitlab_branch
short_description: Create or delete a branch
version_added: 4.2.0
description:
  - This module allows to create or delete branches.
author:
  - paytroff (@paytroff)
requirements:
  - python-gitlab >= 2.3.0
extends_documentation_fragment:
  - community.general.auth_basic
  - community.general.gitlab
  - community.general.attributes

attributes:
  check_mode:
    support: none
  diff_mode:
    support: none

options:
  state:
    description:
      - Create or delete branch.
    default: present
    type: str
    choices: ["present", "absent"]
  project:
    description:
      - The path or name of the project.
    required: true
    type: str
  branch:
    description:
      - The name of the branch that needs to be created.
    required: true
    type: str
  ref_branch:
    description:
      - Reference branch to create from.
      - This must be specified if O(state=present).
    type: str
"""


EXAMPLES = r"""
- name: Create branch branch2 from main
  community.general.gitlab_branch:
    api_url: https://gitlab.com
    api_token: secret_access_token
    project: "group1/project1"
    branch: branch2
    ref_branch: main
    state: present

- name: Delete branch branch2
  community.general.gitlab_branch:
    api_url: https://gitlab.com
    api_token: secret_access_token
    project: "group1/project1"
    branch: branch2
    state: absent
"""

RETURN = r"""
"""

import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.api import basic_auth_argument_spec

from ansible_collections.community.general.plugins.module_utils.version import LooseVersion
from ansible_collections.community.general.plugins.module_utils.gitlab import (
    auth_argument_spec, gitlab_authentication, gitlab
)


class GitlabBranch(object):

    def __init__(self, module, project, gitlab_instance):
        self.repo = gitlab_instance
        self._module = module
        self.project = self.get_project(project)

    def get_project(self, project):
        try:
            return self.repo.projects.get(project)
        except Exception as e:
            return False

    def get_branch(self, branch):
        try:
            return self.project.branches.get(branch)
        except Exception as e:
            return False

    def create_branch(self, branch, ref_branch):
        return self.project.branches.create({'branch': branch, 'ref': ref_branch})

    def delete_branch(self, branch):
        return branch.delete()


def main():
    argument_spec = basic_auth_argument_spec()
    argument_spec.update(auth_argument_spec())
    argument_spec.update(
        project=dict(type='str', required=True),
        branch=dict(type='str', required=True),
        ref_branch=dict(type='str'),
        state=dict(type='str', default="present", choices=["absent", "present"]),
    )

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
            ['api_username', 'api_token', 'api_oauth_token', 'api_job_token']
        ],
        required_if=[
            ['state', 'present', ['ref_branch'], True],
        ],
        supports_check_mode=False
    )

    # check prerequisites and connect to gitlab server
    gitlab_instance = gitlab_authentication(module)

    project = module.params['project']
    branch = module.params['branch']
    ref_branch = module.params['ref_branch']
    state = module.params['state']

    gitlab_version = gitlab.__version__
    if LooseVersion(gitlab_version) < LooseVersion('2.3.0'):
        module.fail_json(msg="community.general.gitlab_proteched_branch requires python-gitlab Python module >= 2.3.0 (installed version: [%s])."
                             " Please upgrade python-gitlab to version 2.3.0 or above." % gitlab_version)

    this_gitlab = GitlabBranch(module=module, project=project, gitlab_instance=gitlab_instance)

    this_branch = this_gitlab.get_branch(branch)

    if not this_branch and state == "present":
        r_branch = this_gitlab.get_branch(ref_branch)
        if not r_branch:
            module.fail_json(msg="Ref branch {b} not exist.".format(b=ref_branch))
        this_gitlab.create_branch(branch, ref_branch)
        module.exit_json(changed=True, msg="Created the branch {b}.".format(b=branch))
    elif this_branch and state == "present":
        module.exit_json(changed=False, msg="Branch {b} already exist".format(b=branch))
    elif this_branch and state == "absent":
        try:
            this_gitlab.delete_branch(this_branch)
            module.exit_json(changed=True, msg="Branch {b} deleted.".format(b=branch))
        except Exception as e:
            module.fail_json(msg="Error delete branch.", exception=traceback.format_exc())
    else:
        module.exit_json(changed=False, msg="No changes are needed.")


if __name__ == '__main__':
    main()
