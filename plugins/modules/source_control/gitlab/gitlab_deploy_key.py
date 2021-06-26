#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Guillaume Martinez (lunik@tiwabbit.fr)
# Copyright: (c) 2018, Marcus Watkins <marwatk@marcuswatkins.net>
# Based on code:
# Copyright: (c) 2013, Phillip Gentry <phillip@cx.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
module: gitlab_deploy_key
short_description: Manages GitLab project deploy keys.
description:
     - Adds, updates and removes project deploy keys
author:
  - Marcus Watkins (@marwatk)
  - Guillaume Martinez (@Lunik)
requirements:
  - python >= 2.7
  - python-gitlab python module
extends_documentation_fragment:
- community.general.auth_basic

options:
  api_token:
    description:
      - GitLab token for logging in.
    type: str
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
    default: no
  state:
    description:
      - When C(present) the deploy key added to the project if it doesn't exist.
      - When C(absent) it will be removed from the project if it exists.
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
    can_push: yes

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

import re
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

from ansible_collections.community.general.plugins.module_utils.gitlab import findProject, gitlabAuthentication


class GitLabDeployKey(object):
    def __init__(self, module, gitlab_instance):
        self._module = module
        self._gitlab = gitlab_instance
        self.deployKeyObject = None

    '''
    @param project Project object
    @param key_title Title of the key
    @param key_key String of the key
    @param key_can_push Option of the deployKey
    @param options Deploy key options
    '''
    def createOrUpdateDeployKey(self, project, key_title, key_key, options):
        changed = False

        # note: unfortunately public key cannot be updated directly by
        #   GitLab REST API, so for that case we need to delete and
        #   than recreate the key
        if self.deployKeyObject and self.deployKeyObject.key != key_key:
            self.deployKeyObject.delete()
            self.deployKeyObject = None

        # Because we have already call existsDeployKey in main()
        if self.deployKeyObject is None:
            deployKey = self.createDeployKey(project, {
                'title': key_title,
                'key': key_key,
                'can_push': options['can_push']})
            changed = True
        else:
            changed, deployKey = self.updateDeployKey(self.deployKeyObject, {
                'can_push': options['can_push']})

        self.deployKeyObject = deployKey
        if changed:
            if self._module.check_mode:
                self._module.exit_json(changed=True, msg="Successfully created or updated the deploy key %s" % key_title)

            try:
                deployKey.save()
            except Exception as e:
                self._module.fail_json(msg="Failed to update deploy key: %s " % e)
            return True
        else:
            return False

    '''
    @param project Project Object
    @param arguments Attributes of the deployKey
    '''
    def createDeployKey(self, project, arguments):
        if self._module.check_mode:
            return True

        try:
            deployKey = project.keys.create(arguments)
        except (gitlab.exceptions.GitlabCreateError) as e:
            self._module.fail_json(msg="Failed to create deploy key: %s " % to_native(e))

        return deployKey

    '''
    @param deployKey Deploy Key Object
    @param arguments Attributes of the deployKey
    '''
    def updateDeployKey(self, deployKey, arguments):
        changed = False

        for arg_key, arg_value in arguments.items():
            if arguments[arg_key] is not None:
                if getattr(deployKey, arg_key) != arguments[arg_key]:
                    setattr(deployKey, arg_key, arguments[arg_key])
                    changed = True

        return (changed, deployKey)

    '''
    @param project Project object
    @param key_title Title of the key
    '''
    def findDeployKey(self, project, key_title):
        deployKeys = project.keys.list()
        for deployKey in deployKeys:
            if (deployKey.title == key_title):
                return deployKey

    '''
    @param project Project object
    @param key_title Title of the key
    '''
    def existsDeployKey(self, project, key_title):
        # When project exists, object will be stored in self.projectObject.
        deployKey = self.findDeployKey(project, key_title)
        if deployKey:
            self.deployKeyObject = deployKey
            return True
        return False

    def deleteDeployKey(self):
        if self._module.check_mode:
            return True

        return self.deployKeyObject.delete()


def main():
    argument_spec = basic_auth_argument_spec()
    argument_spec.update(dict(
        api_token=dict(type='str', no_log=True),
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
            ['api_password', 'api_token']
        ],
        required_together=[
            ['api_username', 'api_password']
        ],
        required_one_of=[
            ['api_username', 'api_token']
        ],
        supports_check_mode=True,
    )

    state = module.params['state']
    project_identifier = module.params['project']
    key_title = module.params['title']
    key_keyfile = module.params['key']
    key_can_push = module.params['can_push']

    if not HAS_GITLAB_PACKAGE:
        module.fail_json(msg=missing_required_lib("python-gitlab"), exception=GITLAB_IMP_ERR)

    gitlab_instance = gitlabAuthentication(module)

    gitlab_deploy_key = GitLabDeployKey(module, gitlab_instance)

    project = findProject(gitlab_instance, project_identifier)

    if project is None:
        module.fail_json(msg="Failed to create deploy key: project %s doesn't exists" % project_identifier)

    deployKey_exists = gitlab_deploy_key.existsDeployKey(project, key_title)

    if state == 'absent':
        if deployKey_exists:
            gitlab_deploy_key.deleteDeployKey()
            module.exit_json(changed=True, msg="Successfully deleted deploy key %s" % key_title)
        else:
            module.exit_json(changed=False, msg="Deploy key deleted or does not exists")

    if state == 'present':
        if gitlab_deploy_key.createOrUpdateDeployKey(project, key_title, key_keyfile, {'can_push': key_can_push}):

            module.exit_json(changed=True, msg="Successfully created or updated the deploy key %s" % key_title,
                             deploy_key=gitlab_deploy_key.deployKeyObject._attrs)
        else:
            module.exit_json(changed=False, msg="No need to update the deploy key %s" % key_title,
                             deploy_key=gitlab_deploy_key.deployKeyObject._attrs)


if __name__ == '__main__':
    main()
