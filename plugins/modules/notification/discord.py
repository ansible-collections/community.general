#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Christian Wollinger <cwollinger@web.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from ansible.module_utils.urls import fetch_url
from ansible.module_utils.basic import AnsibleModule
__metaclass__ = type

DOCUMENTATION = '''
---
module: discord
short_description: Send discord messages
description:
    - Send a messages to a discord channel via the discord webhook API.
author: Christian Wollinger (@cwollinger)
notes:
  - Find the API documentation for Discord API here: U(https://discord.com/developers/docs/resources/webhook#execute-webhook).
options:
  webhook_id:
    description:
      - The webhook id
      - Format from discord webhook URL: C(/webhooks/{webhook.id}/{webhook.token})
    required: yes
    type: str
  webhook_token:
    description:
      - The webhook token
      - Format from discord webhook URL: C(/webhooks/{webhook.id}/{webhook.token})
    required: yes
    type: str
  content:
    description:
      - The the message contents
    type: str
  username:
    description:
      - Override the default username of the webhook
    type: str
  avatar_url:
    description:
      - Override the default avatar of the webhook
    type: str
  tts:
    description:
      - True if this is a TTS message
      - Text to speech message
    type: bool
  embeds:
    description:
      - Embedded rich content
      - Send messages as Embeds
    type: str
'''

EXAMPLES = """
- name: Send a message to the discord channel
  community.general.discord:
    webhook_id: "00000"
    webhook_token: "XXXYYY"
    content: "This is a message from ansible"

- name: Send a message to the discord channel with specific username and avatar
  community.general.discord:
    webhook_id: "00000"
    webhook_token: "XXXYYY"
    content: "This is a message from ansible"
    username: Ansible
    avatar_url: "https://docs.ansible.com/ansible/latest/_static/images/logo_invert.png"

- name: Send a embedded message to the discord channel
  community.general.discord:
    webhook_id: "00000"
    webhook_token: "XXXYYY"
      embeds:
        - title: "Embedded message"
          description: "This is an embedded message"
          footer:
            text: "Author: Ansible"
          image:
            url: "https://docs.ansible.com/ansible/latest/_static/images/logo_invert.png"
"""

RETURN = """
http_code:
  description:
    - Response Code returned by discord API.
  returned: always
  type: int
  sample: 204
"""


def discord_text_msg(module):

    webhook_id = module.params['webhook_id']
    webhook_token = module.params['webhook_token']
    content = module.params['content']
    user = module.params['username']
    avatar_url = module.params['avatar_url']
    tts = module.params['tts']
    embeds = module.params['embeds']

    headers = {
        'content-type': 'application/json'
    }

    url = "https://discord.com/api/webhooks/%s/%s" % (
        webhook_id, webhook_token)

    payload = {
        'content': content,
        'username': user,
        'avatar_url': avatar_url,
        'tts': tts,
        'embeds': embeds,
    }

    payload = module.jsonify(payload)

    response, info = fetch_url(module, url, data=payload, headers=headers)
    return response, info


def main():
    module = AnsibleModule(
        argument_spec=dict(
            webhook_id=dict(type='str', required=True),
            webhook_token=dict(type='str', required=True, no_log=True),
            content=dict(type='str', required=False),
            username=dict(type='str', required=False),
            avatar_url=dict(type='str', required=False),
            tts=dict(type='bool', required=False, default=False),
            embeds=dict(type='list', required=False),
        ),
        required_one_of=[['content', 'embeds']],
        supports_check_mode=True
    )

    result = dict(
        changed=False,
        stdout='',
        stderr='',
        http_code='',
        rc=0
    )

    if module.check_mode:
        module.exit_json(changed=False)
    else:
        response, info = discord_text_msg(module)

    if info['status'] != 204:
        result['http_code'] = info['status']
        result['stderr'] = info['msg']
        result['failed'] = True
        result['rc'] = 1
        module.fail_json(msg="Failed to send message",
                         info=info, response=response, result=result)
    else:
        result['stdout'] = info['msg']
        result['failed'] = False
        result['changed'] = True
        result['http_code'] = info['status']

    module.exit_json(**result)


if __name__ == "__main__":
    main()
