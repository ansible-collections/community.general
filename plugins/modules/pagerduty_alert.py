#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''

module: pagerduty_alert
short_description: Trigger, acknowledge or resolve PagerDuty incidents
description:
    - This module will let you trigger, acknowledge or resolve a PagerDuty incident by sending events
author:
    - "Amanpreet Singh (@ApsOps)"
    - "Xiao Shen (@xshen1)"
requirements:
    - PagerDuty API access
extends_documentation_fragment:
    - community.general.attributes
attributes:
    check_mode:
        support: full
    diff_mode:
        support: none
options:
    name:
        type: str
        description:
            - PagerDuty unique subdomain. Obsolete. It is not used with PagerDuty REST v2 API.
    api_key:
        type: str
        description:
            - The pagerduty API key (readonly access), generated on the pagerduty site.
            - Required C(v1) I(api_version)
    integration_key:
        type: str
        description:
            - The GUID of one of your 'Generic API' services.
            - This is the 'integration key' listed on a 'Integrations' tab of PagerDuty service.
    service_id:
        type: str
        description:
            - ID of PagerDuty service when incidents will be triggered, acknowledged or resolved.
            - Required C(v1) I(api_version)
    service_key:
        type: str
        description:
            - The GUID of one of your 'Generic API' services. Obsolete. Please use I(integration_key).
    state:
        type: str
        description:
            - Type of event to be sent.
        required: true
        choices:
            - 'triggered'
            - 'acknowledged'
            - 'resolved'
    api_version:
        type: str
        description:
            - The API version we want to use to run the module.
            - V1 is more limited with option we can provide to trigger incident.
            - V2 has more variables for example, I(severity), I(source), I(custom_detail),etc.
        default: 'v1'
        choices:
            - 'v1'
            - 'v2'
        version_added: 6.6.0
    client:
        type: str
        description:
        - The name of the monitoring client that is triggering this event.
        required: false
    client_url:
        type: str
        description:
        -  The URL of the monitoring client that is triggering this event.
        required: false
    component:
        type: str
        description:
        -  Component of the source machine that is responsible for the event, for example C(mysql) or C(eth0).
        required: false
    custom_details:
        type: dict
        description:
        - Additional details about the event and affected system
        - A dictionary with custom keys and values.
        required: false
    desc:
        type: str
        description:
            - For C(triggered) I(state) - Required. Short description of the problem that led to this trigger. This field (or a truncated version)
              will be used when generating phone calls, SMS messages and alert emails. It will also appear on the incidents tables in the PagerDuty UI.
              The maximum length is 1024 characters.
            - For C(acknowledged) or C(resolved) I(state) - Text that will appear in the incident's log associated with this event.
        required: false
        default: Created via Ansible
    incident_class:
        type: str
        description:
        - The class/type of the event, for example C(ping failure) or C(cpu load).
        required: false
    incident_key:
        type: str
        description:
            - Identifies the incident to which this I(state) should be applied.
            - For C(triggered) I(state) - If there's no open (i.e. unresolved) incident with this key, a new one will be created. If there's already an
              open incident with a matching key, this event will be appended to that incident's log. The event key provides an easy way to 'de-dup'
              problem reports. If no I(incident_key) is provided, then it will be generated by PagerDuty.
            - For C(acknowledged) or C(resolved) I(state) - This should be the incident_key you received back when the incident was first opened by a
              trigger event. Acknowledge events referencing resolved or nonexistent incidents will be discarded.
        required: false
    link_url:
        type: str
        description:
        - Relevant link url to the alert. For example, the website or the job link
        required: false
    link_text:
        type: str
        description:
        - A short decription of the link_url.
        required: false
    source:
        type: str
        description:
        - The unique location of the affected system, preferably a hostname or FQDN.
        - Required in case of C(trigger) I(state) and C(v2) I(api_version)
        required: false
    severity:
        type: str
        description:
            - The perceived severity of the status the event is describing with respect to the affected system.
            - Required in case of C(trigger) I(state) and C(v2) I(api_version)
        default: 'critical'
        choices:
            - 'critical'
            - 'warning'
            - 'error'
            - 'info'
