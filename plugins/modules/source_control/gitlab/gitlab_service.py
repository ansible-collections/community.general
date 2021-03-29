#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Raphaël Droz <raphael@droz.eu>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: gitlab_service
short_description: Setup or delete GitLab integration services
version_added: '2.4.0'
description:
  - Creates, updates or deletes GitLab services (aka "integrations").
author:
  - Raphaël Droz (@drzraf)
requirements:
  - python >= 2.6
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
      - The ID or path of the project (urlencoded or not).
    required: true
    type: str
  active:
    description:
      - Not yet supported (U(https://gitlab.com/gitlab-org/gitlab-ce/issues/41113)).
    type: bool
    default: yes
  service:
    description:
      - The service
    required: true
    type: str
    choices:
      - asana
      - assembla
      - bamboo
      - bugzilla
      - buildkite
      - campfire
      - custom-issue-tracker
      - discord
      - drone-ci
      - emails-on-push
      - external-wiki
      - flowdock
      - hangouts-chat
      - hipchat
      - irker
      - jira
      - mattermost
      - mattermost-slash-commands
      - microsoft-teams
      - packagist
      - pipelines-email
      - pivotaltracker
      - prometheus
      - pushover
      - redmine
      - slack
      - slack-slash-commands
      - teamcity
      - unify-circuit
      - webex-teams
      - youtrack
  params:
    description:
      - The description of the service, see documentation U(https://docs.gitlab.com/ee/api/services.html)
    type: dict
  events:
    description:
      - The events that trigger the service (required if I(state=present))
    choices: ["push", "issues", "confidential_issues", "merge_requests", "tag_push", "note", "confidential_note", "job", "pipeline", "wiki_page"]
    default: ["push", "issues", "confidential_issues", "merge_requests", "tag_push", "note", "confidential_note", "job", "pipeline", "wiki_page"]
    type: list
    elements: str
  state:
    description:
      - Create or delete a service.
      - Possible values are C(present) and C(absent).
    default: "present"
    choices: ["present", "absent"]
    type: str
'''

EXAMPLES = '''
# Setup email on push for this project
- name: emails me on push
  community.general.gitlab_service:
    api_url: https://gitlab.com
    api_token: foobar
    project: 123456
    service: emails-on-push
    params:
      recipients: foo@example.com
      disable_diffs: true
    state: present
  delegate_to: localhost

# This will always be set to change because a non-null token is mandatory
- name: trigger packagist update on push events (only)
  community.general.gitlab_service:
    api_url: https://gitlab.com
    api_token: foobar
    project: foo/proj
    service: packagist
    events: ["push"]
    params:
      username: foo
      token: bar
      server: https://packagist.org
  delegate_to: localhost

- Idempotency is only partially provided since GitLab does
  not expose secret parameters like tokens or passwords.
  See U(https://gitlab.com/gitlab-org/gitlab-ce/issues/46313)
'''

RETURN = '''
---
service:
  description: A dict containing key/value pairs representing GitLab service
  returned: success
  type: dict
  sample:
    id: 40812345
    push_events: true
    issues_events: true
    confidential_issues_events: true
    merge_requests_events: true
    tag_push_events: true
    note_events: true
    confidential_note_events: true
    job_events: true
    pipeline_events: true
    wiki_page_events: true
    recipients: me@example.com
    disable_diffs: null
    send_from_committer_email: null
    title: Emails on push
    created_at: '2018-05-13T03:08:07.943Z'
    updated_at: '2018-05-13T03:09:17.651Z'
    active: true
    properties:
      send_from_committer_email: null
      disable_diffs: null
      recipients: me@example.com
    project_id: 1234567
state:
  description: A string indicating whether the service was "created" or "changed"
  returned: success
  type: str
  sample: created
'''

import traceback

from ansible.module_utils.six import iteritems

GITLAB_IMP_ERR = None
try:
    import gitlab
    HAS_GITLAB_PACKAGE = True
except ImportError:
    GITLAB_IMP_ERR = traceback.format_exc()
    HAS_GITLAB_PACKAGE = False

from ansible.module_utils.api import basic_auth_argument_spec
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils._text import to_native

from ansible_collections.community.general.plugins.module_utils.gitlab import findProject, gitlabAuthentication

# auto-generated 2020/07/09 from https://gitlab.com/gitlab-org/gitlab/-/blob/master/lib/api/helpers/services_helpers.rb
RAW_SERVICES_DEFINITIONS = {"asana":{"api_key":{"required":1}, "restrict_to_branch":{}},
                            "assembla":{"token":{"required":1}, "subdomain":{}},
                            "bamboo":{"bamboo_url":{"required":1}, "build_key":{"required":1}, "username":{"required":1}, "password":{"required":1}},
                            "bugzilla":{"new_issue_url":{"required":1}, "issues_url":{"required":1}, "project_url":{"required":1}},
                            "buildkite":{"token":{"required":1}, "project_url":{"required":1}, "enable_ssl_verification":{"type":"bool"}},
                            "campfire":{"token":{"required":1}, "subdomain":{}, "room":{}},
                            "confluence":{"confluence_url":{"required":1}},
                            "custom-issue-tracker":{"new_issue_url":{"required":1}, "issues_url":{"required":1}, "project_url":{"required":1}},
                            "datadog":{"api_key":{"required":1}, "datadog_site":{}, "api_url":{}, "datadog_service":{}, "datadog_env":{}},
                            "discord":{"webhook":{"required":1}},
                            "drone-ci":{"token":{"required":1}, "drone_url":{"required":1}, "enable_ssl_verification":{"type":"bool"}},
                            "emails-on-push":{"recipients":{"required":1}, "disable_diffs":{"type":"bool"}, "send_from_committer_email":{"type":"bool"},
                                              "branches_to_be_notified":{}},
                            "external-wiki":{"external_wiki_url":{"required":1}},
                            "flowdock":{"token":{"required":1}},
                            "hangouts-chat":{"webhook":{"required":1}, "branches_to_be_notified":{}, "push_events":{"type":"bool"},
                                             "issues_events":{"type":"bool"}, "confidential_issues_events":{"type":"bool"},
                                             "merge_requests_events":{"type":"bool"}, "note_events":{"type":"bool"},
                                             "confidential_note_events":{"type":"bool"}, "tag_push_events":{"type":"bool"},
                                             "pipeline_events":{"type":"bool"}, "wiki_page_events":{"type":"bool"}},
                            "hipchat":{"token":{"required":1}, "room":{}, "color":{}, "notify":{"type":"bool"}, "api_version":{}, "server":{}},
                            "irker":{"recipients":{"required":1}, "default_irc_uri":{}, "server_host":{}, "server_port":{"type":"int"},
                                     "colorize_messages":{"type":"bool"}},
                            "jenkins":{"jenkins_url":{"required":1}, "project_name":{"required":1}, "username":{}, "password":{}},
                            "jira":{"url":{"required":1}, "api_url":{}, "username":{"required":1}, "password":{"required":1},
                                    "jira_issue_transition_id":{}, "comment_on_event_enabled":{"type":"bool"}},
                            "mattermost-slash-commands":{"token":{"required":1}},
                            "slack-slash-commands":{"token":{"required":1}},
                            "packagist":{"username":{"required":1}, "token":{"required":1}, "server":{}},
                            "pipelines-email":{"recipients":{"required":1}, "notify_only_broken_pipelines":{"type":"bool"}, "branches_to_be_notified":{}},
                            "pivotaltracker":{"token":{"required":1}, "restrict_to_branch":{}},
                            "prometheus":{"api_url":{"required":1}, "google_iap_audience_client_id":{"required":1},
                            "google_iap_service_account_json":{"required":1}},
                            "pushover":{"api_key":{"required":1}, "user_key":{"required":1}, "priority":{"required":1},
                                        "device":{"required":1}, "sound":{"required":1}},
                            "redmine":{"new_issue_url":{"required":1}, "project_url":{"required":1}, "issues_url":{"required":1}},
                            "ewm":{"new_issue_url":{"required":1}, "project_url":{"required":1}, "issues_url":{"required":1}},
                            "youtrack":{"project_url":{"required":1}, "issues_url":{"required":1}},
                            "slack":{"webhook":{"required":1}, "username":{}, "channel":{}, "branches_to_be_notified":{},
                                     "notify_only_broken_pipelines":{"type":"bool"}, "push_channel":{}, "issue_channel":{},
                                     "confidential_issue_channel":{}, "merge_request_channel":{}, "note_channel":{},
                                     "tag_push_channel":{}, "pipeline_channel":{}, "wiki_page_channel":{}, "push_events":{"type":"bool"},
                                     "issues_events":{"type":"bool"}, "confidential_issues_events":{"type":"bool"},
                                     "merge_requests_events":{"type":"bool"}, "note_events":{"type":"bool"}, "confidential_note_events":{"type":"bool"},
                                     "tag_push_events":{"type":"bool"}, "pipeline_events":{"type":"bool"}, "wiki_page_events":{"type":"bool"}},
                            "microsoft-teams":{"webhook":{"required":1}, "branches_to_be_notified":{}, "notify_only_broken_pipelines":{"type":"bool"}},
                            "mattermost":{"webhook":{"required":1}, "username":{}, "channel":{}, "branches_to_be_notified":{},
                                          "notify_only_broken_pipelines":{"type":"bool"}, "push_channel":{}, "issue_channel":{},
                                          "confidential_issue_channel":{}, "merge_request_channel":{}, "note_channel":{},
                                          "tag_push_channel":{}, "pipeline_channel":{}, "wiki_page_channel":{}, "push_events":{"type":"bool"},
                                          "issues_events":{"type":"bool"}, "confidential_issues_events":{"type":"bool"},
                                          "merge_requests_events":{"type":"bool"}, "note_events":{"type":"bool"},
                                          "confidential_note_events":{"type":"bool"}, "tag_push_events":{"type":"bool"},
                                          "pipeline_events":{"type":"bool"}, "wiki_page_events":{"type":"bool"}},
                            "teamcity":{"teamcity_url":{"required":1}, "build_type":{"required":1}, "username":{"required":1},
                                        "password":{"required":1}},
                            "unify-circuit":{"webhook":{"required":1}, "push_events":{"type":"bool"}, "issues_events":{"type":"bool"},
                                             "confidential_issues_events":{"type":"bool"}, "merge_requests_events":{"type":"bool"},
                                             "note_events":{"type":"bool"}, "confidential_note_events":{"type":"bool"},
                                             "tag_push_events":{"type":"bool"}, "pipeline_events":{"type":"bool"}, "wiki_page_events":{"type":"bool"}},
                            "webex-teams":{"webhook":{"required":1}, "push_events":{"type":"bool"}, "issues_events":{"type":"bool"},
                                           "confidential_issues_events":{"type":"bool"}, "merge_requests_events":{"type":"bool"},
                                           "note_events":{"type":"bool"}, "confidential_note_events":{"type":"bool"},
                                           "tag_push_events":{"type":"bool"}, "pipeline_events":{"type":"bool"}, "wiki_page_events":{"type":"bool"}}}



def init_definitions():
    for params in RAW_SERVICES_DEFINITIONS.values():
        for name, definition in params.items():
            if 'type' in definition:
                definition['type'] = bool if definition['type'] == 'bool' else int if definition['type'] == 'int' else definition['type']
            if name in GitLab_Services.credentialParams:
                definition['no_log'] = True
    return RAW_SERVICES_DEFINITIONS


class GitLab_Services(object):
    HOOK_EVENTS = ['push', 'issues', 'confidential_issues', 'merge_requests', 'tag_push', 'note', 'confidential_note', 'job', 'pipeline', 'wiki_page']
    credentialParams = ['password', 'token', 'api_key']

    def __init__(self, module, name):
        self._module = module
        self.name = name

    # "create" can only happen once for this service during the life of the project)
    # merge new attributes in the object retrieved from the server
    def create(self, remote_service, active, params, events):
        local_service = self.as_api_object(active, params, events)
        for k, v in local_service.items():
            setattr(remote_service, k, v)
        if not self._module.check_mode:
            remote_service.save()
        return {'before': {}, 'after': str(remote_service.attributes)}

    def update(self, remote, active, params, events):
        diff = not self.equals(remote.attributes, active, params, events)
        if diff:
            # remote.active = active
            for k, v in self.expand_events(events).items():
                setattr(remote, k, v)
            # when saving, params does directly in the request
            # (remember they get retrieved under the "property" key of the remote dict())
            for k, v in params.items():
                setattr(remote, k, v)
            if not self._module.check_mode:
                remote.save()
            return remote

        return False

    def as_api_object(self, active, params, events):
        obj = {'active': active}
        obj.update(self.expand_events(events))
        obj.update(params)
        return obj

    def expand_events(self, events):
        try:
            # See https://gitlab.com/gitlab-org/gitlab-ce/issues/58321 for why it's useful to
            # discard unsupported events before comparing
            supported_events = RAW_SERVICES_DEFINITIONS[self.name]['_events']
        except KeyError:
            supported_events = None
        # ret = {value + '_events': bool(value in events) for value in self.HOOK_EVENTS if supported_events is None or value in supported_events}
        # python2.6 remove-me:
        ret = {}
        for value in iteritems(self.HOOK_EVENTS):
            if supported_events is None or value in supported_events:
                ret[value + '_events'] = bool(value in events)
        return ret

    @staticmethod
    def events_equal(obj, events):
        return all((k in obj and obj[k] == v) for k, v in events.items())

    @staticmethod
    def has_credentials(attr):
        return ('password' in attr and attr['password']) or ('token' in attr and attr['token']) or ('api_key' in attr and attr['api_key'])

    def equals(self, prev_attr, active, params, events):
        # filtered_params = {k: v for k, v in params.items() if k not in self.credentialParams}
        # python2.6 remove-me:
        filtered_params = {}
        for k, v in iteritems(params):
            if k not in self.credentialParams:
                filtered_params[k] = v

        if prev_attr['active'] != active:
            self._module.debug("active status differs")
            return False
        if self.has_credentials(params):
            self._module.debug("has credentials: assuming difference")
            return False
        if not self.events_equal(prev_attr, self.expand_events(events)):
            self._module.debug("events differs: %s != %s" % (prev_attr, events))
            return False
        if prev_attr['properties'] != filtered_params:
            self._module.debug("services attributes differs: %s != %s" % (prev_attr['properties'], filtered_params))
            return False
        return True

    def setattrs(self, obj, new_attr):
        for k, v in new_attr.items():
            setattr(obj, k, v)


def main():
    definitions = init_definitions()

    base_spec = basic_auth_argument_spec()
    base_spec.update(dict(
        api_token=dict(type='str', no_log=True),
        project=dict(required=True),
        service=dict(required=True, type='str', choices=list(definitions.keys())),
        active=dict(required=False, default=True, type='bool'),
        params=dict(required=False, type='dict'),
        events=dict(required=False, type='list', elements='str', default=GitLab_Services.HOOK_EVENTS, choices=GitLab_Services.HOOK_EVENTS),
        state=dict(default='present', choices=['present', 'absent']),
    ))

    constraints = dict(
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
        required_if=[
            ['state', 'present', ['params']]
        ],
        supports_check_mode=True
    )

    stub_init = AnsibleModule(argument_spec=base_spec, **constraints)
    service = stub_init.params['service']
    state = stub_init.params['state']
    if state == 'present':
        # since we know the service (which has been validated), recreate a module_specs to validate suboptions
        # sub_arg_specs = {i: definitions[service][i] for i in definitions[service] if i != '_events'}
        # python2.6 remove-me:
        sub_arg_specs = {}
        for i in iteritems(definitions[service]):
            if i != '_events':
                sub_arg_specs[i] = definitions[service][i]

        base_spec['params'] = dict(required=False, type='dict', options=sub_arg_specs)
        if '_events' in definitions[service]:
            base_spec['events'] = dict(required=True, type='list', elements='str', choices=definitions[service]['_events'])
        module = AnsibleModule(argument_spec=base_spec, **constraints)
    else:
        module = stub_init

    project = module.params['project']
    active = True
    # active = module.params['active']
    params = module.params['params']
    events = module.params['events']

    if not HAS_GITLAB_PACKAGE:
        module.fail_json(msg=missing_required_lib("python-gitlab"), exception=GITLAB_IMP_ERR)

    gitlab_instance = gitlabAuthentication(module)

    try:
        project = gitlab_instance.projects.get(project)
    except gitlab.GitlabGetError as e:
        module.fail_json(msg='No such a project %s' % project, exception=to_native(e))

    try:
        remote_service = project.services.get(service)
        original_attributes = remote_service.attributes.copy()
    except gitlab.GitlabGetError as e:
        module.fail_json(msg='No such a service %s' % service, exception=to_native(e))

    Services_Helper = GitLab_Services(module, service)
    if state == 'absent':
        if not remote_service or not remote_service.created_at:
            module.exit_json(changed=False, service={}, msg='Service not found', details='Service %s not found' % service)
        else:
            try:
                if not module.check_mode:
                    remote_service.delete()
            except (gitlab.GitlabHttpError, gitlab.GitlabDeleteError) as e:
                module.fail_json(msg='Failed to remove service %s' % service, exception=to_native(e))
            else:
                module.exit_json(changed=True, service=remote_service.attributes, msg='Successfully deleted service %s' % service)

    else:
        if remote_service.created_at:
            # update
            try:
                h = Services_Helper.update(remote_service, active, params, events)
            except gitlab.GitlabUpdateError as e:
                module.fail_json(changed=False, msg='Could not update service %s' % service, exception=to_native(e))
            else:
                diff = {'before': original_attributes,
                        'after': remote_service.attributes if module.check_mode else project.services.get(service).attributes} if module._diff else None
                if h:
                    module.exit_json(changed=True, service=remote_service.attributes, diff=diff, state='changed',
                                     msg='Successfully updated service %s' % service)
                else:
                    module.exit_json(changed=False)

        else:
            try:
                diff = Services_Helper.create(remote_service, active, params, events)
            except (gitlab.GitlabCreateError, gitlab.GitlabUpdateError) as e:
                module.fail_json(changed=False, msg='Could not create service %s' % service, exception=to_native(e))
            else:
                module.exit_json(changed=True, service=remote_service.attributes, diff=diff, state='created',
                                 msg='Successfully created service %s' % service)


if __name__ == '__main__':
    main()
