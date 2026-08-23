# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import ctypes
import unittest
from unittest.mock import Mock, patch

from ansible_collections.community.general.plugins.module_utils._authselect import (
    authselect_lib,
)
from ansible_collections.community.general.plugins.module_utils._authselect.authselect_files import (
    AuthselectFiles,
)
from ansible_collections.community.general.plugins.module_utils._authselect.authselect_profile import (
    AuthselectProfile,
)
from ansible_collections.community.general.plugins.module_utils._authselect.c_array import (
    CStringArray,
    NullTerminatedStringArray,
)
from ansible_collections.community.general.plugins.module_utils._authselect.c_string import (
    AllocatedCString,
)

AUTHSELECT_FUNCTION_NAMES = (
    "authselect_set_debug_fn",
    "authselect_array_free",
    "authselect_path_systemauth",
    "authselect_path_nsswitch",
    "authselect_path_passwordauth",
    "authselect_path_smartcardauth",
    "authselect_path_fingerprintauth",
    "authselect_path_switchableauth",
    "authselect_path_postlogin",
    "authselect_path_dconf_db",
    "authselect_path_dconf_lock",
    "authselect_list",
    "authselect_backup_list",
    "authselect_profile",
    "authselect_profile_id",
    "authselect_profile_name",
    "authselect_profile_path",
    "authselect_profile_description",
    "authselect_profile_features",
    "authselect_profile_nsswitch_maps",
    "authselect_profile_requirements",
    "authselect_profile_free",
    "authselect_current_configuration",
    "authselect_activate",
    "authselect_validate_configuration",
    "authselect_files",
    "authselect_files_nsswitch",
    "authselect_files_systemauth",
    "authselect_files_passwordauth",
    "authselect_files_smartcardauth",
    "authselect_files_fingerprintauth",
    "authselect_files_switchableauth",
    "authselect_files_postlogin",
    "authselect_files_dconf_db",
    "authselect_files_dconf_lock",
    "authselect_files_free",
    "authselect_feature_enabled",
    "authselect_apply_changes",
    "authselect_backup",
    "authselect_backup_remove",
    "authselect_backup_restore",
    "authselect_feature_enable",
    "authselect_feature_disable",
    "authselect_profile_create",
    "authselect_uninstall",
)


def make_authselect_library():
    lib = Mock()

    for name in AUTHSELECT_FUNCTION_NAMES:
        setattr(lib, name, Mock(name=name))

    return lib


