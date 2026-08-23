# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import errno
import os
import unittest
from unittest.mock import Mock, patch

from ansible_collections.community.general.plugins.module_utils._authselect import authselect
from ansible_collections.community.general.plugins.module_utils._authselect.authselect_enums import (
    AuthselectProfileType,
    AuthselectSymlinkFlag,
    AuthselectValidationStatus,
)


class FakeAllocatedCString:
    def __init__(self, value: str | None = None):
        self.value = value
        self.entered = False
        self.exited = False
        self.closed = False

    def __bool__(self):
        return self.value is not None

    def __enter__(self):
        self.entered = True
        return self

    def __exit__(self, *args):
        self.exited = True
        self.closed = True

    def close(self):
        self.closed = True

    def decode(self, encoding="utf-8"):
        if self.value is None:
            raise RuntimeError("cannot decode NULL fake string")
        return self.value.encode("utf-8").decode(encoding)


class FakeStringArray:
    def __init__(self, values: list[str] | None = None):
        self.values = values
        self.entered = False
        self.exited = False

    def __bool__(self):
        return self.values is not None

    def __enter__(self):
        self.entered = True
        return self

    def __exit__(self, *args):
        self.exited = True

    def __iter__(self):
        return iter(self.values or [])


class FakePointer:
    def __init__(self, valid=True):
        self.valid = valid

    def __bool__(self):
        return self.valid


