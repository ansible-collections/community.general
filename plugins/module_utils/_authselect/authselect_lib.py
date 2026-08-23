# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import ctypes
from ctypes import cdll
from ctypes.util import find_library

from .authselect_files import AuthselectFiles
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
    # const char *authselect_path_systemauth(void)
    #
    lib.authselect_path_systemauth.argtypes = []
    lib.authselect_path_systemauth.restype = ctypes.c_char_p

    #
    # const char *authselect_path_nsswitch(void)
    #
    lib.authselect_path_nsswitch.argtypes = []
    lib.authselect_path_nsswitch.restype = ctypes.c_char_p

    #
    # const char *authselect_path_passwordauth(void)
    #
    lib.authselect_path_passwordauth.argtypes = []
    lib.authselect_path_passwordauth.restype = ctypes.c_char_p

    #
    # const char *authselect_path_smartcardauth(void)
    #
    lib.authselect_path_smartcardauth.argtypes = []
    lib.authselect_path_smartcardauth.restype = ctypes.c_char_p

    #
    # const char *authselect_path_fingerprintauth(void)
    #
    lib.authselect_path_fingerprintauth.argtypes = []
    lib.authselect_path_fingerprintauth.restype = ctypes.c_char_p

    #
    # const char *authselect_path_switchableauth(void)
    #
    if hasattr(lib, "authselect_path_switchableauth"):
        lib.authselect_path_switchableauth.argtypes = []
        lib.authselect_path_switchableauth.restype = ctypes.c_char_p

    #
    # const char *authselect_path_postlogin(void)
    #
    lib.authselect_path_postlogin.argtypes = []
    lib.authselect_path_postlogin.restype = ctypes.c_char_p

    #
    # const char *authselect_path_dconf_db(void)
    #
    lib.authselect_path_dconf_db.argtypes = []
    lib.authselect_path_dconf_db.restype = ctypes.c_char_p

    #
    # const char *authselect_path_dconf_lock(void)
    #
    lib.authselect_path_dconf_lock.argtypes = []
    lib.authselect_path_dconf_lock.restype = ctypes.c_char_p

    #
    # char **authselect_list(void)
    #
    lib.authselect_list.argtypes = []
    lib.authselect_list.restype = NullTerminatedStringArray

    #
    # char **authselect_backup_list(void)
    #
    lib.authselect_backup_list.argtypes = []
    lib.authselect_backup_list.restype = NullTerminatedStringArray

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
    # const char *
    # authselect_profile_id(
    #     const struct authselect_profile *profile
    # );
    #
    lib.authselect_profile_id.argtypes = [
        AuthselectProfile,
    ]
    lib.authselect_profile_id.restype = ctypes.c_char_p

    #
    # const char *
    # authselect_profile_name(
    #     const struct authselect_profile *profile
    # );
    #
    lib.authselect_profile_name.argtypes = [
        AuthselectProfile,
    ]
    lib.authselect_profile_name.restype = ctypes.c_char_p

    #
    # const char *
    # authselect_profile_path(
    #     const struct authselect_profile *profile
    # );
    #
    lib.authselect_profile_path.argtypes = [
        AuthselectProfile,
    ]
    lib.authselect_profile_path.restype = ctypes.c_char_p

    #
    # const char *
    # authselect_profile_description(
    #     const struct authselect_profile *profile
    # );
    #
    lib.authselect_profile_description.argtypes = [
        AuthselectProfile,
    ]
    lib.authselect_profile_description.restype = ctypes.c_char_p

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
    # char **
    # authselect_profile_nsswitch_maps(
    #     const struct authselect_profile *profile,
    #     const char **features
    # );
    #
    lib.authselect_profile_nsswitch_maps.argtypes = [
        AuthselectProfile,
        CStringArray,
    ]
    lib.authselect_profile_nsswitch_maps.restype = NullTerminatedStringArray

    #
    # char *
    # authselect_profile_requirements(
    #     const struct authselect_profile *profile,
    #     const char **features
    # );
    #
    lib.authselect_profile_requirements.argtypes = [
        AuthselectProfile,
        CStringArray,
    ]
    lib.authselect_profile_requirements.restype = AllocatedCString

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
    # int authselect_files(
    #     const char *profile_id,
    #     const char **features,
    #     struct authselect_files **_files
    # );
    #
    lib.authselect_files.argtypes = [
        ctypes.c_char_p,
        CStringArray,
        ctypes.POINTER(AuthselectFiles),
    ]
    lib.authselect_files.restype = ctypes.c_int

    #
    # const char *
    # authselect_files_nsswitch(
    #     const struct authselect_files *files
    # );
    #
    lib.authselect_files_nsswitch.argtypes = [
        AuthselectFiles,
    ]
    lib.authselect_files_nsswitch.restype = ctypes.c_char_p

    #
    # const char *
    # authselect_files_systemauth(
    #     const struct authselect_files *files
    # );
    #
    lib.authselect_files_systemauth.argtypes = [
        AuthselectFiles,
    ]
    lib.authselect_files_systemauth.restype = ctypes.c_char_p

    #
    # const char *
    # authselect_files_passwordauth(
    #     const struct authselect_files *files
    # );
    #
    lib.authselect_files_passwordauth.argtypes = [
        AuthselectFiles,
    ]
    lib.authselect_files_passwordauth.restype = ctypes.c_char_p

    #
    # const char *
    # authselect_files_smartcardauth(
    #     const struct authselect_files *files
    # );
    #
    lib.authselect_files_smartcardauth.argtypes = [
        AuthselectFiles,
    ]
    lib.authselect_files_smartcardauth.restype = ctypes.c_char_p

    #
    # const char *
    # authselect_files_fingerprintauth(
    #     const struct authselect_files *files
    # );
    #
    lib.authselect_files_fingerprintauth.argtypes = [
        AuthselectFiles,
    ]
    lib.authselect_files_fingerprintauth.restype = ctypes.c_char_p

    #
    # const char *
    # authselect_files_switchableauth(
    #     const struct authselect_files *files
    # );
    #
    if hasattr(lib, "authselect_files_switchableauth"):
        lib.authselect_files_switchableauth.argtypes = [
            AuthselectFiles,
        ]
        lib.authselect_files_switchableauth.restype = ctypes.c_char_p

    #
    # const char *
    # authselect_files_postlogin(
    #     const struct authselect_files *files
    # );
    #
    lib.authselect_files_postlogin.argtypes = [
        AuthselectFiles,
    ]
    lib.authselect_files_postlogin.restype = ctypes.c_char_p

    #
    # const char *
    # authselect_files_dconf_db(
    #     const struct authselect_files *files
    # );
    #
    lib.authselect_files_dconf_db.argtypes = [
        AuthselectFiles,
    ]
    lib.authselect_files_dconf_db.restype = ctypes.c_char_p

    #
    # const char *
    # authselect_files_dconf_lock(
    #     const struct authselect_files *files
    # );
    #
    lib.authselect_files_dconf_lock.argtypes = [
        AuthselectFiles,
    ]
    lib.authselect_files_dconf_lock.restype = ctypes.c_char_p

    #
    # void authselect_files_free(
    #     struct authselect_files *files
    # );
    #
    lib.authselect_files_free.argtypes = [
        AuthselectFiles,
    ]
    lib.authselect_files_free.restype = None

    #
    # int authselect_feature_enabled(
    #     const char *feature
    # );
    #
    lib.authselect_feature_enabled.argtypes = [
        ctypes.c_char_p,
    ]
    lib.authselect_feature_enabled.restype = ctypes.c_int

    #
    # int authselect_apply_changes(
    #     bool upgrade
    # );
    #
    lib.authselect_apply_changes.argtypes = [
        ctypes.c_bool,
    ]
    lib.authselect_apply_changes.restype = ctypes.c_int

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

    #
    # int authselect_feature_enable(
    #     const char *feature
    # );
    #
    lib.authselect_feature_enable.argtypes = [
        ctypes.c_char_p,
    ]
    lib.authselect_feature_enable.restype = ctypes.c_int

    #
    # int authselect_feature_disable(
    #     const char *feature
    # );
    #
    lib.authselect_feature_disable.argtypes = [
        ctypes.c_char_p,
    ]
    lib.authselect_feature_disable.restype = ctypes.c_int

    #
    # int authselect_profile_create(
    #     const char *name,
    #     enum authselect_profile_type type,
    #     const char *base_id,
    #     enum authselect_profile_type base_type,
    #     uint32_t symlink_flags,
    #     const char **symlinks,
    #     char **_path
    # );
    #
    lib.authselect_profile_create.argtypes = [
        ctypes.c_char_p,
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_int,
        ctypes.c_uint32,
        CStringArray,
        ctypes.POINTER(AllocatedCString),
    ]
    lib.authselect_profile_create.restype = ctypes.c_int

    #
    # int authselect_uninstall(void);
    #
    lib.authselect_uninstall.argtypes = []
    lib.authselect_uninstall.restype = ctypes.c_int

    AuthselectProfile._free = staticmethod(lib.authselect_profile_free)
    AuthselectProfile._get_id = staticmethod(lib.authselect_profile_id)
    AuthselectProfile._get_name = staticmethod(lib.authselect_profile_name)
    AuthselectProfile._get_path = staticmethod(lib.authselect_profile_path)
    AuthselectProfile._get_description = staticmethod(lib.authselect_profile_description)
    AuthselectProfile._get_features = staticmethod(lib.authselect_profile_features)
    AuthselectProfile._get_nsswitch_maps = staticmethod(lib.authselect_profile_nsswitch_maps)
    AuthselectProfile._get_requirements = staticmethod(lib.authselect_profile_requirements)

    AuthselectFiles._free = staticmethod(lib.authselect_files_free)
    AuthselectFiles._get_nsswitch = staticmethod(lib.authselect_files_nsswitch)
    AuthselectFiles._get_systemauth = staticmethod(lib.authselect_files_systemauth)
    AuthselectFiles._get_passwordauth = staticmethod(lib.authselect_files_passwordauth)
    AuthselectFiles._get_smartcardauth = staticmethod(lib.authselect_files_smartcardauth)
    AuthselectFiles._get_fingerprintauth = staticmethod(lib.authselect_files_fingerprintauth)
    if hasattr(lib, "authselect_files_switchableauth"):
        AuthselectFiles._get_switchableauth = staticmethod(lib.authselect_files_switchableauth)
    AuthselectFiles._get_postlogin = staticmethod(lib.authselect_files_postlogin)
    AuthselectFiles._get_dconf_db = staticmethod(lib.authselect_files_dconf_db)
    AuthselectFiles._get_dconf_lock = staticmethod(lib.authselect_files_dconf_lock)

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
