#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2020, Lee Goolsbee <lgoolsbee@atlassian.com>
# (c) 2020, Michal Middleton <mm.404@icloud.com>
# (c) 2017, Steve Pletcher <steve@steve-pletcher.com>
# (c) 2016, René Moser <mail@renemoser.net>
# (c) 2015, Stefan Berggren <nsg@nsg.cc>
# (c) 2014, Ramon de la Fuente <ramon@delafuente.nl>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = """
module: slack
short_description: Send Slack notifications
description:
    - The C(slack) module sends notifications to U(http://slack.com) via the Incoming WebHook integration
author: "Ramon de la Fuente (@ramondelafuente)"
options:
  domain:
    type: str
    description:
      - Slack (sub)domain for your environment without protocol. (i.e.
        C(example.slack.com)) In 1.8 and beyond, this is deprecated and may
        be ignored.  See token documentation for information.
  token:
    type: str
    description:
      - Slack integration token. This authenticates you to the slack service.
        Make sure to use the correct type of token, depending on what method you use.
      - "Webhook token:
        Prior to 1.8, a token looked like C(3Ffe373sfhRE6y42Fg3rvf4GlK).  In
        1.8 and above, ansible adapts to the new slack API where tokens look
        like C(G922VJP24/D921DW937/3Ffe373sfhRE6y42Fg3rvf4GlK).  If tokens
        are in the new format then slack will ignore any value of domain.  If
        the token is in the old format the domain is required.  Ansible has no
        control of when slack will get rid of the old API.  When slack does
        that the old format will stop working.  ** Please keep in mind the tokens
        are not the API tokens but are the webhook tokens.  In slack these are
        found in the webhook URL which are obtained under the apps and integrations.
        The incoming webhooks can be added in that area.  In some cases this may
        be locked by your Slack admin and you must request access.  It is there
        that the incoming webhooks can be added.  The key is on the end of the
        URL given to you in that section."
      - "WebAPI token:
        Slack WebAPI requires a personal, bot or work application token. These tokens start with C(xoxp-), C(xoxb-)
        or C(xoxa-), eg. C(xoxb-1234-56789abcdefghijklmnop). WebAPI token is required if you intend to receive thread_id.
        See Slack's documentation (U(https://api.slack.com/docs/token-types)) for more information."
    required: true
  msg:
    type: str
    description:
      - Message to send. Note that the module does not handle escaping characters.
        Plain-text angle brackets and ampersands should be converted to HTML entities (e.g. & to &amp;) before sending.
        See Slack's documentation (U(https://api.slack.com/docs/message-formatting)) for more.
  channel:
    type: str
    description:
      - Channel to send the message to. If absent, the message goes to the channel selected for the I(token).
  thread_id:
    description:
      - Optional. Timestamp of parent message to thread this message. https://api.slack.com/docs/message-threading
    type: str
  message_id:
    description:
      - Optional. Message ID to edit, instead of posting a new message.
        Corresponds to C(ts) in the Slack API (U(https://api.slack.com/messaging/modifying)).
    type: str
    version_added: 1.2.0
  username:
    type: str
    description:
      - This is the sender of the message.
    default: "Ansible"
  icon_url:
    type: str
    description:
      - Url for the message sender's icon (default C(https://www.ansible.com/favicon.ico))
    default: https://www.ansible.com/favicon.ico
  icon_emoji:
    type: str
    description:
      - Emoji for the message sender. See Slack documentation for options.
        (if I(icon_emoji) is set, I(icon_url) will not be used)
  link_names:
    type: int
    description:
      - Automatically create links for channels and usernames in I(msg).
    default: 1
    choices:
      - 1
      - 0
  parse:
    type: str
    description:
      - Setting for the message parser at Slack
    choices:
      - 'full'
      - 'none'
  validate_certs:
    description:
      - If C(no), SSL certificates will not be validated. This should only be used
        on personally controlled sites using self-signed certificates.
    type: bool
    default: 'yes'
  color:
    type: str
    description:
      - Allow text to use default colors - use the default of 'normal' to not send a custom color bar at the start of the message.
      - Allowed values for color can be one of 'normal', 'good', 'warning', 'danger', any valid 3 digit or 6 digit hex color value.
      - Specifying value in hex is supported since Ansible 2.8.
    default: 'normal'
  attachments:
    type: list
    elements: dict
    description:
      - Define a list of attachments. This list mirrors the Slack JSON API.
      - For more information, see U(https://api.slack.com/docs/attachments).
  blocks:
    description:
      - Define a list of blocks. This list mirrors the Slack JSON API.
      - For more information, see U(https://api.slack.com/block-kit).
    type: list
    elements: dict
    version_added: 1.0.0
"""

EXAMPLES = """
- name: Send notification message via Slack
  community.general.slack:
    token: thetoken/generatedby/slack
    msg: '{{ inventory_hostname }} completed'
  delegate_to: localhost

- name: Send notification message via Slack all options
  community.general.slack:
    token: thetoken/generatedby/slack
    msg: '{{ inventory_hostname }} completed'
    channel: '#ansible'
    thread_id: '1539917263.000100'
    username: 'Ansible on {{ inventory_hostname }}'
    icon_url: http://www.example.com/some-image-file.png
    link_names: 0
    parse: 'none'
  delegate_to: localhost

- name: Insert a color bar in front of the message for visibility purposes and use the default webhook icon and name configured in Slack
  community.general.slack:
    token: thetoken/generatedby/slack
    msg: '{{ inventory_hostname }} is alive!'
    color: good
    username: ''
    icon_url: ''

- name: Insert a color bar in front of the message with valid hex color value
  community.general.slack:
    token: thetoken/generatedby/slack
    msg: 'This message uses color in hex value'
    color: '#00aacc'
    username: ''
    icon_url: ''

- name: Use the attachments API
  community.general.slack:
    token: thetoken/generatedby/slack
    attachments:
      - text: Display my system load on host A and B
        color: '#ff00dd'
        title: System load
        fields:
          - title: System A
            value: "load average: 0,74, 0,66, 0,63"
            short: True
          - title: System B
            value: 'load average: 5,16, 4,64, 2,43'
            short: True

- name: Use the blocks API
  community.general.slack:
    token: thetoken/generatedby/slack
    blocks:
      - type: section
        text:
          type: mrkdwn
          text: |-
            *System load*
            Display my system load on host A and B
      - type: context
        elements:
        - type: mrkdwn
          text: |-
            *System A*
            load average: 0,74, 0,66, 0,63
        - type: mrkdwn
          text: |-
            *System B*
            load average: 5,16, 4,64, 2,43

- name: Send a message with a link using Slack markup
  community.general.slack:
    token: thetoken/generatedby/slack
    msg: We sent this message using <https://www.ansible.com|Ansible>!

- name: Send a message with angle brackets and ampersands
  community.general.slack:
    token: thetoken/generatedby/slack
    msg: This message has &lt;brackets&gt; &amp; ampersands in plain text.

- name: Initial Threaded Slack message
  community.general.slack:
    channel: '#ansible'
    token: xoxb-1234-56789abcdefghijklmnop
    msg: 'Starting a thread with my initial post.'
  register: slack_response
- name: Add more info to thread
  community.general.slack:
    channel: '#ansible'
    token: xoxb-1234-56789abcdefghijklmnop
    thread_id: "{{ slack_response['ts'] }}"
    color: good
    msg: 'And this is my threaded response!'

- name: Send a message to be edited later on
  community.general.slack:
    token: thetoken/generatedby/slack
    channel: '#ansible'
    msg: Deploying something...
  register: slack_response
- name: Edit message
  community.general.slack:
    token: thetoken/generatedby/slack
    channel: "{{ slack_response.channel }}"
    msg: Deployment complete!
    message_id: "{{ slack_response.ts }}"
"""

import re
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves.urllib.parse import urlencode
from ansible.module_utils.urls import fetch_url

OLD_SLACK_INCOMING_WEBHOOK = 'https://%s/services/hooks/incoming-webhook?token=%s'
SLACK_INCOMING_WEBHOOK = 'https://hooks.slack.com/services/%s'
SLACK_POSTMESSAGE_WEBAPI = 'https://slack.com/api/chat.postMessage'
SLACK_UPDATEMESSAGE_WEBAPI = 'https://slack.com/api/chat.update'
SLACK_CONVERSATIONS_HISTORY_WEBAPI = 'https://slack.com/api/conversations.history'

# Escaping quotes and apostrophes to avoid ending string prematurely in ansible call.
# We do not escape other characters used as Slack metacharacters (e.g. &, <, >).
escape_table = {
    '"': "\"",
    "'": "\'",
}


def is_valid_hex_color(color_choice):
    if re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', color_choice):
        return True
    return False


def escape_quotes(text):
    """Backslash any quotes within text."""
    return "".join(escape_table.get(c, c) for c in text)


def recursive_escape_quotes(obj, keys):
    """Recursively escape quotes inside supplied keys inside block kit objects"""
    if isinstance(obj, dict):
        escaped = {}
        for k, v in obj.items():
            if isinstance(v, str) and k in keys:
                escaped[k] = escape_quotes(v)
            else:
                escaped[k] = recursive_escape_quotes(v, keys)
    elif isinstance(obj, list):
        escaped = [recursive_escape_quotes(v, keys) for v in obj]
    else:
        escaped = obj
    return escaped


def build_payload_for_slack(text, channel, thread_id, username, icon_url, icon_emoji, link_names,
                            parse, color, attachments, blocks, message_id):
    payload = {}
    if color == "normal" and text is not None:
        payload = dict(text=escape_quotes(text))
    elif text is not None:
        # With a custom color we have to set the message as attachment, and explicitly turn markdown parsing on for it.
        payload = dict(attachments=[dict(text=escape_quotes(text), color=color, mrkdwn_in=["text"])])
    if channel is not None:
        if channel.startswith(('#', '@', 'C0')):
            payload['channel'] = channel
        else:
            payload['channel'] = '#' + channel
    if thread_id is not None:
        payload['thread_ts'] = thread_id
    if username is not None:
        payload['username'] = username
    if icon_emoji is not None:
        payload['icon_emoji'] = icon_emoji
    else:
        payload['icon_url'] = icon_url
    if link_names is not None:
        payload['link_names'] = link_names
    if parse is not None:
        payload['parse'] = parse
    if message_id is not None:
        payload['ts'] = message_id

    if attachments is not None:
        if 'attachments' not in payload:
            payload['attachments'] = []

    if attachments is not None:
        attachment_keys_to_escape = [
            'title',
            'text',
            'author_name',
            'pretext',
            'fallback',
        ]
        for attachment in attachments:
            for key in attachment_keys_to_escape:
                if key in attachment:
                    attachment[key] = escape_quotes(attachment[key])

            if 'fallback' not in attachment:
                attachment['fallback'] = attachment['text']

            payload['attachments'].append(attachment)

    if blocks is not None:
        block_keys_to_escape = [
            'text',
            'alt_text'
        ]
        payload['blocks'] = recursive_escape_quotes(blocks, block_keys_to_escape)

    return payload


def get_slack_message(module, token, channel, ts):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + token
    }
    qs = urlencode({
        'channel': channel,
        'ts': ts,
        'limit': 1,
        'inclusive': 'true',
    })
    url = SLACK_CONVERSATIONS_HISTORY_WEBAPI + '?' + qs
    response, info = fetch_url(module=module, url=url, headers=headers, method='GET')
    if info['status'] != 200:
        module.fail_json(msg="failed to get slack message")
    data = module.from_json(response.read())
    if len(data['messages']) < 1:
        module.fail_json(msg="no messages matching ts: %s" % ts)
    if len(data['messages']) > 1:
        module.fail_json(msg="more than 1 message matching ts: %s" % ts)
    return data['messages'][0]


def do_notify_slack(module, domain, token, payload):
    use_webapi = False
    if token.count('/') >= 2:
        # New style webhook token
        slack_uri = SLACK_INCOMING_WEBHOOK % token
    elif re.match(r'^xox[abp]-\S+$', token):
        slack_uri = SLACK_UPDATEMESSAGE_WEBAPI if 'ts' in payload else SLACK_POSTMESSAGE_WEBAPI
        use_webapi = True
    else:
        if not domain:
            module.fail_json(msg="Slack has updated its webhook API.  You need to specify a token of the form "
                                 "XXXX/YYYY/ZZZZ in your playbook")
        slack_uri = OLD_SLACK_INCOMING_WEBHOOK % (domain, token)

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    if use_webapi:
        headers['Authorization'] = 'Bearer ' + token

    data = module.jsonify(payload)
    response, info = fetch_url(module=module, url=slack_uri, headers=headers, method='POST', data=data)

    if info['status'] != 200:
        if use_webapi:
            obscured_incoming_webhook = slack_uri
        else:
            obscured_incoming_webhook = SLACK_INCOMING_WEBHOOK % '[obscured]'
        module.fail_json(msg=" failed to send %s to %s: %s" % (data, obscured_incoming_webhook, info['msg']))

    # each API requires different handling
    if use_webapi:
        return module.from_json(response.read())
    else:
        return {'webhook': 'ok'}


def main():
    module = AnsibleModule(
        argument_spec=dict(
            domain=dict(type='str'),
            token=dict(type='str', required=True, no_log=True),
            msg=dict(type='str'),
            channel=dict(type='str'),
            thread_id=dict(type='str'),
            username=dict(type='str', default='Ansible'),
            icon_url=dict(type='str', default='https://www.ansible.com/favicon.ico'),
            icon_emoji=dict(type='str'),
            link_names=dict(type='int', default=1, choices=[0, 1]),
            parse=dict(type='str', choices=['none', 'full']),
            validate_certs=dict(default=True, type='bool'),
            color=dict(type='str', default='normal'),
            attachments=dict(type='list', elements='dict'),
            blocks=dict(type='list', elements='dict'),
            message_id=dict(type='str'),
        ),
        supports_check_mode=True,
    )

    domain = module.params['domain']
    token = module.params['token']
    text = module.params['msg']
    channel = module.params['channel']
    thread_id = module.params['thread_id']
    username = module.params['username']
    icon_url = module.params['icon_url']
    icon_emoji = module.params['icon_emoji']
    link_names = module.params['link_names']
    parse = module.params['parse']
    color = module.params['color']
    attachments = module.params['attachments']
    blocks = module.params['blocks']
    message_id = module.params['message_id']

    color_choices = ['normal', 'good', 'warning', 'danger']
    if color not in color_choices and not is_valid_hex_color(color):
        module.fail_json(msg="Color value specified should be either one of %r "
                             "or any valid hex value with length 3 or 6." % color_choices)

    changed = True

    # if updating an existing message, we can check if there's anything to update
    if message_id is not None:
        changed = False
        msg = get_slack_message(module, token, channel, message_id)
        for key in ('icon_url', 'icon_emoji', 'link_names', 'color', 'attachments', 'blocks'):
            if msg.get(key) != module.params.get(key):
                changed = True
                break
        # if check mode is active, we shouldn't do anything regardless.
        # if changed=False, we don't need to do anything, so don't do it.
        if module.check_mode or not changed:
            module.exit_json(changed=changed, ts=msg['ts'], channel=msg['channel'])
    elif module.check_mode:
        module.exit_json(changed=changed)

    payload = build_payload_for_slack(text, channel, thread_id, username, icon_url, icon_emoji, link_names,
                                      parse, color, attachments, blocks, message_id)
    slack_response = do_notify_slack(module, domain, token, payload)

    if 'ok' in slack_response:
        # Evaluate WebAPI response
        if slack_response['ok']:
            # return payload as a string for backwards compatibility
            payload_json = module.jsonify(payload)
            module.exit_json(changed=changed, ts=slack_response['ts'], channel=slack_response['channel'],
                             api=slack_response, payload=payload_json)
        else:
            module.fail_json(msg="Slack API error", error=slack_response['error'])
    else:
        # Exit with plain OK from WebHook, since we don't have more information
        # If we get 200 from webhook, the only answer is OK
        module.exit_json(msg="OK")


if __name__ == '__main__':
    main()
