# Copyright (c) 2020 Red Hat Inc.
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from io import StringIO

from ansible_collections.community.general.tests.unit.compat import unittest
from ansible_collections.community.general.plugins.connection import lxc
from ansible.playbook.play_context import PlayContext


class TestLXCConnectionClass(unittest.TestCase):

    def test_lxc_connection_module(self):
        play_context = PlayContext()
        play_context.prompt = (
            '[sudo via ansible, key=ouzmdnewuhucvuaabtjmweasarviygqq] password: '
        )
        in_stream = StringIO()

        self.assertIsInstance(lxc.Connection(play_context, in_stream), lxc.Connection)
