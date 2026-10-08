# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import ctypes
import gc
from contextlib import nullcontext

import pytest

from ansible_collections.community.general.plugins.module_utils._authselect.c_array import (
    CStringArray,
    NullTerminatedStringArray,
)


@pytest.fixture
def free(mocker):
    mocker.patch.object(NullTerminatedStringArray, "_free", None)
    callback = mocker.Mock()
    NullTerminatedStringArray.set_free_function(callback)
    return callback


@pytest.fixture
def array(free):
    backing = (ctypes.c_char_p * 2)(b"with-faillock", None)
    yield ctypes.cast(backing, NullTerminatedStringArray)


@pytest.mark.parametrize(
    "values, expected",
    [
        ([], []),
        ([""], [b""]),
        (["with-faillock", "mkhomedir-ü"], [b"with-faillock", b"mkhomedir-\xc3\xbc"]),
    ],
    ids=["empty-array", "empty-string", "utf8"],
)
def test_from_strings_owns_utf8_data_and_null_terminator(values, expected):
    source = list(values)
    pointer = CStringArray.from_strings(source)
    source.clear()
    gc.collect()

    assert isinstance(pointer, CStringArray)
    assert [pointer[index] for index in range(len(expected) + 1)] == [*expected, None]


@pytest.mark.parametrize(
    "values, expected, error",
    [
        ([None], [], None),
        ([b"with-faillock", b"mkhomedir-\xc3\xbc", None], ["with-faillock", "mkhomedir-ü"], None),
        ([b"", b"after-empty", None], ["", "after-empty"], None),
        ([b"first", None, b"ignored", None], ["first"], None),
        ([b"\xff", None], None, UnicodeDecodeError),
    ],
    ids=["empty-array", "utf8", "empty-string", "first-null", "invalid-utf8"],
)
def test_iteration_decodes_until_first_null(free, values, expected, error):
    backing = (ctypes.c_char_p * len(values))(*values)
    pointer = ctypes.cast(backing, NullTerminatedStringArray)

    with pytest.raises(error) if error else nullcontext():
        assert list(pointer) == expected

    free.assert_not_called()


@pytest.mark.parametrize("state", ["null", "closed"])
def test_invalid_arrays_cannot_be_used(array, free, state):
    if state == "closed":
        array.close()
    else:
        array = NullTerminatedStringArray()

    with pytest.raises(RuntimeError):
        list(array)
    with pytest.raises(RuntimeError):
        with array:
            pass

    assert free.call_count == int(state == "closed")


def test_close_on_null_pointer_is_noop(free):
    NullTerminatedStringArray().close()

    free.assert_not_called()


def test_missing_free_callback_can_be_configured_and_retried(array, free, mocker):
    mocker.patch.object(NullTerminatedStringArray, "_free", None)

    with pytest.raises(RuntimeError):
        array.close()

    NullTerminatedStringArray.set_free_function(free)
    array.close()
    free.assert_called_once_with(array)


@pytest.mark.parametrize("fail", [False, True], ids=["normal-exit", "body-failure"])
def test_context_manager_frees_exactly_once(array, free, fail):
    error = ValueError("context body failed")

    with pytest.raises(ValueError) if fail else nullcontext() as exc:
        with array as entered:
            assert entered is array
            free.assert_not_called()
            if fail:
                raise error

    if fail:
        assert exc.value is error
    free.assert_called_once_with(array)
    array.close()
    free.assert_called_once_with(array)