class TestAuthselectLib(unittest.TestCase):
    PROFILE_CALLBACK_ATTRIBUTES = (
        "_free",
        "_get_id",
        "_get_name",
        "_get_path",
        "_get_description",
        "_get_features",
        "_get_nsswitch_maps",
        "_get_requirements",
    )

    FILES_CALLBACK_ATTRIBUTES = (
        "_free",
        "_get_nsswitch",
        "_get_systemauth",
        "_get_passwordauth",
        "_get_smartcardauth",
        "_get_fingerprintauth",
        "_get_switchableauth",
        "_get_postlogin",
        "_get_dconf_db",
        "_get_dconf_lock",
    )

    def setUp(self):
        authselect_lib._LIB = None
        authselect_lib._LIBC = None
        authselect_lib._DEBUG_CALLBACK = None

        AllocatedCString._free = None
        NullTerminatedStringArray._free = None

        for attribute in self.PROFILE_CALLBACK_ATTRIBUTES:
            setattr(AuthselectProfile, attribute, None)

        for attribute in self.FILES_CALLBACK_ATTRIBUTES:
            setattr(AuthselectFiles, attribute, None)

    def tearDown(self):
        authselect_lib._LIB = None
        authselect_lib._LIBC = None
        authselect_lib._DEBUG_CALLBACK = None

        AllocatedCString._free = None
        NullTerminatedStringArray._free = None

        for attribute in self.PROFILE_CALLBACK_ATTRIBUTES:
            setattr(AuthselectProfile, attribute, None)

        for attribute in self.FILES_CALLBACK_ATTRIBUTES:
            setattr(AuthselectFiles, attribute, None)

    # ------------------------------------------------------------------
    # libc configuration and loading
    # ------------------------------------------------------------------

    def test_configure_libc_sets_free_signature_and_allocated_string_free_function(self):
        libc = Mock()
        libc.free = Mock()

        authselect_lib._configure_libc_lib(libc)

        self.assertEqual(
            libc.free.argtypes,
            [ctypes.c_void_p],
        )
        self.assertIsNone(libc.free.restype)
        self.assertIs(AllocatedCString._free, libc.free)

    def test_get_libc_lib_returns_cached_library_without_lookup(self):
        cached_libc = object()
        authselect_lib._LIBC = cached_libc

        with patch.object(authselect_lib, "find_library") as find_library, patch.object(
            authselect_lib.cdll, "LoadLibrary"
        ) as load_library:
            result = authselect_lib.get_libc_lib()

        self.assertIs(result, cached_libc)
        find_library.assert_not_called()
        load_library.assert_not_called()

    def test_get_libc_lib_fails_when_libc_cannot_be_found(self):
        with patch.object(
            authselect_lib,
            "find_library",
            return_value=None,
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "Cannot find libc",
            ):
                authselect_lib.get_libc_lib()

        self.assertIsNone(authselect_lib._LIBC)

    def test_get_libc_lib_loads_configures_and_caches_library(self):
        libc = Mock()

        with patch.object(
            authselect_lib,
            "find_library",
            return_value="libc.so.6",
        ) as find_library, patch.object(
            authselect_lib.cdll,
            "LoadLibrary",
            return_value=libc,
        ) as load_library, patch.object(
            authselect_lib,
            "_configure_libc_lib",
        ) as configure_libc:
            result = authselect_lib.get_libc_lib()

        self.assertIs(result, libc)
        self.assertIs(authselect_lib._LIBC, libc)
        find_library.assert_called_once_with("c")
        load_library.assert_called_once_with("libc.so.6")
        configure_libc.assert_called_once_with(libc)

    def test_get_libc_lib_does_not_cache_library_when_configuration_fails(self):
        libc = Mock()

        with patch.object(
            authselect_lib,
            "find_library",
            return_value="libc.so.6",
        ), patch.object(
            authselect_lib.cdll,
            "LoadLibrary",
            return_value=libc,
        ), patch.object(
            authselect_lib,
            "_configure_libc_lib",
            side_effect=RuntimeError("configuration failed"),
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "configuration failed",
            ):
                authselect_lib.get_libc_lib()

        self.assertIsNone(authselect_lib._LIBC)

    # ------------------------------------------------------------------
    # authselect library ctypes declarations
    # ------------------------------------------------------------------

    def test_configure_authselect_sets_function_signatures(self):
        lib = make_authselect_library()

        authselect_lib._configure_authselect_lib(lib)

        expected_signatures = {
            "authselect_array_free": (
                [ctypes.POINTER(ctypes.c_char_p)],
                None,
            ),
            "authselect_path_systemauth": ([], ctypes.c_char_p),
            "authselect_path_nsswitch": ([], ctypes.c_char_p),
            "authselect_path_passwordauth": ([], ctypes.c_char_p),
            "authselect_path_smartcardauth": ([], ctypes.c_char_p),
            "authselect_path_fingerprintauth": ([], ctypes.c_char_p),
            "authselect_path_switchableauth": ([], ctypes.c_char_p),
            "authselect_path_postlogin": ([], ctypes.c_char_p),
            "authselect_path_dconf_db": ([], ctypes.c_char_p),
            "authselect_path_dconf_lock": ([], ctypes.c_char_p),
            "authselect_list": ([], NullTerminatedStringArray),
            "authselect_backup_list": ([], NullTerminatedStringArray),
            "authselect_profile": (
                [
                    ctypes.c_char_p,
                    ctypes.POINTER(AuthselectProfile),
                ],
                ctypes.c_int,
            ),
            "authselect_profile_id": (
                [AuthselectProfile],
                ctypes.c_char_p,
            ),
            "authselect_profile_name": (
                [AuthselectProfile],
                ctypes.c_char_p,
            ),
            "authselect_profile_path": (
                [AuthselectProfile],
                ctypes.c_char_p,
            ),
            "authselect_profile_description": (
                [AuthselectProfile],
                ctypes.c_char_p,
            ),
            "authselect_profile_features": (
                [AuthselectProfile],
                NullTerminatedStringArray,
            ),
            "authselect_profile_nsswitch_maps": (
                [
                    AuthselectProfile,
                    CStringArray,
                ],
                NullTerminatedStringArray,
            ),
            "authselect_profile_requirements": (
                [
                    AuthselectProfile,
                    CStringArray,
                ],
                AllocatedCString,
            ),
            "authselect_profile_free": (
                [AuthselectProfile],
                None,
            ),
            "authselect_current_configuration": (
                [
                    ctypes.POINTER(AllocatedCString),
                    ctypes.POINTER(NullTerminatedStringArray),
                ],
                ctypes.c_int,
            ),
            "authselect_activate": (
                [
                    ctypes.c_char_p,
                    CStringArray,
                    ctypes.c_bool,
                ],
                ctypes.c_int,
            ),
            "authselect_validate_configuration": (
                [ctypes.POINTER(ctypes.c_bool)],
                ctypes.c_int,
            ),
            "authselect_files": (
                [
                    ctypes.c_char_p,
                    CStringArray,
                    ctypes.POINTER(AuthselectFiles),
                ],
                ctypes.c_int,
            ),
            "authselect_files_nsswitch": (
                [AuthselectFiles],
                ctypes.c_char_p,
            ),
            "authselect_files_systemauth": (
                [AuthselectFiles],
                ctypes.c_char_p,
            ),
            "authselect_files_passwordauth": (
                [AuthselectFiles],
                ctypes.c_char_p,
            ),
            "authselect_files_smartcardauth": (
                [AuthselectFiles],
                ctypes.c_char_p,
            ),
            "authselect_files_fingerprintauth": (
                [AuthselectFiles],
                ctypes.c_char_p,
            ),
            "authselect_files_switchableauth": (
                [AuthselectFiles],
                ctypes.c_char_p,
            ),
            "authselect_files_postlogin": (
                [AuthselectFiles],
                ctypes.c_char_p,
            ),
            "authselect_files_dconf_db": (
                [AuthselectFiles],
                ctypes.c_char_p,
            ),
            "authselect_files_dconf_lock": (
                [AuthselectFiles],
                ctypes.c_char_p,
            ),
            "authselect_files_free": (
                [AuthselectFiles],
                None,
            ),
            "authselect_feature_enabled": (
                [ctypes.c_char_p],
                ctypes.c_int,
            ),
            "authselect_apply_changes": (
                [ctypes.c_bool],
                ctypes.c_int,
            ),
            "authselect_backup": (
                [
                    ctypes.c_char_p,
                    ctypes.POINTER(AllocatedCString),
                ],
                ctypes.c_int,
            ),
            "authselect_backup_remove": (
                [ctypes.c_char_p],
                ctypes.c_int,
            ),
            "authselect_backup_restore": (
                [ctypes.c_char_p],
                ctypes.c_int,
            ),
            "authselect_feature_enable": (
                [ctypes.c_char_p],
                ctypes.c_int,
            ),
            "authselect_feature_disable": (
                [ctypes.c_char_p],
                ctypes.c_int,
            ),
            "authselect_profile_create": (
                [
                    ctypes.c_char_p,
                    ctypes.c_int,
                    ctypes.c_char_p,
                    ctypes.c_int,
                    ctypes.c_uint32,
                    CStringArray,
                    ctypes.POINTER(AllocatedCString),
                ],
                ctypes.c_int,
            ),
            "authselect_uninstall": (
                [],
                ctypes.c_int,
            ),
        }

        for function_name, (expected_argtypes, expected_restype) in expected_signatures.items():
            with self.subTest(function=function_name):
                function = getattr(lib, function_name)
                self.assertEqual(
                    function.argtypes,
                    expected_argtypes,
                )
                self.assertIs(
                    function.restype,
                    expected_restype,
                )

    def test_configure_authselect_configures_debug_callback_signature_and_registers_callback(self):
        lib = make_authselect_library()

        authselect_lib._configure_authselect_lib(lib)

        self.assertEqual(
            len(lib.authselect_set_debug_fn.argtypes),
            2,
        )
        self.assertIs(
            lib.authselect_set_debug_fn.argtypes[1],
            ctypes.c_void_p,
        )
        self.assertIsNone(
            lib.authselect_set_debug_fn.restype,
        )
        self.assertIsNotNone(authselect_lib._DEBUG_CALLBACK)
        lib.authselect_set_debug_fn.assert_called_once_with(
            authselect_lib._DEBUG_CALLBACK,
            None,
        )

    def test_configure_authselect_keeps_debug_callback_alive_globally(self):
        lib = make_authselect_library()

        authselect_lib._configure_authselect_lib(lib)

        callback = authselect_lib._DEBUG_CALLBACK

        self.assertIsNotNone(callback)
        self.assertIs(
            lib.authselect_set_debug_fn.call_args.args[0],
            callback,
        )

    # ------------------------------------------------------------------
    # Wrapper callback wiring
    # ------------------------------------------------------------------

    def test_configure_authselect_wires_profile_callbacks(self):
        lib = make_authselect_library()

        authselect_lib._configure_authselect_lib(lib)

        expected_callbacks = {
            "_free": lib.authselect_profile_free,
            "_get_id": lib.authselect_profile_id,
            "_get_name": lib.authselect_profile_name,
            "_get_path": lib.authselect_profile_path,
            "_get_description": lib.authselect_profile_description,
            "_get_features": lib.authselect_profile_features,
            "_get_nsswitch_maps": lib.authselect_profile_nsswitch_maps,
            "_get_requirements": lib.authselect_profile_requirements,
        }

        for attribute, expected in expected_callbacks.items():
            with self.subTest(attribute=attribute):
                self.assertIs(
                    getattr(AuthselectProfile, attribute),
                    expected,
                )

    def test_configure_authselect_wires_files_callbacks(self):
        lib = make_authselect_library()

        authselect_lib._configure_authselect_lib(lib)

        expected_callbacks = {
            "_free": lib.authselect_files_free,
            "_get_nsswitch": lib.authselect_files_nsswitch,
            "_get_systemauth": lib.authselect_files_systemauth,
            "_get_passwordauth": lib.authselect_files_passwordauth,
            "_get_smartcardauth": lib.authselect_files_smartcardauth,
            "_get_fingerprintauth": lib.authselect_files_fingerprintauth,
            "_get_switchableauth": lib.authselect_files_switchableauth,
            "_get_postlogin": lib.authselect_files_postlogin,
            "_get_dconf_db": lib.authselect_files_dconf_db,
            "_get_dconf_lock": lib.authselect_files_dconf_lock,
        }

        for attribute, expected in expected_callbacks.items():
            with self.subTest(attribute=attribute):
                self.assertIs(
                    getattr(AuthselectFiles, attribute),
                    expected,
                )

    def test_configure_authselect_wires_array_free_function(self):
        lib = make_authselect_library()

        authselect_lib._configure_authselect_lib(lib)

        self.assertIs(
            NullTerminatedStringArray._free,
            lib.authselect_array_free,
        )

    # ------------------------------------------------------------------
    # authselect library loading
    # ------------------------------------------------------------------

    def test_get_authselect_lib_returns_cached_library_without_lookup(self):
        cached_lib = object()
        authselect_lib._LIB = cached_lib

        with patch.object(authselect_lib, "find_library") as find_library, patch.object(
            authselect_lib.cdll, "LoadLibrary"
        ) as load_library, patch.object(authselect_lib, "get_libc_lib") as get_libc, patch.object(
            authselect_lib, "_configure_authselect_lib"
        ) as configure_authselect:
            result = authselect_lib.get_authselect_lib()

        self.assertIs(result, cached_lib)
        find_library.assert_not_called()
        load_library.assert_not_called()
        get_libc.assert_not_called()
        configure_authselect.assert_not_called()

    def test_get_authselect_lib_fails_when_library_cannot_be_found(self):
        with patch.object(
            authselect_lib,
            "find_library",
            return_value=None,
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                r"Cannot find libauthselect\.so",
            ):
                authselect_lib.get_authselect_lib()

        self.assertIsNone(authselect_lib._LIB)

    def test_get_authselect_lib_loads_libc_configures_and_caches_library(self):
        lib = Mock()
        libc = Mock()

        with patch.object(
            authselect_lib,
            "find_library",
            return_value="libauthselect.so.1",
        ) as find_library, patch.object(
            authselect_lib.cdll,
            "LoadLibrary",
            return_value=lib,
        ) as load_library, patch.object(
            authselect_lib,
            "get_libc_lib",
            return_value=libc,
        ) as get_libc, patch.object(
            authselect_lib,
            "_configure_authselect_lib",
        ) as configure_authselect:
            result = authselect_lib.get_authselect_lib()

        self.assertIs(result, lib)
        self.assertIs(authselect_lib._LIB, lib)
        find_library.assert_called_once_with("authselect")
        load_library.assert_called_once_with("libauthselect.so.1")
        get_libc.assert_called_once_with()
        configure_authselect.assert_called_once_with(lib)

    def test_get_authselect_lib_configures_before_caching(self):
        lib = Mock()

        def configure(candidate):
            self.assertIs(candidate, lib)
            self.assertIsNone(authselect_lib._LIB)

        with patch.object(
            authselect_lib,
            "find_library",
            return_value="libauthselect.so.1",
        ), patch.object(
            authselect_lib.cdll,
            "LoadLibrary",
            return_value=lib,
        ), patch.object(authselect_lib, "get_libc_lib"), patch.object(
            authselect_lib,
            "_configure_authselect_lib",
            side_effect=configure,
        ):
            result = authselect_lib.get_authselect_lib()

        self.assertIs(result, lib)
        self.assertIs(authselect_lib._LIB, lib)

    def test_get_authselect_lib_does_not_cache_library_when_libc_loading_fails(self):
        lib = Mock()

        with patch.object(
            authselect_lib,
            "find_library",
            return_value="libauthselect.so.1",
        ), patch.object(
            authselect_lib.cdll,
            "LoadLibrary",
            return_value=lib,
        ), patch.object(
            authselect_lib,
            "get_libc_lib",
            side_effect=RuntimeError("libc failed"),
        ), patch.object(
            authselect_lib,
            "_configure_authselect_lib",
        ) as configure_authselect:
            with self.assertRaisesRegex(
                RuntimeError,
                "libc failed",
            ):
                authselect_lib.get_authselect_lib()

        self.assertIsNone(authselect_lib._LIB)
        configure_authselect.assert_not_called()

    def test_get_authselect_lib_does_not_cache_library_when_configuration_fails(self):
        lib = Mock()

        with patch.object(
            authselect_lib,
            "find_library",
            return_value="libauthselect.so.1",
        ), patch.object(
            authselect_lib.cdll,
            "LoadLibrary",
            return_value=lib,
        ), patch.object(authselect_lib, "get_libc_lib"), patch.object(
            authselect_lib,
            "_configure_authselect_lib",
            side_effect=RuntimeError("configuration failed"),
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "configuration failed",
            ):
                authselect_lib.get_authselect_lib()

        self.assertIsNone(authselect_lib._LIB)


if __name__ == "__main__":
    unittest.main()
