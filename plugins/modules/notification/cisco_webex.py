#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: cisco_webex
short_description: Send a webexmsg to a Cisco Webex Teams Room or Individual
description:
    - Send a webexmsg to a Cisco Webex Teams Room or Individual with options to control the formatting.
version_added: "2.10"
author: Drew Rusell (@drew-russell)
notes:
  - The C(recipient_id) type must be valid for the supplied C(recipient_id).
  - Full API documentation can be found at U(https://developer.ciscospark.com/endpoint-webexmsgs-post.html).

options:

  recipient_type:
    description:
       - The request parameter you would like to send the webexmsg to.
       - Messages can be sent to either a room or individual (by ID or E-Mail).
    required: yes
    choices: ['roomId', 'toPersonEmail', 'toPersonId']

  recipient_id:
    description:
      - The unique identifier associated with the supplied C(recipient_type).
    required: yes

  webexmsg_type:
    description:
       - Specifies how you would like the webexmsg formatted.
    default: text
    choices: ['text', 'markdown']

  personal_token:
    description:
      - Your personal access token required to validate the Webex Teams API.
    required: yes

  webexmsg:
    description:
      - The webexmsg you would like to send.
    required: yes
'''

EXAMPLES = """
# Note: The following examples assume a variable file has been imported
# that contains the appropriate information.

- name: Cisco Webex Teams - Markdown Message to a Room
  cisco_webex:
    recipient_type: roomId
    recipient_id: "{{ room_id }}"
    webexmsg_type: markdown
    personal_token: "{{ token }}"
    webexmsg: "**Cisco Webex Teams Ansible Module - Room Message in Markdown**"

- name: Cisco Webex Teams - Text Message to a Room
  cisco_webex:
    recipient_type: roomId
    recipient_id: "{{ room_id }}"
    webexmsg_type: text
    personal_token: "{{ token }}"
    webexmsg: "Cisco Webex Teams Ansible Module - Room Message in Text"

- name: Cisco Webex Teams - Text Message by an Individuals ID
  cisco_webex:
    recipient_type: toPersonId
    recipient_id: "{{ person_id}}"
    webexmsg_type: text
    personal_token: "{{ token }}"
    webexmsg: "Cisco Webex Teams Ansible Module - Text Message to Individual by ID"

- name: Cisco Webex Teams - Text Message by an Individuals E-Mail Address
  cisco_webex:
    recipient_type: toPersonEmail
    recipient_id: "{{ person_email }}"
    webexmsg_type: text
    personal_token: "{{ token }}"
    webexmsg: "Cisco Webex Teams Ansible Module - Text Message to Individual by E-Mail"

"""

RETURN = """
status_code:
  description:
    - The Response Code returned by the Webex Teams API.
    - Full Response Code explanations can be found at U(https://developer.ciscospark.com/endpoint-webexmsgs-post.html).
  returned: always
  type: int
  sample: 200

webexmsg:
    description:
      - The Response Message returned by the Webex Teams API.
      - Full Response Code explanations can be found at U(https://developer.ciscospark.com/endpoint-webexmsgs-post.html).
    returned: always
    type: str
    sample: OK (585 bytes)
"""
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url


def spark_webexmsg(module):
    """When check mode is specified, establish a read only connection, that does not return any user specific
    data, to validate connectivity. In regular mode, send a webexmsg to a Cisco Webex Teams Room or Individual"""

    # Ansible Specific Variables
    results = {}
    ansible = module.params

    headers = {
        'Authorization': 'Bearer {0}'.format(ansible['personal_token']),
        'content-type': 'application/json'
    }

    if module.check_mode:
        url = "https://api.ciscospark.com/v1/people/me"
        payload = None

    else:
        url = "https://api.ciscospark.com/v1/messages"

        payload = {
            ansible['recipient_type']: ansible['recipient_id'],
            ansible['webexmsg_type']: ansible['webexmsg']
        }

        payload = module.jsonify(payload)

    response, info = fetch_url(module, url, data=payload, headers=headers)

    status_code = info['status']
    webexmsg = info['msg']

    # Module will fail if the response is not 200
    if status_code != 200:
        results['failed'] = True
        results['status_code'] = status_code
        results['webexmsg'] = webexmsg
    else:
        results['failed'] = False
        results['status_code'] = status_code

        if module.check_mode:
            results['webexmsg'] = 'Authentication Successful.'
        else:
            results['webexmsg'] = webexmsg

    return results


def main():
    '''Ansible main. '''
    module = AnsibleModule(
        argument_spec=dict(
            recipient_type=dict(required=True, choices=['roomId', 'toPersonEmail', 'toPersonId']),
            recipient_id=dict(required=True, no_log=True),
            webexmsg_type=dict(required=False, default=['text'], choices=['text', 'markdown']),
            personal_token=dict(required=True, no_log=True),
            webexmsg=dict(required=True)
        ),

        supports_check_mode=True
    )

    results = spark_webexmsg(module)

    module.exit_json(**results)


if __name__ == "__main__":
    main()
