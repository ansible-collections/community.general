# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import ctypes
from ctypes import cdll
from ctypes.util import find_library

from .authselect_profile import AuthselectProfile
from .c_array import CStringArray, NullTerminatedStringArray
from .c_string import AllocatedCString

_LIB = None
_LIBC = None
_DEBUG_CALLBACK = None


def _configure_libc_lib(lib):
    lib.free.argtypes = [ctypes.c_void_p]
    lib.free.restype = None
    AllocatedCString.set_free_function(lib.free)
    return


def get_libc_lib():
    global _LIBC

    if _LIBC is not None:
        return _LIBC

    _possible_libc = find_library("c")
    if _possible_libc is None:
        raise RuntimeError("Cannot find libc")
    libc = cdll.LoadLibrary(_possible_libc)

    _configure_libc_lib(libc)
    _LIBC = libc
    return _LIBC


def _configure_authselect_lib(lib):
    global _DEBUG_CALLBACK

    _AUTHSELECT_DEBUG_FUNCTION = ctypes.CFUNCTYPE(
        None,
        ctypes.c_void_p,
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_ulong,
        ctypes.c_char_p,
        ctypes.c_char_p,
    )

    lib.authselect_set_debug_fn.argtypes = [
        _AUTHSELECT_DEBUG_FUNCTION,
        ctypes.c_void_p,
    ]
    lib.authselect_set_debug_fn.restype = None

    _DEBUG_CALLBACK = _AUTHSELECT_DEBUG_FUNCTION(lambda pvt, level, file, line, function, msg: None)
    lib.authselect_set_debug_fn(
        _DEBUG_CALLBACK,
        None,
    )

    #
    # void authselect_array_free(char **array)
    #
    lib.authselect_array_free.argtypes = [ctypes.POINTER(ctypes.c_char_p)]
    lib.authselect_array_free.restype = None

    #
    # char **authselect_list(void)
    #
    lib.authselect_list.argtypes = []
    lib.authselect_list.restype = NullTerminatedStringArray

    #
    # int authselect_profile(
    #     const char *profile_id,
    #     struct authselect_profile **_profile
    # );
    #
    lib.authselect_profile.argtypes = [
        ctypes.c_char_p,
        ctypes.POINTER(AuthselectProfile),
    ]
    lib.authselect_profile.restype = ctypes.c_int

    #
    # char **
    # authselect_profile_features(
    #     const struct authselect_profile *profile
    # );
    #
    lib.authselect_profile_features.argtypes = [
        AuthselectProfile,
    ]
    lib.authselect_profile_features.restype = NullTerminatedStringArray

    #
    # void authselect_profile_free(
    #     struct authselect_profile *profile
    # );
    #
    lib.authselect_profile_free.argtypes = [
        AuthselectProfile,
    ]
    lib.authselect_profile_free.restype = None

    #
    # int authselect_current_configuration(
    #     char **_profile_id,
    #     char ***_features
    # );
    #
    lib.authselect_current_configuration.argtypes = [
        ctypes.POINTER(AllocatedCString),
        ctypes.POINTER(NullTerminatedStringArray),
    ]
    lib.authselect_current_configuration.restype = ctypes.c_int

    #
    # int authselect_activate(
    #     const char *profile_id,
    #     const char **features,
    #     bool force_overwrite
    # );
    #
    lib.authselect_activate.argtypes = [
        ctypes.c_char_p,
        CStringArray,
        ctypes.c_bool,
    ]
    lib.authselect_activate.restype = ctypes.c_int

    #
    # int authselect_validate_configuration(
    #     bool *_is_valid
    # );
    #
    lib.authselect_validate_configuration.argtypes = [
        ctypes.POINTER(ctypes.c_bool),
    ]
    lib.authselect_validate_configuration.restype = ctypes.c_int

    #
    # int authselect_backup(
    #     const char *name,
    #     char **_path
    # );
    #
    lib.authselect_backup.argtypes = [
        ctypes.c_char_p,
        ctypes.POINTER(AllocatedCString),
    ]
    lib.authselect_backup.restype = ctypes.c_int

    #
    # int authselect_backup_remove(
    #     const char *name
    # );
    #
    lib.authselect_backup_remove.argtypes = [
        ctypes.c_char_p,
    ]
    lib.authselect_backup_remove.restype = ctypes.c_int

    #
    # int authselect_backup_restore(
    #     const char *name
    # );
    #
    lib.authselect_backup_restore.argtypes = [
        ctypes.c_char_p,
    ]
    lib.authselect_backup_restore.restype = ctypes.c_int

    AuthselectProfile._free = staticmethod(lib.authselect_profile_free)
    AuthselectProfile._get_features = staticmethod(lib.authselect_profile_features)

    NullTerminatedStringArray.set_free_function(lib.authselect_array_free)

    return


def get_authselect_lib():
    global _LIB

    if _LIB is not None:
        return _LIB

    _possible_shared_library = find_library("authselect")
    if _possible_shared_library is None:
        raise RuntimeError("Cannot find libauthselect.so")
    lib = cdll.LoadLibrary(_possible_shared_library)

    get_libc_lib()

    _configure_authselect_lib(lib)
    _LIB = lib
    return _LIB