'''

EXAMPLES = '''
- name: Trigger an incident with just the basic options
  community.general.pagerduty_alert:
    name: companyabc
    integration_key: xxx
    api_key: yourapikey
    service_id: PDservice
    state: triggered
    desc: problem that led to this trigger

- name: Trigger an incident with more options
  community.general.pagerduty_alert:
    integration_key: xxx
    api_key: yourapikey
    service_id: PDservice
    state: triggered
    desc: problem that led to this trigger
    incident_key: somekey
    client: Sample Monitoring Service
    client_url: http://service.example.com

- name: Acknowledge an incident based on incident_key
  community.general.pagerduty_alert:
    integration_key: xxx
    api_key: yourapikey
    service_id: PDservice
    state: acknowledged
    incident_key: somekey
    desc: "some text for incident's log"

- name: Resolve an incident based on incident_key
  community.general.pagerduty_alert:
    integration_key: xxx
    api_key: yourapikey
    service_id: PDservice
    state: resolved
    incident_key: somekey
    desc: "some text for incident's log"

- name: Trigger an v2 incident with just the basic options
  community.general.pagerduty_alert:
    integration_key: xxx
    api_version: v2
    source: My Ansible Script
    state: triggered
    desc: problem that led to this trigger

- name: Trigger an v2 incident with more options
  community.general.pagerduty_alert:
    integration_key: xxx
    api_version: v2
    source: My Ansible Script
    state: triggered
    desc: problem that led to this trigger
    incident_key: somekey
    client: Sample Monitoring Service
    client_url: http://service.example.com
    component: mysql
    incident_class: ping failure
    link_url: https://pagerduty.com
    link_text: PagerDuty

- name: Acknowledge an incident based on incident_key using v2
  community.general.pagerduty_alert:
    api_version: v2
    integration_key: xxx
    incident_key: somekey
    state: acknowledged

- name: Resolve an incident based on incident_key
  community.general.pagerduty_alert:
    api_version: v2
    integration_key: xxx
    incident_key: somekey
    state: resolved
