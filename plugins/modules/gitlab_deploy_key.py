#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2019, Guillaume Martinez (lunik@tiwabbit.fr)
# Copyright (c) 2018, Marcus Watkins <marwatk@marcuswatkins.net>
# Based on code:
# Copyright (c) 2013, Phillip Gentry <phillip@cx.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
module: gitlab_deploy_key
short_description: Manages GitLab project deploy keys
description:
  - Adds, updates and removes project deploy keys
author:
  - Marcus Watkins (@marwatk)
  - Guillaume Martinez (@Lunik)
requirements:
  - python-gitlab python module
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
      - Id or Full path of project in the form of group/name.
    required: true
    type: str
  title:
    description:
      - Deploy key's title.
    required: true
    type: str
  key:
    description:
      - Deploy key
    required: true
    type: str
  can_push:
    description:
      - Whether this key can push to the project.
    type: bool
    default: false
  state:
    description:
      - When V(present) the deploy key added to the project if it doesn't exist.
      - When V(absent) it will be removed from the project if it exists.
    default: present
    type: str
    choices: [ "present", "absent" ]
'''

EXAMPLES = '''
- name: "Adding a project deploy key"
  community.general.gitlab_deploy_key:
    api_url: https://gitlab.example.com/
    api_token: "{{ api_token }}"
    project: "my_group/my_project"
    title: "Jenkins CI"
    state: present
    key: "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAIEAiPWx6WM4lhHNedGfBpPJNPpZ7yKu+dnn1SJejgt4596k6YjzGGphH2TUxwKzxcKDKKezwkpfnxPkSMkuEspGRt/aZZ9w..."

- name: "Update the above deploy key to add push access"
  community.general.gitlab_deploy_key:
    api_url: https://gitlab.example.com/
    api_token: "{{ api_token }}"
    project: "my_group/my_project"
    title: "Jenkins CI"
    state: present
    can_push: true

- name: "Remove the previous deploy key from the project"
  community.general.gitlab_deploy_key:
    api_url: https://gitlab.example.com/
    api_token: "{{ api_token }}"
    project: "my_group/my_project"
    state: absent
    key: "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAIEAiPWx6WM4lhHNedGfBpPJNPpZ7yKu+dnn1SJejgt4596k6YjzGGphH2TUxwKzxcKDKKezwkpfnxPkSMkuEspGRt/aZZ9w..."

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
  sample: "400: key is already in use"

deploy_key:
  description: API object
  returned: always
  type: dict
