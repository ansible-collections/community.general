# -*- coding: utf-8 -*-
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Make coding more python3-ish
from __future__ import annotations

DOCUMENTATION = r"""
author: Unknown (!UNKNOWN)
name: 'null'
type: stdout
requirements:
  - set as main display callback
short_description: Do not display stuff to screen
description:
  - This callback prevents outputting events to screen.
"""

from ansible.plugins.callback import CallbackBase


class CallbackModule(CallbackBase):

    '''
    This callback won't print messages to stdout when new callback events are received.
    '''

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'community.general.null'