'''
import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url
from ansible.module_utils.six.moves.urllib.parse import urlparse, urlencode, urlunparse
from datetime import datetime


def check(module, name, state, service_id, integration_key, api_key, incident_key=None, http_call=fetch_url):
    url = 'https://api.pagerduty.com/incidents'
    headers = {
        "Content-type": "application/json",
        "Authorization": "Token token=%s" % api_key,
        'Accept': 'application/vnd.pagerduty+json;version=2'
    }

    params = {
        'service_ids[]': service_id,
        'sort_by': 'incident_number:desc',
        'time_zone': 'UTC'
    }
    if incident_key:
        params['incident_key'] = incident_key

    url_parts = list(urlparse(url))
    url_parts[4] = urlencode(params, True)

    url = urlunparse(url_parts)

    response, info = http_call(module, url, method='get', headers=headers)

    if info['status'] != 200:
        module.fail_json(msg="failed to check current incident status."
                             "Reason: %s" % info['msg'])

    incidents = json.loads(response.read())["incidents"]
    msg = "No corresponding incident"

    if len(incidents) == 0:
        if state in ('acknowledged', 'resolved'):
            return msg, False
        return msg, True
    elif state != incidents[0]["status"]:
        return incidents[0], True

    return incidents[0], False


def send_event_v1(module, service_key, event_type, desc,
                  incident_key=None, client=None, client_url=None):
    url = "https://events.pagerduty.com/generic/2010-04-15/create_event.json"
    headers = {
        "Content-type": "application/json"
    }

    data = {
        "service_key": service_key,
        "event_type": event_type,
        "incident_key": incident_key,
        "description": desc,
        "client": client,
        "client_url": client_url
    }

    response, info = fetch_url(module, url, method='post',
                               headers=headers, data=json.dumps(data))
    if info['status'] != 200:
        module.fail_json(msg="failed to %s. Reason: %s" %
                         (event_type, info['msg']))
    json_out = json.loads(response.read())
    return json_out


def send_event_v2(module, service_key, event_type, payload, link,
                  incident_key=None, client=None, client_url=None):
    url = "https://events.pagerduty.com/v2/enqueue"
    headers = {
        "Content-type": "application/json"
    }
    data = {
        "routing_key": service_key,
        "event_action": event_type,
        "payload": payload,
        "client": client,
        "client_url": client_url,
    }
    if link:
        data["links"] = [link]
    if incident_key:
        data["dedup_key"] = incident_key
    if event_type != "trigger":
        data.pop("payload")
    response, info = fetch_url(module, url, method="post",
                               headers=headers, data=json.dumps(data))
    if info["status"] != 202:
        module.fail_json(msg="failed to %s. Reason: %s" %
                         (event_type, info['msg']))
    json_out = json.loads(response.read())
    return json_out, True


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=False),
            api_key=dict(required=False, no_log=True),
            integration_key=dict(required=False, no_log=True),
            service_id=dict(required=False),
            service_key=dict(required=False, no_log=True),
            state=dict(
                required=True, choices=['triggered', 'acknowledged', 'resolved']
            ),
            api_version=dict(type='str', default='v1', choices=['v1', 'v2']),
            client=dict(required=False),
            client_url=dict(required=False),
            component=dict(required=False),
            custom_details=dict(required=False, type='dict'),
            desc=dict(required=False, default='Created via Ansible'),
            incident_class=dict(required=False),
            incident_key=dict(required=False, no_log=False),
            link_url=dict(required=False),
            link_text=dict(required=False),
            source=dict(required=False),
            severity=dict(
                default='critical', choices=['critical', 'warning', 'error', 'info']
            ),
        ),
        required_if=[
            ('api_version', 'v1', ['service_id', 'api_key']),
            ('state', 'acknowledged', ['incident_key']),
            ('state', 'resolved', ['incident_key']),
        ],
        required_one_of=[('service_key', 'integration_key')],
        supports_check_mode=True,
    )

    name = module.params['name']
    service_id = module.params.get('service_id')
    integration_key = module.params.get('integration_key')
    service_key = module.params.get('service_key')
    api_key = module.params.get('api_key')
    state = module.params.get('state')
    client = module.params.get('client')
    client_url = module.params.get('client_url')
    desc = module.params.get('desc')
    incident_key = module.params.get('incident_key')
    payload = {
        'summary': desc,
        'source': module.params.get('source'),
        'timestamp': datetime.now().isoformat(),
        'severity': module.params.get('severity'),
        'component': module.params.get('component'),
        'class': module.params.get('incident_class'),
        'custom_details': module.params.get('custom_details'),
    }
    link = {}
    if module.params.get('link_url'):
        link['href'] = module.params.get('link_url')
        if module.params.get('link_text'):
            link['text'] = module.params.get('link_text')
    if integration_key is None:
        integration_key = service_key
        module.warn(
            '"service_key" is obsolete parameter and will be removed.'
            ' Please, use "integration_key" instead'
        )

    state_event_dict = {
        'triggered': 'trigger',
        'acknowledged': 'acknowledge',
        'resolved': 'resolve',
    }

    event_type = state_event_dict[state]
    if module.params.get('api_version') == 'v1':
        out, changed = check(module, name, state, service_id,
                             integration_key, api_key, incident_key)
        if not module.check_mode and changed is True:
            out = send_event_v1(module, integration_key, event_type, desc,
                                incident_key, client, client_url)
    else:
        changed = True
        if event_type == 'trigger' and not payload['source']:
            module.fail_json(msg='"service" is a required variable for v2 api endpoint.')
        out, changed = send_event_v2(
            module,
            integration_key,
            event_type,
            payload,
            link,
            incident_key,
            client,
            client_url,
        )

    module.exit_json(result=out, changed=changed)


if __name__ == '__main__':
    main()
