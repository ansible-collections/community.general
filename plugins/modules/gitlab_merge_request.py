#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2021, Lennert Mertens (lennert@nubera.be)
# Copyright (c) 2021, Werner Dijkerman (ikben@werner-dijkerman.nl)
# Copyright (c) 2015, Werner Dijkerman (ikben@werner-dijkerman.nl)
# Copyright (c) 2019, Guillaume Martinez (lunik@tiwabbit.fr)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
module: gitlab_merge_request
short_description: Create, update or delete a merge requests.
version_added: 4.2.0
description:
  - This module allows to create, update or merge requests.
author:
  - paytroff (@paytroff)
requirements:
  - python >= 2.7
  - python-gitlab >= 2.3.0
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
  state:
    description:
      - Create or delete merge request.
    default: present
    type: str
    choices: ["present", "absent"]
  project:
    description:
      - The path or name of the project.
    required: true
    type: str
  source_branch:
    description:
      - Merge request's source branch.
      - Ignored while updating existing merge request.
    required: true
    type: str
  target_branch:
    description:
      - Merge request's target branch.
    required: true
    type: str
  title:
    description:
      - A title for the merge request.
    type: str
    required: true
  description:
    description:
      - A description for the merge request.
      - Gets overriden by a content of file specified at description_path, if found.
    type: str
  description_path:
    description:
      - A path of file containing merge request's description.
      - Accepts markdown formatted files.
    type: str
  labels:
    description:
      - Comma separated list of label names.
    type: str
    default: ""
  remove_source_branch:
    description:
      - Flag indicating if a merge request should remove the source branch when merging.
    type: bool
    default: false
  state_filter:
    description:
      - Filter specifying state of merge requests while searching.
      - If empty string, merge requests of all states are searched.
      - Possible values are "opened", "closed", "locked", "merged" or empty string.
    type: str
    choices: ["opened", "closed", "locked", "merged"]
    default: opened
  assignee_ids:
    description:
      - Comma separated list of assignees usernames omitting "@" character.
      - Set to empty string to unassign all assignees.
    type: str
  reviewer_ids:
    description:
      - Comma separated list of reviewers usernames omitting "@" character.
      - Set to empty string to unassign all reviewers.
    type: str
'''


EXAMPLES = '''
- name: Create branch branch2 from main
  community.general.gitlab_merge_request:
    api_url: https://gitlab.com
    api_token: secret_access_token
    project: "group1/project1"
    branch: branch2
    ref_branch: main
    state: present

- name: Delete branch branch2
  community.general.gitlab_merge_request:
    api_url: https://gitlab.com
    api_token: secret_access_token
    project: "group1/project1"
    branch: branch2
    state: absent

'''

RETURN = '''
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.api import basic_auth_argument_spec
from ansible.module_utils.common.text.converters import to_native, to_text

from ansible_collections.community.general.plugins.module_utils.version import LooseVersion
from ansible_collections.community.general.plugins.module_utils.gitlab import (
    auth_argument_spec, gitlab_authentication, gitlab, ensure_gitlab_package
)


