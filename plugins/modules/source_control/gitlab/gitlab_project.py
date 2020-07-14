#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Guillaume Martinez (lunik@tiwabbit.fr)
# Copyright: (c) 2015, Werner Dijkerman (ikben@werner-dijkerman.nl)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gitlab_project
short_description: Creates/updates/deletes GitLab Projects
description:
  - When the project does not exist in GitLab, it will be created.
  - When the project does exists and state=absent, the project will be deleted.
  - When changes are made to the project, the project will be updated.
author:
  - Werner Dijkerman (@dj-wasabi)
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
  group:
    description:
      - Id or The full path of the group of which this projects belongs to.
    type: str
  name:
    description:
      - The name of the project
    required: true
    type: str
  path:
    description:
      - The path of the project you want to create, this will be server_url/<group>/path.
      - If not supplied, name will be used.
    type: str
  description:
    description:
      - An description for the project.
    type: str
  issues_enabled:
    description:
      - Whether you want to create issues or not.
      - Possible values are true and false.
    type: bool
    default: yes
  merge_requests_enabled:
    description:
      - If merge requests can be made or not.
      - Possible values are true and false.
    type: bool
    default: yes
  wiki_enabled:
    description:
      - If an wiki for this project should be available or not.
      - Possible values are true and false.
    type: bool
    default: yes
  snippets_enabled:
    description:
      - If creating snippets should be available or not.
      - Possible values are true and false.
    type: bool
    default: yes
  visibility:
    description:
      - Private. Project access must be granted explicitly for each user.
      - Internal. The project can be cloned by any logged in user.
      - Public. The project can be cloned without any authentication.
    default: private
    type: str
    choices: ["private", "internal", "public"]
    aliases:
      - visibility_level
  import_url:
    description:
      - Git repository which will be imported into gitlab.
      - GitLab server needs read access to this git repository.
    required: false
    type: str
  state:
    description:
      - create or delete project.
      - Possible values are present and absent.
    default: present
    type: str
    choices: ["present", "absent"]
  merge_method:
    description:
      - What requirements are placed upon merges.
      - Possible values are C(merge), C(rebase_merge) merge commit with semi-linear history, C(ff) fast-forward merges only.
    type: str
    choices: ["ff", "merge", "rebase_merge"]
    default: merge
    version_added: "1.0.0"
'''

EXAMPLES = r'''
- name: Delete GitLab Project
  community.general.gitlab_project:
    api_url: https://gitlab.example.com/
    api_token: "{{ access_token }}"
    validate_certs: False
    name: my_first_project
    state: absent
  delegate_to: localhost

- name: Create GitLab Project in group Ansible
  community.general.gitlab_project:
    api_url: https://gitlab.example.com/
    validate_certs: True
    api_username: dj-wasabi
    api_password: "MySecretPassword"
    name: my_first_project
    group: ansible
    issues_enabled: False
    merge_method: rebase_merge
    wiki_enabled: True
    snippets_enabled: True
    import_url: http://git.example.com/example/lab.git
    state: present
  delegate_to: localhost
'''

RETURN = r'''
msg:
  description: Success or failure message.
  returned: always
  type: str
  sample: "Success"

result:
  description: json parsed response from the server.
  returned: always
  type: dict

error:
  description: the error message returned by the GitLab API.
  returned: failed
  type: str
  sample: "400: path is already in use"

project:
  description: API object.
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
from ansible.module_utils._text import to_native

from ansible_collections.community.general.plugins.module_utils.gitlab import findGroup, findProject, gitlabAuthentication


class GitLabProject(object):
    def __init__(self, module, gitlab_instance):
        self._module = module
        self._gitlab = gitlab_instance
        self.projectObject = None

    '''
    @param project_name Name of the project
    @param namespace Namespace Object (User or Group)
    @param options Options of the project
    '''
    def createOrUpdateProject(self, project_name, namespace, options):
        changed = False

        # Because we have already call userExists in main()
        if self.projectObject is None:
            project = self.createProject(namespace, {
                'name': project_name,
                'path': options['path'],
                'description': options['description'],
                'issues_enabled': options['issues_enabled'],
                'merge_requests_enabled': options['merge_requests_enabled'],
                'merge_method': options['merge_method'],
                'wiki_enabled': options['wiki_enabled'],
                'snippets_enabled': options['snippets_enabled'],
                'visibility': options['visibility'],
                'import_url': options['import_url']})
            changed = True
        else:
            changed, project = self.updateProject(self.projectObject, {
                'name': project_name,
                'description': options['description'],
                'issues_enabled': options['issues_enabled'],
                'merge_requests_enabled': options['merge_requests_enabled'],
                'merge_method': options['merge_method'],
                'wiki_enabled': options['wiki_enabled'],
                'snippets_enabled': options['snippets_enabled'],
                'visibility': options['visibility']})

        self.projectObject = project
        if changed:
            if self._module.check_mode:
                self._module.exit_json(changed=True, msg="Successfully created or updated the project %s" % project_name)

            try:
                project.save()
            except Exception as e:
                self._module.fail_json(msg="Failed update project: %s " % e)
            return True
        else:
            return False

    '''
    @param namespace Namespace Object (User or Group)
    @param arguments Attributes of the project
    '''
    def createProject(self, namespace, arguments):
        if self._module.check_mode:
            return True

        arguments['namespace_id'] = namespace.id
        try:
            project = self._gitlab.projects.create(arguments)
        except (gitlab.exceptions.GitlabCreateError) as e:
            self._module.fail_json(msg="Failed to create project: %s " % to_native(e))

        return project

    '''
    @param project Project Object
    @param arguments Attributes of the project
    '''
    def updateProject(self, project, arguments):
        changed = False

        for arg_key, arg_value in arguments.items():
            if arguments[arg_key] is not None:
                if getattr(project, arg_key) != arguments[arg_key]:
                    setattr(project, arg_key, arguments[arg_key])
                    changed = True

        return (changed, project)

    def deleteProject(self):
        if self._module.check_mode:
            return True

        project = self.projectObject

        return project.delete()

    '''
    @param namespace User/Group object
    @param name Name of the project
    '''
    def existsProject(self, namespace, path):
        # When project exists, object will be stored in self.projectObject.
        project = findProject(self._gitlab, namespace.full_path + '/' + path)
        if project:
            self.projectObject = project
            return True
        return False


