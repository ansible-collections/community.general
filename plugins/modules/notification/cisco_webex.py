#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: cisco_webex
<<<<<<< HEAD
short_description: Send a msg to a Cisco Webex Teams Room or Individual
description:
    - Send a msg to a Cisco Webex Teams Room or Individual with options to control the formatting.
=======
short_description: Send a webexmsg to a Cisco Webex Teams Room or Individual
description:
    - Send a webexmsg to a Cisco Webex Teams Room or Individual with options to control the formatting.
version_added: "2.10"
>>>>>>> Resolve conversation
author: Drew Rusell (@drew-russell)
notes:
  - The C(recipient_id) type must be valid for the supplied C(recipient_id).
  - Full API documentation can be found at U(https://developer.webex.com/docs/api/basics).

options:

  recipient_type:
    description:
<<<<<<< HEAD
       - The request parameter you would like to send the I(msg) to.
=======
       - The request parameter you would like to send the webexmsg to.
>>>>>>> Resolve conversation
       - Messages can be sent to either a room or individual (by ID or E-Mail).
    required: yes
    choices: ['roomId', 'toPersonEmail', 'toPersonId']
    type: str

  recipient_id:
    description:
      - The unique identifier associated with the supplied C(recipient_type).
    required: yes
    type: str

<<<<<<< HEAD
  msg_type:
    description:
       - Specifies how you would like the msg formatted.
=======
  webexmsg_type:
    description:
       - Specifies how you would like the webexmsg formatted.
>>>>>>> Resolve conversation
    default: text
    choices: ['text', 'markdown']
    type: str

  personal_token:
    description:
      - Your personal access token required to validate the Webex Teams API.
    required: yes
    type: str

<<<<<<< HEAD
  msg:
    description:
      - The message you would like to send.
=======
  webexmsg:
    description:
      - The webexmsg you would like to send.
>>>>>>> Resolve conversation
    required: yes
    type: str
'''

EXAMPLES = """
# Note: The following examples assume a variable file has been imported
# that contains the appropriate information.

- name: Cisco Webex Teams - Markdown Message to a Room
  cisco_webex:
    recipient_type: roomId
    recipient_id: "{{ room_id }}"
<<<<<<< HEAD
    msg_type: markdown
    personal_token: "{{ token }}"
    msg: "**Cisco Webex Teams Ansible Module - Room Message in Markdown**"
=======
    webexmsg_type: markdown
    personal_token: "{{ token }}"
    webexmsg: "**Cisco Webex Teams Ansible Module - Room Message in Markdown**"
>>>>>>> Resolve conversation

- name: Cisco Webex Teams - Text Message to a Room
  cisco_webex:
    recipient_type: roomId
    recipient_id: "{{ room_id }}"
<<<<<<< HEAD
    msg_type: text
    personal_token: "{{ token }}"
    msg: "Cisco Webex Teams Ansible Module - Room Message in Text"
=======
    webexmsg_type: text
    personal_token: "{{ token }}"
    webexmsg: "Cisco Webex Teams Ansible Module - Room Message in Text"
>>>>>>> Resolve conversation

- name: Cisco Webex Teams - Text Message by an Individuals ID
  cisco_webex:
    recipient_type: toPersonId
    recipient_id: "{{ person_id}}"
<<<<<<< HEAD
    msg_type: text
    personal_token: "{{ token }}"
    msg: "Cisco Webex Teams Ansible Module - Text Message to Individual by ID"
=======
    webexmsg_type: text
    personal_token: "{{ token }}"
    webexmsg: "Cisco Webex Teams Ansible Module - Text Message to Individual by ID"
>>>>>>> Resolve conversation

- name: Cisco Webex Teams - Text Message by an Individuals E-Mail Address
  cisco_webex:
    recipient_type: toPersonEmail
    recipient_id: "{{ person_email }}"
<<<<<<< HEAD
    msg_type: text
    personal_token: "{{ token }}"
    msg: "Cisco Webex Teams Ansible Module - Text Message to Individual by E-Mail"
=======
    webexmsg_type: text
    personal_token: "{{ token }}"
    webexmsg: "Cisco Webex Teams Ansible Module - Text Message to Individual by E-Mail"
>>>>>>> Resolve conversation

"""

RETURN = """
status_code:
  description:
    - The Response Code returned by the Webex Teams API.
    - Full Response Code explanations can be found at U(https://developer.webex.com/docs/api/basics).
  returned: always
  type: int
  sample: 200

<<<<<<< HEAD
msg:
=======
webexmsg:
>>>>>>> Resolve conversation
    description:
      - The Response Message returned by the Webex Teams API.
      - Full Response Code explanations can be found at U(https://developer.webex.com/docs/api/basics).
    returned: always
    type: str
    sample: OK (585 bytes)
"""
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url


<<<<<<< HEAD
def spark_msg(module):
    """When check mode is specified, establish a read only connection, that does not return any user specific
    data, to validate connectivity. In regular mode, send a msg to a Cisco Webex Teams Room or Individual"""
=======
def spark_webexmsg(module):
    """When check mode is specified, establish a read only connection, that does not return any user specific
    data, to validate connectivity. In regular mode, send a webexmsg to a Cisco Webex Teams Room or Individual"""
>>>>>>> Resolve conversation

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
<<<<<<< HEAD
            ansible['msg_type']: ansible['msg']
=======
            ansible['webexmsg_type']: ansible['webexmsg']
>>>>>>> Resolve conversation
        }

        payload = module.jsonify(payload)

    response, info = fetch_url(module, url, data=payload, headers=headers)

    status_code = info['status']
<<<<<<< HEAD
    msg = info['msg']
=======
    webexmsg = info['msg']
>>>>>>> Resolve conversation

    # Module will fail if the response is not 200
    if status_code != 200:
        results['failed'] = True
        results['status_code'] = status_code
<<<<<<< HEAD
        results['msg'] = msg
=======
        results['webexmsg'] = webexmsg
>>>>>>> Resolve conversation
    else:
        results['failed'] = False
        results['status_code'] = status_code

        if module.check_mode:
<<<<<<< HEAD
            results['msg'] = 'Authentication Successful.'
        else:
            results['msg'] = msg
=======
            results['webexmsg'] = 'Authentication Successful.'
        else:
            results['webexmsg'] = webexmsg
>>>>>>> Resolve conversation

    return results


def main():
    '''Ansible main. '''
    module = AnsibleModule(
        argument_spec=dict(
            recipient_type=dict(required=True, choices=['roomId', 'toPersonEmail', 'toPersonId']),
            recipient_id=dict(required=True, no_log=True),
<<<<<<< HEAD
            msg_type=dict(required=False, default='text', choices=['text', 'markdown']),
            personal_token=dict(required=True, no_log=True),
            msg=dict(required=True)
=======
            webexmsg_type=dict(required=False, default='text', choices=['text', 'markdown']),
            personal_token=dict(required=True, no_log=True),
            webexmsg=dict(required=True)
>>>>>>> Resolve conversation
        ),

        supports_check_mode=True
    )

<<<<<<< HEAD
    results = spark_msg(module)
=======
    results = spark_webexmsg(module)
>>>>>>> Resolve conversation

    module.exit_json(**results)


if __name__ == "__main__":
    main()