'''

from ansible.module_utils.api import basic_auth_argument_spec
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native

from ansible_collections.community.general.plugins.module_utils.gitlab import (
    auth_argument_spec, find_project, gitlab_authentication, gitlab, list_all_kwargs
)


class GitLabDeployKey(object):
    def __init__(self, module, gitlab_instance):
        self._module = module
        self._gitlab = gitlab_instance
        self.deploy_key_object = None

    '''
    @param project Project object
    @param key_title Title of the key
    @param key_key String of the key
    @param key_can_push Option of the deploy_key
    @param options Deploy key options
    '''
    def create_or_update_deploy_key(self, project, key_title, key_key, options):
        changed = False

        # note: unfortunately public key cannot be updated directly by
        #   GitLab REST API, so for that case we need to delete and
        #   than recreate the key
        if self.deploy_key_object and self.deploy_key_object.key != key_key:
            if not self._module.check_mode:
                self.deploy_key_object.delete()
            self.deploy_key_object = None

        # Because we have already call exists_deploy_key in main()
        if self.deploy_key_object is None:
            deploy_key = self.create_deploy_key(project, {
                'title': key_title,
                'key': key_key,
                'can_push': options['can_push']})
            changed = True
        else:
            changed, deploy_key = self.update_deploy_key(self.deploy_key_object, {
                'title': key_title,
                'can_push': options['can_push']})

        self.deploy_key_object = deploy_key
        if changed:
            if self._module.check_mode:
                self._module.exit_json(changed=True, msg="Successfully created or updated the deploy key %s" % key_title)

            try:
                deploy_key.save()
            except Exception as e:
                self._module.fail_json(msg="Failed to update deploy key: %s " % e)
            return True
        else:
            return False

    '''
    @param project Project Object
    @param arguments Attributes of the deploy_key
    '''
    def create_deploy_key(self, project, arguments):
        if self._module.check_mode:
            return True

        try:
            deploy_key = project.keys.create(arguments)
        except (gitlab.exceptions.GitlabCreateError) as e:
            self._module.fail_json(msg="Failed to create deploy key: %s " % to_native(e))

        return deploy_key

    '''
    @param deploy_key Deploy Key Object
    @param arguments Attributes of the deploy_key
    '''
    def update_deploy_key(self, deploy_key, arguments):
        changed = False

        for arg_key, arg_value in arguments.items():
            if arg_value is not None:
                if getattr(deploy_key, arg_key) != arg_value:
                    setattr(deploy_key, arg_key, arg_value)
                    changed = True

        return (changed, deploy_key)

    '''
    @param project Project object
    @param key_title Title of the key
    '''
    def find_deploy_key(self, project, key_title):
        for deploy_key in project.keys.list(**list_all_kwargs):
            if (deploy_key.title == key_title):
                return deploy_key

    '''
    @param project Project object
    @param key_title Title of the key
    '''
    def exists_deploy_key(self, project, key_title):
        # When project exists, object will be stored in self.project_object.
        deploy_key = self.find_deploy_key(project, key_title)
        if deploy_key:
            self.deploy_key_object = deploy_key
            return True
        return False

    def delete_deploy_key(self):
        if self._module.check_mode:
            return True

        return self.deploy_key_object.delete()


def main():
    argument_spec = basic_auth_argument_spec()
    argument_spec.update(auth_argument_spec())
    argument_spec.update(dict(
        state=dict(type='str', default="present", choices=["absent", "present"]),
        project=dict(type='str', required=True),
        key=dict(type='str', required=True, no_log=False),
        can_push=dict(type='bool', default=False),
        title=dict(type='str', required=True)
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
            ['api_username', 'api_password']
        ],
        required_one_of=[
            ['api_username', 'api_token', 'api_oauth_token', 'api_job_token']
        ],
        supports_check_mode=True,
    )

    # check prerequisites and connect to gitlab server
    gitlab_instance = gitlab_authentication(module)

    state = module.params['state']
    project_identifier = module.params['project']
    key_title = module.params['title']
    key_keyfile = module.params['key']
    key_can_push = module.params['can_push']

    gitlab_deploy_key = GitLabDeployKey(module, gitlab_instance)

    project = find_project(gitlab_instance, project_identifier)

    if project is None:
        module.fail_json(msg="Failed to create deploy key: project %s doesn't exists" % project_identifier)

    deploy_key_exists = gitlab_deploy_key.exists_deploy_key(project, key_title)

    if state == 'absent':
        if deploy_key_exists:
            gitlab_deploy_key.delete_deploy_key()
            module.exit_json(changed=True, msg="Successfully deleted deploy key %s" % key_title)
        else:
            module.exit_json(changed=False, msg="Deploy key deleted or does not exists")

    if state == 'present':
        if gitlab_deploy_key.create_or_update_deploy_key(project, key_title, key_keyfile, {'can_push': key_can_push}):

            module.exit_json(changed=True, msg="Successfully created or updated the deploy key %s" % key_title,
                             deploy_key=gitlab_deploy_key.deploy_key_object._attrs)
        else:
            module.exit_json(changed=False, msg="No need to update the deploy key %s" % key_title,
                             deploy_key=gitlab_deploy_key.deploy_key_object._attrs)


if __name__ == '__main__':
    main()
