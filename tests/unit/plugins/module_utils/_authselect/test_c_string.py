# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import ctypes
from contextlib import nullcontext

import pytest

from ansible_collections.community.general.plugins.module_utils._authselect.c_string import AllocatedCString


@pytest.fixture
def free(mocker):
    mocker.patch.object(AllocatedCString, "_free", None)
    callback = mocker.Mock()
    AllocatedCString.set_free_function(callback)
    return callback


@pytest.fixture
def string(free):
    backing = ctypes.create_string_buffer(b"authselect")
    yield ctypes.cast(backing, AllocatedCString)


@pytest.mark.parametrize(
    "data, args, expected, error",
    [
        (b"", (), "", None),
        (b"mkhomedir-\xc3\xbc", (), "mkhomedir-ü", None),
        (b"mkhomedir-\xfc", ("latin-1",), "mkhomedir-ü", None),
        (b"authselect\0ignored", (), "authselect", None),
        (b"\xff", (), None, UnicodeDecodeError),
    ],
    ids=["empty-string", "default-utf8", "requested-encoding", "first-null", "invalid-utf8"],
)
def test_decode_leaves_ownership_with_caller(free, data, args, expected, error):
    backing = ctypes.create_string_buffer(data)
    value = ctypes.cast(backing, AllocatedCString)

    with pytest.raises(error) if error else nullcontext():
        assert value.decode(*args) == expected

    free.assert_not_called()


@pytest.mark.parametrize("state", ["null", "closed"])
def test_invalid_strings_cannot_be_used(string, free, state):
    if state == "closed":
        string.close()
    else:
        string = AllocatedCString()

    with pytest.raises(RuntimeError):
        string.decode()
    with pytest.raises(RuntimeError):
        with string:
            pass

    assert free.call_count == int(state == "closed")


def test_close_on_null_pointer_is_noop(free):
    AllocatedCString().close()

    free.assert_not_called()


def test_missing_free_callback_can_be_configured_and_retried(string, free, mocker):
    mocker.patch.object(AllocatedCString, "_free", None)

    with pytest.raises(RuntimeError):
        string.close()

    AllocatedCString.set_free_function(free)
    string.close()
    free.assert_called_once_with(string)


@pytest.mark.parametrize("fail", [False, True], ids=["normal-exit", "body-failure"])
def test_context_manager_frees_exactly_once(string, free, fail):
    error = ValueError("context body failed")

    with pytest.raises(ValueError) if fail else nullcontext() as exc:
        with string as entered:
            assert entered is string
            free.assert_not_called()
            if fail:
                raise error

    if fail:
        assert exc.value is error
    free.assert_called_once_with(string)
    string.close()
    free.assert_called_once_with(string)
