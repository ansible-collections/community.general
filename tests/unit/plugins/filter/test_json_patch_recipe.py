# -*- coding: utf-8 -*-
# Copyright (c) Stanislav Meduna (@numo68)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type  # pylint: disable=C0103

import unittest
import json
from ansible_collections.community.general.plugins.filter.json_patch import FilterModule
from ansible.errors import AnsibleError, AnsibleFilterError, AnsibleOptionsError


class TestJsonPatch(unittest.TestCase):
    def setUp(self):
        self.filter = FilterModule()
        self.json_patch_recipe = self.filter.filters()["json_patch_recipe"]

    def test_process(self):
        result = json.dumps(
            self.json_patch_recipe(
                {},
                [
                    {"op": "add", "path": "/foo", "value": 1},
                    {"op": "add", "path": "/bar", "value": []},
                    {"op": "add", "path": "/bar/-", "value": 2},
                    {"op": "add", "path": "/bar/0", "value": 1},
                    {"op": "remove", "path": "/bar/0"},
                    {"op": "move", "from": "/foo", "path": "/baz"},
                    {"op": "copy", "from": "/baz", "path": "/bax"},
                    {"op": "copy", "from": "/baz", "path": "/bay"},
                    {"op": "replace", "path": "/baz", "value": [10, 20, 30]},
                    {"op": "add", "path": "/foo", "value": 1},
                    {"op": "add", "path": "/foo", "value": 1},
                    {"op": "test", "path": "/baz/1", "value": 20},
                ],
            ),
            sort_keys=True,
            separators=(",", ":"),
        )
        self.assertEqual(result, '{"bar":[2],"bax":1,"bay":1,"baz":[10,20,30],"foo":1}')

    def test_test_fail(self):
        result = self.json_patch_recipe(
            {},
            [
                {"op": "add", "path": "/bar", "value": []},
                {"op": "add", "path": "/bar/-", "value": 2},
                {"op": "test", "path": "/bar/0", "value": 20},
                {"op": "add", "path": "/bar/0", "value": 1},
            ],
        )
        self.assertIsNone(result)

    def test_missing_lib(self):
        with unittest.mock.patch(
            "ansible_collections.community.general.plugins.filter.json_patch.HAS_LIB",
            False,
        ):
            with self.assertRaises(AnsibleError) as context:
                self.json_patch_recipe({}, [])
            self.assertEqual(
                str(context.exception),
                'You need to install "jsonpatch" package prior to running "json_patch_recipe" filter',
            )

    def test_missing_from(self):
        with self.assertRaises(AnsibleFilterError) as context:
            self.json_patch_recipe({}, [{"op": "copy", "path": "/a"}])
        self.assertEqual(
            str(context.exception),
            "JSON patch failed: The operation does not contain a 'from' member",
        )

    def test_incorrect_type(self):
        with self.assertRaises(AnsibleOptionsError) as context:
            self.json_patch_recipe({}, "copy")
        self.assertEqual(
            str(context.exception),
            '"operations" needs to be a list',
        )
