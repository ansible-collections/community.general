#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2023, Ondrej Zvara (ozvara1@gmail.com)
# Based on code:
# Copyright (c) 2021, Lennert Mertens (lennert@nubera.be)
# Copyright (c) 2021, Werner Dijkerman (ikben@werner-dijkerman.nl)
# Copyright (c) 2015, Werner Dijkerman (ikben@werner-dijkerman.nl)
# Copyright (c) 2019, Guillaume Martinez (lunik@tiwabbit.fr)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
module: gitlab_issue
short_description: Create, update, or delete GitLab issues
version_added: '8.1.0'
description:
  - Creates an issue if it does not exist.
  - When an issue does exist, it will be updated if the provided parameters are different.
  - When an issue does exist and O(state=absent), the issue will be deleted.
  - When multiple issues are detected, the task fails.
  - Existing issues are matched based on O(title) and O(state_filter) filters.
author:
  - zvaraondrej (@zvaraondrej)
requirements:
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
  assignee_ids:
    description:
      - A list of assignee usernames omitting V(@) character.
      - Set to an empty array to unassign all assignees.
    type: list
    elements: str
  description:
    description:
      - A description of the issue.
      - Gets overridden by a content of file specified at O(description_path), if found.
    type: str
  description_path:
    description:
      - A path of file containing issue's description.
      - Accepts MarkDown formatted files.
    type: path
  issue_type:
    description:
      - Type of the issue.
    default: issue
    type: str
    choices: ["issue", "incident", "test_case"]
  labels:
    description:
      - A list of label names.
      - Set to an empty array to remove all labels.
    type: list
    elements: str
  milestone_search:
    description:
      - The name of the milestone.
      - Set to empty string to unassign milestone.
    type: str
  milestone_group_id:
    description:
      - The path or numeric ID of the group hosting desired milestone.
    type: str
  project:
    description:
      - The path or name of the project.
    required: true
    type: str
  state:
    description:
      - Create or delete issue.
    default: present
    type: str
    choices: ["present", "absent"]
  state_filter:
    description:
      - Filter specifying state of issues while searching.
    type: str
    choices: ["opened", "closed"]
    default: opened
  title:
    description:
      - A title for the issue. The title is used as a unique identifier to ensure idempotency.
    type: str
    required: true
'''


EXAMPLES = '''
- name: Create Issue
  community.general.gitlab_issue:
    api_url: https://gitlab.com
    api_token: secret_access_token
    project: "group1/project1"
    title: "Ansible demo Issue"
    description: "Demo Issue description"
    labels:
        - Ansible
        - Demo
    assignee_ids:
        - testassignee
    state_filter: "opened"
    state: present

- name: Delete Issue
  community.general.gitlab_issue:
    api_url: https://gitlab.com
    api_token: secret_access_token
    project: "group1/project1"
    title: "Ansible demo Issue"
    state_filter: "opened"
    state: absent
'''

RETURN = r'''
msg:
  description: Success or failure message.
  returned: always
  type: str
  sample: "Success"

issue:
  description: API object.
  returned: success
  type: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.api import basic_auth_argument_spec
from ansible.module_utils.common.text.converters import to_native, to_text

from ansible_collections.community.general.plugins.module_utils.gitlab import (
    auth_argument_spec, gitlab_authentication, gitlab, find_project, find_group
)


class GitlabIssue(object):

    def __init__(self, module, project, gitlab_instance):
        self._gitlab = gitlab_instance
        self._module = module
        self.project = project

    '''
    @param milestone_id Title of the milestone
    '''
    def get_milestone(self, milestone_id, group):
        milestones = []
        try:
            milestones = group.milestones.list(search=milestone_id)
        except gitlab.exceptions.GitlabGetError as e:
            self._module.fail_json(msg="Failed to list the Milestones: %s" % to_native(e))

        if len(milestones) > 1:
            self._module.fail_json(msg="Multiple Milestones matched search criteria.")
        if len(milestones) < 1:
            self._module.fail_json(msg="No Milestones matched search criteria.")
        if len(milestones) == 1:
            try:
                return group.milestones.get(id=milestones[0].id)
            except gitlab.exceptions.GitlabGetError as e:
                self._module.fail_json(msg="Failed to get the Milestones: %s" % to_native(e))

    '''
    @param title Title of the Issue
    @param state_filter Issue's state to filter on
    '''
    def get_issue(self, title, state_filter):
        issues = []
        try:
            issues = self.project.issues.list(query_parameters={"search": title, "in": "title", "state": state_filter})
        except gitlab.exceptions.GitlabGetError as e:
            self._module.fail_json(msg="Failed to list the Issues: %s" % to_native(e))

        if len(issues) > 1:
            self._module.fail_json(msg="Multiple Issues matched search criteria.")
        if len(issues) == 1:
            try:
                return self.project.issues.get(id=issues[0].iid)
            except gitlab.exceptions.GitlabGetError as e:
                self._module.fail_json(msg="Failed to get the Issue: %s" % to_native(e))

    '''
    @param username Name of the user
    '''
    def get_user(self, username):
        users = []
        try:
            users = [user for user in self.project.users.list(username=username, all=True) if user.username == username]
        except gitlab.exceptions.GitlabGetError as e:
            self._module.fail_json(msg="Failed to list the users: %s" % to_native(e))

        if len(users) > 1:
            self._module.fail_json(msg="Multiple Users matched search criteria.")
        elif len(users) < 1:
            self._module.fail_json(msg="No User matched search criteria.")
        else:
            return users[0]

    '''
    @param users List of usernames
    '''
    def get_user_ids(self, users):
        return [self.get_user(user).id for user in users]

    '''
    @param options Options of the Issue
    '''
    def create_issue(self, options):
        if self._module.check_mode:
            self._module.exit_json(changed=True, msg="Successfully created Issue '%s'." % options["title"])

        try:
            return self.project.issues.create(options)
        except gitlab.exceptions.GitlabCreateError as e:
            self._module.fail_json(msg="Failed to create Issue: %s " % to_native(e))

    '''
    @param issue Issue object to delete
    '''
    def delete_issue(self, issue):
        if self._module.check_mode:
            self._module.exit_json(changed=True, msg="Successfully deleted Issue '%s'." % issue["title"])

        try:
            return issue.delete()
        except gitlab.exceptions.GitlabDeleteError as e:
            self._module.fail_json(msg="Failed to delete Issue: '%s'." % to_native(e))

    '''
    @param issue Issue object to update
    @param options Options of the Issue
    '''
    def update_issue(self, issue, options):
        if self._module.check_mode:
            self._module.exit_json(changed=True, msg="Successfully updated Issue '%s'." % issue["title"])

        try:
            return self.project.issues.update(issue.iid, options)
        except gitlab.exceptions.GitlabUpdateError as e:
            self._module.fail_json(msg="Failed to update Issue %s." % to_native(e))

    '''
    @param issue Issue object to evaluate
    @param options New options to update Issue with
    '''
    def issue_has_changed(self, issue, options):
        for key, value in options.items():
            if value is not None:

                if key == 'milestone_id':
                    old_milestone = getattr(issue, 'milestone')['id'] if getattr(issue, 'milestone') else ""
                    if options[key] != old_milestone:
                        return True
                elif key == 'assignee_ids':
                    if options[key] != sorted([user["id"] for user in getattr(issue, 'assignees')]):
                        return True

                elif key == 'labels':
                    if options[key] != sorted(getattr(issue, key)):
                        return True

                elif getattr(issue, key) != value:
                    return True

        return False


