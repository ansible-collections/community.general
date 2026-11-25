# Copyright (c) 2026, Alexey Immoreev <lexx92@mail.ru>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import pytest

from ansible_collections.community.general.plugins.modules import osx_defaults


@pytest.mark.parametrize(
    ("base", "update", "expected"),
    [
        ({}, {"a": 1}, {"a": 1}),
        ({"a": 1, "b": 2}, {"a": 3}, {"a": 3, "b": 2}),
        ({"outer": {"keep": "x"}}, {"outer": {"new": "y"}}, {"outer": {"keep": "x", "new": "y"}}),
        ({"outer": {"keep": "x"}}, {"outer": "replaced"}, {"outer": "replaced"}),
        ({"list": [1, 2]}, {"list": [3]}, {"list": [3]}),
    ],
)
def test_deep_merge(base, update, expected):
    assert osx_defaults.OSXDefaults._deep_merge(base, update) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ({"a": 1}, {"a": 1}),
        ({10: {"b": [1, {20: 2}]}}, {"10": {"b": [1, {"20": 2}]}}),
    ],
)
def test_stringify_keys(value, expected):
    assert osx_defaults.OSXDefaults._stringify_keys(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ({"a": 1}, True),
        ([{"a": 1}], True),
        (["a", 1], False),
        ("a", False),
    ],
)
def test_has_nested_value(value, expected):
    assert osx_defaults.OSXDefaults._has_nested_value(value) is expected
