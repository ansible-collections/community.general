#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Author: Artūras 'arturaz' Šlajus <x11@arturaz.net>
# Author: Naoya Nakazawa <naoya.n@gmail.com>
#
# This module is proudly sponsored by iGeolise (www.igeolise.com) and
# Tiny Lab Productions (www.tinylabproductions.com).
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: datadog_event
short_description: Posts events to Datadog  service
description:
- "Allows to post events to Datadog (www.datadoghq.com) service."
- "Uses http://docs.datadoghq.com/api/#events API."
author:
- "Artūras `arturaz` Šlajus (@arturaz)"
- "Naoya Nakazawa (@n0ts)"
options:
    api_key:
        type: str
        description: ["Your DataDog API key."]
        required: true
    app_key:
        type: str
        description: ["Your DataDog app key."]
        required: true
    title:
        type: str
        description: ["The event title."]
        required: true
    text:
        type: str
        description: ["The body of the event."]
        required: true
    date_happened:
        type: int
        description:
        - POSIX timestamp of the event.
        - Default value is now.
    priority:
        type: str
        description: ["The priority of the event."]
        default: normal
        choices: [normal, low]
    host:
        type: str
        description:
        - Host name to associate with the event.
        - If not specified, it defaults to the remote system's hostname.
    api_host:
        type: str
        description:
        - DataDog API endpoint URL.
        version_added: '3.3.0'
    tags:
        type: list
        elements: str
        description: ["Comma separated list of tags to apply to the event."]
    alert_type:
        type: str
        description: ["Type of alert."]
        default: info
        choices: ['error', 'warning', 'info', 'success']
    aggregation_key:
        type: str
        description: ["An arbitrary string to use for aggregation."]
    validate_certs:
        description:
            - If C(no), SSL certificates will not be validated. This should only be used
              on personally controlled sites using self-signed certificates.
        type: bool
        default: 'yes'
'''

EXAMPLES = '''
- name: Post an event with low priority
  community.general.datadog_event:
    title: Testing from ansible
    text: Test
    priority: low
    api_key: 9775a026f1ca7d1c6c5af9d94d9595a4
    app_key: j4JyCYfefWHhgFgiZUqRm63AXHNZQyPGBfJtAzmN

- name: Post an event with several tags
  community.general.datadog_event:
    title: Testing from ansible
    text: Test
    api_key: 9775a026f1ca7d1c6c5af9d94d9595a4
    app_key: j4JyCYfefWHhgFgiZUqRm63AXHNZQyPGBfJtAzmN
    tags: 'aa,bb,#host:{{ inventory_hostname }}'

- name: Post an event with several tags to another endpoint
  community.general.datadog_event:
    title: Testing from ansible
    text: Test
    api_key: 9775a026f1ca7d1c6c5af9d94d9595a4
    app_key: j4JyCYfefWHhgFgiZUqRm63AXHNZQyPGBfJtAzmN
    api_host: 'https://example.datadoghq.eu'
    tags:
      - aa
      - b
      - '#host:{{ inventory_hostname }}'

'''

import platform
import traceback

# Import Datadog
DATADOG_IMP_ERR = None
try:
    from datadog import initialize, api
    HAS_DATADOG = True
except Exception:
    DATADOG_IMP_ERR = traceback.format_exc()
    HAS_DATADOG = False

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_native


def main():
    module = AnsibleModule(
        argument_spec=dict(
            api_key=dict(required=True, no_log=True),
            app_key=dict(required=True, no_log=True),
            api_host=dict(type='str'),
            title=dict(required=True),
            text=dict(required=True),
            date_happened=dict(type='int'),
            priority=dict(default='normal', choices=['normal', 'low']),
            host=dict(),
            tags=dict(type='list', elements='str'),
            alert_type=dict(default='info', choices=['error', 'warning', 'info', 'success']),
            aggregation_key=dict(no_log=False),
            validate_certs=dict(default=True, type='bool'),
        )
    )

    # Prepare Datadog
    if not HAS_DATADOG:
        module.fail_json(msg=missing_required_lib('datadogpy'), exception=DATADOG_IMP_ERR)

    options = {
        'api_key': module.params['api_key'],
        'app_key': module.params['app_key'],
    }
    if module.params['api_host'] is not None:
        options['api_host'] = module.params['api_host']

    initialize(**options)

    _post_event(module)


def _post_event(module):
    try:
        if module.params['host'] is None:
            module.params['host'] = platform.node().split('.')[0]
        msg = api.Event.create(title=module.params['title'],
                               text=module.params['text'],
                               host=module.params['host'],
                               tags=module.params['tags'],
                               priority=module.params['priority'],
                               alert_type=module.params['alert_type'],
                               aggregation_key=module.params['aggregation_key'],
                               source_type_name='ansible')
        if msg['status'] != 'ok':
            module.fail_json(msg=msg)

        module.exit_json(changed=True, msg=msg)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=traceback.format_exc())


if __name__ == '__main__':
    main()
