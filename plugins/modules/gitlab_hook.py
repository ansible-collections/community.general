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
---
module: gitlab_hook
short_description: Manages GitLab project hooks
description:
  - Adds, updates and removes project hook
author:
  - Marcus Watkins (@marwatk)
  - Guillaume Martinez (@Lunik)
requirements:
  - python >= 2.7
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
      - Id or Full path of the project in the form of group/name.
    required: true
    type: str
  hook_url:
    description:
      - The url that you want GitLab to post to, this is used as the primary key for updates and deletion.
    required: true
    type: str
  state:
    description:
      - When C(present) the hook will be updated to match the input or created if it doesn't exist.
      - When C(absent) hook will be deleted if it exists.
    default: present
    type: str
    choices: [ "present", "absent" ]
  push_events:
    description:
      - Trigger hook on push events.
    type: bool
    default: true
  push_events_branch_filter:
    description:
      - Branch name of wildcard to trigger hook on push events
    type: str
    version_added: '0.2.0'
    default: ''
  issues_events:
    description:
      - Trigger hook on issues events.
    type: bool
    default: false
  merge_requests_events:
    description:
      - Trigger hook on merge requests events.
    type: bool
    default: false
  tag_push_events:
    description:
      - Trigger hook on tag push events.
    type: bool
    default: false
  note_events:
    description:
      - Trigger hook on note events or when someone adds a comment.
    type: bool
    default: false
  job_events:
    description:
      - Trigger hook on job events.
    type: bool
    default: false
  pipeline_events:
    description:
      - Trigger hook on pipeline events.
    type: bool
    default: false
  wiki_page_events:
    description:
      - Trigger hook on wiki events.
    type: bool
    default: false
  hook_validate_certs:
    description:
      - Whether GitLab will do SSL verification when triggering the hook.
    type: bool
    default: false
    aliases: [ enable_ssl_verification ]
  token:
    description:
      - Secret token to validate hook messages at the receiver.
      - If this is present it will always result in a change as it cannot be retrieved from GitLab.
      - Will show up in the X-GitLab-Token HTTP request header.
    required: false
    type: str
'''

EXAMPLES = '''
- name: "Adding a project hook"
  community.general.gitlab_hook:
    api_url: https://gitlab.example.com/
    api_token: "{{ access_token }}"
    project: "my_group/my_project"
    hook_url: "https://my-ci-server.example.com/gitlab-hook"
    state: present
    push_events: true
    tag_push_events: true
    hook_validate_certs: false
    token: "my-super-secret-token-that-my-ci-server-will-check"

- name: "Delete the previous hook"
  community.general.gitlab_hook:
    api_url: https://gitlab.example.com/
    api_token: "{{ access_token }}"
    project: "my_group/my_project"
    hook_url: "https://my-ci-server.example.com/gitlab-hook"
    state: absent

- name: "Delete a hook by numeric project id"
  community.general.gitlab_hook:
    api_url: https://gitlab.example.com/
    api_token: "{{ access_token }}"
    project: 10
    hook_url: "https://my-ci-server.example.com/gitlab-hook"
    state: absent
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

hook:
  description: API object
  returned: always
  type: dict
