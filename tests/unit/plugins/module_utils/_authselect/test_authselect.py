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


if __name__ == "__main__":
    unittest.main()
