# -*- coding: utf-8 -*-
# Author: Alexei Znamensky (russoz@gmail.com)
# Largely adapted from test_redhat_subscription by
# Jiri Hnidek (jhnidek@redhat.com)
#
# Copyright (c) Alexei Znamensky (russoz@gmail.com)
# Copyright (c) Jiri Hnidek (jhnidek@redhat.com)
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


from ansible_collections.community.general.plugins.modules import puppet
from .helper import Helper, RunCommandMock  # pylint: disable=unused-import


Helper.from_module(puppet, __name__)