'''

from ansible.module_utils.api import basic_auth_argument_spec
from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.general.plugins.module_utils.gitlab import (
    auth_argument_spec, find_project, gitlab_authentication, ensure_gitlab_package
)


class GitLabHook(object):
    def __init__(self, module, gitlab_instance):
        self._module = module
        self._gitlab = gitlab_instance
        self.hook_object = None

    '''
    @param project Project Object
    @param hook_url Url to call on event
    @param description Description of the group
    @param parent Parent group full path
    '''
    def create_or_update_hook(self, project, hook_url, options):
        changed = False

        # Because we have already call userExists in main()
        if self.hook_object is None:
            hook = self.create_hook(project, {
                'url': hook_url,
                'push_events': options['push_events'],
                'push_events_branch_filter': options['push_events_branch_filter'],
                'issues_events': options['issues_events'],
                'merge_requests_events': options['merge_requests_events'],
                'tag_push_events': options['tag_push_events'],
                'note_events': options['note_events'],
                'job_events': options['job_events'],
                'pipeline_events': options['pipeline_events'],
                'wiki_page_events': options['wiki_page_events'],
                'enable_ssl_verification': options['enable_ssl_verification'],
                'token': options['token'],
            })
            changed = True
        else:
            changed, hook = self.update_hook(self.hook_object, {
                'push_events': options['push_events'],
                'push_events_branch_filter': options['push_events_branch_filter'],
                'issues_events': options['issues_events'],
                'merge_requests_events': options['merge_requests_events'],
                'tag_push_events': options['tag_push_events'],
                'note_events': options['note_events'],
                'job_events': options['job_events'],
                'pipeline_events': options['pipeline_events'],
                'wiki_page_events': options['wiki_page_events'],
                'enable_ssl_verification': options['enable_ssl_verification'],
                'token': options['token'],
            })

        self.hook_object = hook
        if changed:
            if self._module.check_mode:
                self._module.exit_json(changed=True, msg="Successfully created or updated the hook %s" % hook_url)

            try:
                hook.save()
            except Exception as e:
                self._module.fail_json(msg="Failed to update hook: %s " % e)

        return changed

    '''
    @param project Project Object
    @param arguments Attributes of the hook
    '''
    def create_hook(self, project, arguments):
        if self._module.check_mode:
            return True

        hook = project.hooks.create(arguments)

        return hook

    '''
    @param hook Hook Object
    @param arguments Attributes of the hook
    '''
    def update_hook(self, hook, arguments):
        changed = False

        for arg_key, arg_value in arguments.items():
            if arg_value is not None:
                if getattr(hook, arg_key, None) != arg_value:
                    setattr(hook, arg_key, arg_value)
                    changed = True

        return (changed, hook)

    '''
    @param project Project object
    @param hook_url Url to call on event
    '''
    def find_hook(self, project, hook_url):
        hooks = project.hooks.list(all=True)
        for hook in hooks:
            if (hook.url == hook_url):
                return hook

    '''
    @param project Project object
    @param hook_url Url to call on event
    '''
    def exists_hook(self, project, hook_url):
        # When project exists, object will be stored in self.project_object.
        hook = self.find_hook(project, hook_url)
        if hook:
            self.hook_object = hook
            return True
        return False

    def delete_hook(self):
        if not self._module.check_mode:
            self.hook_object.delete()


def main():
    argument_spec = basic_auth_argument_spec()
    argument_spec.update(auth_argument_spec())
    argument_spec.update(dict(
        state=dict(type='str', default="present", choices=["absent", "present"]),
        project=dict(type='str', required=True),
        hook_url=dict(type='str', required=True),
        push_events=dict(type='bool', default=True),
        push_events_branch_filter=dict(type='str', default=''),
        issues_events=dict(type='bool', default=False),
        merge_requests_events=dict(type='bool', default=False),
        tag_push_events=dict(type='bool', default=False),
        note_events=dict(type='bool', default=False),
        job_events=dict(type='bool', default=False),
        pipeline_events=dict(type='bool', default=False),
        wiki_page_events=dict(type='bool', default=False),
        hook_validate_certs=dict(type='bool', default=False, aliases=['enable_ssl_verification']),
        token=dict(type='str', no_log=True),
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
    ensure_gitlab_package(module)

    state = module.params['state']
    project_identifier = module.params['project']
    hook_url = module.params['hook_url']
    push_events = module.params['push_events']
    push_events_branch_filter = module.params['push_events_branch_filter']
    issues_events = module.params['issues_events']
    merge_requests_events = module.params['merge_requests_events']
    tag_push_events = module.params['tag_push_events']
    note_events = module.params['note_events']
    job_events = module.params['job_events']
    pipeline_events = module.params['pipeline_events']
    wiki_page_events = module.params['wiki_page_events']
    enable_ssl_verification = module.params['hook_validate_certs']
    hook_token = module.params['token']

    gitlab_instance = gitlab_authentication(module)

    gitlab_hook = GitLabHook(module, gitlab_instance)

    project = find_project(gitlab_instance, project_identifier)

    if project is None:
        module.fail_json(msg="Failed to create hook: project %s doesn't exists" % project_identifier)

    hook_exists = gitlab_hook.exists_hook(project, hook_url)

    if state == 'absent':
        if hook_exists:
            gitlab_hook.delete_hook()
            module.exit_json(changed=True, msg="Successfully deleted hook %s" % hook_url)
        else:
            module.exit_json(changed=False, msg="Hook deleted or does not exists")

    if state == 'present':
        if gitlab_hook.create_or_update_hook(project, hook_url, {
            "push_events": push_events,
            "push_events_branch_filter": push_events_branch_filter,
            "issues_events": issues_events,
            "merge_requests_events": merge_requests_events,
            "tag_push_events": tag_push_events,
            "note_events": note_events,
            "job_events": job_events,
            "pipeline_events": pipeline_events,
            "wiki_page_events": wiki_page_events,
            "enable_ssl_verification": enable_ssl_verification,
            "token": hook_token,
        }):

            module.exit_json(changed=True, msg="Successfully created or updated the hook %s" % hook_url, hook=gitlab_hook.hook_object._attrs)
        else:
            module.exit_json(changed=False, msg="No need to update the hook %s" % hook_url, hook=gitlab_hook.hook_object._attrs)


if __name__ == '__main__':
    main()
