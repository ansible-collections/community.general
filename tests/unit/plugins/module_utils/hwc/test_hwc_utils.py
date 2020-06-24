# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.community.general.tests.unit.compat import unittest
from ansible_collections.community.general.plugins.module_utils.hwc_utils import (HwcModuleException, navigate_value)


class HwcUtilsTestCase(unittest.TestCase):
    def test_navigate_value(self):
        value = {
            'foo': {
                'quiet': {
                    'tree': 'test',
                    "trees": [0, 1]
                },
            }
        }

        self.assertEqual(navigate_value(value, ["foo", "quiet", "tree"]),
                         "test")

        self.assertEqual(
            navigate_value(value, ["foo", "quiet", "trees"],
                           {"foo.quiet.trees": 1}),
            1)

        self.assertRaisesRegexp(HwcModuleException,
                                r".* key\(q\) is not exist in dict",
                                navigate_value, value, ["foo", "q", "tree"])

        self.assertRaisesRegexp(HwcModuleException,
                                r".* the index is out of list",
                                navigate_value, value,
                                ["foo", "quiet", "trees"],
                                {"foo.quiet.trees": 2})
