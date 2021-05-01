#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Christian Wollinger <cwollinger@web.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: discord
short_description: Send discord messages
description:
  - Send a messages to a discord channel via the discord webhook API.
author: Christian Wollinger (@cwollinger)
notes:
  - "Find the API documentation for Discord API here: U(https://discord.com/developers/docs/resources/webhook#execute-webhook)."
options:
  webhook_id:
    description:
      - "Format from discord webhook URL: C(/webhooks/{webhook.id}/{webhook.token})."
    required: yes
    type: str
  webhook_token:
    description:
      - "Format from discord webhook URL: C(/webhooks/{webhook.id}/{webhook.token})."
    required: yes
    type: str
  content:
    description:
      - Content of the message to the discord channel
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
      - Set this to C(true) if this is a TTS (Test to Speech) message.
    type: bool
    default: false
  embeds:
    description:
      - Send messages as Embeds to the discord channel
      - Embeds can have a colored border, embedded images, text fields and more.
    type: list
    elements: string
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

from ansible.module_utils.urls import fetch_url
from ansible.module_utils.basic import AnsibleModule


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
            content=dict(type='str'),
            username=dict(type='str'),
            avatar_url=dict(type='str'),
            tts=dict(type='bool', elements='string', default=False),
            embeds=dict(type='list'),
        ),
        required_one_of=[['content', 'embeds']],
        supports_check_mode=True
    )

    result = dict(
        changed=False,
        http_code='',
    )

    if module.check_mode:
        module.exit_json(changed=False)
    else:
        response, info = discord_text_msg(module)

    if info['status'] != 204:
        result['http_code'] = info['status']
        result['msg'] = info['msg']
        result['failed'] = True
        result['response'] = response
        module.fail_json(**result)
    else:
        result['msg'] = info['msg']
        result['failed'] = False
        result['changed'] = True
        result['http_code'] = info['status']

    module.exit_json(**result)


if __name__ == "__main__":
    main()
