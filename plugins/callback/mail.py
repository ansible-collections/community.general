# -*- coding: utf-8 -*-

# Copyright (c) 2012, Dag Wieers <dag@wieers.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
name: mail
type: notification
short_description: Sends failure events through email
description:
  - This callback reports failures through email.
author:
  - Dag Wieers (@dagwieers)
requirements:
  - whitelisting in configuration
options:
  mta:
    description:
      - Mail Transfer Agent, server that accepts SMTP.
    type: str
    env:
      - name: SMTPHOST
    ini:
      - section: callback_mail
        key: smtphost
    default: localhost
  mtaport:
    description:
      - Mail Transfer Agent Port.
      - Port at which server SMTP.
    type: int
    ini:
      - section: callback_mail
        key: smtpport
    default: 25
  to:
    description:
      - Mail recipient.
    type: list
    elements: str
    ini:
      - section: callback_mail
        key: to
    default: [root]
  sender:
    description:
      - Mail sender.
      - This is required since community.general 6.0.0.
    type: str
    required: true
    ini:
      - section: callback_mail
        key: sender
  cc:
    description:
      - CC'd recipients.
    type: list
    elements: str
    ini:
      - section: callback_mail
        key: cc
  bcc:
    description:
      - BCC'd recipients.
    type: list
    elements: str
    ini:
      - section: callback_mail
        key: bcc
  message_id_domain:
    description:
      - The domain name to use for the L(Message-ID header, https://en.wikipedia.org/wiki/Message-ID).
      - The default is the hostname of the control node.
    type: str
    ini:
      - section: callback_mail
        key: message_id_domain
    version_added: 8.2.0
"""

import json
import os
import re
import email.utils
import smtplib

from ansible.module_utils.common.text.converters import to_bytes
from ansible.parsing.ajson import AnsibleJSONEncoder
from ansible.plugins.callback import CallbackBase


class CallbackModule(CallbackBase):
    ''' This Ansible callback plugin mails errors to interested parties. '''
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'community.general.mail'
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self, display=None):
        super(CallbackModule, self).__init__(display=display)
        self.sender = None
        self.to = 'root'
        self.smtphost = os.getenv('SMTPHOST', 'localhost')
        self.smtpport = 25
        self.cc = None
        self.bcc = None

    def set_options(self, task_keys=None, var_options=None, direct=None):

        super(CallbackModule, self).set_options(task_keys=task_keys, var_options=var_options, direct=direct)

        self.sender = self.get_option('sender')
        self.to = self.get_option('to')
        self.smtphost = self.get_option('mta')
        self.smtpport = self.get_option('mtaport')
        self.cc = self.get_option('cc')
        self.bcc = self.get_option('bcc')

    def mail(self, subject='Ansible error mail', body=None):
        if body is None:
            body = subject

        smtp = smtplib.SMTP(self.smtphost, port=self.smtpport)

        sender_address = email.utils.parseaddr(self.sender)
        if self.to:
            to_addresses = email.utils.getaddresses(self.to)
        if self.cc:
            cc_addresses = email.utils.getaddresses(self.cc)
        if self.bcc:
            bcc_addresses = email.utils.getaddresses(self.bcc)

        content = f'Date: {email.utils.formatdate()}\n'
        content += f'From: {email.utils.formataddr(sender_address)}\n'
        if self.to:
            content += f"To: {', '.join([email.utils.formataddr(pair) for pair in to_addresses])}\n"
        if self.cc:
            content += f"Cc: {', '.join([email.utils.formataddr(pair) for pair in cc_addresses])}\n"
        content += f"Message-ID: {email.utils.make_msgid(domain=self.get_option('message_id_domain'))}\n"
        content += f'Subject: {subject.strip()}\n\n'
        content += body

        addresses = to_addresses
        if self.cc:
            addresses += cc_addresses
        if self.bcc:
            addresses += bcc_addresses

        if not addresses:
            self._display.warning('No receiver has been specified for the mail callback plugin.')

        smtp.sendmail(self.sender, [address for name, address in addresses], to_bytes(content))

        smtp.quit()

    def subject_msg(self, multiline, failtype, linenr):
        msg = multiline.strip('\r\n').splitlines()[linenr]
        return f'{failtype}: {msg}'

    def indent(self, multiline, indent=8):
        return re.sub('^', ' ' * indent, multiline, flags=re.MULTILINE)

    def body_blob(self, multiline, texttype):
        ''' Turn some text output in a well-indented block for sending in a mail body '''
        intro = f'with the following {texttype}:\n\n'
        blob = "\n".join(multiline.strip('\r\n').splitlines())
        return f"{intro}{self.indent(blob)}\n"

    def mail_result(self, result, failtype):
        host = result._host.get_name()
        if not self.sender:
            self.sender = f'"Ansible: {host}" <root>'

        # Add subject
        if self.itembody:
            subject = self.itemsubject
        elif result._result.get('failed_when_result') is True:
            subject = "Failed due to 'failed_when' condition"
        elif result._result.get('msg'):
            subject = self.subject_msg(result._result['msg'], failtype, 0)
        elif result._result.get('stderr'):
            subject = self.subject_msg(result._result['stderr'], failtype, -1)
        elif result._result.get('stdout'):
            subject = self.subject_msg(result._result['stdout'], failtype, -1)
        elif result._result.get('exception'):  # Unrelated exceptions are added to output :-/
            subject = self.subject_msg(result._result['exception'], failtype, -1)
        else:
            subject = f'{failtype}: {result._task.name or result._task.action}'

        # Make playbook name visible (e.g. in Outlook/Gmail condensed view)
        body = f'Playbook: {os.path.basename(self.playbook._file_name)}\n'
        if result._task.name:
            body += f'Task: {result._task.name}\n'
        body += f'Module: {result._task.action}\n'
        body += f'Host: {host}\n'
        body += '\n'

        # Add task information (as much as possible)
        body += 'The following task failed:\n\n'
        if 'invocation' in result._result:
            body += self.indent(f"{result._task.action}: {json.dumps(result._result['invocation']['module_args'], indent=4)}\n")
        elif result._task.name:
            body += self.indent(f'{result._task.name} ({result._task.action})\n')
        else:
            body += self.indent(f'{result._task.action}\n')
        body += '\n'

        # Add item / message
        if self.itembody:
            body += self.itembody
        elif result._result.get('failed_when_result') is True:
            fail_cond_list = '\n- '.join(result._task.failed_when)
            fail_cond = self.indent(f"failed_when:\n- {fail_cond_list}")
            body += f"due to the following condition:\n\n{fail_cond}\n\n"
        elif result._result.get('msg'):
            body += self.body_blob(result._result['msg'], 'message')

        # Add stdout / stderr / exception / warnings / deprecations
        if result._result.get('stdout'):
            body += self.body_blob(result._result['stdout'], 'standard output')
        if result._result.get('stderr'):
            body += self.body_blob(result._result['stderr'], 'error output')
        if result._result.get('exception'):  # Unrelated exceptions are added to output :-/
            body += self.body_blob(result._result['exception'], 'exception')
        if result._result.get('warnings'):
            for i in range(len(result._result.get('warnings'))):
                body += self.body_blob(result._result['warnings'][i], f'exception {i + 1}')
        if result._result.get('deprecations'):
            for i in range(len(result._result.get('deprecations'))):
                body += self.body_blob(result._result['deprecations'][i], f'exception {i + 1}')

        body += 'and a complete dump of the error:\n\n'
        body += self.indent(f'{failtype}: {json.dumps(result._result, cls=AnsibleJSONEncoder, indent=4)}')

        self.mail(subject=subject, body=body)

    def v2_playbook_on_start(self, playbook):
        self.playbook = playbook
        self.itembody = ''

    def v2_runner_on_failed(self, result, ignore_errors=False):
        if ignore_errors:
            return

        self.mail_result(result, 'Failed')

    def v2_runner_on_unreachable(self, result):
        self.mail_result(result, 'Unreachable')

    def v2_runner_on_async_failed(self, result):
        self.mail_result(result, 'Async failure')

    def v2_runner_item_on_failed(self, result):
        # Pass item information to task failure
        self.itemsubject = result._result['msg']
        self.itembody += self.body_blob(json.dumps(result._result, cls=AnsibleJSONEncoder, indent=4), f"failed item dump '{result._result['item']}'")
