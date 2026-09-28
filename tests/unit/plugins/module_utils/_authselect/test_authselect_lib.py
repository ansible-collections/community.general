# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import ctypes

import pytest

from ansible_collections.community.general.plugins.module_utils._authselect import authselect_lib
from ansible_collections.community.general.plugins.module_utils._authselect.authselect_profile import AuthselectProfile
from ansible_collections.community.general.plugins.module_utils._authselect.c_array import (
    CStringArray,
    NullTerminatedStringArray,
)
from ansible_collections.community.general.plugins.module_utils._authselect.c_string import AllocatedCString

# ABI declarations
SIGNATURES: dict[str, tuple[list[type], type | None]] = {
    "authselect_array_free": ([ctypes.POINTER(ctypes.c_char_p)], None),
    "authselect_list": ([], NullTerminatedStringArray),
    "authselect_profile": ([ctypes.c_char_p, ctypes.POINTER(AuthselectProfile)], ctypes.c_int),
    "authselect_profile_features": ([AuthselectProfile], NullTerminatedStringArray),
    "authselect_profile_free": ([AuthselectProfile], None),
    "authselect_current_configuration": (
        [ctypes.POINTER(AllocatedCString), ctypes.POINTER(NullTerminatedStringArray)],
        ctypes.c_int,
    ),
    "authselect_activate": ([ctypes.c_char_p, CStringArray, ctypes.c_bool], ctypes.c_int),
    "authselect_validate_configuration": ([ctypes.POINTER(ctypes.c_bool)], ctypes.c_int),
    "authselect_backup": ([ctypes.c_char_p, ctypes.POINTER(AllocatedCString)], ctypes.c_int),
    "authselect_backup_remove": ([ctypes.c_char_p], ctypes.c_int),
    "authselect_backup_restore": ([ctypes.c_char_p], ctypes.c_int),
}
LOADERS = [
    (authselect_lib.get_libc_lib, "c", "_LIBC"),
    (authselect_lib.get_authselect_lib, "authselect", "_LIB"),
]


@pytest.fixture
def libraries(mocker):
    # restore the original globals and descriptors after every test
    for target, attributes in (
        (authselect_lib, ("_LIB", "_LIBC", "_DEBUG_CALLBACK")),
        (AllocatedCString, ("_free",)),
        (NullTerminatedStringArray, ("_free",)),
        (AuthselectProfile, ("_free", "_get_features")),
    ):
        for attribute in attributes:
            mocker.patch.object(target, attribute, None)

    # strict export list catches accidental dependencies on unsupported symbols
    libraries = {
        "c": mocker.Mock(spec_set=["free"]),
        "authselect": mocker.Mock(spec_set=["authselect_set_debug_fn", *SIGNATURES]),
    }
    paths = {"c": "libc.so.6", "authselect": "libauthselect.so.1"}
    mocker.patch.object(authselect_lib, "find_library", side_effect=paths.get)
    mocker.patch.object(
        authselect_lib.cdll,
        "LoadLibrary",
        side_effect={paths[name]: library for name, library in libraries.items()}.__getitem__,
    )
    return libraries


@pytest.mark.parametrize("name, signature", SIGNATURES.items(), ids=SIGNATURES)
def test_authselect_function_signatures(libraries, name, signature):
    lib = libraries["authselect"]
    authselect_lib._configure_authselect_lib(lib)

    function = getattr(lib, name)
    assert (function.argtypes, function.restype) == signature


def test_loaders_configure_and_cache_libraries(libraries, mocker):
    lib, libc = libraries["authselect"], libraries["c"]

    assert authselect_lib.get_authselect_lib() is lib
    assert authselect_lib.get_authselect_lib() is lib
    assert authselect_lib.get_libc_lib() is libc
    assert authselect_lib._LIB is lib
    assert authselect_lib._LIBC is libc
    assert authselect_lib.find_library.call_args_list == [mocker.call("authselect"), mocker.call("c")]
    assert authselect_lib.cdll.LoadLibrary.call_args_list == [
        mocker.call("libauthselect.so.1"),
        mocker.call("libc.so.6"),
    ]
    lib.authselect_set_debug_fn.assert_called_once()
    assert libc.free.argtypes == [ctypes.c_void_p]
    assert libc.free.restype is None
    assert AllocatedCString._free is libc.free
    assert NullTerminatedStringArray._free is lib.authselect_array_free
    assert AuthselectProfile._free is lib.authselect_profile_free
    assert AuthselectProfile._get_features is lib.authselect_profile_features


def test_debug_callback_is_retained_and_silent(libraries, capsys):
    lib = libraries["authselect"]
    authselect_lib._configure_authselect_lib(lib)

    callback_type = ctypes.CFUNCTYPE(
        None, ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_ulong, ctypes.c_char_p, ctypes.c_char_p
    )
    callback = authselect_lib._DEBUG_CALLBACK
    assert isinstance(callback, callback_type)
    assert lib.authselect_set_debug_fn.argtypes == [callback_type, ctypes.c_void_p]
    assert lib.authselect_set_debug_fn.restype is None
    lib.authselect_set_debug_fn.assert_called_once_with(callback, None)
    callback(None, 1, b"source.c", 42, b"authselect_activate", b"debug message")
    assert capsys.readouterr() == ("", "")


@pytest.mark.parametrize("getter, name, cache", LOADERS)
def test_missing_library_does_not_load_or_cache(libraries, getter, name, cache):
    authselect_lib.find_library.side_effect = None
    authselect_lib.find_library.return_value = None

    with pytest.raises(RuntimeError):
        getter()

    authselect_lib.find_library.assert_called_once_with(name)
    authselect_lib.cdll.LoadLibrary.assert_not_called()
    assert getattr(authselect_lib, cache) is None


@pytest.mark.parametrize("getter, name, cache", LOADERS)
def test_load_error_is_propagated_and_can_be_retried(libraries, getter, name, cache):
    load = authselect_lib.cdll.LoadLibrary
    successful_load = load.side_effect
    error = OSError("library cannot be loaded")
    load.side_effect = error

    with pytest.raises(OSError) as exc:
        getter()

    assert exc.value is error
    assert getattr(authselect_lib, cache) is None
    load.side_effect = successful_load
    assert getter() is libraries[name]


@pytest.mark.parametrize("getter, name, cache", LOADERS)
def test_missing_symbol_does_not_cache_a_partially_configured_library(libraries, getter, name, cache):
    lib = libraries[name]
    symbol = "free" if name == "c" else "authselect_backup_restore"
    function = getattr(lib, symbol)
    delattr(lib, symbol)

    with pytest.raises(AttributeError):
        getter()

    assert getattr(authselect_lib, cache) is None
    setattr(lib, symbol, function)
    assert getter() is lib


def test_libc_failure_prevents_authselect_configuration(libraries):
    lib = libraries["authselect"]
    authselect_lib.find_library.side_effect = ["libauthselect.so.1", None]

    with pytest.raises(RuntimeError):
        authselect_lib.get_authselect_lib()

    assert authselect_lib._LIB is None
    assert authselect_lib._LIBC is None
    lib.authselect_set_debug_fn.assert_not_called()
