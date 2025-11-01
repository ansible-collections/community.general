# Copyright (c) 2024, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Make coding more python3-ish
from __future__ import annotations

import pytest

from ansible_collections.community.internal_test_tools.tests.unit.utils.trust import (
    make_untrusted as _make_untrusted,
    make_trusted as _make_trusted,
    is_trusted as _is_trusted,
    SUPPORTS_DATA_TAGGING,
)

from ansible_collections.community.general.plugins.plugin_utils.unsafe import (
    make_unsafe,
)


TEST_MAKE_UNSAFE = [
    (
        _make_trusted("text"),
        [],
        [
            (),
        ],
    ),
    (
        _make_trusted("{{text}}"),
        [
            (),
        ],
        [],
    ),
    (
        {
            _make_trusted("skey"): _make_trusted("value"),
            _make_trusted("ukey"): _make_trusted("{{value}}"),
            1: [
                _make_trusted("value"),
                _make_trusted("{{value}}"),
                {
                    1.0: _make_trusted("{{value}}"),
                    2.0: _make_trusted("value"),
                },
            ],
        },
        [
            ("ukey",),
            (1, 1),
            (1, 2, 1.0),
        ],
        [
            ("skey",),
            (1, 0),
            (1, 2, 2.0),
        ],
    ),
    (
        [_make_trusted("value"), _make_trusted("{{value}}")],
        [
            (1,),
        ],
        [
            (0,),
        ],
    ),
]

if not SUPPORTS_DATA_TAGGING:
    TEST_MAKE_UNSAFE.extend(
        [
            (
                _make_trusted(b"text"),
                [],
                [
                    (),
                ],
            ),
            (
                _make_trusted(b"{{text}}"),
                [
                    (),
                ],
                [],
            ),
        ]
    )


@pytest.mark.parametrize("value, check_unsafe_paths, check_safe_paths", TEST_MAKE_UNSAFE)
def test_make_unsafe(value, check_unsafe_paths, check_safe_paths):
    unsafe_value = make_unsafe(value)
    assert unsafe_value == value
    for check_path in check_unsafe_paths:
        obj = unsafe_value
        for elt in check_path:
            obj = obj[elt]
        assert not _is_trusted(obj)
    for check_path in check_safe_paths:
        obj = unsafe_value
        for elt in check_path:
            obj = obj[elt]
        assert _is_trusted(obj)


def test_make_unsafe_idempotence():
    assert make_unsafe(None) is None

    unsafe_str = _make_untrusted("{{test}}")
    assert id(make_unsafe(unsafe_str)) == id(unsafe_str)

    safe_str = _make_trusted("{{test}}")
    assert id(make_unsafe(safe_str)) != id(safe_str)


def test_make_unsafe_dict_key():
    value = {
        _make_trusted("test"): 2,
    }
    if not SUPPORTS_DATA_TAGGING:
        value[_make_trusted(b"test")] = 1
    unsafe_value = make_unsafe(value)
    assert unsafe_value == value
    for obj in unsafe_value:
        assert _is_trusted(obj)

    value = {
        _make_trusted("{{test}}"): 2,
    }
    if not SUPPORTS_DATA_TAGGING:
        value[_make_trusted(b"{{test}}")] = 1
    unsafe_value = make_unsafe(value)
    assert unsafe_value == value
    for obj in unsafe_value:
        assert not _is_trusted(obj)


def test_make_unsafe_set():
    value = set([_make_trusted("test")])
    if not SUPPORTS_DATA_TAGGING:
        value.add(_make_trusted(b"test"))
    unsafe_value = make_unsafe(value)
    assert unsafe_value == value
    for obj in unsafe_value:
        assert _is_trusted(obj)

    value = set([_make_trusted("{{test}}")])
    if not SUPPORTS_DATA_TAGGING:
        value.add(_make_trusted(b"{{test}}"))
    unsafe_value = make_unsafe(value)
    assert unsafe_value == value
    for obj in unsafe_value:
        assert not _is_trusted(obj)
