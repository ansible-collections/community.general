# Copyright (c) 2020, Thales Netherlands
# Copyright (c) 2021, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import unittest
from copy import deepcopy
from unittest.mock import patch

from ansible.errors import AnsibleError
from ansible.plugins import AnsiblePlugin
from ansible.template import Templar
from ansible.utils.display import Display
from ansible_collections.community.internal_test_tools.tests.unit.mock.loader import DictDataLoader

from ansible_collections.community.general.plugins.lookup import merge_variables

merge_hash_data = {
    "low_prio": {"a": {"a": {"x": "low_value", "y": "low_value", "list": ["low_value"]}}, "b": [1, 1, 2, 3]},
    "high_prio": {
        "a": {"a": {"y": "high_value", "z": "high_value", "list": ["high_value"]}},
        "b": [3, 4, 4, {"5": "value"}],
    },
}


class TestMergeVariablesLookup(unittest.TestCase):
    class HostVarsMock(dict):
        def __getattr__(self, item):
            return super().__getitem__(item)

        def __setattr__(self, item, value):
            return super().__setitem__(item, value)

        def raw_get(self, host):
            return super().__getitem__(host)

    def setUp(self):
        self.loader = DictDataLoader({})
        self.templar = Templar(loader=self.loader, variables={})
        self.merge_vars_lookup = merge_variables.LookupModule(loader=self.loader, templar=self.templar)

    @patch.object(AnsiblePlugin, "set_options")
    @patch.object(
        AnsiblePlugin,
        "get_option",
        side_effect=[None, "ignore", "suffix", None, "deep", "append", "replace", "replace", []],
    )
    @patch.object(Templar, "template", side_effect=[["item1"], ["item3"]])
    def test_merge_list(self, mock_set_options, mock_get_option, mock_template):
        results = self.merge_vars_lookup.run(
            ["__merge_list"],
            {"testlist1__merge_list": ["item1"], "testlist2": ["item2"], "testlist3__merge_list": ["item3"]},
        )

        self.assertEqual(results, [["item1", "item3"]])

    @patch.object(AnsiblePlugin, "set_options")
    @patch.object(
        AnsiblePlugin,
        "get_option",
        side_effect=[["initial_item"], "ignore", "suffix", None, "deep", "append", "replace", "replace", []],
    )
    @patch.object(Templar, "template", side_effect=[["item1"], ["item3"]])
    def test_merge_list_with_initial_value(self, mock_set_options, mock_get_option, mock_template):
        results = self.merge_vars_lookup.run(
            ["__merge_list"],
            {"testlist1__merge_list": ["item1"], "testlist2": ["item2"], "testlist3__merge_list": ["item3"]},
        )

        self.assertEqual(results, [["initial_item", "item1", "item3"]])

    @patch.object(AnsiblePlugin, "set_options")
    @patch.object(
        AnsiblePlugin,
        "get_option",
        side_effect=[None, "ignore", "suffix", None, "deep", "append", "replace", "replace", []],
    )
    @patch.object(
        Templar,
        "template",
        side_effect=[{"item1": "test", "list_item": ["test1"]}, {"item2": "test", "list_item": ["test2"]}],
    )
    def test_merge_dict(self, mock_set_options, mock_get_option, mock_template):
        results = self.merge_vars_lookup.run(
            ["__merge_dict"],
            {
                "testdict1__merge_dict": {"item1": "test", "list_item": ["test1"]},
                "testdict2__merge_dict": {"item2": "test", "list_item": ["test2"]},
            },
        )

        self.assertEqual(results, [{"item1": "test", "item2": "test", "list_item": ["test1", "test2"]}])

    @patch.object(AnsiblePlugin, "set_options")
    @patch.object(
        AnsiblePlugin,
        "get_option",
        side_effect=[
            {"initial_item": "random value", "list_item": ["test0"]},
            "ignore",
            "suffix",
            None,
            "deep",
            "append",
            "replace",
            "replace",
            [],
        ],
    )
    @patch.object(
        Templar,
        "template",
        side_effect=[{"item1": "test", "list_item": ["test1"]}, {"item2": "test", "list_item": ["test2"]}],
    )
    def test_merge_dict_with_initial_value(self, mock_set_options, mock_get_option, mock_template):
        results = self.merge_vars_lookup.run(
            ["__merge_dict"],
            {
                "testdict1__merge_dict": {"item1": "test", "list_item": ["test1"]},
                "testdict2__merge_dict": {"item2": "test", "list_item": ["test2"]},
            },
        )

        self.assertEqual(
            results,
            [
                {
                    "initial_item": "random value",
                    "item1": "test",
                    "item2": "test",
                    "list_item": ["test0", "test1", "test2"],
                }
            ],
        )

    @patch.object(AnsiblePlugin, "set_options")
    @patch.object(
        AnsiblePlugin,
        "get_option",
        side_effect=[None, "warn", "suffix", None, "deep", "append", "replace", "replace", []],
    )
    @patch.object(Templar, "template", side_effect=[{"item": "value1"}, {"item": "value2"}])
    @patch.object(Display, "warning")
    def test_merge_dict_non_unique_warning(self, mock_set_options, mock_get_option, mock_template, mock_display):
        results = self.merge_vars_lookup.run(
            ["__merge_non_unique"],
            {"testdict1__merge_non_unique": {"item": "value1"}, "testdict2__merge_non_unique": {"item": "value2"}},
        )

        self.assertTrue(mock_display.called)
        self.assertEqual(results, [{"item": "value2"}])

    @patch.object(AnsiblePlugin, "set_options")
    @patch.object(
        AnsiblePlugin,
        "get_option",
        side_effect=[None, "error", "suffix", None, "deep", "append", "replace", "replace", []],
    )
    @patch.object(Templar, "template", side_effect=[{"item": "value1"}, {"item": "value2"}])
    def test_merge_dict_non_unique_error(self, mock_set_options, mock_get_option, mock_template):
        with self.assertRaises(AnsibleError):
            self.merge_vars_lookup.run(
                ["__merge_non_unique"],
                {"testdict1__merge_non_unique": {"item": "value1"}, "testdict2__merge_non_unique": {"item": "value2"}},
            )

    @patch.object(AnsiblePlugin, "set_options")
    @patch.object(
        AnsiblePlugin,
        "get_option",
        side_effect=[None, "ignore", "suffix", None, "deep", "append", "replace", "replace", []],
    )
    @patch.object(Templar, "template", side_effect=[{"item1": "test", "list_item": ["test1"]}, ["item2", "item3"]])
    def test_merge_list_and_dict(self, mock_set_options, mock_get_option, mock_template):
        with self.assertRaises(AnsibleError):
            self.merge_vars_lookup.run(
                ["__merge_var"],
                {
                    "testlist__merge_var": {"item1": "test", "list_item": ["test1"]},
                    "testdict__merge_var": ["item2", "item3"],
                },
            )

    @patch.object(AnsiblePlugin, "set_options")
    @patch.object(
        AnsiblePlugin,
        "get_option",
        side_effect=[None, "ignore", "suffix", ["all"], "deep", "append", "replace", "replace", []],
    )
    @patch.object(
        Templar,
        "template",
        side_effect=[
            {"var": [{"item1": "value1", "item2": "value2"}]},
            {"var": [{"item5": "value5", "item6": "value6"}]},
        ],
    )
    def test_merge_dict_group_all(self, mock_set_options, mock_get_option, mock_template):
        hostvars = self.HostVarsMock(
            {
                "host1": {
                    "group_names": ["dummy1"],
                    "inventory_hostname": "host1",
                    "1testlist__merge_var": {"var": [{"item1": "value1", "item2": "value2"}]},
                },
                "host2": {
                    "group_names": ["dummy1"],
                    "inventory_hostname": "host2",
                    "2otherlist__merge_var": {"var": [{"item5": "value5", "item6": "value6"}]},
                },
            }
        )
        variables = {"inventory_hostname": "host1", "hostvars": hostvars}

        results = self.merge_vars_lookup.run(["__merge_var"], variables)

        self.assertEqual(
            results, [{"var": [{"item1": "value1", "item2": "value2"}, {"item5": "value5", "item6": "value6"}]}]
        )

    @patch.object(AnsiblePlugin, "set_options")
    @patch.object(
        AnsiblePlugin,
        "get_option",
        side_effect=[None, "ignore", "suffix", ["dummy1"], "deep", "append", "replace", "replace", []],
    )
    @patch.object(
        Templar,
        "template",
        side_effect=[
            {"var": [{"item1": "value1", "item2": "value2"}]},
            {"var": [{"item5": "value5", "item6": "value6"}]},
        ],
    )
    def test_merge_dict_group_single(self, mock_set_options, mock_get_option, mock_template):
        hostvars = self.HostVarsMock(
            {
                "host1": {
                    "group_names": ["dummy1"],
                    "inventory_hostname": "host1",
                    "1testlist__merge_var": {"var": [{"item1": "value1", "item2": "value2"}]},
                },
                "host2": {
                    "group_names": ["dummy1"],
                    "inventory_hostname": "host2",
                    "2otherlist__merge_var": {"var": [{"item5": "value5", "item6": "value6"}]},
                },
                "host3": {
                    "group_names": ["dummy2"],
                    "inventory_hostname": "host3",
                    "3otherlist__merge_var": {"var": [{"item3": "value3", "item4": "value4"}]},
                },
            }
        )
        variables = {"inventory_hostname": "host1", "hostvars": hostvars}

        results = self.merge_vars_lookup.run(["__merge_var"], variables)

        self.assertEqual(
            results, [{"var": [{"item1": "value1", "item2": "value2"}, {"item5": "value5", "item6": "value6"}]}]
        )

    @patch.object(AnsiblePlugin, "set_options")
    @patch.object(
        AnsiblePlugin,
        "get_option",
        side_effect=[None, "ignore", "suffix", ["dummy1", "dummy2"], "deep", "append", "replace", "replace", []],
    )
    @patch.object(
        Templar,
        "template",
        side_effect=[
            {"var": [{"item1": "value1", "item2": "value2"}]},
            {"var": [{"item5": "value5", "item6": "value6"}]},
        ],
    )
    def test_merge_dict_group_multiple(self, mock_set_options, mock_get_option, mock_template):
        hostvars = self.HostVarsMock(
            {
                "host1": {
                    "group_names": ["dummy1"],
                    "inventory_hostname": "host1",
                    "1testlist__merge_var": {"var": [{"item1": "value1", "item2": "value2"}]},
                },
                "host2": {
                    "group_names": ["dummy2"],
                    "inventory_hostname": "host2",
                    "2otherlist__merge_var": {"var": [{"item5": "value5", "item6": "value6"}]},
                },
                "host3": {
                    "group_names": ["dummy3"],
                    "inventory_hostname": "host3",
                    "3otherlist__merge_var": {"var": [{"item3": "value3", "item4": "value4"}]},
                },
            }
        )
        variables = {"inventory_hostname": "host1", "hostvars": hostvars}
        results = self.merge_vars_lookup.run(["__merge_var"], variables)

        self.assertEqual(
            results, [{"var": [{"item1": "value1", "item2": "value2"}, {"item5": "value5", "item6": "value6"}]}]
        )

    @patch.object(AnsiblePlugin, "set_options")
    @patch.object(
        AnsiblePlugin,
        "get_option",
        side_effect=[None, "ignore", "suffix", ["dummy1", "dummy2"], "deep", "append", "replace", "replace", []],
    )
    @patch.object(
        Templar,
        "template",
        side_effect=[
            ["item1"],
            ["item5"],
        ],
    )
    def test_merge_list_group_multiple(self, mock_set_options, mock_get_option, mock_template):
        hostvars = self.HostVarsMock(
            {
                "host1": {"group_names": ["dummy1"], "inventory_hostname": "host1", "1testlist__merge_var": ["item1"]},
                "host2": {"group_names": ["dummy2"], "inventory_hostname": "host2", "2otherlist__merge_var": ["item5"]},
                "host3": {"group_names": ["dummy3"], "inventory_hostname": "host3", "3otherlist__merge_var": ["item3"]},
            }
        )
        variables = {"inventory_hostname": "host1", "hostvars": hostvars}
        results = self.merge_vars_lookup.run(["__merge_var"], variables)

        self.assertEqual(results, [["item1", "item5"]])

    @patch.object(AnsiblePlugin, "set_options")
    @patch.object(
        AnsiblePlugin,
        "get_option",
        side_effect=[None, "ignore", "suffix", None, "shallow", "replace", "replace", "replace", []],
    )
    @patch.object(
        Templar, "template", side_effect=[deepcopy(merge_hash_data["low_prio"]), deepcopy(merge_hash_data["high_prio"])]
    )
    def test_merge_dict_shallow_and_list_replace(self, mock_set_options, mock_get_option, mock_template):
        results = self.merge_vars_lookup.run(
            ["__merge_dict_shallow_and_list_replace"],
            {
                "testdict1__merge_dict_shallow_and_list_replace": merge_hash_data["low_prio"],
                "testdict2__merge_dict_shallow_and_list_replace": merge_hash_data["high_prio"],
            },
        )

        self.assertEqual(results, [merge_hash_data["high_prio"]])

    @patch.object(AnsiblePlugin, "set_options")
    @patch.object(
        AnsiblePlugin,
        "get_option",
        side_effect=[None, "ignore", "suffix", None, "shallow", "keep", "replace", "replace", []],
    )
    @patch.object(
        Templar, "template", side_effect=[deepcopy(merge_hash_data["low_prio"]), deepcopy(merge_hash_data["high_prio"])]
    )
    def test_merge_dict_shallow_and_list_keep(self, mock_set_options, mock_get_option, mock_template):
        results = self.merge_vars_lookup.run(
            ["__merge_dict_shallow_and_list_keep"],
            {
                "testdict1__merge_dict_shallow_and_list_keep": merge_hash_data["low_prio"],
                "testdict2__merge_dict_shallow_and_list_keep": merge_hash_data["high_prio"],
            },
        )

        self.assertEqual(results, [{"a": merge_hash_data["high_prio"]["a"], "b": merge_hash_data["low_prio"]["b"]}])

    @patch.object(AnsiblePlugin, "set_options")
    @patch.object(
        AnsiblePlugin,
        "get_option",
        side_effect=[None, "ignore", "suffix", None, "shallow", "append", "replace", "replace", []],
    )
    @patch.object(
        Templar, "template", side_effect=[deepcopy(merge_hash_data["low_prio"]), deepcopy(merge_hash_data["high_prio"])]
    )
    def test_merge_dict_shallow_and_list_append(self, mock_set_options, mock_get_option, mock_template):
        results = self.merge_vars_lookup.run(
            ["__merge_dict_shallow_and_list_append"],
            {
                "testdict1__merge_dict_shallow_and_list_append": merge_hash_data["low_prio"],
                "testdict2__merge_dict_shallow_and_list_append": merge_hash_data["high_prio"],
            },
        )

        self.assertEqual(
            results,
            [
                {
                    "a": merge_hash_data["high_prio"]["a"],
                    "b": merge_hash_data["low_prio"]["b"] + merge_hash_data["high_prio"]["b"],
                }
            ],
        )

    @patch.object(AnsiblePlugin, "set_options")
    @patch.object(
        AnsiblePlugin,
        "get_option",
        side_effect=[None, "ignore", "suffix", None, "shallow", "prepend", "replace", "replace", []],
    )
    @patch.object(
        Templar, "template", side_effect=[deepcopy(merge_hash_data["low_prio"]), deepcopy(merge_hash_data["high_prio"])]
    )
    def test_merge_dict_shallow_and_list_prepend(self, mock_set_options, mock_get_option, mock_template):
        results = self.merge_vars_lookup.run(
            ["__merge_dict_shallow_and_list_prepend"],
            {
                "testdict1__merge_dict_shallow_and_list_prepend": merge_hash_data["low_prio"],
                "testdict2__merge_dict_shallow_and_list_prepend": merge_hash_data["high_prio"],
            },
        )

        self.assertEqual(
            results,
            [
                {
                    "a": merge_hash_data["high_prio"]["a"],
                    "b": merge_hash_data["high_prio"]["b"] + merge_hash_data["low_prio"]["b"],
                }
            ],
        )

    @patch.object(AnsiblePlugin, "set_options")
    @patch.object(
        AnsiblePlugin,
        "get_option",
        side_effect=[None, "ignore", "suffix", None, "shallow", "append_rp", "replace", "replace", []],
    )
    @patch.object(
        Templar, "template", side_effect=[deepcopy(merge_hash_data["low_prio"]), deepcopy(merge_hash_data["high_prio"])]
    )
    def test_merge_dict_shallow_and_list_append_rp(self, mock_set_options, mock_get_option, mock_template):
        results = self.merge_vars_lookup.run(
            ["__merge_dict_shallow_and_list_append_rp"],
            {
                "testdict1__merge_dict_shallow_and_list_append_rp": merge_hash_data["low_prio"],
                "testdict2__merge_dict_shallow_and_list_append_rp": merge_hash_data["high_prio"],
            },
        )

        self.assertEqual(
            results, [{"a": merge_hash_data["high_prio"]["a"], "b": [1, 1, 2] + merge_hash_data["high_prio"]["b"]}]
        )

    @patch.object(AnsiblePlugin, "set_options")
    @patch.object(
        AnsiblePlugin,
        "get_option",
        side_effect=[None, "ignore", "suffix", None, "shallow", "prepend_rp", "replace", "replace", []],
    )
    @patch.object(
        Templar, "template", side_effect=[deepcopy(merge_hash_data["low_prio"]), deepcopy(merge_hash_data["high_prio"])]
    )
    def test_merge_dict_shallow_and_list_prepend_rp(self, mock_set_options, mock_get_option, mock_template):
        results = self.merge_vars_lookup.run(
            ["__merge_dict_shallow_and_list_prepend_rp"],
            {
                "testdict1__merge_dict_shallow_and_list_prepend_rp": merge_hash_data["low_prio"],
                "testdict2__merge_dict_shallow_and_list_prepend_rp": merge_hash_data["high_prio"],
            },
        )

        self.assertEqual(
            results, [{"a": merge_hash_data["high_prio"]["a"], "b": merge_hash_data["high_prio"]["b"] + [1, 1, 2]}]
        )

    @patch.object(AnsiblePlugin, "set_options")
    @patch.object(
        AnsiblePlugin,
        "get_option",
        side_effect=[None, "ignore", "suffix", None, "deep", "replace", "replace", "replace", []],
    )
    @patch.object(
        Templar, "template", side_effect=[deepcopy(merge_hash_data["low_prio"]), deepcopy(merge_hash_data["high_prio"])]
    )
    def test_merge_dict_deep_and_list_replace(self, mock_set_options, mock_get_option, mock_template):
        results = self.merge_vars_lookup.run(
            ["__merge_dict_deep_and_list_replace"],
            {
                "testdict1__merge_dict_deep_and_list_replace": merge_hash_data["low_prio"],
                "testdict2__merge_dict_deep_and_list_replace": merge_hash_data["high_prio"],
            },
        )

        self.assertEqual(
            results,
            [
                {
                    "a": {"a": {"x": "low_value", "y": "high_value", "z": "high_value", "list": ["high_value"]}},
                    "b": merge_hash_data["high_prio"]["b"],
                }
            ],
        )

    @patch.object(AnsiblePlugin, "set_options")
    @patch.object(
        AnsiblePlugin,
        "get_option",
        side_effect=[None, "ignore", "suffix", None, "deep", "keep", "replace", "replace", []],
    )
    @patch.object(
        Templar, "template", side_effect=[deepcopy(merge_hash_data["low_prio"]), deepcopy(merge_hash_data["high_prio"])]
    )
    def test_merge_dict_deep_and_list_keep(self, mock_set_options, mock_get_option, mock_template):
        results = self.merge_vars_lookup.run(
            ["__merge_dict_deep_and_list_keep"],
            {
                "testdict1__merge_dict_deep_and_list_keep": merge_hash_data["low_prio"],
                "testdict2__merge_dict_deep_and_list_keep": merge_hash_data["high_prio"],
            },
        )

        self.assertEqual(
            results,
            [
                {
                    "a": {"a": {"x": "low_value", "y": "high_value", "z": "high_value", "list": ["low_value"]}},
                    "b": merge_hash_data["low_prio"]["b"],
                }
            ],
        )

    @patch.object(AnsiblePlugin, "set_options")
    @patch.object(
        AnsiblePlugin,
        "get_option",
        side_effect=[None, "ignore", "suffix", None, "deep", "append", "replace", "replace", []],
    )
    @patch.object(
        Templar, "template", side_effect=[deepcopy(merge_hash_data["low_prio"]), deepcopy(merge_hash_data["high_prio"])]
    )
    def test_merge_dict_deep_and_list_append(self, mock_set_options, mock_get_option, mock_template):
        results = self.merge_vars_lookup.run(
            ["__merge_dict_deep_and_list_append"],
            {
                "testdict1__merge_dict_deep_and_list_append": merge_hash_data["low_prio"],
                "testdict2__merge_dict_deep_and_list_append": merge_hash_data["high_prio"],
            },
        )

        self.assertEqual(
            results,
            [
                {
                    "a": {
                        "a": {
                            "x": "low_value",
                            "y": "high_value",
                            "z": "high_value",
                            "list": ["low_value", "high_value"],
                        }
                    },
                    "b": merge_hash_data["low_prio"]["b"] + merge_hash_data["high_prio"]["b"],
                }
            ],
        )

    @patch.object(AnsiblePlugin, "set_options")
    @patch.object(
        AnsiblePlugin,
        "get_option",
        side_effect=[None, "ignore", "suffix", None, "deep", "prepend", "replace", "replace", []],
    )
    @patch.object(
        Templar, "template", side_effect=[deepcopy(merge_hash_data["low_prio"]), deepcopy(merge_hash_data["high_prio"])]
    )
    def test_merge_dict_deep_and_list_prepend(self, mock_set_options, mock_get_option, mock_template):
        results = self.merge_vars_lookup.run(
            ["__merge_dict_deep_and_list_prepend"],
            {
                "testdict1__merge_dict_deep_and_list_prepend": merge_hash_data["low_prio"],
                "testdict2__merge_dict_deep_and_list_prepend": merge_hash_data["high_prio"],
            },
        )

        self.assertEqual(
            results,
            [
                {
                    "a": {
                        "a": {
                            "x": "low_value",
                            "y": "high_value",
                            "z": "high_value",
                            "list": ["high_value", "low_value"],
                        }
                    },
                    "b": merge_hash_data["high_prio"]["b"] + merge_hash_data["low_prio"]["b"],
                }
            ],
        )

    @patch.object(AnsiblePlugin, "set_options")
    @patch.object(
        AnsiblePlugin,
        "get_option",
        side_effect=[None, "ignore", "suffix", None, "deep", "append_rp", "replace", "replace", []],
    )
    @patch.object(
        Templar, "template", side_effect=[deepcopy(merge_hash_data["low_prio"]), deepcopy(merge_hash_data["high_prio"])]
    )
    def test_merge_dict_deep_and_list_append_rp(self, mock_set_options, mock_get_option, mock_template):
        results = self.merge_vars_lookup.run(
            ["__merge_dict_deep_and_list_append_rp"],
            {
                "testdict1__merge_dict_deep_and_list_append_rp": merge_hash_data["low_prio"],
                "testdict2__merge_dict_deep_and_list_append_rp": merge_hash_data["high_prio"],
            },
        )

        self.assertEqual(
            results,
            [
                {
                    "a": {
                        "a": {
                            "x": "low_value",
                            "y": "high_value",
                            "z": "high_value",
                            "list": ["low_value", "high_value"],
                        }
                    },
                    "b": [1, 1, 2] + merge_hash_data["high_prio"]["b"],
                }
            ],
        )

    @patch.object(AnsiblePlugin, "set_options")
    @patch.object(
        AnsiblePlugin,
        "get_option",
        side_effect=[None, "ignore", "suffix", None, "deep", "prepend_rp", "replace", "replace", []],
    )
    @patch.object(
        Templar, "template", side_effect=[deepcopy(merge_hash_data["low_prio"]), deepcopy(merge_hash_data["high_prio"])]
    )
    def test_merge_dict_deep_and_list_prepend_rp(self, mock_set_options, mock_get_option, mock_template):
        results = self.merge_vars_lookup.run(
            ["__merge_dict_deep_and_list_prepend_rp"],
            {
                "testdict1__merge_dict_deep_and_list_prepend_rp": merge_hash_data["low_prio"],
                "testdict2__merge_dict_deep_and_list_prepend_rp": merge_hash_data["high_prio"],
            },
        )

        self.assertEqual(
            results,
            [
                {
                    "a": {
                        "a": {
                            "x": "low_value",
                            "y": "high_value",
                            "z": "high_value",
                            "list": ["high_value", "low_value"],
                        }
                    },
                    "b": merge_hash_data["high_prio"]["b"] + [1, 1, 2],
                }
            ],
        )

    @patch.object(AnsiblePlugin, "set_options")
    @patch.object(
        AnsiblePlugin,
        "get_option",
        side_effect=[None, "ignore", "suffix", None, "replace", "append", "keep", "keep", []],
    )
    @patch.object(
        Templar, "template", side_effect=[deepcopy(merge_hash_data["low_prio"]), deepcopy(merge_hash_data["high_prio"])]
    )
    def test_merge_dict_replace(self, mock_set_options, mock_get_option, mock_template):
        results = self.merge_vars_lookup.run(
            ["__merge_dict_replace"],
            {
                "testdict1__merge_dict_replace": merge_hash_data["low_prio"],
                "testdict2__merge_dict_replace": merge_hash_data["high_prio"],
            },
        )

        self.assertEqual(results, [merge_hash_data["high_prio"]])

    @patch.object(AnsiblePlugin, "set_options")
    @patch.object(
        AnsiblePlugin,
        "get_option",
        side_effect=[None, "ignore", "suffix", None, "keep", "append", "replace", "replace", []],
    )
    @patch.object(
        Templar, "template", side_effect=[deepcopy(merge_hash_data["low_prio"]), deepcopy(merge_hash_data["high_prio"])]
    )
    def test_merge_dict_keep(self, mock_set_options, mock_get_option, mock_template):
        results = self.merge_vars_lookup.run(
            ["__merge_dict_keep"],
            {
                "testdict1__merge_dict_keep": merge_hash_data["low_prio"],
                "testdict2__merge_dict_keep": merge_hash_data["high_prio"],
            },
        )

        self.assertEqual(results, [merge_hash_data["low_prio"]])

    @patch.object(AnsiblePlugin, "set_options")
    @patch.object(
        AnsiblePlugin,
        "get_option",
        side_effect=[None, "ignore", "suffix", None, "deep", "merge", "replace", "replace", []],
    )
    @patch.object(
        Templar,
        "template",
        side_effect=[[{"a": "b", "c": "d"}, {"c": "d"}], [{"a": "x", "y": "z"}, {"c": "z"}, {"a": "y"}]],
    )
    def test_merge_list_deep(self, mock_set_options, mock_get_option, mock_template):
        results = self.merge_vars_lookup.run(
            ["__merge_list_deep"],
            {
                "testdict1__merge_list_deep": [{"a": "b", "c": "d"}, {"c": "d"}],
                "testdict2__merge_list_deep": [{"a": "x", "y": "z"}, {"c": "z"}, {"a": "y"}],
            },
        )

        self.assertEqual(results, [[{"a": "x", "c": "d", "y": "z"}, {"c": "z"}, {"a": "y"}]])

    @patch.object(AnsiblePlugin, "set_options")
    @patch.object(
        AnsiblePlugin,
        "get_option",
        side_effect=[None, "ignore", "suffix", None, "deep", "append", "replace", "replace", [{"name": "dedup"}]],
    )
    @patch.object(
        Templar, "template", side_effect=[deepcopy(merge_hash_data["low_prio"]), deepcopy(merge_hash_data["high_prio"])]
    )
    def test_merge_dict_deep_and_list_dedup(self, mock_set_options, mock_get_option, mock_template):
        results = self.merge_vars_lookup.run(
            ["__merge_dict_deep_and_list_dedup"],
            {
                "testdict1__merge_dict_deep_and_list_dedup": merge_hash_data["low_prio"],
                "testdict2__merge_dict_deep_and_list_dedup": merge_hash_data["high_prio"],
            },
        )

        self.assertEqual(
            results,
            [
                {
                    "a": {
                        "a": {
                            "x": "low_value",
                            "y": "high_value",
                            "z": "high_value",
                            "list": ["low_value", "high_value"],
                        }
                    },
                    "b": [1, 2, 3, 4, {"5": "value"}],
                }
            ],
        )