class TestAuthselect(unittest.TestCase):
    def setUp(self):
        self.lib = Mock()

        with patch.object(
            authselect,
            "get_authselect_lib",
            return_value=self.lib,
        ) as get_authselect_lib:
            self.wrapper = authselect.Authselect()

        get_authselect_lib.assert_called_once_with()
        self.assertIs(self.wrapper._lib, self.lib)

    # ------------------------------------------------------------------
    # Static authselect file paths
    # ------------------------------------------------------------------

    def test_get_authselect_paths_decode_utf8(self):
        path_methods = (
            ("get_nsswitch_path", "authselect_path_nsswitch", "/etc/nsswitch.conf"),
            ("get_systemauth_path", "authselect_path_systemauth", "/etc/pam.d/system-auth"),
            ("get_passwordauth_path", "authselect_path_passwordauth", "/etc/pam.d/password-auth"),
            ("get_smartcardauth_path", "authselect_path_smartcardauth", "/etc/pam.d/smartcard-auth"),
            ("get_fingerprintauth_path", "authselect_path_fingerprintauth", "/etc/pam.d/fingerprint-auth"),
            ("get_switchableauth_path", "authselect_path_switchableauth", "/etc/pam.d/switchable-auth"),
            ("get_postlogin_path", "authselect_path_postlogin", "/etc/pam.d/postlogin"),
            ("get_dconf_db_path", "authselect_path_dconf_db", "/etc/dconf/db/distro.d/20-authselect"),
            ("get_dconf_lock_path", "authselect_path_dconf_lock", "/etc/dconf/db/distro.d/locks/20-authselect"),
        )

        for wrapper_method, library_method, expected in path_methods:
            with self.subTest(wrapper_method=wrapper_method):
                getattr(self.lib, library_method).reset_mock()
                getattr(self.lib, library_method).return_value = expected.encode("utf-8")

                result = getattr(self.wrapper, wrapper_method)()

                self.assertEqual(result, expected)
                getattr(self.lib, library_method).assert_called_once_with()

    # ------------------------------------------------------------------
    # Profile and backup lists
    # ------------------------------------------------------------------

    def test_get_profiles_list_returns_values_and_closes_array(self):
        profiles = FakeStringArray(["sssd", "minimal"])
        self.lib.authselect_list.return_value = profiles

        result = self.wrapper.get_profiles_list()

        self.assertEqual(result, ["sssd", "minimal"])
        self.assertTrue(profiles.entered)
        self.assertTrue(profiles.exited)
        self.lib.authselect_list.assert_called_once_with()

    def test_get_backups_list_returns_values_and_closes_array(self):
        backups = FakeStringArray(["backup-1", "backup-2"])
        self.lib.authselect_backup_list.return_value = backups

        result = self.wrapper.get_backups_list()

        self.assertEqual(result, ["backup-1", "backup-2"])
        self.assertTrue(backups.entered)
        self.assertTrue(backups.exited)
        self.lib.authselect_backup_list.assert_called_once_with()

    # ------------------------------------------------------------------
    # Profiles
    # ------------------------------------------------------------------

    def test_get_profile_passes_utf8_profile_id_and_returns_profile(self):
        profile = FakePointer(valid=True)
        self.lib.authselect_profile.return_value = 0

        with patch.object(authselect, "AuthselectProfile", return_value=profile), patch.object(
            authselect.ctypes, "byref", side_effect=lambda value: value
        ):
            result = self.wrapper.get_profile("sssd-ü")

        self.assertIs(result, profile)
        self.lib.authselect_profile.assert_called_once_with(
            "sssd-ü".encode("utf-8"),
            profile,
        )

    def test_get_profile_propagates_nonzero_status_as_runtime_error(self):
        profile = FakePointer(valid=True)
        self.lib.authselect_profile.return_value = errno.EINVAL

        with patch.object(authselect, "AuthselectProfile", return_value=profile), patch.object(
            authselect.ctypes, "byref", side_effect=lambda value: value
        ):
            with self.assertRaisesRegex(RuntimeError, r"authselect_profile\(\) failed"):
                self.wrapper.get_profile("sssd")

    def test_get_profile_fails_when_success_returns_null_profile(self):
        profile = FakePointer(valid=False)
        self.lib.authselect_profile.return_value = 0

        with patch.object(authselect, "AuthselectProfile", return_value=profile), patch.object(
            authselect.ctypes, "byref", side_effect=lambda value: value
        ):
            with self.assertRaisesRegex(RuntimeError, r"authselect_profile\(\) returned a NULL profile"):
                self.wrapper.get_profile("sssd")

    # ------------------------------------------------------------------
    # Rendered profile files
    # ------------------------------------------------------------------

    def test_get_files_passes_profile_and_requested_features(self):
        files = FakePointer(valid=True)
        c_features = object()
        self.lib.authselect_files.return_value = 0

        with patch.object(authselect, "AuthselectFiles", return_value=files), patch.object(
            authselect.CStringArray, "from_strings", return_value=c_features
        ) as from_strings, patch.object(authselect.ctypes, "byref", side_effect=lambda value: value):
            result = self.wrapper.get_files(
                "sssd-ü",
                ["with-faillock", "with-mkhomedir"],
            )

        self.assertIs(result, files)
        from_strings.assert_called_once_with(["with-faillock", "with-mkhomedir"])
        self.lib.authselect_files.assert_called_once_with(
            "sssd-ü".encode("utf-8"),
            c_features,
            files,
        )

    def test_get_files_uses_empty_feature_array_when_features_omitted(self):
        files = FakePointer(valid=True)
        c_features = object()
        self.lib.authselect_files.return_value = 0

        with patch.object(authselect, "AuthselectFiles", return_value=files), patch.object(
            authselect.CStringArray, "from_strings", return_value=c_features
        ) as from_strings, patch.object(authselect.ctypes, "byref", side_effect=lambda value: value):
            self.wrapper.get_files("sssd")

        from_strings.assert_called_once_with([])

    def test_get_files_reports_missing_profile(self):
        files = FakePointer(valid=True)
        self.lib.authselect_files.return_value = errno.ENOENT

        with patch.object(authselect, "AuthselectFiles", return_value=files), patch.object(
            authselect.ctypes, "byref", side_effect=lambda value: value
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "Authselect profile 'missing' does not exist",
            ):
                self.wrapper.get_files("missing")

    def test_get_files_reports_other_library_error(self):
        files = FakePointer(valid=True)
        self.lib.authselect_files.return_value = errno.EACCES

        with patch.object(authselect, "AuthselectFiles", return_value=files), patch.object(
            authselect.ctypes, "byref", side_effect=lambda value: value
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                r"authselect_files\(\) failed",
            ):
                self.wrapper.get_files("sssd")

    def test_get_files_fails_when_success_returns_null_pointer(self):
        files = FakePointer(valid=False)
        self.lib.authselect_files.return_value = 0

        with patch.object(authselect, "AuthselectFiles", return_value=files), patch.object(
            authselect.ctypes, "byref", side_effect=lambda value: value
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "succeeded but returned a NULL AuthselectFiles pointer",
            ):
                self.wrapper.get_files("sssd")

    # ------------------------------------------------------------------
    # Current configuration
    # ------------------------------------------------------------------

    def test_get_current_profile_id_returns_profile_and_closes_string(self):
        profile_id = FakeAllocatedCString("sssd-ü")
        self.lib.authselect_current_configuration.return_value = 0

        with patch.object(authselect, "AllocatedCString", return_value=profile_id), patch.object(
            authselect.ctypes, "byref", side_effect=lambda value: value
        ):
            result = self.wrapper.get_current_profile_id()

        self.assertEqual(result, "sssd-ü")
        self.assertTrue(profile_id.entered)
        self.assertTrue(profile_id.exited)
        self.lib.authselect_current_configuration.assert_called_once_with(
            profile_id,
            None,
        )

    def test_get_current_profile_id_returns_none_when_no_configuration_exists(self):
        profile_id = FakeAllocatedCString()
        self.lib.authselect_current_configuration.return_value = errno.ENOENT

        with patch.object(authselect, "AllocatedCString", return_value=profile_id), patch.object(
            authselect.ctypes, "byref", side_effect=lambda value: value
        ):
            result = self.wrapper.get_current_profile_id()

        self.assertIsNone(result)

    def test_get_current_profile_id_reports_other_library_error(self):
        profile_id = FakeAllocatedCString()
        self.lib.authselect_current_configuration.return_value = errno.EACCES

        with patch.object(authselect, "AllocatedCString", return_value=profile_id), patch.object(
            authselect.ctypes, "byref", side_effect=lambda value: value
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                r"authselect_current_configuration\(\) failed",
            ):
                self.wrapper.get_current_profile_id()

    def test_get_current_profile_id_fails_when_success_returns_null_profile_id(self):
        profile_id = FakeAllocatedCString()
        self.lib.authselect_current_configuration.return_value = 0

        with patch.object(authselect, "AllocatedCString", return_value=profile_id), patch.object(
            authselect.ctypes, "byref", side_effect=lambda value: value
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "returned a NULL profile ID",
            ):
                self.wrapper.get_current_profile_id()

    def test_get_current_features_returns_features_and_closes_outputs(self):
        features = FakeStringArray(["with-faillock", "with-mkhomedir"])
        profile_id = FakeAllocatedCString("sssd")
        self.lib.authselect_current_configuration.return_value = 0

        with patch.object(authselect, "NullTerminatedStringArray", return_value=features), patch.object(
            authselect, "AllocatedCString", return_value=profile_id
        ), patch.object(authselect.ctypes, "byref", side_effect=lambda value: value):
            result = self.wrapper.get_current_features()

        self.assertEqual(
            result,
            ["with-faillock", "with-mkhomedir"],
        )
        self.assertTrue(features.entered)
        self.assertTrue(features.exited)
        self.assertTrue(profile_id.closed)
        self.lib.authselect_current_configuration.assert_called_once_with(
            profile_id,
            features,
        )

    def test_get_current_features_returns_none_when_no_configuration_exists(self):
        features = FakeStringArray()
        profile_id = FakeAllocatedCString()
        self.lib.authselect_current_configuration.return_value = errno.ENOENT

        with patch.object(authselect, "NullTerminatedStringArray", return_value=features), patch.object(
            authselect, "AllocatedCString", return_value=profile_id
        ), patch.object(authselect.ctypes, "byref", side_effect=lambda value: value):
            result = self.wrapper.get_current_features()

        self.assertIsNone(result)

    def test_get_current_features_reports_other_library_error(self):
        features = FakeStringArray()
        profile_id = FakeAllocatedCString()
        self.lib.authselect_current_configuration.return_value = errno.EACCES

        with patch.object(authselect, "NullTerminatedStringArray", return_value=features), patch.object(
            authselect, "AllocatedCString", return_value=profile_id
        ), patch.object(authselect.ctypes, "byref", side_effect=lambda value: value):
            with self.assertRaisesRegex(
                RuntimeError,
                r"authselect_current_configuration\(\) failed",
            ):
                self.wrapper.get_current_features()

    def test_get_current_features_fails_when_success_returns_null_features(self):
        features = FakeStringArray()
        profile_id = FakeAllocatedCString("sssd")
        self.lib.authselect_current_configuration.return_value = 0

        with patch.object(authselect, "NullTerminatedStringArray", return_value=features), patch.object(
            authselect, "AllocatedCString", return_value=profile_id
        ), patch.object(authselect.ctypes, "byref", side_effect=lambda value: value):
            with self.assertRaisesRegex(
                RuntimeError,
                "succeeded but returned NULL features",
            ):
                self.wrapper.get_current_features()

        self.assertTrue(profile_id.closed)

    # ------------------------------------------------------------------
    # Profile activation
    # ------------------------------------------------------------------

    def test_activate_profile_passes_encoded_arguments(self):
        c_features = object()
        self.lib.authselect_activate.return_value = 0

        with patch.object(
            authselect.CStringArray,
            "from_strings",
            return_value=c_features,
        ) as from_strings:
            result = self.wrapper.activate_profile(
                "sssd-ü",
                ["with-faillock"],
                force_overwrite=True,
            )

        self.assertIsNone(result)
        from_strings.assert_called_once_with(["with-faillock"])
        self.lib.authselect_activate.assert_called_once_with(
            "sssd-ü".encode("utf-8"),
            c_features,
            True,
        )

    def test_activate_profile_uses_empty_feature_array_when_features_omitted(self):
        self.lib.authselect_activate.return_value = 0

        with patch.object(
            authselect.CStringArray,
            "from_strings",
            return_value=object(),
        ) as from_strings:
            self.wrapper.activate_profile("sssd")

        from_strings.assert_called_once_with([])

    def test_activate_profile_reports_missing_profile(self):
        self.lib.authselect_activate.return_value = errno.ENOENT

        with self.assertRaisesRegex(
            RuntimeError,
            "Authselect profile 'missing' does not exist",
        ):
            self.wrapper.activate_profile("missing")

    def test_activate_profile_reports_unsupported_feature(self):
        self.lib.authselect_activate.return_value = errno.EINVAL

        with self.assertRaisesRegex(
            RuntimeError,
            "One or more features are not supported",
        ):
            self.wrapper.activate_profile("sssd", ["invalid"])

    def test_activate_profile_reports_existing_unmanaged_configuration(self):
        self.lib.authselect_activate.return_value = errno.EEXIST

        with self.assertRaisesRegex(
            RuntimeError,
            "Existing system authentication configuration prevents authselect",
        ):
            self.wrapper.activate_profile("sssd")

    def test_activate_profile_reports_permission_error(self):
        self.lib.authselect_activate.return_value = errno.EACCES

        with self.assertRaisesRegex(
            PermissionError,
            "Permission denied while activating authselect profile 'sssd'",
        ):
            self.wrapper.activate_profile("sssd")

    def test_activate_profile_reports_other_library_error(self):
        result_code = errno.EIO
        self.lib.authselect_activate.return_value = result_code

        with self.assertRaisesRegex(
            RuntimeError,
            rf"\[{result_code}\].*{os.strerror(result_code)}",
        ):
            self.wrapper.activate_profile("sssd")

    # ------------------------------------------------------------------
    # Configuration validation and feature state
    # ------------------------------------------------------------------

    def test_validate_configuration_returns_complete_status_and_valid_flag(self):
        self.lib.authselect_validate_configuration.side_effect = lambda is_valid: setattr(is_valid, "value", True) or 0

        with patch.object(
            authselect.ctypes,
            "byref",
            side_effect=lambda value: value,
        ):
            result = self.wrapper.validate_configuration()

        self.assertEqual(
            result,
            (AuthselectValidationStatus.VALIDATION_COMPLETE, True),
        )

    def test_validate_configuration_returns_no_configuration_status(self):
        self.lib.authselect_validate_configuration.return_value = errno.ENOENT

        result = self.wrapper.validate_configuration()

        self.assertEqual(
            result,
            (AuthselectValidationStatus.NO_CONFIGURATION, False),
        )

    def test_validate_configuration_returns_not_managed_status(self):
        self.lib.authselect_validate_configuration.return_value = errno.EEXIST

        result = self.wrapper.validate_configuration()

        self.assertEqual(
            result,
            (AuthselectValidationStatus.NOT_MANAGED, False),
        )

    def test_validate_configuration_rejects_unknown_status(self):
        result_code = errno.EIO
        self.lib.authselect_validate_configuration.return_value = result_code

        with self.assertRaisesRegex(
            RuntimeError,
            rf"authselect_validate_configuration\(\) failed: \[{result_code}\]",
        ):
            self.wrapper.validate_configuration()

    def test_is_feature_enabled_returns_true_when_library_returns_zero(self):
        self.lib.authselect_feature_enabled.return_value = 0

        self.assertTrue(self.wrapper.is_feature_enabled("with-faillock"))
        self.lib.authselect_feature_enabled.assert_called_once_with(b"with-faillock")

    def test_is_feature_enabled_returns_false_when_feature_is_not_enabled(self):
        self.lib.authselect_feature_enabled.return_value = errno.ENOENT

        self.assertFalse(self.wrapper.is_feature_enabled("with-faillock"))

    def test_is_feature_enabled_reports_other_library_error(self):
        self.lib.authselect_feature_enabled.return_value = errno.EIO

        with self.assertRaisesRegex(
            RuntimeError,
            r"authselect_feature_enabled\(\) failed",
        ):
            self.wrapper.is_feature_enabled("with-faillock")

    # ------------------------------------------------------------------
    # Feature mutation
    # ------------------------------------------------------------------

    def test_enable_feature_passes_encoded_feature(self):
        self.lib.authselect_feature_enable.return_value = 0

        result = self.wrapper.enable_feature("with-faillock")

        self.assertIsNone(result)
        self.lib.authselect_feature_enable.assert_called_once_with(b"with-faillock")

    def test_enable_feature_fails_without_existing_configuration(self):
        self.lib.authselect_feature_enable.return_value = errno.ENOENT

        with self.assertRaisesRegex(
            RuntimeError,
            "Cannot enable feature because there is no existing authselect configuration",
        ):
            self.wrapper.enable_feature("with-faillock")

    def test_enable_feature_reports_other_library_error(self):
        result_code = errno.EIO
        self.lib.authselect_feature_enable.return_value = result_code

        with self.assertRaisesRegex(
            RuntimeError,
            rf"\[{result_code}\].*{os.strerror(result_code)}",
        ):
            self.wrapper.enable_feature("with-faillock")

    def test_disable_feature_passes_encoded_feature(self):
        self.lib.authselect_feature_disable.return_value = 0

        result = self.wrapper.disable_feature("with-faillock")

        self.assertIsNone(result)
        self.lib.authselect_feature_disable.assert_called_once_with(b"with-faillock")

    def test_disable_feature_fails_without_existing_configuration(self):
        self.lib.authselect_feature_disable.return_value = errno.ENOENT

        with self.assertRaisesRegex(
            RuntimeError,
            "Cannot disable feature because there is no existing authselect configuration",
        ):
            self.wrapper.disable_feature("with-faillock")

    def test_disable_feature_reports_other_library_error(self):
        result_code = errno.EIO
        self.lib.authselect_feature_disable.return_value = result_code

        with self.assertRaisesRegex(
            RuntimeError,
            rf"\[{result_code}\].*{os.strerror(result_code)}",
        ):
            self.wrapper.disable_feature("with-faillock")

    def test_apply_changes_returns_true_when_changes_are_applied(self):
        self.lib.authselect_apply_changes.return_value = 0

        self.assertTrue(self.wrapper.apply_changes())
        self.lib.authselect_apply_changes.assert_called_once_with(False)

    def test_apply_changes_passes_upgrade_flag(self):
        self.lib.authselect_apply_changes.return_value = 0

        self.wrapper.apply_changes(upgrade=True)

        self.lib.authselect_apply_changes.assert_called_once_with(True)

    def test_apply_changes_returns_false_when_changes_are_not_required(self):
        self.lib.authselect_apply_changes.return_value = errno.EAGAIN

        self.assertFalse(self.wrapper.apply_changes())

    def test_apply_changes_fails_without_existing_configuration(self):
        self.lib.authselect_apply_changes.return_value = errno.ENOENT

        with self.assertRaisesRegex(
            RuntimeError,
            "No existing authselect configuration",
        ):
            self.wrapper.apply_changes()

    def test_apply_changes_fails_for_unmanaged_configuration(self):
        self.lib.authselect_apply_changes.return_value = errno.EEXIST

        with self.assertRaisesRegex(
            RuntimeError,
            "Existing configuration is not managed by authselect",
        ):
            self.wrapper.apply_changes()

    def test_apply_changes_reports_other_library_error(self):
        self.lib.authselect_apply_changes.return_value = errno.EIO

        with self.assertRaisesRegex(
            RuntimeError,
            r"authselect_apply_changes\(\) failed",
        ):
            self.wrapper.apply_changes()

    # ------------------------------------------------------------------
    # Backups
    # ------------------------------------------------------------------

    def test_create_profile_backup_passes_name_and_returns_path(self):
        path = FakeAllocatedCString("/var/lib/authselect/backups/test")
        self.lib.authselect_backup.return_value = 0

        with patch.object(authselect, "AllocatedCString", return_value=path), patch.object(
            authselect.ctypes, "byref", side_effect=lambda value: value
        ):
            result = self.wrapper.create_profile_backup("test-ü")

        self.assertEqual(result, "/var/lib/authselect/backups/test")
        self.lib.authselect_backup.assert_called_once_with(
            "test-ü".encode("utf-8"),
            path,
        )
        self.assertTrue(path.entered)
        self.assertTrue(path.exited)

    def test_create_profile_backup_passes_null_name_when_name_omitted(self):
        path = FakeAllocatedCString("/var/lib/authselect/backups/generated")
        self.lib.authselect_backup.return_value = 0

        with patch.object(authselect, "AllocatedCString", return_value=path), patch.object(
            authselect.ctypes, "byref", side_effect=lambda value: value
        ):
            self.wrapper.create_profile_backup()

        self.lib.authselect_backup.assert_called_once_with(
            None,
            path,
        )

    def test_create_profile_backup_reports_library_error(self):
        path = FakeAllocatedCString()
        self.lib.authselect_backup.return_value = errno.EIO

        with patch.object(authselect, "AllocatedCString", return_value=path), patch.object(
            authselect.ctypes, "byref", side_effect=lambda value: value
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                r"authselect_backup\(\) failed",
            ):
                self.wrapper.create_profile_backup("test")

    def test_create_profile_backup_fails_when_success_returns_null_path(self):
        path = FakeAllocatedCString()
        self.lib.authselect_backup.return_value = 0

        with patch.object(authselect, "AllocatedCString", return_value=path), patch.object(
            authselect.ctypes, "byref", side_effect=lambda value: value
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "succeeded but returned a NULL path",
            ):
                self.wrapper.create_profile_backup("test")

    def test_remove_profile_backup_passes_encoded_name(self):
        self.lib.authselect_backup_remove.return_value = 0

        result = self.wrapper.remove_profile_backup("backup-ü")

        self.assertIsNone(result)
        self.lib.authselect_backup_remove.assert_called_once_with("backup-ü".encode("utf-8"))

    def test_remove_profile_backup_reports_library_error(self):
        self.lib.authselect_backup_remove.return_value = errno.EIO

        with self.assertRaisesRegex(
            RuntimeError,
            r"authselect_backup_remove\(\) failed",
        ):
            self.wrapper.remove_profile_backup("backup")

    def test_restore_profile_backup_passes_encoded_name(self):
        self.lib.authselect_backup_restore.return_value = 0

        result = self.wrapper.restore_profile_backup("backup-ü")

        self.assertIsNone(result)
        self.lib.authselect_backup_restore.assert_called_once_with("backup-ü".encode("utf-8"))

    def test_restore_profile_backup_reports_library_error(self):
        self.lib.authselect_backup_restore.return_value = errno.EIO

        with self.assertRaisesRegex(
            RuntimeError,
            r"authselect_backup_restore\(\) failed",
        ):
            self.wrapper.restore_profile_backup("backup")

    # ------------------------------------------------------------------
    # Custom profile creation
    # ------------------------------------------------------------------

    def test_create_profile_passes_all_encoded_arguments_and_returns_path(self):
        path = FakeAllocatedCString("/etc/authselect/custom/test")
        c_symlinks = object()
        self.lib.authselect_profile_create.return_value = 0

        with patch.object(authselect, "AllocatedCString", return_value=path), patch.object(
            authselect.CStringArray, "from_strings", return_value=c_symlinks
        ) as from_strings, patch.object(authselect.ctypes, "byref", side_effect=lambda value: value):
            result = self.wrapper.create_profile(
                name="test-ü",
                profile_type=AuthselectProfileType.CUSTOM,
                base_id="sssd-ü",
                base_type=AuthselectProfileType.DEFAULT,
                symlink_flags=(AuthselectSymlinkFlag.PAM | AuthselectSymlinkFlag.NSSWITCH),
                symlinks=["system-auth", "password-auth"],
            )

        self.assertEqual(result, "/etc/authselect/custom/test")
        from_strings.assert_called_once_with(["system-auth", "password-auth"])
        self.lib.authselect_profile_create.assert_called_once_with(
            "test-ü".encode("utf-8"),
            int(AuthselectProfileType.CUSTOM),
            "sssd-ü".encode("utf-8"),
            int(AuthselectProfileType.DEFAULT),
            int(AuthselectSymlinkFlag.PAM | AuthselectSymlinkFlag.NSSWITCH),
            c_symlinks,
            path,
        )
        self.assertTrue(path.entered)
        self.assertTrue(path.exited)

    def test_create_profile_uses_default_optional_arguments(self):
        path = FakeAllocatedCString("/etc/authselect/custom/test")
        c_symlinks = object()
        self.lib.authselect_profile_create.return_value = 0

        with patch.object(authselect, "AllocatedCString", return_value=path), patch.object(
            authselect.CStringArray, "from_strings", return_value=c_symlinks
        ) as from_strings, patch.object(authselect.ctypes, "byref", side_effect=lambda value: value):
            self.wrapper.create_profile(
                name="test",
                profile_type=AuthselectProfileType.CUSTOM,
            )

        from_strings.assert_called_once_with([])
        self.lib.authselect_profile_create.assert_called_once_with(
            b"test",
            int(AuthselectProfileType.CUSTOM),
            None,
            int(AuthselectProfileType.ANY),
            int(AuthselectSymlinkFlag.NONE),
            c_symlinks,
            path,
        )

    def test_create_profile_reports_existing_profile(self):
        path = FakeAllocatedCString()
        self.lib.authselect_profile_create.return_value = errno.EEXIST

        with patch.object(authselect, "AllocatedCString", return_value=path), patch.object(
            authselect.ctypes, "byref", side_effect=lambda value: value
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "Authselect profile 'test' already exists",
            ):
                self.wrapper.create_profile(
                    "test",
                    AuthselectProfileType.CUSTOM,
                )

    def test_create_profile_reports_missing_base_profile(self):
        path = FakeAllocatedCString()
        self.lib.authselect_profile_create.return_value = errno.ENOENT

        with patch.object(authselect, "AllocatedCString", return_value=path), patch.object(
            authselect.ctypes, "byref", side_effect=lambda value: value
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "Base authselect profile 'missing' does not exist",
            ):
                self.wrapper.create_profile(
                    "test",
                    AuthselectProfileType.CUSTOM,
                    base_id="missing",
                )

    def test_create_profile_reports_invalid_arguments(self):
        path = FakeAllocatedCString()
        self.lib.authselect_profile_create.return_value = errno.EINVAL

        with patch.object(authselect, "AllocatedCString", return_value=path), patch.object(
            authselect.ctypes, "byref", side_effect=lambda value: value
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                r"Invalid arguments supplied to authselect_profile_create\(\)",
            ):
                self.wrapper.create_profile(
                    "test",
                    AuthselectProfileType.CUSTOM,
                )

    def test_create_profile_reports_other_library_error(self):
        path = FakeAllocatedCString()
        self.lib.authselect_profile_create.return_value = errno.EIO

        with patch.object(authselect, "AllocatedCString", return_value=path), patch.object(
            authselect.ctypes, "byref", side_effect=lambda value: value
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                r"authselect_profile_create\(\) failed",
            ):
                self.wrapper.create_profile(
                    "test",
                    AuthselectProfileType.CUSTOM,
                )

    def test_create_profile_fails_when_success_returns_null_path(self):
        path = FakeAllocatedCString()
        self.lib.authselect_profile_create.return_value = 0

        with patch.object(authselect, "AllocatedCString", return_value=path), patch.object(
            authselect.ctypes, "byref", side_effect=lambda value: value
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "succeeded but returned a NULL path",
            ):
                self.wrapper.create_profile(
                    "test",
                    AuthselectProfileType.CUSTOM,
                )

    # ------------------------------------------------------------------
    # Uninstall
    # ------------------------------------------------------------------

    def test_uninstall_returns_none_on_success(self):
        self.lib.authselect_uninstall.return_value = 0

        result = self.wrapper.uninstall()

        self.assertIsNone(result)
        self.lib.authselect_uninstall.assert_called_once_with()

    def test_uninstall_reports_library_error(self):
        result_code = errno.EIO
        self.lib.authselect_uninstall.return_value = result_code

        with self.assertRaisesRegex(
            RuntimeError,
            rf"\[{result_code}\].*{os.strerror(result_code)}",
        ):
            self.wrapper.uninstall()


if __name__ == "__main__":
    unittest.main()
