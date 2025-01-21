# -*- coding: utf-8 -*-
# Copyright (c) Stanislav Meduna (@numo68)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type  # pylint: disable=C0103

import unittest
from ansible_collections.community.general.plugins.filter.json_patch import FilterModule
from ansible.errors import AnsibleFilterError


class TestJsonPatch(unittest.TestCase):
    def setUp(self):
        self.filter = FilterModule()
        self.json_patch = self.filter.filters()["json_patch"]
        self.json_diff = self.filter.filters()["json_diff"]
        self.json_patch_recipe = self.filter.filters()["json_patch_recipe"]

    # json_patch

    def test_patch_add_to_empty(self):
        result = self.json_patch({}, "add", "/a", 1)
        self.assertEqual(result, {"a": 1})

    def test_patch_add_to_dict(self):
        result = self.json_patch({"b": 2}, "add", "/a", 1)
        self.assertEqual(result, {"a": 1, "b": 2})

    def test_patch_add_to_array_index(self):
        result = self.json_patch([1, 2, 3], "add", "/1", 99)
        self.assertEqual(result, [1, 99, 2, 3])

    def test_patch_add_to_array_last(self):
        result = self.json_patch({"a": [1, 2, 3]}, "add", "/a/-", 99)
        self.assertEqual(result, {"a": [1, 2, 3, 99]})

    def test_patch_add_from_string(self):
        result = self.json_patch("[1, 2, 3]", "add", "/-", 99)
        self.assertEqual(result, [1, 2, 3, 99])

    def test_patch_path_escape(self):
        result = self.json_patch({}, "add", "/x~0~1y", 99)
        self.assertEqual(result, {"x~/y": 99})

    def test_patch_remove(self):
        result = self.json_patch({"a": 1, "b": {"c": 2}, "d": 3}, "remove", "/b")
        self.assertEqual(result, {"a": 1, "d": 3})

    def test_patch_replace(self):
        result = self.json_patch(
            {"a": 1, "b": {"c": 2}, "d": 3}, "replace", "/b", {"x": 99}
        )
        self.assertEqual(result, {"a": 1, "b": {"x": 99}, "d": 3})

    def test_patch_copy(self):
        result = self.json_patch(
            {"a": 1, "b": {"c": 2}, "d": 3}, "copy", "/d", **{"from": "/b"}
        )
        self.assertEqual(result, {"a": 1, "b": {"c": 2}, "d": {"c": 2}})

    def test_patch_move(self):
        result = self.json_patch(
            {"a": 1, "b": {"c": 2}, "d": 3}, "move", "/d", **{"from": "/b"}
        )
        self.assertEqual(result, {"a": 1, "d": {"c": 2}})

    def test_patch_test_pass(self):
        result = self.json_patch({"a": 1, "b": {"c": 2}, "d": 3}, "test", "/b/c", 2)
        self.assertEqual(result, {"a": 1, "b": {"c": 2}, "d": 3})

    def test_patch_test_fail_none(self):
        result = self.json_patch({"a": 1, "b": {"c": 2}, "d": 3}, "test", "/b/c", 99)
        self.assertIsNone(result)

    def test_patch_test_fail_fail(self):
        with self.assertRaises(AnsibleFilterError) as context:
            self.json_patch(
                {"a": 1, "b": {"c": 2}, "d": 3}, "test", "/b/c", 99, fail_test=True
            )
        self.assertTrue("json_patch: test operation failed" in str(context.exception))

    def test_patch_remove_nonexisting(self):
        with self.assertRaises(AnsibleFilterError) as context:
            self.json_patch({"a": 1, "b": {"c": 2}, "d": 3}, "remove", "/e")
        self.assertEqual(
            str(context.exception),
            "json_patch: patch failed: can't remove a non-existent object 'e'",
        )

    def test_patch_missing_lib(self):
        with unittest.mock.patch(
            "ansible_collections.community.general.plugins.filter.json_patch.HAS_LIB",
            False,
        ):
            with self.assertRaises(AnsibleFilterError) as context:
                self.json_patch({}, "add", "/a", 1)
            self.assertEqual(
                str(context.exception),
                "You need to install 'jsonpatch' package prior to running 'json_patch' filter",
            )

    def test_patch_invalid_operation(self):
        with self.assertRaises(AnsibleFilterError) as context:
            self.json_patch({}, "invalid", "/a", 1)
        self.assertEqual(
            str(context.exception),
            "json_patch: unsupported 'op' argument: invalid",
        )

    def test_patch_arg_checking(self):
        with self.assertRaises(AnsibleFilterError) as context:
            self.json_patch(1, "add", "/a", 1)
        self.assertEqual(
            str(context.exception),
            "json_patch: input is not dictionary, list or string",
        )
        with self.assertRaises(AnsibleFilterError) as context:
            self.json_patch({}, 1, "/a", 1)
        self.assertEqual(
            str(context.exception),
            "json_patch: 'op' argument is not a string",
        )
        with self.assertRaises(AnsibleFilterError) as context:
            self.json_patch({}, None, "/a", 1)
        self.assertEqual(
            str(context.exception),
            "json_patch: 'op' argument is not a string",
        )
        with self.assertRaises(AnsibleFilterError) as context:
            self.json_patch({}, "add", 1, 1)
        self.assertEqual(
            str(context.exception),
            "json_patch: 'path' argument is not a string",
        )
        with self.assertRaises(AnsibleFilterError) as context:
            self.json_patch({}, "copy", "/a", **{"from": 1})
        self.assertEqual(
            str(context.exception),
            "json_patch: 'from' argument is not a string",
        )

    def test_patch_extra_kwarg(self):
        with self.assertRaises(AnsibleFilterError) as context:
            self.json_patch({}, "add", "/a", 1, invalid=True)
        self.assertEqual(
            str(context.exception),
            "json_patch: unexpected keywords arguments: invalid",
        )

    def test_patch_missing_from(self):
        with self.assertRaises(AnsibleFilterError) as context:
            self.json_patch({}, "copy", "/a", 1)
        self.assertEqual(
            str(context.exception),
            "json_patch: 'from' argument missing for 'copy' operation",
        )
        with self.assertRaises(AnsibleFilterError) as context:
            self.json_patch({}, "move", "/a", 1)
        self.assertEqual(
            str(context.exception),
            "json_patch: 'from' argument missing for 'move' operation",
        )

    def test_patch_add_to_dict_binary(self):
        result = self.json_patch(b'{"b": 2}', "add", "/a", 1)
        self.assertEqual(result, {"a": 1, "b": 2})
        result = self.json_patch(bytearray(b'{"b": 2}'), "add", "/a", 1)
        self.assertEqual(result, {"a": 1, "b": 2})

    # json_patch_recipe

    def test_patch_recipe_process(self):
        result = self.json_patch_recipe(
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
        )
        self.assertEqual(
            result, {"bar": [2], "bax": 1, "bay": 1, "baz": [10, 20, 30], "foo": 1}
        )

    def test_patch_recipe_test_fail(self):
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

    def test_patch_recipe_missing_lib(self):
        with unittest.mock.patch(
            "ansible_collections.community.general.plugins.filter.json_patch.HAS_LIB",
            False,
        ):
            with self.assertRaises(AnsibleFilterError) as context:
                self.json_patch_recipe({}, [])
            self.assertEqual(
                str(context.exception),
                "You need to install 'jsonpatch' package prior to running 'json_patch_recipe' filter",
            )

    def test_patch_recipe_missing_from(self):
        with self.assertRaises(AnsibleFilterError) as context:
            self.json_patch_recipe({}, [{"op": "copy", "path": "/a"}])
        self.assertEqual(
            str(context.exception),
            "json_patch_recipe: 'from' argument missing for 'copy' operation",
        )

    def test_patch_recipe_incorrect_type(self):
        with self.assertRaises(AnsibleFilterError) as context:
            self.json_patch_recipe({}, "copy")
        self.assertEqual(
            str(context.exception),
            "json_patch_recipe: 'operations' needs to be a list",
        )

    def test_patch_recipe_test_fail_none(self):
        result = self.json_patch_recipe(
            {"a": 1, "b": {"c": 2}, "d": 3},
            [{"op": "test", "path": "/b/c", "value": 99}],
        )
        self.assertIsNone(result)

    def test_patch_recipe_test_fail_fail_pos(self):
        with self.assertRaises(AnsibleFilterError) as context:
            self.json_patch_recipe(
                {"a": 1, "b": {"c": 2}, "d": 3},
                [{"op": "test", "path": "/b/c", "value": 99}],
                True,
            )
        self.assertTrue(
            "json_patch_recipe: test operation failed" in str(context.exception)
        )

    def test_patch_recipe_test_fail_fail_kw(self):
        with self.assertRaises(AnsibleFilterError) as context:
            self.json_patch_recipe(
                {"a": 1, "b": {"c": 2}, "d": 3},
                [{"op": "test", "path": "/b/c", "value": 99}],
                fail_test=True,
            )
        self.assertTrue(
            "json_patch_recipe: test operation failed" in str(context.exception)
        )

    # json_diff

    def test_diff_process(self):
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

        # Sort as the order is unstable
        self.assertEqual(
            sorted(result, key=lambda k: k["path"]),
            [
                {"op": "add", "path": "/baq", "value": {"baz": 2}},
                {"op": "remove", "path": "/baw/1"},
                {"op": "replace", "path": "/hello", "value": "night"},
            ],
        )

    def test_diff_missing_lib(self):
        with unittest.mock.patch(
            "ansible_collections.community.general.plugins.filter.json_patch.HAS_LIB",
            False,
        ):
            with self.assertRaises(AnsibleFilterError) as context:
                self.json_diff({}, {})
            self.assertEqual(
                str(context.exception),
                "You need to install 'jsonpatch' package prior to running 'json_diff' filter",
            )

    def test_diff_arg_checking(self):
        with self.assertRaises(AnsibleFilterError) as context:
            self.json_diff(1, {})
        self.assertEqual(
            str(context.exception), "json_diff: input is not dictionary, list or string"
        )
        with self.assertRaises(AnsibleFilterError) as context:
            self.json_diff({}, 1)
        self.assertEqual(
            str(context.exception),
            "json_diff: target is not dictionary, list or string",
        )
