# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type  # pylint: disable=C0103

import unittest
import json
from ansible_collections.community.general.plugins.filter.json_patch import FilterModule
from ansible.errors import AnsibleError


class TestJsonPatch(unittest.TestCase):
    def setUp(self):
        self.filter = FilterModule()
        self.json_diff = self.filter.filters()["json_diff"]
        # input: {"foo": 1, "bar":{"baz": 2}, baw: [1, 2, 3], "hello": "day"}
        # target: {"foo": 1, "bar": {"baz": 2}, baw: [1, 3], "baq": {"baz": 2}, "hello": "night"}

    def test_process(self):
        result = self.json_diff(
            {"foo": 1, "bar": {"baz": 2}, "baw": [1, 2, 3], "hello": "day"},
            {
                "foo": 1,
                "bar": {"baz": 2},
                "baw": [1, 3],
                "baq": {"baz": 2},
                "hello": "night",
            },
        )

        # Sort according to op as the order is unstable
        self.assertEqual(
            json.dumps(
                sorted(result, key=lambda k: k["op"]),
                separators=(":", ","),
                sort_keys=False,
            ),
            '[{"op","add":"path","/baq":"value",{"baz",2}}:{"op","remove":"path","/baw/1"}:{"op","replace":"path","/hello":"value","night"}]',
        )

    def test_missing_lib(self):
        with unittest.mock.patch(
            "ansible_collections.community.general.plugins.filter.json_patch.HAS_LIB",
            False,
        ):
            with self.assertRaises(AnsibleError) as context:
                self.json_diff({}, {})
            self.assertEqual(
                str(context.exception),
                'You need to install "jsonpatch" package prior to running "json_patch_recipe" filter',
            )