class GitlabMergeRequest(object):

    def __init__(self, module, project, gitlab_instance):
        self.repo = gitlab_instance
        self._module = module
        self.project = self.get_project(project)

    '''
    @param project Name of the project
    '''
    def get_project(self, project):
        try:
            return self.repo.projects.get(project)
        except gitlab.exceptions.GitlabGetError as e:
            self._module.fail_json(msg="Failed to get the project: %s" % to_native(e))

    '''
    @param branch Name of the branch
    '''
    def get_branch(self, branch):
        try:
            return self.project.branches.get(branch)
        except gitlab.exceptions.GitlabGetError as e:
            self._module.fail_json(msg="Failed to get the branch: %s" % to_native(e))

    '''
    @param title Title of the Merge Request
    @param source_branch Merge Request's source branch
    @param target_branch Merge Request's target branch
    @param state_filter Merge Request's state to filter on
    '''
    def get_mr(self, title, source_branch, target_branch, state_filter):
        mrs = []
        try:
            mrs = self.project.mergerequests.list(search=title, source_branch=source_branch, target_branch=target_branch, state=state_filter)
        except gitlab.exceptions.GitlabGetError as e:
            self._module.fail_json(msg="Failed to list the Merge Request: %s" % to_native(e))

        if len(mrs) > 1:
            self._module.fail_json(msg="Multiple Merge Requests matched search criteria.")
        if len(mrs) == 1:
            try:
                return self.project.mergerequests.get(id=mrs[0].iid)
            except gitlab.exceptions.GitlabGetError as e:
                self._module.fail_json(msg="Failed to get the Merge Request: %s" % to_native(e))

    def get_user(self, username):
        try:
            users = self.project.users.list(search=username, all=True)
        except gitlab.exceptions.GitlabGetError as e:
            self._module.fail_json(msg="Failed to list the users: %s" % to_native(e))

        for user in users:
            if (user.username == username):
                return user

    def get_user_ids(self, users):
        return [self.get_user(user).id for user in users]

    '''
    @param options Options of the Merge Request
    '''
    def create_mr(self, options):
        if self._module.check_mode:
            self._module.exit_json(changed=True, msg="Successfully created the Merge Request %s" % options["title"])

        try:
            return self.project.mergerequests.create(options)
        except gitlab.exceptions.GitlabCreateError as e:
            self._module.fail_json(msg="Failed to create Merge Request: %s " % to_native(e))

    '''
    @param mr Merge Request object to delete
    '''
    def delete_mr(self, mr):
        if self._module.check_mode:
            self._module.exit_json(changed=True, msg="Successfully deleted the Merge Request %s" % mr["title"])

        try:
            mr.delete()
        except gitlab.exceptions.GitlabDeleteError as e:
            self._module.fail_json(msg="Failed to delete Merge Request: %s " % to_native(e))

    '''
    @param mr Merge Request object to update
    '''
    def update_mr(self, mr, options):
        if self._module.check_mode:
            self._module.exit_json(changed=True, msg="Successfully updated the Merge Request %s" % mr["title"])

        try:
            return self.project.mergerequests.update(mr.iid, options)
        except gitlab.exceptions.GitlabUpdateError as e:
            self._module.fail_json(msg="Failed to update Merge Request: %s " % to_native(e))

    def mr_has_changed(self, mr, options):
        for key, value in options.items():
            if value is not None:
                # see https://gitlab.com/gitlab-org/gitlab-foss/-/issues/27355
                if key == 'remove_source_branch':
                    key = 'force_remove_source_branch'

                if key == 'assignee_ids':
                    if options[key] != sorted([user["id"] for user in getattr(mr, 'assignees')]):
                        return True

                elif key == 'reviewer_ids':
                    if options[key] != sorted([user["id"] for user in getattr(mr, 'reviewers')]):
                        return True

                elif key == 'labels':
                    if options[key] != sorted(getattr(mr, key)):
                        return True

                elif getattr(mr, key) != value:
                    return True

        return False


