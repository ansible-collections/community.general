#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2016, Jiangge Zhang <tonyseek@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: bearychat
short_description: Send BearyChat notifications
description:
  - The M(community.general.bearychat) module sends notifications to U(https://bearychat.com) using the Incoming Robot integration.
deprecated:
  removed_in: 12.0.0
  why: Chat service is no longer available.
  alternative: There is none.
author: "Jiangge Zhang (@tonyseek)"
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options:
  url:
    type: str
    description:
      - BearyChat WebHook URL. This authenticates you to the bearychat service. It looks like
        V(https://hook.bearychat.com/=ae2CF/incoming/e61bd5c57b164e04b11ac02e66f47f60).
    required: true
  text:
    type: str
    description:
      - Message to send.
  markdown:
    description:
      - If V(true), text is parsed as markdown.
    default: true
    type: bool
  channel:
    type: str
    description:
      - Channel to send the message to. If absent, the message goes to the default channel selected by the O(url).
  attachments:
    type: list
    elements: dict
    description:
      - Define a list of attachments. For more information, see
        U(https://github.com/bearyinnovative/bearychat-tutorial/blob/master/robots/incoming.md#attachments).
"""

EXAMPLES = r"""
- name: Send notification message via BearyChat
  local_action:
    module: bearychat
    url: |
      https://hook.bearychat.com/=ae2CF/incoming/e61bd5c57b164e04b11ac02e66f47f60
    text: "{{ inventory_hostname }} completed"

- name: Send notification message via BearyChat all options
  local_action:
    module: bearychat
    url: |
      https://hook.bearychat.com/=ae2CF/incoming/e61bd5c57b164e04b11ac02e66f47f60
    text: "{{ inventory_hostname }} completed"
    markdown: false
    channel: "#ansible"
    attachments:
      - title: "Ansible on {{ inventory_hostname }}"
        text: "May the Force be with you."
        color: "#ffffff"
        images:
          - http://example.com/index.png
"""

RETURN = r"""
msg:
  description: Execution result.
  returned: success
  type: str
  sample: "OK"
"""

try:
    from ansible.module_utils.six.moves.urllib.parse import urlparse, urlunparse
    HAS_URLPARSE = True
except Exception:
    HAS_URLPARSE = False
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url


def build_payload_for_bearychat(module, text, markdown, channel, attachments):
    payload = {}
    if text is not None:
        payload['text'] = text
    if markdown is not None:
        payload['markdown'] = markdown
    if channel is not None:
        payload['channel'] = channel
    if attachments is not None:
        payload.setdefault('attachments', []).extend(
            build_payload_for_bearychat_attachment(
                module, item.get('title'), item.get('text'), item.get('color'),
                item.get('images'))
            for item in attachments)
    payload = 'payload=%s' % module.jsonify(payload)
    return payload


def build_payload_for_bearychat_attachment(module, title, text, color, images):
    attachment = {}
    if title is not None:
        attachment['title'] = title
    if text is not None:
        attachment['text'] = text
    if color is not None:
        attachment['color'] = color
    if images is not None:
        target_images = attachment.setdefault('images', [])
        if not isinstance(images, (list, tuple)):
            images = [images]
        for image in images:
            if isinstance(image, dict) and 'url' in image:
                image = {'url': image['url']}
            elif hasattr(image, 'startswith') and image.startswith('http'):
                image = {'url': image}
            else:
                module.fail_json(
                    msg="BearyChat doesn't have support for this kind of "
                        "attachment image")
            target_images.append(image)
    return attachment


def do_notify_bearychat(module, url, payload):
    response, info = fetch_url(module, url, data=payload)
    if info['status'] != 200:
        url_info = urlparse(url)
        obscured_incoming_webhook = urlunparse(
            (url_info.scheme, url_info.netloc, '[obscured]', '', '', ''))
        module.fail_json(
            msg=" failed to send %s to %s: %s" % (
                payload, obscured_incoming_webhook, info['msg']))


def main():
    module = AnsibleModule(argument_spec={
        'url': dict(type='str', required=True, no_log=True),
        'text': dict(type='str'),
        'markdown': dict(default=True, type='bool'),
        'channel': dict(type='str'),
        'attachments': dict(type='list', elements='dict'),
    })

    if not HAS_URLPARSE:
        module.fail_json(msg='urlparse is not installed')

    url = module.params['url']
    text = module.params['text']
    markdown = module.params['markdown']
    channel = module.params['channel']
    attachments = module.params['attachments']

    payload = build_payload_for_bearychat(
        module, text, markdown, channel, attachments)
    do_notify_bearychat(module, url, payload)

    module.exit_json(msg="OK")


if __name__ == '__main__':
    main()