def main():
    argument_spec = basic_auth_argument_spec()
    argument_spec.update(auth_argument_spec())
    argument_spec.update(
        assignee_ids=dict(type='list', elements='str', required=False),
        description=dict(type='str', required=False),
        description_path=dict(type='path', required=False),
        issue_type=dict(type='str', default='issue', choices=["issue", "incident", "test_case"], required=False),
        labels=dict(type='list', elements='str', required=False),
        milestone_search=dict(type='str', required=False),
        milestone_group_id=dict(type='str', required=False),
        project=dict(type='str', required=True),
        state=dict(type='str', default="present", choices=["absent", "present"]),
        state_filter=dict(type='str', default="opened", choices=["opened", "closed"]),
        title=dict(type='str', required=True),
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
            ['milestone_search', 'milestone_group_id'],
        ],
        required_one_of=[
            ['api_username', 'api_token', 'api_oauth_token', 'api_job_token']
        ],
        supports_check_mode=True
    )

    assignee_ids = module.params['assignee_ids']
    description = module.params['description']
    description_path = module.params['description_path']
    issue_type = module.params['issue_type']
    labels = module.params['labels']
    milestone_id = module.params['milestone_search']
    milestone_group_id = module.params['milestone_group_id']
    project = module.params['project']
    state = module.params['state']
    state_filter = module.params['state_filter']
    title = module.params['title']

    # check prerequisites and connect to gitlab server
    gitlab_instance = gitlab_authentication(module, min_version='2.3.0')

    this_project = find_project(gitlab_instance, project)
    if this_project is None:
        module.fail_json(msg="Failed to get the project: %s" % project)

    this_gitlab = GitlabIssue(module=module, project=this_project, gitlab_instance=gitlab_instance)

    if milestone_id and milestone_group_id:
        this_group = find_group(gitlab_instance, milestone_group_id)
        if this_group is None:
            module.fail_json(msg="Failed to get the group: %s" % milestone_group_id)

        milestone_id = this_gitlab.get_milestone(milestone_id, this_group).id

    this_issue = this_gitlab.get_issue(title, state_filter)

    if state == "present":
        if description_path:
            try:
                with open(description_path, 'rb') as f:
                    description = to_text(f.read(), errors='surrogate_or_strict')
            except IOError as e:
                module.fail_json(msg='Cannot open {0}: {1}'.format(description_path, e))

        # sorting necessary in order to properly detect changes, as we don't want to get false positive
        # results due to differences in ids ordering;
        assignee_ids = sorted(this_gitlab.get_user_ids(assignee_ids)) if assignee_ids else assignee_ids
        labels = sorted(labels) if labels else labels

        options = {
            "title": title,
            "description": description,
            "labels": labels,
            "issue_type": issue_type,
            "milestone_id": milestone_id,
            "assignee_ids": assignee_ids,
        }

        if not this_issue:
            issue = this_gitlab.create_issue(options)
            module.exit_json(
                changed=True, msg="Created Issue '{t}'.".format(t=title),
                issue=issue.asdict()
            )
        else:
            if this_gitlab.issue_has_changed(this_issue, options):
                issue = this_gitlab.update_issue(this_issue, options)
                module.exit_json(
                    changed=True, msg="Updated Issue '{t}'.".format(t=title),
                    issue=issue
                )
            else:
                module.exit_json(
                    changed=False, msg="Issue '{t}' already exists".format(t=title),
                    issue=this_issue.asdict()
                )
    elif state == "absent":
        if not this_issue:
            module.exit_json(changed=False, msg="Issue '{t}' does not exist or has already been deleted.".format(t=title))
        else:
            issue = this_gitlab.delete_issue(this_issue)
            module.exit_json(
                changed=True, msg="Issue '{t}' deleted.".format(t=title),
                issue=issue
            )


if __name__ == '__main__':
    main()