def main():
    argument_spec = basic_auth_argument_spec()
    argument_spec.update(auth_argument_spec())
    argument_spec.update(
        project=dict(type='str', required=True),
        source_branch=dict(type='str', required=True),
        target_branch=dict(type='str', required=True),
        title=dict(type='str', required=True),
        description=dict(type='str', required=False),
        labels=dict(type='str', default="", required=False),
        description_path=dict(type='str', required=False),
        remove_source_branch=dict(type='bool', default=False, required=False),
        state_filter=dict(type='str', default="opened", choices=["opened", "closed", "locked", "merged"]),
        assignee_ids=dict(type='str', required=False),
        reviewer_ids=dict(type='str', required=False),
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
            ['description', 'description_path'],
        ],
        required_together=[
            ['api_username', 'api_password'],
        ],
        required_one_of=[
            ['api_username', 'api_token', 'api_oauth_token', 'api_job_token']
        ],
        required_if=[
            ['state', 'present', ['source_branch', 'target_branch', 'title'], True],
            ['state', 'absent', ['source_branch', 'target_branch', 'title'], True],
        ],
        supports_check_mode=True
    )
    ensure_gitlab_package(module)

    project = module.params['project']
    source_branch = module.params['source_branch']
    target_branch = module.params['target_branch']
    title = module.params['title']
    description = module.params['description']
    labels = module.params['labels']
    description_path = module.params['description_path']
    remove_source_branch = module.params['remove_source_branch']
    state_filter = module.params['state_filter']
    assignee_ids = module.params['assignee_ids']
    reviewer_ids = module.params['reviewer_ids']
    state = module.params['state']

    gitlab_version = gitlab.__version__
    if LooseVersion(gitlab_version) < LooseVersion('2.3.0'):
        module.fail_json(msg="community.general.gitlab_proteched_branch requires python-gitlab Python module >= 2.3.0 (installed version: [%s])."
                             " Please upgrade python-gitlab to version 2.3.0 or above." % gitlab_version)

    gitlab_instance = gitlab_authentication(module)
    this_gitlab = GitlabMergeRequest(module=module, project=project, gitlab_instance=gitlab_instance)

    r_source_branch = this_gitlab.get_branch(source_branch)
    if not r_source_branch:
        module.fail_json(msg="Source branch {b} not exist.".format(b=r_source_branch))

    r_target_branch = this_gitlab.get_branch(target_branch)
    if not r_target_branch:
        module.fail_json(msg="Destination branch {b} not exist.".format(b=r_target_branch))

    r_target_branch = this_gitlab.get_branch(target_branch)
    if not r_target_branch:
        module.fail_json(msg="Destination branch {b} not exist.".format(b=r_target_branch))

    this_mr = this_gitlab.get_mr(title, source_branch, target_branch, state_filter)

    if state == "present":
        if description_path:
            try:
                f = open(description_path, 'rb')
                description = to_text(f.read(), errors='surrogate_or_strict')
                f.close()
            except IOError as e:
                module.fail_json(msg='Cannot open {0}: {1}'.format(description_path, e))

        assignee_ids = sorted(this_gitlab.get_user_ids(assignee_ids.split(","))) if assignee_ids else []
        reviewer_ids = sorted(this_gitlab.get_user_ids(reviewer_ids.split(","))) if reviewer_ids else []
        labels = sorted(labels.split(",")) if labels else []

        options = {
            "target_branch": target_branch,
            "title": title,
            "description": description,
            "labels": labels,
            "remove_source_branch": remove_source_branch,
            "reviewer_ids": reviewer_ids,
            "assignee_ids": assignee_ids,
        }

        if not this_mr:
            options["source_branch"] = source_branch

            this_gitlab.create_mr(options)
            module.exit_json(changed=True, msg="Created the Merge Request {t} from branch {d} to branch {s}.".format(t=title, d=target_branch, s=source_branch))
        else:
            if this_gitlab.mr_has_changed(this_mr, options):
                mr = this_gitlab.update_mr(this_mr, options)
                module.exit_json(
                    changed=True, msg="Merge Request {t} from branch {d} to branch {s} updated.".format(t=title, d=target_branch, s=source_branch),
                    mr=mr
                )
            else:
                module.exit_json(
                    changed=False, msg="Merge Request {t} from branch {d} to branch {s} already exist".format(t=title, d=target_branch, s=source_branch),
                    mr=this_mr.asdict()
                )
    elif this_mr and state == "absent":
        this_gitlab.delete_mr(this_mr)
        module.exit_json(changed=True, msg="Merge Request {t} from branch {d} to branch {s} deleted.".format(t=title, d=target_branch, s=source_branch))
    else:
        module.exit_json(changed=False, msg="No changes are needed.", mr=this_mr.asdict())


if __name__ == '__main__':
    main()
