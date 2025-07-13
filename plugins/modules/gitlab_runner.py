#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2021, Raphaël Droz (raphael.droz@gmail.com)
# Copyright (c) 2019, Guillaume Martinez (lunik@tiwabbit.fr)
# Copyright (c) 2018, Samy Coenen <samy.coenen@nubera.be>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: gitlab_runner
short_description: Create, modify and delete GitLab Runners
description:
  - Register, update and delete runners on GitLab Server side with the GitLab API.
  - All operations are performed using the GitLab API v4.
  - For details, consult the full API documentation at U(https://docs.gitlab.com/ee/api/runners.html) and
    U(https://docs.gitlab.com/ee/api/users.html#create-a-runner-linked-to-a-user).
  - A valid private API token is required for all operations. You can create as many tokens as you like using the GitLab web
    interface at U(https://$GITLAB_URL/profile/personal_access_tokens).
  - A valid registration token is required for registering a new runner. To create shared runners, you need to ask your administrator
    to give you this token. It can be found at U(https://$GITLAB_URL/admin/runners/).
  - This module does not handle the C(gitlab-runner) process part, but only manages the runner on GitLab Server side through
    its API. Once the module has created the runner, you may use the generated token to run C(gitlab-runner register) command.
notes:
  - To create a new runner at least the O(api_token), O(description) and O(api_url) options are required.
  - Runners need to have unique descriptions, since this attribute is used as key for idempotency.
author:
  - Samy Coenen (@SamyCoenen)
  - Guillaume Martinez (@Lunik)
requirements:
  - python-gitlab >= 1.5.0 for legacy runner registration workflow (runner registration token -
    U(https://docs.gitlab.com/runner/register/#register-with-a-runner-registration-token-deprecated))
  - python-gitlab >= 4.0.0 for new runner registration workflow (runner authentication token -
    U(https://docs.gitlab.com/runner/register/#register-with-a-runner-authentication-token))
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
  group:
    description:
      - ID or full path of the group in the form group/subgroup.
      - Mutually exclusive with O(owned) and O(project).
      - Must be group's numeric ID if O(registration_token) is not set and O(state=present).
    type: str
    version_added: '6.5.0'
  project:
    description:
      - ID or full path of the project in the form of group/name.
      - Mutually exclusive with O(owned) since community.general 4.5.0.
      - Mutually exclusive with O(group).
      - Must be project's numeric ID if O(registration_token) is not set and O(state=present).
    type: str
    version_added: '3.7.0'
  description:
    description:
      - The unique name of the runner.
    required: true
    type: str
    aliases:
      - name
  state:
    description:
      - Make sure that the runner with the same name exists with the same configuration or delete the runner with the same
        name.
    required: false
    default: present
    choices: ["present", "absent"]
    type: str
  registration_token:
    description:
      - The registration token is used to register new runners before GitLab 16.0.
      - Required if O(state=present) for GitLab < 16.0.
      - If set, the runner is created using the old runner creation workflow.
      - If not set, the runner is created using the new runner creation workflow, introduced in GitLab 16.0.
      - If not set, requires python-gitlab >= 4.0.0.
    type: str
  owned:
    description:
      - Searches only runners available to the user when searching for existing, when false admin token required.
      - Mutually exclusive with O(project) since community.general 4.5.0.
      - Mutually exclusive with O(group).
    default: false
    type: bool
    version_added: 2.0.0
  active:
    description:
      - Define if the runners is immediately active after creation.
      - Mutually exclusive with O(paused).
    required: false
    default: true
    type: bool
  paused:
    description:
      - Define if the runners is active or paused after creation.
      - Mutually exclusive with O(active).
    required: false
    default: false
    type: bool
    version_added: 8.1.0
  locked:
    description:
      - Determines if the runner is locked or not.
    required: false
    default: false
    type: bool
  access_level:
    description:
      - Determines if a runner can pick up jobs only from protected branches.
      - If O(access_level_on_creation) is not explicitly set to V(true), this option is ignored on registration and is only
        applied on updates.
      - If set to V(not_protected), runner can pick up jobs from both protected and unprotected branches.
      - If set to V(ref_protected), runner can pick up jobs only from protected branches.
      - Before community.general 8.0.0 the default was V(ref_protected). This was changed to no default in community.general
        8.0.0. If this option is not specified explicitly, GitLab uses V(not_protected) on creation, and the value set is
        not changed on any updates.
    required: false
    choices: ["not_protected", "ref_protected"]
    type: str
  access_level_on_creation:
    description:
      - Whether the runner should be registered with an access level or not.
      - If set to V(true), the value of O(access_level) is used for runner registration.
      - If set to V(false), GitLab registers the runner with the default access level.
      - The default of this option changed to V(true) in community.general 7.0.0. Before, it was V(false).
    required: false
    default: true
    type: bool
    version_added: 6.3.0
  maximum_timeout:
    description:
      - The maximum time that a runner has to complete a specific job.
    required: false
    default: 3600
    type: int
  run_untagged:
    description:
      - Run untagged jobs or not.
    required: false
    default: true
    type: bool
  tag_list:
    description: The tags that apply to the runner.
    required: false
    default: []
    type: list
    elements: str
"""

EXAMPLES = r"""
- name: Create an instance-level runner
  community.general.gitlab_runner:
    api_url: https://gitlab.example.com/
    api_token: "{{ access_token }}"
    description: Docker Machine t1
    state: present
    active: true
    tag_list: ['docker']
    run_untagged: false
    locked: false
  register: runner # Register module output to run C(gitlab-runner register) command in another task

- name: Create a group-level runner
  community.general.gitlab_runner:
    api_url: https://gitlab.example.com/
    api_token: "{{ access_token }}"
    description: Docker Machine t1
    state: present
    active: true
    tag_list: ['docker']
    run_untagged: false
    locked: false
    group: top-level-group/subgroup
  register: runner # Register module output to run C(gitlab-runner register) command in another task

- name: Create a project-level runner
  community.general.gitlab_runner:
    api_url: https://gitlab.example.com/
    api_token: "{{ access_token }}"
    description: Docker Machine t1
    state: present
    active: true
    tag_list: ['docker']
    run_untagged: false
    locked: false
    project: top-level-group/subgroup/project
  register: runner # Register module output to run C(gitlab-runner register) command in another task

- name: "Register instance-level runner with registration token (deprecated)"
  community.general.gitlab_runner:
    api_url: https://gitlab.example.com/
    api_token: "{{ access_token }}"
    registration_token: 4gfdsg345
    description: Docker Machine t1
    state: present
    active: true
    tag_list: ['docker']
    run_untagged: false
    locked: false
  register: runner # Register module output to run C(gitlab-runner register) command in another task

- name: "Delete runner"
  community.general.gitlab_runner:
    api_url: https://gitlab.example.com/
    api_token: "{{ access_token }}"
    description: Docker Machine t1
    state: absent

- name: Delete an owned runner as a non-admin
  community.general.gitlab_runner:
    api_url: https://gitlab.example.com/
    api_token: "{{ access_token }}"
    description: Docker Machine t1
    owned: true
    state: absent

- name: "Register a project-level runner with registration token (deprecated)"
  community.general.gitlab_runner:
    api_url: https://gitlab.example.com/
    api_token: "{{ access_token }}"
    registration_token: 4gfdsg345
    description: MyProject runner
    state: present
    project: mygroup/mysubgroup/myproject
  register: runner # Register module output to run C(gitlab-runner register) command in another task
"""

RETURN = r"""
msg:
  description: Success or failure message.
  returned: always
  type: str
  sample: "Success"

result:
  description: JSON-parsed response from the server.
  returned: always
  type: dict

error:
  description: The error message returned by the GitLab API.
  returned: failed
  type: str
  sample: "400: path is already in use"

runner:
  description: API object.
  returned: always
  type: dict
"""

from ansible.module_utils.api import basic_auth_argument_spec
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native

from ansible_collections.community.general.plugins.module_utils.gitlab import (
    auth_argument_spec, gitlab_authentication, gitlab, list_all_kwargs
)


from ansible_collections.community.general.plugins.module_utils.version import LooseVersion


class GitLabRunner(object):
    def __init__(self, module, gitlab_instance, group=None, project=None):
        self._module = module
        self._gitlab = gitlab_instance
        self.runner_object = None

        # Whether to operate on GitLab-instance-wide or project-wide runners
        # See https://gitlab.com/gitlab-org/gitlab-ce/issues/60774
        # for group runner token access
        if project:
            self._runners_endpoint = project.runners.list
        elif group:
            self._runners_endpoint = group.runners.list
        elif module.params['owned']:
            self._runners_endpoint = gitlab_instance.runners.list
        else:
            self._runners_endpoint = gitlab_instance.runners.all

    def create_or_update_runner(self, description, options):
        changed = False

        arguments = {
            'locked': options['locked'],
            'run_untagged': options['run_untagged'],
            'maximum_timeout': options['maximum_timeout'],
            'tag_list': options['tag_list'],
        }

        if options.get('paused') is not None:
            arguments['paused'] = options['paused']
        else:
            arguments['active'] = options['active']

        if options.get('access_level') is not None:
            arguments['access_level'] = options['access_level']
        # Because we have already call userExists in main()
        if self.runner_object is None:
            arguments['description'] = description
            if options.get('registration_token') is not None:
                arguments['token'] = options['registration_token']
            elif options.get('group') is not None:
                arguments['runner_type'] = 'group_type'
                arguments['group_id'] = options['group']
            elif options.get('project') is not None:
                arguments['runner_type'] = 'project_type'
                arguments['project_id'] = options['project']
            else:
                arguments['runner_type'] = 'instance_type'

            access_level_on_creation = self._module.params['access_level_on_creation']
            if not access_level_on_creation:
                arguments.pop('access_level', None)

            runner = self.create_runner(arguments)
            changed = True
        else:
            changed, runner = self.update_runner(self.runner_object, arguments)
            if changed:
                if self._module.check_mode:
                    self._module.exit_json(changed=True, msg="Successfully updated the runner %s" % description)

                try:
                    runner.save()
                except Exception as e:
                    self._module.fail_json(msg="Failed to update runner: %s " % to_native(e))

        self.runner_object = runner
        return changed

    '''
    @param arguments Attributes of the runner
    '''
    def create_runner(self, arguments):
        if self._module.check_mode:
            return True

        try:
            if arguments.get('token') is not None:
                runner = self._gitlab.runners.create(arguments)
            elif LooseVersion(gitlab.__version__) < LooseVersion('4.0.0'):
                self._module.fail_json(msg="New runner creation workflow requires python-gitlab 4.0.0 or higher")
            else:
                runner = self._gitlab.user.runners.create(arguments)
        except (gitlab.exceptions.GitlabCreateError) as e:
            self._module.fail_json(msg="Failed to create runner: %s " % to_native(e))

        return runner

    '''
    @param runner Runner object
    @param arguments Attributes of the runner
    '''
    def update_runner(self, runner, arguments):
        changed = False

        for arg_key, arg_value in arguments.items():
            if arg_value is not None:
                if isinstance(arg_value, list):
                    list1 = getattr(runner, arg_key)
                    list1.sort()
                    list2 = arg_value
                    list2.sort()
                    if list1 != list2:
                        setattr(runner, arg_key, arg_value)
                        changed = True
                else:
                    if getattr(runner, arg_key) != arg_value:
                        setattr(runner, arg_key, arg_value)
                        changed = True

        return (changed, runner)

    '''
    @param description Description of the runner
    '''
    def find_runner(self, description):
        runners = self._runners_endpoint(**list_all_kwargs)

        for runner in runners:
            # python-gitlab 2.2 through at least 2.5 returns a list of dicts for list() instead of a Runner
            # object, so we need to handle both
            if hasattr(runner, "description"):
                if (runner.description == description):
                    return self._gitlab.runners.get(runner.id)
            else:
                if (runner['description'] == description):
                    return self._gitlab.runners.get(runner['id'])

    '''
    @param description Description of the runner
    '''
    def exists_runner(self, description):
        # When runner exists, object will be stored in self.runner_object.
        runner = self.find_runner(description)

        if runner:
            self.runner_object = runner
            return True
        return False

    def delete_runner(self):
        if self._module.check_mode:
            return True

        runner = self.runner_object

        return runner.delete()


def main():
    argument_spec = basic_auth_argument_spec()
    argument_spec.update(auth_argument_spec())
    argument_spec.update(dict(
        description=dict(type='str', required=True, aliases=["name"]),
        active=dict(type='bool', default=True),
        paused=dict(type='bool', default=False),
        owned=dict(type='bool', default=False),
        tag_list=dict(type='list', elements='str', default=[]),
        run_untagged=dict(type='bool', default=True),
        locked=dict(type='bool', default=False),
        access_level=dict(type='str', choices=["not_protected", "ref_protected"]),
        access_level_on_creation=dict(type='bool', default=True),
        maximum_timeout=dict(type='int', default=3600),
        registration_token=dict(type='str', no_log=True),
        project=dict(type='str'),
        group=dict(type='str'),
        state=dict(type='str', default="present", choices=["absent", "present"]),
    ))

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[
            ['api_username', 'api_token'],
            ['api_username', 'api_oauth_token'],
            ['api_username', 'api_job_token'],
            ['api_token', 'api_oauth_token'],
            ['api_token', 'api_job_token'],
            ['project', 'owned'],
            ['group', 'owned'],
            ['project', 'group'],
            ['active', 'paused'],
        ],
        required_together=[
            ['api_username', 'api_password'],
        ],
        required_one_of=[
            ['api_username', 'api_token', 'api_oauth_token', 'api_job_token'],
        ],
        supports_check_mode=True,
    )

    # check prerequisites and connect to gitlab server
    gitlab_instance = gitlab_authentication(module)

    state = module.params['state']
    runner_description = module.params['description']
    runner_active = module.params['active']
    runner_paused = module.params['paused']
    tag_list = module.params['tag_list']
    run_untagged = module.params['run_untagged']
    runner_locked = module.params['locked']
    access_level = module.params['access_level']
    maximum_timeout = module.params['maximum_timeout']
    registration_token = module.params['registration_token']
    project = module.params['project']
    group = module.params['group']

    gitlab_project = None
    gitlab_group = None

    if project:
        try:
            gitlab_project = gitlab_instance.projects.get(project)
        except gitlab.exceptions.GitlabGetError as e:
            module.fail_json(msg='No such a project %s' % project, exception=to_native(e))
    elif group:
        try:
            gitlab_group = gitlab_instance.groups.get(group)
        except gitlab.exceptions.GitlabGetError as e:
            module.fail_json(msg='No such a group %s' % group, exception=to_native(e))

    gitlab_runner = GitLabRunner(module, gitlab_instance, gitlab_group, gitlab_project)
    runner_exists = gitlab_runner.exists_runner(runner_description)

    if state == 'absent':
        if runner_exists:
            gitlab_runner.delete_runner()
            module.exit_json(changed=True, msg="Successfully deleted runner %s" % runner_description)
        else:
            module.exit_json(changed=False, msg="Runner deleted or does not exists")

    if state == 'present':
        runner_values = {
            "active": runner_active,
            "tag_list": tag_list,
            "run_untagged": run_untagged,
            "locked": runner_locked,
            "access_level": access_level,
            "maximum_timeout": maximum_timeout,
            "registration_token": registration_token,
            "group": group,
            "project": project,
        }
        if LooseVersion(gitlab_runner._gitlab.version()[0]) >= LooseVersion("14.8.0"):
            # the paused attribute for runners is available since 14.8
            runner_values["paused"] = runner_paused
        if gitlab_runner.create_or_update_runner(runner_description, runner_values):
            module.exit_json(changed=True, runner=gitlab_runner.runner_object._attrs,
                             msg="Successfully created or updated the runner %s" % runner_description)
        else:
            module.exit_json(changed=False, runner=gitlab_runner.runner_object._attrs,
                             msg="No need to update the runner %s" % runner_description)


if __name__ == '__main__':
    main()
