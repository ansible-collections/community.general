# Copyright (C) 2016 maxn nikolaev.makc@gmail.com
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
author: Unknown (!UNKNOWN)
name: jabber
type: notification
short_description: Post task events to a Jabber server
description:
  - The chatty part of ChatOps with a Hipchat server as a target.
  - This callback plugin sends status updates to a HipChat channel during playbook execution.
requirements:
  - xmpp (Python library U(https://github.com/ArchipelProject/xmpppy))
options:
  server:
    description: Connection info to Jabber server.
    type: str
    required: true
    env:
      - name: JABBER_SERV
  user:
    description: Jabber user to authenticate as.
    type: str
    required: true
    env:
      - name: JABBER_USER
  password:
    description: Password for the user to the Jabber server.
    type: str
    required: true
    env:
      - name: JABBER_PASS
  to:
    description: Chat identifier that receives the message.
    type: str
    required: true
    env:
      - name: JABBER_TO
"""

import os

HAS_XMPP = True
try:
    import xmpp
except ImportError:
    HAS_XMPP = False

from ansible.plugins.callback import CallbackBase


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "notification"
    CALLBACK_NAME = "community.general.jabber"
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self, display=None):
        super().__init__(display=display)

        if not HAS_XMPP:
            self._display.warning(
                "The required python xmpp library (xmpppy) is not installed. "
                "pip install git+https://github.com/ArchipelProject/xmpppy"
            )
            self.disabled = True

        self.serv = os.getenv("JABBER_SERV")
        self.j_user = os.getenv("JABBER_USER")
        self.j_pass = os.getenv("JABBER_PASS")
        self.j_to = os.getenv("JABBER_TO")

        if (self.j_user or self.j_pass or self.serv or self.j_to) is None:
            self.disabled = True
            self._display.warning(
                "Jabber CallBack wants the JABBER_SERV, JABBER_USER, JABBER_PASS and JABBER_TO environment variables"
            )

    def send_msg(self, msg):
        """Send message"""
        jid = xmpp.JID(self.j_user)
        client = xmpp.Client(self.serv, debug=[])
        client.connect(server=(self.serv, 5222))
        client.auth(jid.getNode(), self.j_pass, resource=jid.getResource())
        message = xmpp.Message(self.j_to, msg)
        message.setAttr("type", "chat")
        client.send(message)
        client.disconnect()

    def v2_runner_on_ok(self, result):
        self._clean_results(result._result, result._task.action)
        self.debug = self._dump_results(result._result)

    def v2_playbook_on_task_start(self, task, is_conditional):
        self.task = task

    def v2_playbook_on_play_start(self, play):
        """Display Playbook and play start messages"""
        self.play = play
        name = play.name
        self.send_msg(f"Ansible starting play: {name}")

    def playbook_on_stats(self, stats):
        name = self.play
        hosts = sorted(stats.processed.keys())
        failures = False
        unreachable = False
        for h in hosts:
            s = stats.summarize(h)
            if s["failures"] > 0:
                failures = True
            if s["unreachable"] > 0:
                unreachable = True

        if failures or unreachable:
            out = self.debug
            self.send_msg(f"{name}: Failures detected \n{self.task} \nHost: {h}\n Failed at:\n{out}")
        else:
            out = self.debug
            self.send_msg(f"Great! \n Playbook {name} completed:\n{s} \n Last task debug:\n {out}")
