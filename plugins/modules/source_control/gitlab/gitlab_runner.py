#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Raphaël Droz (raphael.droz@gmail.com)
# Copyright: (c) 2019, Guillaume Martinez (lunik@tiwabbit.fr)
# Copyright: (c) 2018, Samy Coenen <samy.coenen@nubera.be>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: gitlab_runner
short_description: Create, modify and delete GitLab Runners.
description:
  - Register, update and delete runners with the GitLab API.
  - All operations are performed using the GitLab API v4.
  - For details, consult the full API documentation at U(https://docs.gitlab.com/ee/api/runners.html).
  - A valid private API token is required for all operations. You can create as many tokens as you like using the GitLab web interface at
    U(https://$GITLAB_URL/profile/personal_access_tokens).
  - A valid registration token is required for registering a new runner.
    To create shared runners, you need to ask your administrator to give you this token.
    It can be found at U(https://$GITLAB_URL/admin/runners/).
notes:
  - To create a new runner at least the C(api_token), C(description) and C(api_url) options are required.
  - Runners need to have unique descriptions.
author:
  - Samy Coenen (@SamyCoenen)
  - Guillaume Martinez (@Lunik)
requirements:
  - python >= 2.7
  - python-gitlab >= 1.5.0
  - requests (python library https://github.com/psf/requests)
extends_documentation_fragment:
  - community.general.auth_basic
  - community.general.gitlab

options:
  project:
    description:
      - ID or full path of the project in the form of group/name.
    type: str
    version_added: '3.7.0'
  description:
    description:
      - The unique name of the runner.
    required: True
    type: str
    aliases:
      - name
  state:
    description:
      - Make sure that the runner with the same name exists with the same configuration or delete the runner with the same name.
    required: False
    default: present
    choices: ["present", "absent"]
    type: str
  registration_token:
    description:
      - The registration token is used to register new runners.
      - Required if I(state) is C(present).
    type: str
  owned:
    description:
      - Searches only runners available to the user when searching for existing, when false admin token required.
    default: no
    type: bool
    version_added: 2.0.0
  active:
    description:
      - Define if the runners is immediately active after creation.
    required: False
    default: yes
    type: bool
  locked:
    description:
      - Determines if the runner is locked or not.
    required: False
    default: False
    type: bool
  access_level:
    description:
      - Determines if a runner can pick up jobs only from protected branches.
      - If set to C(ref_protected), runner can pick up jobs only from protected branches.
      - If set to C(not_protected), runner can pick up jobs from both protected and unprotected branches.
    required: False
    default: ref_protected
    choices: ["ref_protected", "not_protected"]
    type: str
  maximum_timeout:
    description:
      - The maximum time that a runner has to complete a specific job.
    required: False
    default: 3600
    type: int
  run_untagged:
    description:
      - Run untagged jobs or not.
    required: False
    default: yes
    type: bool
  tag_list:
    description: The tags that apply to the runner.
    required: False
    default: []
    type: list
    elements: str
'''

EXAMPLES = '''
- name: "Register runner"
  community.general.gitlab_runner:
    api_url: https://gitlab.example.com/
    api_token: "{{ access_token }}"
    registration_token: 4gfdsg345
    description: Docker Machine t1
    state: present
    active: True
    tag_list: ['docker']
    run_untagged: False
    locked: False

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
    owned: yes
    state: absent

- name: Register runner for a specific project
  community.general.gitlab_runner:
    api_url: https://gitlab.example.com/
    api_token: "{{ access_token }}"
    registration_token: 4gfdsg345
    description: MyProject runner
    state: present
    project: mygroup/mysubgroup/myproject
'''

RETURN = '''
msg:
  description: Success or failure message
  returned: always
  type: str
  sample: "Success"

result:
  description: json parsed response from the server
  returned: always
  type: dict

error:
  description: the error message returned by the GitLab API
  returned: failed
  type: str
  sample: "400: path is already in use"

runner:
  description: API object
  returned: always
  type: dict
'''

import traceback

GITLAB_IMP_ERR = None
try:
    import gitlab
    HAS_GITLAB_PACKAGE = True
except Exception:
    GITLAB_IMP_ERR = traceback.format_exc()
    HAS_GITLAB_PACKAGE = False

from ansible.module_utils.api import basic_auth_argument_spec
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_native

from ansible_collections.community.general.plugins.module_utils.gitlab import auth_argument_spec, gitlab_authentication

try:
    cmp
except NameError:
    def cmp(a, b):
        return (a > b) - (a < b)


class GitLabRunner(object):
    def __init__(self, module, gitlab_instance, project=None):
        self._module = module
        self._gitlab = gitlab_instance
        # Whether to operate on GitLab-instance-wide or project-wide runners
        # See https://gitlab.com/gitlab-org/gitlab-ce/issues/60774
        # for group runner token access
        self._runners_endpoint = project.runners if project else gitlab_instance.runners
        self.runner_object = None

    def create_or_update_runner(self, description, options):
        changed = False

        # Because we have already call userExists in main()
        if self.runner_object is None:
            runner = self.create_runner({
                'description': description,
                'active': options['active'],
                'token': options['registration_token'],
                'locked': options['locked'],
                'run_untagged': options['run_untagged'],
                'maximum_timeout': options['maximum_timeout'],
                'tag_list': options['tag_list'],
            })
            changed = True
        else:
            changed, runner = self.update_runner(self.runner_object, {
                'active': options['active'],
                'locked': options['locked'],
                'run_untagged': options['run_untagged'],
                'maximum_timeout': options['maximum_timeout'],
                'access_level': options['access_level'],
                'tag_list': options['tag_list'],
            })

        self.runner_object = runner
        if changed:
            if self._module.check_mode:
                self._module.exit_json(changed=True, msg="Successfully created or updated the runner %s" % description)

            try:
                runner.save()
            except Exception as e:
                self._module.fail_json(msg="Failed to update runner: %s " % to_native(e))
            return True
        else:
            return False

    '''
    @param arguments Attributes of the runner
    '''
    def create_runner(self, arguments):
        if self._module.check_mode:
            return True

        try:
            runner = self._runners_endpoint.create(arguments)
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
            if arguments[arg_key] is not None:
                if isinstance(arguments[arg_key], list):
                    list1 = getattr(runner, arg_key)
                    list1.sort()
                    list2 = arguments[arg_key]
                    list2.sort()
                    if cmp(list1, list2):
                        setattr(runner, arg_key, arguments[arg_key])
                        changed = True
                else:
                    if getattr(runner, arg_key) != arguments[arg_key]:
                        setattr(runner, arg_key, arguments[arg_key])
                        changed = True

        return (changed, runner)

    '''
    @param description Description of the runner
    '''
    def find_runner(self, description, owned=False):
        if owned:
            runners = self._runners_endpoint.list(as_list=False)
        else:
            runners = self._runners_endpoint.all(as_list=False)

        for runner in runners:
            # python-gitlab 2.2 through at least 2.5 returns a list of dicts for list() instead of a Runner
            # object, so we need to handle both
            if hasattr(runner, "description"):
                if (runner.description == description):
                    return self._runners_endpoint.get(runner.id)
            else:
                if (runner['description'] == description):
                    return self._runners_endpoint.get(runner['id'])

    '''
    @param description Description of the runner
    '''
    def exists_runner(self, description, owned=False):
        # When runner exists, object will be stored in self.runner_object.
        runner = self.find_runner(description, owned)

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
        owned=dict(type='bool', default=False),
        tag_list=dict(type='list', elements='str', default=[]),
        run_untagged=dict(type='bool', default=True),
        locked=dict(type='bool', default=False),
        access_level=dict(type='str', default='ref_protected', choices=["not_protected", "ref_protected"]),
        maximum_timeout=dict(type='int', default=3600),
        registration_token=dict(type='str', no_log=True),
        project=dict(type='str'),
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
        ],
        required_together=[
            ['api_username', 'api_password'],
        ],
        required_one_of=[
            ['api_username', 'api_token', 'api_oauth_token', 'api_job_token'],
        ],
        required_if=[
            ('state', 'present', ['registration_token']),
        ],
        supports_check_mode=True,
    )

    state = module.params['state']
    owned = module.params['owned']
    runner_description = module.params['description']
    runner_active = module.params['active']
    tag_list = module.params['tag_list']
    run_untagged = module.params['run_untagged']
    runner_locked = module.params['locked']
    access_level = module.params['access_level']
    maximum_timeout = module.params['maximum_timeout']
    registration_token = module.params['registration_token']
    project = module.params['project']

    if not HAS_GITLAB_PACKAGE:
        module.fail_json(msg=missing_required_lib("python-gitlab"), exception=GITLAB_IMP_ERR)

    gitlab_instance = gitlab_authentication(module)
    gitlab_project = None
    if project:
        try:
            gitlab_project = gitlab_instance.projects.get(project)
        except gitlab.exceptions.GitlabGetError as e:
            module.fail_json(msg='No such a project %s' % project, exception=to_native(e))

    gitlab_runner = GitLabRunner(module, gitlab_instance, gitlab_project)
    runner_exists = gitlab_runner.exists_runner(runner_description, owned)

    if state == 'absent':
        if runner_exists:
            gitlab_runner.delete_runner()
            module.exit_json(changed=True, msg="Successfully deleted runner %s" % runner_description)
        else:
            module.exit_json(changed=False, msg="Runner deleted or does not exists")

    if state == 'present':
        if gitlab_runner.create_or_update_runner(runner_description, {
            "active": runner_active,
            "tag_list": tag_list,
            "run_untagged": run_untagged,
            "locked": runner_locked,
            "access_level": access_level,
            "maximum_timeout": maximum_timeout,
            "registration_token": registration_token,
        }):
            module.exit_json(changed=True, runner=gitlab_runner.runner_object._attrs,
                             msg="Successfully created or updated the runner %s" % runner_description)
        else:
            module.exit_json(changed=False, runner=gitlab_runner.runner_object._attrs,
                             msg="No need to update the runner %s" % runner_description)


if __name__ == '__main__':
    main()
