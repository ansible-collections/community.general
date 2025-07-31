#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2020, Adam Vaughan (@adamvaughan) avaughan@pagerduty.com
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r"""
module: pagerduty_change
short_description: Track a code or infrastructure change as a PagerDuty change event
version_added: 1.3.0
description:
  - This module lets you create a PagerDuty change event each time the module is run.
  - This is not an idempotent action and a new change event is created each time it is run.
author:
  - Adam Vaughan (@adamvaughan)
requirements:
  - PagerDuty integration key
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
    details:
      - Check mode simply does nothing except returning C(changed=true) in case the O(url) seems to be correct.
  diff_mode:
    support: none
options:
  integration_key:
    description:
      - The integration key that identifies the service the change was made to. This can be found by adding an integration
        to a service in PagerDuty.
    required: true
    type: str
  summary:
    description:
      - A short description of the change that occurred.
    required: true
    type: str
  source:
    description:
      - The source of the change event.
    default: Ansible
    type: str
  user:
    description:
      - The name of the user or process that triggered this deployment.
    type: str
  repo:
    description:
      - The URL of the project repository.
    required: false
    type: str
  revision:
    description:
      - An identifier of the revision being deployed, typically a number or SHA from a version control system.
    required: false
    type: str
  environment:
    description:
      - The environment name, typically V(production), V(staging), and so on.
    required: false
    type: str
  link_url:
    description:
      - A URL where more information about the deployment can be obtained.
    required: false
    type: str
  link_text:
    description:
      - Descriptive text for a URL where more information about the deployment can be obtained.
    required: false
    type: str
  url:
    description:
      - URL to submit the change event to.
    required: false
    default: https://events.pagerduty.com/v2/change/enqueue
    type: str
  validate_certs:
    description:
      - If V(false), SSL certificates for the target URL are not validated. This should only be used on personally controlled
        sites using self-signed certificates.
    required: false
    default: true
    type: bool
"""

EXAMPLES = r"""
- name: Track the deployment as a PagerDuty change event
  community.general.pagerduty_change:
    integration_key: abc123abc123abc123abc123abc123ab
    summary: The application was deployed

- name: Track the deployment as a PagerDuty change event with more details
  community.general.pagerduty_change:
    integration_key: abc123abc123abc123abc123abc123ab
    summary: The application was deployed
    source: Ansible Deploy
    user: ansible
    repo: github.com/ansible/ansible
    revision: '4.2'
    environment: production
    link_url: https://github.com/ansible-collections/community.general/pull/1269
    link_text: View changes on GitHub
"""

from ansible.module_utils.urls import fetch_url
from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.general.plugins.module_utils.datetime import (
    now,
)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            integration_key=dict(required=True, type='str', no_log=True),
            summary=dict(required=True, type='str'),
            source=dict(default='Ansible', type='str'),
            user=dict(type='str'),
            repo=dict(type='str'),
            revision=dict(type='str'),
            environment=dict(type='str'),
            link_url=dict(type='str'),
            link_text=dict(type='str'),
            url=dict(default='https://events.pagerduty.com/v2/change/enqueue', type='str'),
            validate_certs=dict(default=True, type='bool')
        ),
        supports_check_mode=True
    )

    # API documented at https://developer.pagerduty.com/docs/events-api-v2/send-change-events/

    url = module.params['url']
    headers = {'Content-Type': 'application/json'}

    if module.check_mode:
        _response, info = fetch_url(
            module, url, headers=headers, method='POST')

        if info['status'] == 400:
            module.exit_json(changed=True)
        else:
            module.fail_json(
                msg='Checking the PagerDuty change event API returned an unexpected response: %d' % (info['status']))

    custom_details = {}

    if module.params['user']:
        custom_details['user'] = module.params['user']

    if module.params['repo']:
        custom_details['repo'] = module.params['repo']

    if module.params['revision']:
        custom_details['revision'] = module.params['revision']

    if module.params['environment']:
        custom_details['environment'] = module.params['environment']

    timestamp = now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    payload = {
        'summary': module.params['summary'],
        'source': module.params['source'],
        'timestamp': timestamp,
        'custom_details': custom_details
    }

    event = {
        'routing_key': module.params['integration_key'],
        'payload': payload
    }

    if module.params['link_url']:
        link = {
            'href': module.params['link_url']
        }

        if module.params['link_text']:
            link['text'] = module.params['link_text']

        event['links'] = [link]

    _response, info = fetch_url(
        module, url, data=module.jsonify(event), headers=headers, method='POST')

    if info['status'] == 202:
        module.exit_json(changed=True)
    else:
        module.fail_json(
            msg='Creating PagerDuty change event failed with %d' % (info['status']))


if __name__ == '__main__':
    main()
