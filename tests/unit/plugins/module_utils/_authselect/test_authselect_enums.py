# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import errno
import unittest

from ansible_collections.community.general.plugins.module_utils._authselect.authselect_enums import (
    AuthselectProfileType,
    AuthselectSymlinkFlag,
    AuthselectValidationStatus,
)


class TestAuthselectValidationStatus(unittest.TestCase):
    def test_validation_complete_value(self):
        self.assertEqual(
            AuthselectValidationStatus.VALIDATION_COMPLETE,
            0,
        )

    def test_no_configuration_uses_enoent(self):
        self.assertEqual(
            AuthselectValidationStatus.NO_CONFIGURATION,
            errno.ENOENT,
        )

    def test_not_managed_uses_eexist(self):
        self.assertEqual(
            AuthselectValidationStatus.NOT_MANAGED,
            errno.EEXIST,
        )


class TestAuthselectProfileType(unittest.TestCase):
    def test_profile_type_values(self):
        self.assertEqual(AuthselectProfileType.DEFAULT, 0)
        self.assertEqual(AuthselectProfileType.VENDOR, 1)
        self.assertEqual(AuthselectProfileType.CUSTOM, 2)
        self.assertEqual(AuthselectProfileType.ANY, 3)

    def test_str_returns_lowercase_name(self):
        self.assertEqual(str(AuthselectProfileType.DEFAULT), "default")
        self.assertEqual(str(AuthselectProfileType.VENDOR), "vendor")
        self.assertEqual(str(AuthselectProfileType.CUSTOM), "custom")
        self.assertEqual(str(AuthselectProfileType.ANY), "any")

    def test_from_string_accepts_lowercase_name(self):
        self.assertIs(
            AuthselectProfileType.from_string("custom"),
            AuthselectProfileType.CUSTOM,
        )

    def test_from_string_accepts_uppercase_name(self):
        self.assertIs(
            AuthselectProfileType.from_string("VENDOR"),
            AuthselectProfileType.VENDOR,
        )

    def test_from_string_is_case_insensitive(self):
        self.assertIs(
            AuthselectProfileType.from_string("DeFaUlT"),
            AuthselectProfileType.DEFAULT,
        )

    def test_from_string_rejects_invalid_name(self):
        with self.assertRaisesRegex(
            ValueError,
            "Invalid authselect profile type: invalid",
        ):
            AuthselectProfileType.from_string("invalid")


class TestAuthselectSymlinkFlag(unittest.TestCase):
    def test_symlink_flag_values(self):
        self.assertEqual(AuthselectSymlinkFlag.NONE, 0x0000)
        self.assertEqual(AuthselectSymlinkFlag.META, 0x0001)
        self.assertEqual(AuthselectSymlinkFlag.NSSWITCH, 0x0002)
        self.assertEqual(AuthselectSymlinkFlag.PAM, 0x0004)
        self.assertEqual(AuthselectSymlinkFlag.DCONF, 0x0008)

    def test_none_to_strings_returns_empty_list(self):
        self.assertEqual(
            AuthselectSymlinkFlag.NONE.to_strings(),
            [],
        )

    def test_single_flag_to_strings_returns_lowercase_name(self):
        self.assertEqual(
            AuthselectSymlinkFlag.PAM.to_strings(),
            ["pam"],
        )

    def test_combined_flags_to_strings_returns_each_flag(self):
        flags = (
            AuthselectSymlinkFlag.META
            | AuthselectSymlinkFlag.PAM
            | AuthselectSymlinkFlag.DCONF
        )

        self.assertEqual(
            flags.to_strings(),
            ["meta", "pam", "dconf"],
        )

    def test_str_none_returns_none(self):
        self.assertEqual(
            str(AuthselectSymlinkFlag.NONE),
            "none",
        )

    def test_str_single_flag_returns_lowercase_name(self):
        self.assertEqual(
            str(AuthselectSymlinkFlag.NSSWITCH),
            "nsswitch",
        )

    def test_str_combined_flags_joins_names_with_pipe(self):
        flags = (
            AuthselectSymlinkFlag.NSSWITCH
            | AuthselectSymlinkFlag.PAM
        )

        self.assertEqual(
            str(flags),
            "nsswitch|pam",
        )

    def test_from_string_accepts_lowercase_name(self):
        self.assertIs(
            AuthselectSymlinkFlag.from_string("dconf"),
            AuthselectSymlinkFlag.DCONF,
        )

    def test_from_string_accepts_uppercase_name(self):
        self.assertIs(
            AuthselectSymlinkFlag.from_string("PAM"),
            AuthselectSymlinkFlag.PAM,
        )

    def test_from_string_is_case_insensitive(self):
        self.assertIs(
            AuthselectSymlinkFlag.from_string("NsSwItCh"),
            AuthselectSymlinkFlag.NSSWITCH,
        )

    def test_from_string_accepts_none(self):
        self.assertIs(
            AuthselectSymlinkFlag.from_string("none"),
            AuthselectSymlinkFlag.NONE,
        )

    def test_from_string_rejects_invalid_name(self):
        with self.assertRaisesRegex(
            ValueError,
            "Invalid authselect symlink flag: invalid",
        ):
            AuthselectSymlinkFlag.from_string("invalid")

    def test_from_strings_combines_flags(self):
        flags = AuthselectSymlinkFlag.from_strings(
            [
                "meta",
                "pam",
                "dconf",
            ]
        )

        self.assertEqual(
            flags,
            (
                AuthselectSymlinkFlag.META
                | AuthselectSymlinkFlag.PAM
                | AuthselectSymlinkFlag.DCONF
            ),
        )

    def test_from_strings_is_case_insensitive(self):
        flags = AuthselectSymlinkFlag.from_strings(
            [
                "META",
                "Pam",
            ]
        )

        self.assertEqual(
            flags,
            AuthselectSymlinkFlag.META | AuthselectSymlinkFlag.PAM,
        )

    def test_from_strings_empty_list_returns_none(self):
        self.assertIs(
            AuthselectSymlinkFlag.from_strings([]),
            AuthselectSymlinkFlag.NONE,
        )

    def test_from_strings_rejects_invalid_flag(self):
        with self.assertRaisesRegex(
            ValueError,
            "Invalid authselect symlink flag: invalid",
        ):
            AuthselectSymlinkFlag.from_strings(
                [
                    "pam",
                    "invalid",
                ]
            )


if __name__ == "__main__":
    unittest.main()
