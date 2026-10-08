# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import ctypes
from contextlib import nullcontext

import pytest

from ansible_collections.community.general.plugins.module_utils._authselect.authselect_profile import (
    AuthselectProfile,
    _AuthselectProfileStruct,
)
from ansible_collections.community.general.plugins.module_utils._authselect.c_array import NullTerminatedStringArray


@pytest.fixture
def profile(mocker):
    mocker.patch.object(AuthselectProfile, "_free")
    mocker.patch.object(AuthselectProfile, "_get_features")
    mocker.patch.object(NullTerminatedStringArray, "_free")
    backing = _AuthselectProfileStruct()
    yield ctypes.cast(ctypes.pointer(backing), AuthselectProfile)


@pytest.mark.parametrize(
    "values, expected, error",
    [
        ([], [], None),
        ([b"with-faillock", b"with-mkhomedir"], ["with-faillock", "with-mkhomedir"], None),
        ([b"\xff"], None, UnicodeDecodeError),
    ],
    ids=["empty", "features", "decoding-failure"],
)
def test_features_releases_array_but_keeps_profile(profile, values, expected, error):
    backing = (ctypes.c_char_p * (len(values) + 1))(*values, None)
    array = ctypes.cast(backing, NullTerminatedStringArray)
    AuthselectProfile._get_features.return_value = array

    with pytest.raises(error) if error else nullcontext():
        assert profile.features == expected

    AuthselectProfile._get_features.assert_called_once_with(profile)
    NullTerminatedStringArray._free.assert_called_once_with(array)
    AuthselectProfile._free.assert_not_called()


@pytest.mark.parametrize("result", [None, NullTerminatedStringArray()], ids=["none", "null-pointer"])
def test_features_rejects_null_output(profile, result):
    AuthselectProfile._get_features.return_value = result

    with pytest.raises(RuntimeError):
        _features = profile.features

    NullTerminatedStringArray._free.assert_not_called()


def test_features_requires_configured_getter(profile, mocker):
    mocker.patch.object(AuthselectProfile, "_get_features", None)

    with pytest.raises(RuntimeError):
        _features = profile.features


@pytest.mark.parametrize("closed", [False, True], ids=["null", "closed"])
def test_invalid_profiles_cannot_be_used(profile, closed):
    if closed:
        profile.close()
    else:
        profile = AuthselectProfile()

    with pytest.raises(RuntimeError):
        _features = profile.features
    with pytest.raises(RuntimeError):
        with profile:
            pass

    AuthselectProfile._get_features.assert_not_called()


def test_close_on_null_pointer_is_noop(profile):
    AuthselectProfile().close()

    AuthselectProfile._free.assert_not_called()


def test_missing_free_callback_can_be_configured_and_retried(profile, mocker):
    free = AuthselectProfile._free
    mocker.patch.object(AuthselectProfile, "_free", None)

    with pytest.raises(RuntimeError):
        profile.close()

    mocker.patch.object(AuthselectProfile, "_free", free)
    profile.close()
    free.assert_called_once_with(profile)


@pytest.mark.parametrize("fail", [False, True], ids=["normal-exit", "body-failure"])
def test_context_manager_frees_exactly_once(profile, fail):
    error = ValueError("context body failed")

    with pytest.raises(ValueError) if fail else nullcontext() as exc:
        with profile as entered:
            assert entered is profile
            AuthselectProfile._free.assert_not_called()
            if fail:
                raise error

    if fail:
        assert exc.value is error
    AuthselectProfile._free.assert_called_once_with(profile)
    profile.close()
    AuthselectProfile._free.assert_called_once_with(profile)
