#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2021, Christian Wollinger <cwollinger@web.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: discord
short_description: Send Discord messages
version_added: 3.1.0
description:
  - Sends a message to a Discord channel using the Discord webhook API.
author: Christian Wollinger (@cwollinger)
seealso:
  - name: API documentation
    description: Documentation for Discord API
    link: https://discord.com/developers/docs/resources/webhook#execute-webhook
options:
  webhook_id:
    description:
      - The webhook ID.
      - "Format from Discord webhook URL: C(/webhooks/{webhook.id}/{webhook.token})."
    required: true
    type: str
  webhook_token:
    description:
      - The webhook token.
      - "Format from Discord webhook URL: C(/webhooks/{webhook.id}/{webhook.token})."
    required: true
    type: str
  content:
    description:
      - Content of the message to the Discord channel.
      - At least one of I(content) and I(embeds) must be specified.
    type: str
  username:
    description:
      - Overrides the default username of the webhook.
    type: str
  avatar_url:
    description:
      - Overrides the default avatar of the webhook.
    type: str
  tts:
    description:
      - Set this to C(true) if this is a TTS (Text to Speech) message.
    type: bool
    default: false
  embeds:
    description:
      - Send messages as Embeds to the Discord channel.
      - Embeds can have a colored border, embedded images, text fields and more.
      - "Allowed parameters are described in the Discord Docs: U(https://discord.com/developers/docs/resources/channel#embed-object)"
      - At least one of I(content) and I(embeds) must be specified.
    type: list
    elements: dict
'''

EXAMPLES = """
- name: Send a message to the Discord channel
  community.general.discord:
    webhook_id: "00000"
    webhook_token: "XXXYYY"
    content: "This is a message from ansible"

- name: Send a message to the Discord channel with specific username and avatar
  community.general.discord:
    webhook_id: "00000"
    webhook_token: "XXXYYY"
    content: "This is a message from ansible"
    username: Ansible
    avatar_url: "https://docs.ansible.com/ansible/latest/_static/images/logo_invert.png"

- name: Send a embedded message to the Discord channel
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

- name: Send two embedded messages
  community.general.discord:
    webhook_id: "00000"
    webhook_token: "XXXYYY"
    embeds:
      - title: "First message"
        description: "This is my first embedded message"
        footer:
          text: "Author: Ansible"
        image:
          url: "https://docs.ansible.com/ansible/latest/_static/images/logo_invert.png"
      - title: "Second message"
        description: "This is my first second message"
        footer:
          text: "Author: Ansible"
          icon_url: "https://docs.ansible.com/ansible/latest/_static/images/logo_invert.png"
        fields:
          - name: "Field 1"
            value: "Value of my first field"
          - name: "Field 2"
            value: "Value of my second field"
        timestamp: "{{ ansible_date_time.iso8601 }}"
"""

RETURN = """
http_code:
  description:
    - Response Code returned by Discord API.
  returned: always
  type: int
  sample: 204
"""

from ansible.module_utils.urls import fetch_url
from ansible.module_utils.basic import AnsibleModule


def discord_check_mode(module):

    webhook_id = module.params['webhook_id']
    webhook_token = module.params['webhook_token']

    headers = {
        'content-type': 'application/json'
    }

    url = "https://discord.com/api/webhooks/%s/%s" % (
        webhook_id, webhook_token)

    response, info = fetch_url(module, url, method='GET', headers=headers)
    return response, info


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

    response, info = fetch_url(module, url, data=payload, headers=headers, method='POST')
    return response, info


def main():
    module = AnsibleModule(
        argument_spec=dict(
            webhook_id=dict(type='str', required=True),
            webhook_token=dict(type='str', required=True, no_log=True),
            content=dict(type='str'),
            username=dict(type='str'),
            avatar_url=dict(type='str'),
            tts=dict(type='bool', default=False),
            embeds=dict(type='list', elements='dict'),
        ),
        required_one_of=[['content', 'embeds']],
        supports_check_mode=True
    )

    result = dict(
        changed=False,
        http_code='',
    )

    if module.check_mode:
        response, info = discord_check_mode(module)
        if info['status'] != 200:
            try:
                module.fail_json(http_code=info['status'], msg=info['msg'], response=module.from_json(info['body']), info=info)
            except Exception:
                module.fail_json(http_code=info['status'], msg=info['msg'], info=info)
        else:
            module.exit_json(msg=info['msg'], changed=False, http_code=info['status'], response=module.from_json(response.read()))
    else:
        response, info = discord_text_msg(module)
        if info['status'] != 204:
            try:
                module.fail_json(http_code=info['status'], msg=info['msg'], response=module.from_json(info['body']), info=info)
            except Exception:
                module.fail_json(http_code=info['status'], msg=info['msg'], info=info)
        else:
            module.exit_json(msg=info['msg'], changed=True, http_code=info['status'])


if __name__ == "__main__":
    main()
