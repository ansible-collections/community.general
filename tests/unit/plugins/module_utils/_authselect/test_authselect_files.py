# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import ctypes
import unittest
from unittest.mock import Mock

from ansible_collections.community.general.plugins.module_utils._authselect.authselect_files import (
    AuthselectFiles,
    _AuthselectFilesStruct,
)


class TestAuthselectFiles(unittest.TestCase):
    CALLBACK_ATTRIBUTES = (
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
        for attribute in self.CALLBACK_ATTRIBUTES:
            setattr(AuthselectFiles, attribute, None)

    def tearDown(self):
        for attribute in self.CALLBACK_ATTRIBUTES:
            setattr(AuthselectFiles, attribute, None)

    @staticmethod
    def make_files():
        backing_struct = _AuthselectFilesStruct()
        pointer = ctypes.cast(
            ctypes.pointer(backing_struct),
            AuthselectFiles,
        )

        # The test owns this memory, so keep it alive while the pointer is used.
        pointer._test_backing_struct = backing_struct

        return pointer

    # ------------------------------------------------------------------
    # Nullable file properties
    # ------------------------------------------------------------------

    def test_nsswitch_decodes_utf8_string(self):
        files = self.make_files()
        getter = Mock(return_value="passwd: files sss ü".encode("utf-8"))
        AuthselectFiles._get_nsswitch = getter

        self.assertEqual(files.nsswitch, "passwd: files sss ü")
        getter.assert_called_once_with(files)

    def test_nsswitch_returns_none_when_getter_returns_null(self):
        files = self.make_files()
        AuthselectFiles._get_nsswitch = Mock(return_value=None)

        self.assertIsNone(files.nsswitch)

    def test_systemauth_decodes_utf8_string(self):
        files = self.make_files()
        getter = Mock(return_value="system-auth ü".encode("utf-8"))
        AuthselectFiles._get_systemauth = getter

        self.assertEqual(files.systemauth, "system-auth ü")
        getter.assert_called_once_with(files)

    def test_systemauth_returns_none_when_getter_returns_null(self):
        files = self.make_files()
        AuthselectFiles._get_systemauth = Mock(return_value=None)

        self.assertIsNone(files.systemauth)

    def test_passwordauth_decodes_utf8_string(self):
        files = self.make_files()
        getter = Mock(return_value="password-auth ü".encode("utf-8"))
        AuthselectFiles._get_passwordauth = getter

        self.assertEqual(files.passwordauth, "password-auth ü")
        getter.assert_called_once_with(files)

    def test_passwordauth_returns_none_when_getter_returns_null(self):
        files = self.make_files()
        AuthselectFiles._get_passwordauth = Mock(return_value=None)

        self.assertIsNone(files.passwordauth)

    def test_smartcardauth_decodes_utf8_string(self):
        files = self.make_files()
        getter = Mock(return_value="smartcard-auth ü".encode("utf-8"))
        AuthselectFiles._get_smartcardauth = getter

        self.assertEqual(files.smartcardauth, "smartcard-auth ü")
        getter.assert_called_once_with(files)

    def test_smartcardauth_returns_none_when_getter_returns_null(self):
        files = self.make_files()
        AuthselectFiles._get_smartcardauth = Mock(return_value=None)

        self.assertIsNone(files.smartcardauth)

    def test_fingerprintauth_decodes_utf8_string(self):
        files = self.make_files()
        getter = Mock(return_value="fingerprint-auth ü".encode("utf-8"))
        AuthselectFiles._get_fingerprintauth = getter

        self.assertEqual(files.fingerprintauth, "fingerprint-auth ü")
        getter.assert_called_once_with(files)

    def test_fingerprintauth_returns_none_when_getter_returns_null(self):
        files = self.make_files()
        AuthselectFiles._get_fingerprintauth = Mock(return_value=None)

        self.assertIsNone(files.fingerprintauth)

    def test_switchableauth_decodes_utf8_string(self):
        files = self.make_files()
        getter = Mock(return_value="switchable-auth ü".encode("utf-8"))
        AuthselectFiles._get_switchableauth = getter

        self.assertEqual(files.switchableauth, "switchable-auth ü")
        getter.assert_called_once_with(files)

    def test_switchableauth_returns_none_when_getter_returns_null(self):
        files = self.make_files()
        AuthselectFiles._get_switchableauth = Mock(return_value=None)

        self.assertIsNone(files.switchableauth)

    def test_postlogin_decodes_utf8_string(self):
        files = self.make_files()
        getter = Mock(return_value="postlogin ü".encode("utf-8"))
        AuthselectFiles._get_postlogin = getter

        self.assertEqual(files.postlogin, "postlogin ü")
        getter.assert_called_once_with(files)

    def test_postlogin_returns_none_when_getter_returns_null(self):
        files = self.make_files()
        AuthselectFiles._get_postlogin = Mock(return_value=None)

        self.assertIsNone(files.postlogin)

    # ------------------------------------------------------------------
    # Required dconf properties
    # ------------------------------------------------------------------

    def test_dconf_db_decodes_utf8_string(self):
        files = self.make_files()
        getter = Mock(return_value="/etc/dconf/db/distro.d/20-authselect ü".encode("utf-8"))
        AuthselectFiles._get_dconf_db = getter

        self.assertEqual(
            files.dconf_db,
            "/etc/dconf/db/distro.d/20-authselect ü",
        )
        getter.assert_called_once_with(files)

    def test_dconf_db_fails_when_getter_returns_null(self):
        files = self.make_files()
        AuthselectFiles._get_dconf_db = Mock(return_value=None)

        with self.assertRaisesRegex(
            RuntimeError,
            r"authselect_files_dconf_db\(\) returned NULL",
        ):
            discard = files.dconf_db

    def test_dconf_lock_decodes_utf8_string(self):
        files = self.make_files()
        getter = Mock(return_value="/etc/dconf/db/distro.d/locks/20-authselect ü".encode("utf-8"))
        AuthselectFiles._get_dconf_lock = getter

        self.assertEqual(
            files.dconf_lock,
            "/etc/dconf/db/distro.d/locks/20-authselect ü",
        )
        getter.assert_called_once_with(files)

    def test_dconf_lock_fails_when_getter_returns_null(self):
        files = self.make_files()
        AuthselectFiles._get_dconf_lock = Mock(return_value=None)

        with self.assertRaisesRegex(
            RuntimeError,
            r"authselect_files_dconf_lock\(\) returned NULL",
        ):
            discard = files.dconf_lock

    # ------------------------------------------------------------------
    # Pointer lifetime
    # ------------------------------------------------------------------

    def test_null_pointer_cannot_enter_context_manager(self):
        files = AuthselectFiles()

        with self.assertRaisesRegex(
            RuntimeError,
            "AuthselectFiles pointer is NULL",
        ):
            with files:
                pass

    def test_null_pointer_cannot_access_properties(self):
        files = AuthselectFiles()

        with self.assertRaisesRegex(
            RuntimeError,
            "AuthselectFiles pointer is NULL",
        ):
            discard = files.nsswitch

    def test_close_on_null_pointer_is_noop(self):
        files = AuthselectFiles()

        files.close()

    def test_close_without_free_function_fails(self):
        files = self.make_files()

        with self.assertRaisesRegex(
            RuntimeError,
            "AuthselectFiles free function has not been configured",
        ):
            files.close()

    def test_close_calls_configured_free_function(self):
        files = self.make_files()
        free_function = Mock()
        AuthselectFiles._free = free_function

        files.close()

        free_function.assert_called_once_with(files)
        self.assertTrue(files._closed)

    def test_close_is_idempotent(self):
        files = self.make_files()
        free_function = Mock()
        AuthselectFiles._free = free_function

        files.close()
        files.close()

        free_function.assert_called_once_with(files)

    def test_closed_files_cannot_access_properties(self):
        files = self.make_files()
        free_function = Mock()
        AuthselectFiles._free = free_function
        AuthselectFiles._get_nsswitch = Mock(return_value=b"passwd: files sss")
        files.close()

        with self.assertRaisesRegex(
            RuntimeError,
            "AuthselectFiles has already been freed",
        ):
            discard = files.nsswitch

    def test_context_manager_returns_same_files_and_frees_on_exit(self):
        files = self.make_files()
        free_function = Mock()
        AuthselectFiles._free = free_function

        with files as entered_files:
            self.assertIs(entered_files, files)
            free_function.assert_not_called()

        free_function.assert_called_once_with(files)
        self.assertTrue(files._closed)

    def test_context_manager_frees_files_when_body_raises(self):
        files = self.make_files()
        free_function = Mock()
        AuthselectFiles._free = free_function

        with self.assertRaisesRegex(RuntimeError, "test failure"):
            with files:
                raise RuntimeError("test failure")

        free_function.assert_called_once_with(files)
        self.assertTrue(files._closed)


if __name__ == "__main__":
    unittest.main()
