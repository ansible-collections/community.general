#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2022, Raphaël Droz <raphael@droz.eu>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: gitlab_integration
short_description: Setup or delete GitLab integrations
version_added: '4.5.0'
description:
  - Creates, updates, or deletes GitLab integrations formerly known as "services".
author:
  - Raphaël Droz (@drzraf)
requirements:
  - python-gitlab python module
extends_documentation_fragment:
  - community.general.auth_basic
  - community.general.gitlab

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
  # TODO: Not yet supported (U(https://gitlab.com/gitlab-org/gitlab/-/issues/20425)).
  # active:
  #   description:
  #     - Whether the integration is active or not.
  #   type: bool
  #   default: true
  integration:
    description:
      - The type of integration.
    required: true
    type: str
    choices:
      - asana
      - assembla
      - bamboo
      - bugzilla
      - buildkite
      - campfire
      - confluence
      - custom-issue-tracker
      - datadog
      - discord
      - drone-ci
      - emails-on-push
      - ewm
      - external-wiki
      - flowdock
      - hangouts-chat
      - irker
      - jenkins
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
      - shimo
      - slack
      - slack-slash-commands
      - teamcity
      - unify-circuit
      - webex-teams
      - youtrack
      - zentao
  params:
    description:
      - The description of the integration, see documentation at U(https://docs.gitlab.com/ee/api/integrations.html).
    type: dict
  events:
    description:
      - The events that trigger the integration.
      - Required if I(state=present).
    choices: ["push", "issues", "confidential_issues", "merge_requests", "tag_push", "note", "confidential_note", "job", "pipeline", "wiki_page"]
    default: ["push", "issues", "confidential_issues", "merge_requests", "tag_push", "note", "confidential_note", "job", "pipeline", "wiki_page"]
    type: list
    elements: str
  state:
    description:
      - Create or delete an integration.
      - Possible values are C(present) and C(absent).
    default: "present"
    choices: ["present", "absent"]
    type: str
'''

EXAMPLES = '''
# Setup email on push for this project
- name: Email me on push
  community.general.gitlab_integration:
    api_url: https://gitlab.com
    api_token: foobar
    project: 123456
    integration: emails-on-push
    params:
      recipients: foo@example.com
      disable_diffs: true
    state: present
  delegate_to: localhost

# This will always be set to change because a non-null token is mandatory
- name: Trigger packagist update on push events (only)
  community.general.gitlab_integration:
    api_url: https://gitlab.com
    api_token: foobar
    project: foo/proj
    integration: packagist
    events: ["push"]
    params:
      username: foo
      token: bar
      server: https://packagist.org
  no_log: True
  delegate_to: localhost

- Idempotency is only partially provided since GitLab does
  not expose secret parameters like tokens or passwords.
  See U(https://gitlab.com/gitlab-org/gitlab/-/issues/22237)
'''

RETURN = '''
---
integration:
  description: A dict containing key/value pairs representing GitLab integration
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
  description: A string indicating whether the integration was "created" or "changed"
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
from ansible.module_utils.common.text.converters import to_native

from ansible_collections.community.general.plugins.module_utils.gitlab import auth_argument_spec, gitlab_authentication

'''
This dict has been auto-generated 2022/02/17 from https://gitlab.com/gitlab-org/gitlab-foss/-/blob/master/lib/api/helpers/integrations_helpers.rb
following these steps:
1. Download above-mentioned file.
2. Prepend:
```ruby
require 'json'
class Boolean
end
```

3. Append:
```ruby
services = API::Helpers::IntegrationsHelpers.integrations
no_log_keys = [:api_key, :webhook, :token, :password]
services.each do |service_slug, params|
  new_settings = {}
  params.each do |entry|
    e = {}
    if (entry[:required] === true)
      e[:required] = 1
    end
    if (entry[:type] == String)
      e[:type] = "str"
    elsif (entry[:type] == Integer)
      e[:type] = "int"
    elsif (entry[:type] == Boolean)
      e[:type] = "bool"
    else
      e[:type] = entry[:type]
    end
    if (no_log_keys.find_index(entry[:name])) != nil
      e[:no_log] = true
    end
    new_settings[entry[:name]] = e
  end
  services[service_slug] = new_settings
end
services = Hash[*services.sort.flatten]
puts JSON.generate(services, options = {
  indent:'',
  space: ' '
}).gsub(/}},/, "}},\n").gsub(/,(?![ ])/, ', ').gsub(/\btrue\b/, 'True')
```
3. Run and wrap/fold/indent
'''

SRV_DEF = {"asana": {"api_key": {"required": 1, "type": "str", "no_log": True}, "restrict_to_branch": {"type": "str"}},
           "assembla": {"token": {"required": 1, "type": "str", "no_log": True}, "subdomain": {"type": "str"}},
           "bamboo": {"bamboo_url": {"required": 1, "type": "str"}, "enable_ssl_verification": {"type": "bool"},
                      "build_key": {"required": 1, "type": "str"}, "username": {"required": 1, "type": "str"},
                      "password": {"required": 1, "type": "str", "no_log": True}},
           "bugzilla": {"new_issue_url": {"required": 1, "type": "str"}, "issues_url": {"required": 1, "type": "str"},
                        "project_url": {"required": 1, "type": "str"}},
           "buildkite": {"token": {"required": 1, "type": "str", "no_log": True}, "project_url": {"required": 1, "type": "str"},
                         "enable_ssl_verification": {"type": "bool"}},
           "campfire": {"token": {"required": 1, "type": "str", "no_log": True}, "subdomain": {"type": "str"}, "room": {"type": "str"}},
           "confluence": {"confluence_url": {"required": 1, "type": "str"}},
           "custom-issue-tracker": {"new_issue_url": {"required": 1, "type": "str"}, "issues_url": {"required": 1, "type": "str"},
                                    "project_url": {"required": 1, "type": "str"}},
           "datadog": {"api_key": {"required": 1, "type": "str", "no_log": True}, "datadog_site": {"type": "str"}, "api_url": {"type": "str"},
                       "datadog_service": {"type": "str"}, "datadog_env": {"type": "str"}, "datadog_tags": {"type": "str"}},
           "discord": {"webhook": {"required": 1, "type": "str", "no_log": True}},
           "drone-ci": {"token": {"required": 1, "type": "str", "no_log": True}, "drone_url": {"required": 1, "type": "str"},
                        "enable_ssl_verification": {"type": "bool"}},
           "emails-on-push": {"recipients": {"required": 1, "type": "str"}, "disable_diffs": {"type": "bool"},
                              "send_from_committer_email": {"type": "bool"}, "branches_to_be_notified": {"type": "str"}},
           "ewm": {"new_issue_url": {"required": 1, "type": "str"}, "project_url": {"required": 1, "type": "str"},
                   "issues_url": {"required": 1, "type": "str"}},
           "external-wiki": {"external_wiki_url": {"required": 1, "type": "str"}},
           "flowdock": {"token": {"required": 1, "type": "str", "no_log": True}},
           "hangouts-chat": {"webhook": {"required": 1, "type": "str", "no_log": True}, "branches_to_be_notified": {"type": "str"},
                             "push_events": {"type": "bool"}, "issues_events": {"type": "bool"}, "confidential_issues_events": {"type": "bool"},
                             "merge_requests_events": {"type": "bool"}, "note_events": {"type": "bool"}, "confidential_note_events": {"type": "bool"},
                             "tag_push_events": {"type": "bool"}, "pipeline_events": {"type": "bool"}, "wiki_page_events": {"type": "bool"}},
           "irker": {"recipients": {"required": 1, "type": "str"}, "default_irc_uri": {"type": "str"}, "server_host": {"type": "str"},
                     "server_port": {"type": "int"}, "colorize_messages": {"type": "bool"}},
           "jenkins": {"jenkins_url": {"required": 1, "type": "str"}, "enable_ssl_verification": {"type": "bool"},
                       "project_name": {"required": 1, "type": "str"}, "username": {"type": "str"}, "password": {"type": "str", "no_log": True}},
           "jira": {"url": {"required": 1, "type": "str"}, "api_url": {"type": "str"}, "username": {"required": 1, "type": "str"},
                    "password": {"required": 1, "type": "str", "no_log": True}, "jira_issue_transition_automatic": {"type": "bool"},
                    "jira_issue_transition_id": {"type": "str"}, "comment_on_event_enabled": {"type": "bool"}},
           "mattermost": {"webhook": {"required": 1, "type": "str", "no_log": True}, "username": {"type": "str"}, "channel": {"type": "str"},
                          "branches_to_be_notified": {"type": "str"}, "notify_only_broken_pipelines": {"type": "bool"}, "push_channel": {"type": "str"},
                          "issue_channel": {"type": "str"}, "confidential_issue_channel": {"type": "str"}, "merge_request_channel": {"type": "str"},
                          "note_channel": {"type": "str"}, "tag_push_channel": {"type": "str"}, "pipeline_channel": {"type": "str"},
                          "wiki_page_channel": {"type": "str"}, "push_events": {"type": "bool"}, "issues_events": {"type": "bool"},
                          "confidential_issues_events": {"type": "bool"}, "merge_requests_events": {"type": "bool"}, "note_events": {"type": "bool"},
                          "confidential_note_events": {"type": "bool"}, "tag_push_events": {"type": "bool"}, "pipeline_events": {"type": "bool"},
                          "wiki_page_events": {"type": "bool"}},
           "mattermost-slash-commands": {"token": {"required": 1, "type": "str", "no_log": True}},
           "microsoft-teams": {"webhook": {"required": 1, "type": "str", "no_log": True}, "branches_to_be_notified": {"type": "str"},
                               "notify_only_broken_pipelines": {"type": "bool"}},
           "packagist": {"username": {"required": 1, "type": "str"}, "token": {"required": 1, "type": "str", "no_log": True},
                         "server": {"type": "str"}},
           "pipelines-email": {"recipients": {"required": 1, "type": "str"}, "notify_only_broken_pipelines": {"type": "bool"},
                               "branches_to_be_notified": {"type": "str"}},
           "pivotaltracker": {"token": {"required": 1, "type": "str", "no_log": True}, "restrict_to_branch": {"type": "str"}},
           "prometheus": {"api_url": {"required": 1, "type": "str"}, "google_iap_audience_client_id": {"required": 1, "type": "str"},
                          "google_iap_service_account_json": {"required": 1, "type": "str"}},
           "pushover": {"api_key": {"required": 1, "type": "str", "no_log": True}, "user_key": {"required": 1, "type": "str"},
                        "priority": {"required": 1, "type": "str"}, "device": {"required": 1, "type": "str"}, "sound": {"required": 1, "type": "str"}},
           "redmine": {"new_issue_url": {"required": 1, "type": "str"}, "project_url": {"required": 1, "type": "str"},
                       "issues_url": {"required": 1, "type": "str"}},
           "shimo": {"external_wiki_url": {"required": 1, "type": "str"}},
           "slack": {"webhook": {"required": 1, "type": "str", "no_log": True}, "username": {"type": "str"}, "channel": {"type": "str"},
                     "branches_to_be_notified": {"type": "str"}, "notify_only_broken_pipelines": {"type": "bool"}, "push_channel": {"type": "str"},
                     "issue_channel": {"type": "str"}, "confidential_issue_channel": {"type": "str"}, "merge_request_channel": {"type": "str"},
                     "note_channel": {"type": "str"}, "tag_push_channel": {"type": "str"}, "pipeline_channel": {"type": "str"},
                     "wiki_page_channel": {"type": "str"}, "push_events": {"type": "bool"}, "issues_events": {"type": "bool"},
                     "confidential_issues_events": {"type": "bool"}, "merge_requests_events": {"type": "bool"}, "note_events": {"type": "bool"},
                     "confidential_note_events": {"type": "bool"}, "tag_push_events": {"type": "bool"}, "pipeline_events": {"type": "bool"},
                     "wiki_page_events": {"type": "bool"}},
           "slack-slash-commands": {"token": {"required": 1, "type": "str", "no_log": True}},
           "teamcity": {"teamcity_url": {"required": 1, "type": "str"}, "enable_ssl_verification": {"type": "bool"},
                        "build_type": {"required": 1, "type": "str"}, "username": {"required": 1, "type": "str"},
                        "password": {"required": 1, "type": "str", "no_log": True}},
           "unify-circuit": {"webhook": {"required": 1, "type": "str", "no_log": True}, "push_events": {"type": "bool"},
                             "issues_events": {"type": "bool"}, "confidential_issues_events": {"type": "bool"}, "merge_requests_events": {"type": "bool"},
                             "note_events": {"type": "bool"}, "confidential_note_events": {"type": "bool"}, "tag_push_events": {"type": "bool"},
                             "pipeline_events": {"type": "bool"}, "wiki_page_events": {"type": "bool"}},
           "webex-teams": {"webhook": {"required": 1, "type": "str", "no_log": True}, "push_events": {"type": "bool"},
                           "issues_events": {"type": "bool"}, "confidential_issues_events": {"type": "bool"}, "merge_requests_events": {"type": "bool"},
                           "note_events": {"type": "bool"}, "confidential_note_events": {"type": "bool"}, "tag_push_events": {"type": "bool"},
                           "pipeline_events": {"type": "bool"}, "wiki_page_events": {"type": "bool"}},
           "youtrack": {"project_url": {"required": 1, "type": "str"}, "issues_url": {"required": 1, "type": "str"}},
           "zentao": {"url": {"required": 1, "type": "str"}, "api_url": {"type": "str"}, "api_token": {"required": 1, "type": "str"},
                      "zentao_product_xid": {"required": 1, "type": "str"}}}


class GitLabIntegrations(object):
    HOOK_EVENTS = ['push', 'issues', 'confidential_issues', 'merge_requests', 'tag_push', 'note', 'confidential_note', 'job', 'pipeline', 'wiki_page']
    CREDENTIAL_PARAMS = ['password', 'token', 'api_key', 'webhook']

    def __init__(self, module, name):
        self._module = module
        self.name = name

    # "create" can only happen once for this integration during the life of the project)
    # merge new attributes in the object retrieved from the server
    def create(self, remote_integration, active, params, events):
        local_integration = self.__as_api_object(active, params, events)
        for k, v in local_integration.items():
            setattr(remote_integration, k, v)
        if not self._module.check_mode:
            remote_integration.save()
        return {'before': {}, 'after': str(remote_integration.attributes)}

    def update(self, remote, active, params, events):
        diff = not self.__equals(remote.attributes, active, params, events)
        if diff:
            # remote.active = active
            for k, v in self.__expand_events(events).items():
                setattr(remote, k, v)
            # when saving, params does directly in the request
            # (remember they get retrieved under the "property" key of the remote dict())
            for k, v in params.items():
                setattr(remote, k, v)
            if not self._module.check_mode:
                remote.save()
            return remote

        return False

    def __as_api_object(self, active, params, events):
        obj = {'active': active}
        obj.update(self.__expand_events(events))
        obj.update(params)
        return obj

    def __expand_events(self, events):
        try:
            # See https://gitlab.com/gitlab-org/gitlab-ce/issues/58321 for why it's useful to
            # discard unsupported events before comparing
            supported_events = SRV_DEF[self.name]['_events']
        except KeyError:
            supported_events = None
        ret = dict((value + '_events', bool(value in events)) for value in self.HOOK_EVENTS if supported_events is None or value in supported_events)
        return ret

    @staticmethod
    def __events_equal(obj, events):
        return all((k in obj and obj[k] == v) for k, v in events.items())

    @staticmethod
    def __has_credentials(attr):
        return ('password' in attr and attr['password']) or ('token' in attr and attr['token']) or ('api_key' in attr and attr['api_key'])

    def __equals(self, prev_attr, active, params, events):
        filtered_params = dict((k, v) for k, v in params.items() if k not in self.CREDENTIAL_PARAMS)
        if prev_attr['active'] != active:
            self._module.debug("active status differs")
            return False
        if self.__has_credentials(params):
            self._module.debug("has credentials: assuming difference")
            return False
        if not self.__events_equal(prev_attr, self.__expand_events(events)):
            self._module.debug("events differs: %s != %s" % (prev_attr, events))
            return False
        if prev_attr['properties'] != filtered_params:
            self._module.debug("integrations attributes differs: %s != %s" % (prev_attr['properties'], filtered_params))
            return False
        return True

    def setattrs(self, obj, new_attr):
        for k, v in new_attr.items():
            setattr(obj, k, v)


# Equivalent of doing `AnsibleModule(argument_spec=base_spec, **constraints)`
def mimic_ansible_module_validation(specs, constraints):
    from ansible.module_utils.basic import ModuleArgumentSpecValidator, _load_params
    from ansible.module_utils.errors import UnsupportedError
    import os

    params = _load_params()
    first_level_validator = ModuleArgumentSpecValidator(specs, **constraints)
    validation_result = first_level_validator.validate(params)
    try:
        error = validation_result.errors[0]
    except IndexError:
        error = None
    # Fail for validation errors, even in check mode
    if error:
        msg = validation_result.errors.msg
        if isinstance(error, UnsupportedError):
            msg = "Unsupported parameters for ({name}) {kind}: {msg}".format(name=os.path.basename(__file__), kind='module', msg=msg)
        # Since we can't use fail_json() before AnsibleModule instanciation, we raise an Exception
        raise Exception(msg)

    return validation_result.validated_parameters

def main():
    base_spec = basic_auth_argument_spec()
    base_spec.update(auth_argument_spec())
    base_spec.update(dict(
        api_token=dict(type='str', no_log=True),
        project=dict(required=True),
        integration=dict(required=True, type='str', choices=list(SRV_DEF.keys())),
        # active=dict(required=False, default=True, type='bool'),
        params=dict(required=False, type='dict', no_log=True),
        events=dict(required=False, type='list', elements='str', default=GitLabIntegrations.HOOK_EVENTS, choices=GitLabIntegrations.HOOK_EVENTS),
        state=dict(default='present', choices=['present', 'absent']),
    ))

    constraints = dict(
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
        required_if=[
            ['state', 'present', ['params']]
        ]
    )

    # Equivalent of doing `AnsibleModule(argument_spec=base_spec, **constraints)`
    try:
        validated_params = mimic_ansible_module_validation(base_spec, constraints)
        state = validated_params['state']
        exception = None
    except Exception as e:
        # Ok, our validator found an error. Preserve it
        # so that we can fail_json() once we have an AnsibleModule ready.
        state = None
        exception = e

    # Some additional constraints once we know the top-level argument structure is correct
    if state == 'present':
        integration = validated_params['integration']
        # since we know the integration (which has been validated), recreate a module_specs to validate suboptions
        sub_arg_specs = dict((k, v) for k, v in SRV_DEF[integration].items() if k != '_events')
        base_spec['params'] = dict(required=False, type='dict', options=sub_arg_specs)
        if '_events' in SRV_DEF[integration]:
            base_spec['events'] = dict(required=True, type='list', elements='str', choices=SRV_DEF[integration]['_events'])

    constraints.update({"supports_check_mode": True})
    module = AnsibleModule(argument_spec=base_spec, **constraints)

    # fail_json() now available
    if exception:
        module.fail_json(e)

    project = module.params['project']
    active = True
    # active = module.params['active']
    params = module.params['params']
    events = module.params['events']

    if not HAS_GITLAB_PACKAGE:
        module.fail_json(msg=missing_required_lib("python-gitlab"), exception=GITLAB_IMP_ERR)

    gitlab_instance = gitlab_authentication(module)

    try:
        project = gitlab_instance.projects.get(project)
    except gitlab.GitlabGetError as e:
        module.fail_json(msg='No such a project %s' % project, exception=to_native(e))

    try:
        remote_integration = project.services.get(integration)
        original_attributes = remote_integration.attributes.copy()
    except gitlab.GitlabGetError as e:
        module.fail_json(msg='No such integration %s' % integration, exception=to_native(e))

    integrations_helper = GitLabIntegrations(module, integration)
    if state == 'absent':
        if not remote_integration or not remote_integration.created_at:
            module.exit_json(changed=False, integration={}, msg='Integration not found', details='Integration %s not found' % integration)
        else:
            try:
                if not module.check_mode:
                    remote_integration.delete()
            except (gitlab.GitlabHttpError, gitlab.GitlabDeleteError) as e:
                module.fail_json(msg='Failed to remove integration %s' % integration, exception=to_native(e))
            else:
                module.exit_json(changed=True, integration=remote_integration.attributes, msg='Successfully deleted integration %s' % integration)

    else:
        if remote_integration.created_at:
            # update
            try:
                h = integrations_helper.update(remote_integration, active, params, events)
            except gitlab.GitlabUpdateError as e:
                module.fail_json(changed=False, msg='Could not update integration %s' % integration, exception=to_native(e))
            else:
                diff = {'before': original_attributes,
                        'after': remote_integration.attributes if module.check_mode else project.services.get(integration).attributes} if module._diff else None
                if h:
                    module.exit_json(changed=True, integration=remote_integration.attributes, diff=diff, state='changed',
                                     msg='Successfully updated integration %s' % integration)
                else:
                    module.exit_json(changed=False)

        else:
            try:
                diff = integrations_helper.create(remote_integration, active, params, events)
            except (gitlab.GitlabCreateError, gitlab.GitlabUpdateError) as e:
                module.fail_json(changed=False, msg='Could not create integration %s' % integration, exception=to_native(e))
            else:
                module.exit_json(changed=True, integration=remote_integration.attributes, diff=diff, state='created',
                                 msg='Successfully created integration %s' % integration)


if __name__ == '__main__':
    main()
