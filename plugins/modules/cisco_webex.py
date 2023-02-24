#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: cisco_webex
short_description: Send a message to a Cisco Webex Teams Room or Individual
description:
    - Send a message to a Cisco Webex Teams Room or Individual with options to control the formatting.
author: Drew Rusell (@drew-russell)
notes:
  - The C(recipient_id) type must be valid for the supplied C(recipient_id).
  - Full API documentation can be found at U(https://developer.webex.com/docs/api/basics).

extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none

options:

  recipient_type:
    description:
       - The request parameter you would like to send the message to.
       - Messages can be sent to either a room or individual (by ID or E-Mail).
    required: true
    choices: ['roomId', 'toPersonEmail', 'toPersonId']
    type: str

  recipient_id:
    description:
      - The unique identifier associated with the supplied C(recipient_type).
    required: true
    type: str

  msg_type:
    description:
       - Specifies how you would like the message formatted.
    default: text
    choices: ['text', 'markdown']
    type: str
    aliases: ['message_type']

  personal_token:
    description:
      - Your personal access token required to validate the Webex Teams API.
    required: true
    aliases: ['token']
    type: str

  msg:
    description:
      - The message you would like to send.
    required: true
    type: str
'''

EXAMPLES = """
# Note: The following examples assume a variable file has been imported
# that contains the appropriate information.

- name: Cisco Webex Teams - Markdown Message to a Room
  community.general.cisco_webex:
    recipient_type: roomId
    recipient_id: "{{ room_id }}"
    msg_type: markdown
    personal_token: "{{ token }}"
    msg: "**Cisco Webex Teams Ansible Module - Room Message in Markdown**"

- name: Cisco Webex Teams - Text Message to a Room
  community.general.cisco_webex:
    recipient_type: roomId
    recipient_id: "{{ room_id }}"
    msg_type: text
    personal_token: "{{ token }}"
    msg: "Cisco Webex Teams Ansible Module - Room Message in Text"

- name: Cisco Webex Teams - Text Message by an Individuals ID
  community.general.cisco_webex:
    recipient_type: toPersonId
    recipient_id: "{{ person_id}}"
    msg_type: text
    personal_token: "{{ token }}"
    msg: "Cisco Webex Teams Ansible Module - Text Message to Individual by ID"

- name: Cisco Webex Teams - Text Message by an Individuals E-Mail Address
  community.general.cisco_webex:
    recipient_type: toPersonEmail
    recipient_id: "{{ person_email }}"
    msg_type: text
    personal_token: "{{ token }}"
    msg: "Cisco Webex Teams Ansible Module - Text Message to Individual by E-Mail"

"""

RETURN = """
status_code:
  description:
    - The Response Code returned by the Webex Teams API.
    - Full Response Code explanations can be found at U(https://developer.webex.com/docs/api/basics).
  returned: always
  type: int
  sample: 200

message:
    description:
      - The Response Message returned by the Webex Teams API.
      - Full Response Code explanations can be found at U(https://developer.webex.com/docs/api/basics).
    returned: always
    type: str
    sample: OK (585 bytes)
"""
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url


def webex_msg(module):
    """When check mode is specified, establish a read only connection, that does not return any user specific
    data, to validate connectivity. In regular mode, send a message to a Cisco Webex Teams Room or Individual"""

    # Ansible Specific Variables
    results = {}
    ansible = module.params

    headers = {
        'Authorization': 'Bearer {0}'.format(ansible['personal_token']),
        'content-type': 'application/json'
    }

    if module.check_mode:
        url = "https://webexapis.com/v1/people/me"
        payload = None

    else:
        url = "https://webexapis.com/v1/messages"

        payload = {
            ansible['recipient_type']: ansible['recipient_id'],
            ansible['msg_type']: ansible['msg']
        }

        payload = module.jsonify(payload)

    response, info = fetch_url(module, url, data=payload, headers=headers)

    status_code = info['status']
    msg = info['msg']

    # Module will fail if the response is not 200
    if status_code != 200:
        results['failed'] = True
        results['status_code'] = status_code
        results['message'] = msg
    else:
        results['failed'] = False
        results['status_code'] = status_code

        if module.check_mode:
            results['message'] = 'Authentication Successful.'
        else:
            results['message'] = msg

    return results


def main():
    '''Ansible main. '''
    module = AnsibleModule(
        argument_spec=dict(
            recipient_type=dict(required=True, choices=['roomId', 'toPersonEmail', 'toPersonId']),
            recipient_id=dict(required=True, no_log=True),
            msg_type=dict(required=False, default='text', aliases=['message_type'], choices=['text', 'markdown']),
            personal_token=dict(required=True, no_log=True, aliases=['token']),
            msg=dict(required=True),
        ),

        supports_check_mode=True
    )

    results = webex_msg(module)

    module.exit_json(**results)


if __name__ == "__main__":
    main()
