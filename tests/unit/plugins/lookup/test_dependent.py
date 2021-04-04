# -*- coding: utf-8 -*-
# (c) 2020-2021, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

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
                    '[1, 2]',
                    '[item.0 + 3, item.0 + 6]',
                    '[item.0 + item.1 * 10]',
                ],
                {},
            ),
            [
                {0: 1, 1: 4, 2: 41},
                {0: 1, 1: 7, 2: 71},
                {0: 2, 1: 5, 2: 52},
                {0: 2, 1: 8, 2: 82},
            ],
        )
