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
        self.json_patch = self.filter.filters()["json_patch"]

    def test_add_to_empty(self):
        result = json.dumps(
            self.json_patch({}, "add", "/a", 1),
            sort_keys=True,
            separators=(",", ":"),
        )
        self.assertEqual(result, '{"a":1}')

    def test_add_to_dict(self):
        result = json.dumps(
            self.json_patch({"b": 2}, "add", "/a", 1),
            sort_keys=True,
            separators=(",", ":"),
        )
        self.assertEqual(result, '{"a":1,"b":2}')

    def test_add_to_array_index(self):
        result = json.dumps(
            self.json_patch([1, 2, 3], "add", "/1", 99),
            sort_keys=True,
            separators=(",", ":"),
        )
        self.assertEqual(result, "[1,99,2,3]")

    def test_add_to_array_last(self):
        result = json.dumps(
            self.json_patch({"a": [1, 2, 3]}, "add", "/a/-", 99),
            sort_keys=True,
            separators=(",", ":"),
        )
        self.assertEqual(result, '{"a":[1,2,3,99]}')

    def test_add_from_string(self):
        result = json.dumps(
            self.json_patch("[1, 2, 3]", "add", "/-", 99),
            sort_keys=True,
            separators=(",", ":"),
        )
        self.assertEqual(result, "[1,2,3,99]")

    def test_path_escape(self):
        result = json.dumps(
            self.json_patch({}, "add", "/x~0~1y", 99),
            sort_keys=True,
            separators=(",", ":"),
        )
        self.assertEqual(result, '{"x~/y":99}')

    def test_remove(self):
        result = json.dumps(
            self.json_patch({"a": 1, "b": {"c": 2}, "d": 3}, "remove", "/b"),
            sort_keys=True,
            separators=(",", ":"),
        )
        self.assertEqual(result, '{"a":1,"d":3}')

    def test_replace(self):
        result = json.dumps(
            self.json_patch(
                {"a": 1, "b": {"c": 2}, "d": 3}, "replace", "/b", {"x": 99}
            ),
            sort_keys=True,
            separators=(",", ":"),
        )
        self.assertEqual(result, '{"a":1,"b":{"x":99},"d":3}')

    def test_copy(self):
        result = json.dumps(
            self.json_patch(
                {"a": 1, "b": {"c": 2}, "d": 3}, "copy", "/d", **{"from": "/b"}
            ),
            sort_keys=True,
            separators=(",", ":"),
        )
        self.assertEqual(result, '{"a":1,"b":{"c":2},"d":{"c":2}}')

    def test_move(self):
        result = json.dumps(
            self.json_patch(
                {"a": 1, "b": {"c": 2}, "d": 3}, "move", "/d", **{"from": "/b"}
            ),
            sort_keys=True,
            separators=(",", ":"),
        )
        self.assertEqual(result, '{"a":1,"d":{"c":2}}')

    def test_test_pass(self):
        result = json.dumps(
            self.json_patch({"a": 1, "b": {"c": 2}, "d": 3}, "test", "/b/c", 2),
            sort_keys=True,
            separators=(",", ":"),
        )
        self.assertEqual(result, '{"a":1,"b":{"c":2},"d":3}')

    def test_test_fail(self):
        result = self.json_patch({"a": 1, "b": {"c": 2}, "d": 3}, "test", "/b/c", 99)
        self.assertIsNone(result)

    def test_remove_nonexisting(self):
        with self.assertRaises(AnsibleFilterError) as context:
            self.json_patch({"a": 1, "b": {"c": 2}, "d": 3}, "remove", "/e")
        self.assertEqual(
            str(context.exception),
            "JSON patch failed: can't remove a non-existent object 'e'",
        )

    def test_missing_lib(self):
        with unittest.mock.patch(
            "ansible_collections.community.general.plugins.filter.json_patch.HAS_LIB",
            False,
        ):
            with self.assertRaises(AnsibleError) as context:
                self.json_patch({}, "add", "/a", 1)
            self.assertEqual(
                str(context.exception),
                'You need to install "jsonpatch" package prior to running "json_patch" filter',
            )

    def test_invalid_operation(self):
        with self.assertRaises(AnsibleFilterError) as context:
            self.json_patch({}, "invalid", "/a", 1)
        self.assertEqual(
            str(context.exception),
            "JSON patch failed: Unknown operation 'invalid'",
        )

    def test_missing_from(self):
        with self.assertRaises(AnsibleOptionsError) as context:
            self.json_patch({}, "copy", "/a", 1)
        self.assertEqual(
            str(context.exception),
            '"copy" operation requires "from" parameter',
        )
        with self.assertRaises(AnsibleOptionsError) as context:
            self.json_patch({}, "move", "/a", 1)
        self.assertEqual(
            str(context.exception),
            '"move" operation requires "from" parameter',
        )
