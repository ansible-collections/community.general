# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import ctypes
import unittest
from unittest.mock import Mock

from ansible_collections.community.general.plugins.module_utils._authselect.authselect_profile import (
    AuthselectProfile,
    _AuthselectProfileStruct,
)


class FakeStringArray:
    def __init__(self, values):
        self.values = list(values)
        self.entered = False
        self.exited = False

    def __enter__(self):
        self.entered = True
        return self

    def __exit__(self, *args):
        self.exited = True

    def __iter__(self):
        return iter(self.values)


class FakeAllocatedString:
    def __init__(self, value):
        self.value = value
        self.entered = False
        self.exited = False

    def __enter__(self):
        self.entered = True
        return self

    def __exit__(self, *args):
        self.exited = True

    def decode(self, encoding="utf-8"):
        return self.value.decode(encoding)


class TestAuthselectProfile(unittest.TestCase):
    CALLBACK_ATTRIBUTES = (
        "_free",
        "_get_id",
        "_get_name",
        "_get_path",
        "_get_description",
        "_get_features",
        "_get_nsswitch_maps",
        "_get_requirements",
    )

    def setUp(self):
        for attribute in self.CALLBACK_ATTRIBUTES:
            setattr(AuthselectProfile, attribute, None)

    def tearDown(self):
        for attribute in self.CALLBACK_ATTRIBUTES:
            setattr(AuthselectProfile, attribute, None)

    @staticmethod
    def make_profile():
        backing_struct = _AuthselectProfileStruct()
        pointer = ctypes.cast(
            ctypes.pointer(backing_struct),
            AuthselectProfile,
        )

        # The test owns this memory, so keep it alive while the pointer is used.
        pointer._test_backing_struct = backing_struct

        return pointer

    # ------------------------------------------------------------------
    # Features and derived profile data
    # ------------------------------------------------------------------

    def test_features_returns_list_and_closes_returned_array(self):
        profile = self.make_profile()
        values = FakeStringArray(
            [
                "with-faillock",
                "with-mkhomedir",
            ]
        )
        get_features = Mock(return_value=values)
        AuthselectProfile._get_features = get_features

        result = profile.features

        self.assertEqual(
            result,
            [
                "with-faillock",
                "with-mkhomedir",
            ],
        )
        get_features.assert_called_once_with(profile)
        self.assertTrue(values.entered)
        self.assertTrue(values.exited)

    def test_features_fails_when_getter_returns_null(self):
        profile = self.make_profile()
        AuthselectProfile._get_features = Mock(return_value=None)

        self.assertRaisesRegex(
            RuntimeError,
            r"authselect_profile_features\(\) returned NULL",
            lambda: profile.features,
        )

    # ------------------------------------------------------------------
    # Pointer lifetime
    # ------------------------------------------------------------------

    def test_null_pointer_cannot_enter_context_manager(self):
        profile = AuthselectProfile()

        with self.assertRaisesRegex(
            RuntimeError,
            "Authselect profile pointer is NULL",
        ):
            with profile:
                pass

    def test_close_on_null_pointer_is_noop(self):
        profile = AuthselectProfile()

        profile.close()

    def test_close_without_free_function_fails(self):
        profile = self.make_profile()

        with self.assertRaisesRegex(
            RuntimeError,
            "AuthselectProfile free function has not been configured",
        ):
            profile.close()

    def test_close_calls_configured_free_function(self):
        profile = self.make_profile()
        free_function = Mock()
        AuthselectProfile._free = free_function

        profile.close()

        free_function.assert_called_once_with(profile)
        self.assertTrue(profile._closed)

    def test_close_is_idempotent(self):
        profile = self.make_profile()
        free_function = Mock()
        AuthselectProfile._free = free_function

        profile.close()
        profile.close()

        free_function.assert_called_once_with(profile)

    def test_context_manager_returns_same_profile_and_frees_on_exit(self):
        profile = self.make_profile()
        free_function = Mock()
        AuthselectProfile._free = free_function

        with profile as entered_profile:
            self.assertIs(entered_profile, profile)
            free_function.assert_not_called()

        free_function.assert_called_once_with(profile)
        self.assertTrue(profile._closed)

    def test_context_manager_frees_profile_when_body_raises(self):
        profile = self.make_profile()
        free_function = Mock()
        AuthselectProfile._free = free_function

        with self.assertRaisesRegex(RuntimeError, "test failure"):
            with profile:
                raise RuntimeError("test failure")

        free_function.assert_called_once_with(profile)
        self.assertTrue(profile._closed)


if __name__ == "__main__":
    unittest.main()