def main():
    argument_spec = basic_auth_argument_spec()
    argument_spec.update(dict(
        api_token=dict(type='str', no_log=True),
        group=dict(type='str'),
        name=dict(type='str', required=True),
        path=dict(type='str'),
        description=dict(type='str'),
        issues_enabled=dict(type='bool', default=True),
        merge_requests_enabled=dict(type='bool', default=True),
        merge_method=dict(type='str', default='merge', choices=["merge", "rebase_merge", "ff"]),
        wiki_enabled=dict(type='bool', default=True),
        snippets_enabled=dict(default=True, type='bool'),
        visibility=dict(type='str', default="private", choices=["internal", "private", "public"], aliases=["visibility_level"]),
        import_url=dict(type='str'),
        state=dict(type='str', default="present", choices=["absent", "present"]),
    ))

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[
            ['api_username', 'api_token'],
            ['api_password', 'api_token'],
        ],
        required_together=[
            ['api_username', 'api_password'],
        ],
        required_one_of=[
            ['api_username', 'api_token']
        ],
        supports_check_mode=True,
    )

    group_identifier = module.params['group']
    project_name = module.params['name']
    project_path = module.params['path']
    project_description = module.params['description']
    issues_enabled = module.params['issues_enabled']
    merge_requests_enabled = module.params['merge_requests_enabled']
    merge_method = module.params['merge_method']
    wiki_enabled = module.params['wiki_enabled']
    snippets_enabled = module.params['snippets_enabled']
    visibility = module.params['visibility']
    import_url = module.params['import_url']
    state = module.params['state']

    if not HAS_GITLAB_PACKAGE:
        module.fail_json(msg=missing_required_lib("python-gitlab"), exception=GITLAB_IMP_ERR)

    gitlab_instance = gitlabAuthentication(module)

    # Set project_path to project_name if it is empty.
    if project_path is None:
        project_path = project_name.replace(" ", "_")

    gitlab_project = GitLabProject(module, gitlab_instance)

    if group_identifier:
        group = findGroup(gitlab_instance, group_identifier)
        if group is None:
            module.fail_json(msg="Failed to create project: group %s doesn't exists" % group_identifier)

        namespace = gitlab_instance.namespaces.get(group.id)
        project_exists = gitlab_project.existsProject(namespace, project_path)
    else:
        user = gitlab_instance.users.list(username=gitlab_instance.user.username)[0]
        namespace = gitlab_instance.namespaces.get(user.id)
        project_exists = gitlab_project.existsProject(namespace, project_path)

    if state == 'absent':
        if project_exists:
            gitlab_project.deleteProject()
            module.exit_json(changed=True, msg="Successfully deleted project %s" % project_name)
        else:
            module.exit_json(changed=False, msg="Project deleted or does not exists")

    if state == 'present':
        if gitlab_project.createOrUpdateProject(project_name, namespace, {
                                                "path": project_path,
                                                "description": project_description,
                                                "issues_enabled": issues_enabled,
                                                "merge_requests_enabled": merge_requests_enabled,
                                                "merge_method": merge_method,
                                                "wiki_enabled": wiki_enabled,
                                                "snippets_enabled": snippets_enabled,
                                                "visibility": visibility,
                                                "import_url": import_url}):

            module.exit_json(changed=True, msg="Successfully created or updated the project %s" % project_name, project=gitlab_project.projectObject._attrs)
        else:
            module.exit_json(changed=False, msg="No need to update the project %s" % project_name, project=gitlab_project.projectObject._attrs)


if __name__ == '__main__':
    main()
