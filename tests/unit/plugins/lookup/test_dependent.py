# -*- coding: utf-8 -*-
# Copyright (c) 2020-2021, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Make coding more python3-ish
from __future__ import absolute_import, division, print_function

__metaclass__ = type


from ansible_collections.community.internal_test_tools.tests.unit.compat.unittest import TestCase
from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import (
    MagicMock,
)

from ansible.plugins.loader import lookup_loader


class TestLookupModule(TestCase):
    def setUp(self):
        templar = MagicMock()
        templar._loader = None
        self.lookup = lookup_loader.get("community.general.dependent", templar=templar)

    def test_empty(self):
        self.assertListEqual(self.lookup.run([], None), [])

    def test_simple(self):
        self.assertListEqual(
            self.lookup.run(
                [
                    {'a': '[1, 2]'},
                    {'b': '[item.a + 3, item.a + 6]'},
                    {'c': '[item.a + item.b * 10]'},
                ],
                {},
            ),
            [
                {'a': 1, 'b': 4, 'c': 41},
                {'a': 1, 'b': 7, 'c': 71},
                {'a': 2, 'b': 5, 'c': 52},
                {'a': 2, 'b': 8, 'c': 82},
            ],
        )
