# Copyright (c) 2012, Michael DeHaan, <michael.dehaan@gmail.com>
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Make coding more python3-ish
from __future__ import annotations

DOCUMENTATION = r"""
author: Unknown (!UNKNOWN)
name: say
type: notification
requirements:
  - whitelisting in configuration
  - the C(/usr/bin/say) command line program (standard on macOS) or C(espeak) command line program
short_description: Notify using software speech synthesizer
description:
  - This plugin uses C(say) or C(espeak) to "speak" about play events.
"""

import platform
import subprocess
import os

from ansible.module_utils.common.process import get_bin_path
from ansible.plugins.callback import CallbackBase


class CallbackModule(CallbackBase):
    """
    makes Ansible much more exciting.
    """

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "notification"
    CALLBACK_NAME = "community.general.say"
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self):
        super().__init__()

        self.FAILED_VOICE = None
        self.REGULAR_VOICE = None
        self.HAPPY_VOICE = None
        self.LASER_VOICE = None

        try:
            self.synthesizer = get_bin_path("say")
            if platform.system() != "Darwin":
                # 'say' binary available, it might be GNUstep tool which doesn't support 'voice' parameter
                self._display.warning(
                    f"'say' executable found but system is '{platform.system()}': ignoring voice parameter"
                )
            else:
                self.FAILED_VOICE = "Zarvox"
                self.REGULAR_VOICE = "Trinoids"
                self.HAPPY_VOICE = "Cellos"
                self.LASER_VOICE = "Princess"
        except ValueError:
            try:
                self.synthesizer = get_bin_path("espeak")
                self.FAILED_VOICE = "klatt"
                self.HAPPY_VOICE = "f5"
                self.LASER_VOICE = "whisper"
            except ValueError:
                self.synthesizer = None

        # plugin disable itself if say is not present
        # ansible will not call any callback if disabled is set to True
        if not self.synthesizer:
            self.disabled = True
            self._display.warning(
                f"Unable to find either 'say' or 'espeak' executable, plugin {os.path.basename(__file__)} disabled"
            )

    def say(self, msg, voice):
        cmd = [self.synthesizer, msg]
        if voice:
            cmd.extend(("-v", voice))
        subprocess.call(cmd)

    def runner_on_failed(self, host, res, ignore_errors=False):
        self.say(f"Failure on host {host}", self.FAILED_VOICE)

    def runner_on_ok(self, host, res):
        self.say("pew", self.LASER_VOICE)

    def runner_on_skipped(self, host, item=None):
        self.say("pew", self.LASER_VOICE)

    def runner_on_unreachable(self, host, res):
        self.say(f"Failure on host {host}", self.FAILED_VOICE)

    def runner_on_async_ok(self, host, res, jid):
        self.say("pew", self.LASER_VOICE)

    def runner_on_async_failed(self, host, res, jid):
        self.say(f"Failure on host {host}", self.FAILED_VOICE)

    def playbook_on_start(self):
        self.say("Running Playbook", self.REGULAR_VOICE)

    def playbook_on_notify(self, host, handler):
        self.say("pew", self.LASER_VOICE)

    def playbook_on_task_start(self, name, is_conditional):
        if not is_conditional:
            self.say(f"Starting task: {name}", self.REGULAR_VOICE)
        else:
            self.say(f"Notifying task: {name}", self.REGULAR_VOICE)

    def playbook_on_setup(self):
        self.say("Gathering facts", self.REGULAR_VOICE)

    def playbook_on_play_start(self, name):
        self.say(f"Starting play: {name}", self.HAPPY_VOICE)

    def playbook_on_stats(self, stats):
        self.say("Play complete", self.HAPPY_VOICE)
