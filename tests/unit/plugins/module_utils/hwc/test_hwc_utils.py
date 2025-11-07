# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import unittest

from ansible_collections.community.general.plugins.module_utils.hwc_utils import HwcModuleException, navigate_value


class HwcUtilsTestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()

    def test_navigate_value(self):
        value = {
            "foo": {
                "quiet": {"tree": "test", "trees": [0, 1]},
            }
        }

        self.assertEqual(navigate_value(value, ["foo", "quiet", "tree"]), "test")

        self.assertEqual(navigate_value(value, ["foo", "quiet", "trees"], {"foo.quiet.trees": 1}), 1)

        self.assertRaisesRegex(
            HwcModuleException, r".* key\(q\) is not exist in dict", navigate_value, value, ["foo", "q", "tree"]
        )

        self.assertRaisesRegex(
            HwcModuleException,
            r".* the index is out of list",
            navigate_value,
            value,
            ["foo", "quiet", "trees"],
            {"foo.quiet.trees": 2},
        )
