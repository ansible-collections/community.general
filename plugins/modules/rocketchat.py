#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Deepak Kothandan <deepak.kothandan@outlook.com>
# Copyright (c) 2015, Stefan Berggren <nsg@nsg.cc>
# Copyright (c) 2014, Ramon de la Fuente <ramon@delafuente.nl>
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
module: rocketchat
short_description: Send notifications to Rocket Chat
description:
    - The C(rocketchat) module sends notifications to Rocket Chat via the Incoming WebHook integration
author: "Ramon de la Fuente (@ramondelafuente)"
options:
  domain:
    type: str
    description:
      - The domain for your environment without protocol. (i.e.
        C(example.com) or C(chat.example.com))
    required: true
  token:
    type: str
    description:
      - Rocket Chat Incoming Webhook integration token.  This provides
        authentication to Rocket Chat's Incoming webhook for posting
        messages.
    required: true
  protocol:
    type: str
    description:
      - Specify the protocol used to send notification messages before the webhook url. (i.e. http or https)
    default: https
    choices:
      - 'http'
      - 'https'
  msg:
    type: str
    description:
      - Message to be sent.
  channel:
    type: str
    description:
      - Channel to send the message to. If absent, the message goes to the channel selected for the I(token)
        specified during the creation of webhook.
  username:
    type: str
    description:
      - This is the sender of the message.
    default: "Ansible"
  icon_url:
    type: str
    description:
      - URL for the message sender's icon.
    default: "https://www.ansible.com/favicon.ico"
  icon_emoji:
    type: str
    description:
      - Emoji for the message sender. The representation for the available emojis can be
        got from Rocket Chat. (for example :thumbsup:) (if I(icon_emoji) is set, I(icon_url) will not be used)
  link_names:
    type: int
    description:
      - Automatically create links for channels and usernames in I(msg).
    default: 1
    choices:
      - 1
      - 0
  validate_certs:
    description:
      - If C(false), SSL certificates will not be validated. This should only be used
        on personally controlled sites using self-signed certificates.
    type: bool
    default: true
  color:
    type: str
    description:
      - Allow text to use default colors - use the default of 'normal' to not send a custom color bar at the start of the message
    default: 'normal'
    choices:
      - 'normal'
      - 'good'
      - 'warning'
      - 'danger'
  attachments:
    type: list
    elements: dict
    description:
      - Define a list of attachments.
'''

EXAMPLES = """
- name: Send notification message via Rocket Chat
  community.general.rocketchat:
    token: thetoken/generatedby/rocketchat
    domain: chat.example.com
    msg: '{{ inventory_hostname }} completed'
  delegate_to: localhost

- name: Send notification message via Rocket Chat all options
  community.general.rocketchat:
    domain: chat.example.com
    token: thetoken/generatedby/rocketchat
    msg: '{{ inventory_hostname }} completed'
    channel: #ansible
    username: 'Ansible on {{ inventory_hostname }}'
    icon_url: http://www.example.com/some-image-file.png
    link_names: 0
  delegate_to: localhost

- name: Insert a color bar in front of the message for visibility purposes and use the default webhook icon and name configured in rocketchat
  community.general.rocketchat:
    token: thetoken/generatedby/rocketchat
    domain: chat.example.com
    msg: '{{ inventory_hostname }} is alive!'
    color: good
    username: ''
    icon_url: ''
  delegate_to: localhost

- name: Use the attachments API
  community.general.rocketchat:
    token: thetoken/generatedby/rocketchat
    domain: chat.example.com
    attachments:
      - text: Display my system load on host A and B
        color: #ff00dd
        title: System load
        fields:
          - title: System A
            value: 'load average: 0,74, 0,66, 0,63'
            short: true
          - title: System B
            value: 'load average: 5,16, 4,64, 2,43'
            short: true
  delegate_to: localhost
"""

RETURN = """
changed:
    description: A flag indicating if any change was made or not.
    returned: success
    type: bool
    sample: false
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url


ROCKETCHAT_INCOMING_WEBHOOK = '%s://%s/hooks/%s'


def build_payload_for_rocketchat(module, text, channel, username, icon_url, icon_emoji, link_names, color, attachments):
    payload = {}
    if color == "normal" and text is not None:
        payload = dict(text=text)
    elif text is not None:
        payload = dict(attachments=[dict(text=text, color=color)])
    if channel is not None:
        if (channel[0] == '#') or (channel[0] == '@'):
            payload['channel'] = channel
        else:
            payload['channel'] = '#' + channel
    if username is not None:
        payload['username'] = username
    if icon_emoji is not None:
        payload['icon_emoji'] = icon_emoji
    else:
        payload['icon_url'] = icon_url
    if link_names is not None:
        payload['link_names'] = link_names

    if attachments is not None:
        if 'attachments' not in payload:
            payload['attachments'] = []

    if attachments is not None:
        for attachment in attachments:
            if 'fallback' not in attachment:
                attachment['fallback'] = attachment['text']
            payload['attachments'].append(attachment)

    payload = "payload=" + module.jsonify(payload)
    return payload


def do_notify_rocketchat(module, domain, token, protocol, payload):

    if token.count('/') < 1:
        module.fail_json(msg="Invalid Token specified, provide a valid token")

    rocketchat_incoming_webhook = ROCKETCHAT_INCOMING_WEBHOOK % (protocol, domain, token)

    response, info = fetch_url(module, rocketchat_incoming_webhook, data=payload)
    if info['status'] != 200:
        module.fail_json(msg="failed to send message, return status=%s" % str(info['status']))


def main():
    module = AnsibleModule(
        argument_spec=dict(
            domain=dict(type='str', required=True),
            token=dict(type='str', required=True, no_log=True),
            protocol=dict(type='str', default='https', choices=['http', 'https']),
            msg=dict(type='str', required=False),
            channel=dict(type='str'),
            username=dict(type='str', default='Ansible'),
            icon_url=dict(type='str', default='https://www.ansible.com/favicon.ico'),
            icon_emoji=dict(type='str'),
            link_names=dict(type='int', default=1, choices=[0, 1]),
            validate_certs=dict(default=True, type='bool'),
            color=dict(type='str', default='normal', choices=['normal', 'good', 'warning', 'danger']),
            attachments=dict(type='list', elements='dict', required=False)
        )
    )

    domain = module.params['domain']
    token = module.params['token']
    protocol = module.params['protocol']
    text = module.params['msg']
    channel = module.params['channel']
    username = module.params['username']
    icon_url = module.params['icon_url']
    icon_emoji = module.params['icon_emoji']
    link_names = module.params['link_names']
    color = module.params['color']
    attachments = module.params['attachments']

    payload = build_payload_for_rocketchat(module, text, channel, username, icon_url, icon_emoji, link_names, color, attachments)
    do_notify_rocketchat(module, domain, token, protocol, payload)

    module.exit_json(msg="OK")


if __name__ == '__main__':
    main()
