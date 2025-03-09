# -*- coding: utf-8 -*-
# Copyright (c) 2014-2015, Matt Martz <matt@sivel.net>
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Make coding more python3-ish
from __future__ import annotations

DOCUMENTATION = r"""
author: Unknown (!UNKNOWN)
name: slack
type: notification
requirements:
  - whitelist in configuration
  - prettytable (python library)
short_description: Sends play events to a Slack channel
description:
  - This is an ansible callback plugin that sends status updates to a Slack channel during playbook execution.
options:
  http_agent:
    description:
      - HTTP user agent to use for requests to Slack.
    type: string
    version_added: "10.5.0"
  webhook_url:
    required: true
    description: Slack Webhook URL.
    type: str
    env:
      - name: SLACK_WEBHOOK_URL
    ini:
      - section: callback_slack
        key: webhook_url
  channel:
    default: "#ansible"
    description: Slack room to post in.
    type: str
    env:
      - name: SLACK_CHANNEL
    ini:
      - section: callback_slack
        key: channel
  username:
    description: Username to post as.
    type: str
    env:
      - name: SLACK_USERNAME
    default: ansible
    ini:
      - section: callback_slack
        key: username
  validate_certs:
    description: Validate the SSL certificate of the Slack server for HTTPS URLs.
    env:
      - name: SLACK_VALIDATE_CERTS
    ini:
      - section: callback_slack
        key: validate_certs
    default: true
    type: bool
"""

import json
import os
import uuid

from ansible import context
from ansible.module_utils.urls import open_url
from ansible.plugins.callback import CallbackBase

try:
    import prettytable
    HAS_PRETTYTABLE = True
except ImportError:
    HAS_PRETTYTABLE = False


class CallbackModule(CallbackBase):
    """This is an ansible callback plugin that sends status
    updates to a Slack channel during playbook execution.
    """
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'community.general.slack'
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self, display=None):

        super(CallbackModule, self).__init__(display=display)

        if not HAS_PRETTYTABLE:
            self.disabled = True
            self._display.warning('The `prettytable` python module is not '
                                  'installed. Disabling the Slack callback '
                                  'plugin.')

        self.playbook_name = None

        # This is a 6 character identifier provided with each message
        # This makes it easier to correlate messages when there are more
        # than 1 simultaneous playbooks running
        self.guid = uuid.uuid4().hex[:6]

    def set_options(self, task_keys=None, var_options=None, direct=None):

        super(CallbackModule, self).set_options(task_keys=task_keys, var_options=var_options, direct=direct)

        self.webhook_url = self.get_option('webhook_url')
        self.channel = self.get_option('channel')
        self.username = self.get_option('username')
        self.show_invocation = (self._display.verbosity > 1)
        self.validate_certs = self.get_option('validate_certs')
        self.http_agent = self.get_option('http_agent')
        if self.webhook_url is None:
            self.disabled = True
            self._display.warning('Slack Webhook URL was not provided. The '
                                  'Slack Webhook URL can be provided using '
                                  'the `SLACK_WEBHOOK_URL` environment '
                                  'variable.')

    def send_msg(self, attachments):
        headers = {
            'Content-type': 'application/json',
        }

        payload = {
            'channel': self.channel,
            'username': self.username,
            'attachments': attachments,
            'parse': 'none',
            'icon_url': ('https://cdn2.hubspot.net/hub/330046/'
                         'file-449187601-png/ansible_badge.png'),
        }

        data = json.dumps(payload)
        self._display.debug(data)
        self._display.debug(self.webhook_url)
        try:
            response = open_url(
                self.webhook_url,
                data=data,
                validate_certs=self.validate_certs,
                headers=headers,
                http_agent=self.http_agent,
            )
            return response.read()
        except Exception as e:
            self._display.warning(f'Could not submit message to Slack: {e}')

    def v2_playbook_on_start(self, playbook):
        self.playbook_name = os.path.basename(playbook._file_name)

        title = [
            f'*Playbook initiated* (_{self.guid}_)'
        ]

        invocation_items = []
        if context.CLIARGS and self.show_invocation:
            tags = context.CLIARGS['tags']
            skip_tags = context.CLIARGS['skip_tags']
            extra_vars = context.CLIARGS['extra_vars']
            subset = context.CLIARGS['subset']
            inventory = [os.path.abspath(i) for i in context.CLIARGS['inventory']]

            invocation_items.append(f"Inventory:  {', '.join(inventory)}")
            if tags and tags != ['all']:
                invocation_items.append(f"Tags:       {', '.join(tags)}")
            if skip_tags:
                invocation_items.append(f"Skip Tags:  {', '.join(skip_tags)}")
            if subset:
                invocation_items.append(f'Limit:      {subset}')
            if extra_vars:
                invocation_items.append(f"Extra Vars: {' '.join(extra_vars)}")

            title.append(f"by *{context.CLIARGS['remote_user']}*")

        title.append(f'\n\n*{self.playbook_name}*')
        msg_items = [' '.join(title)]
        if invocation_items:
            _inv_item = '\n'.join(invocation_items)
            msg_items.append(f'```\n{_inv_item}\n```')

        msg = '\n'.join(msg_items)

        attachments = [{
            'fallback': msg,
            'fields': [
                {
                    'value': msg
                }
            ],
            'color': 'warning',
            'mrkdwn_in': ['text', 'fallback', 'fields'],
        }]

        self.send_msg(attachments=attachments)

    def v2_playbook_on_play_start(self, play):
        """Display Play start messages"""

        name = play.name or f'Play name not specified ({play._uuid})'
        msg = f'*Starting play* (_{self.guid}_)\n\n*{name}*'
        attachments = [
            {
                'fallback': msg,
                'text': msg,
                'color': 'warning',
                'mrkdwn_in': ['text', 'fallback', 'fields'],
            }
        ]
        self.send_msg(attachments=attachments)

    def v2_playbook_on_stats(self, stats):
        """Display info about playbook statistics"""

        hosts = sorted(stats.processed.keys())

        t = prettytable.PrettyTable(['Host', 'Ok', 'Changed', 'Unreachable',
                                     'Failures', 'Rescued', 'Ignored'])

        failures = False
        unreachable = False

        for h in hosts:
            s = stats.summarize(h)

            if s['failures'] > 0:
                failures = True
            if s['unreachable'] > 0:
                unreachable = True

            t.add_row([h] + [s[k] for k in ['ok', 'changed', 'unreachable',
                                            'failures', 'rescued', 'ignored']])

        attachments = []
        msg_items = [
            f'*Playbook Complete* (_{self.guid}_)'
        ]
        if failures or unreachable:
            color = 'danger'
            msg_items.append('\n*Failed!*')
        else:
            color = 'good'
            msg_items.append('\n*Success!*')

        msg_items.append(f'```\n{t}\n```')

        msg = '\n'.join(msg_items)

        attachments.append({
            'fallback': msg,
            'fields': [
                {
                    'value': msg
                }
            ],
            'color': color,
            'mrkdwn_in': ['text', 'fallback', 'fields']
        })

        self.send_msg(attachments=attachments)
