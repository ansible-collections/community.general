# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import ctypes
import unittest
from unittest.mock import Mock, patch

from ansible_collections.community.general.plugins.module_utils._authselect import (
    authselect_profile,
)
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
    # Basic profile properties
    # ------------------------------------------------------------------

    def test_id_decodes_utf8_string(self):
        profile = self.make_profile()
        get_id = Mock(return_value="sssd-ü".encode("utf-8"))
        AuthselectProfile._get_id = get_id

        self.assertEqual(profile.id, "sssd-ü")
        get_id.assert_called_once_with(profile)

    def test_id_fails_when_getter_returns_null(self):
        profile = self.make_profile()
        AuthselectProfile._get_id = Mock(return_value=None)

        with self.assertRaisesRegex(
            RuntimeError,
            r"authselect_profile_id\(\) returned NULL",
        ):
            discard = profile.id

    def test_name_decodes_utf8_string(self):
        profile = self.make_profile()
        get_name = Mock(return_value="SSSD profile-ü".encode("utf-8"))
        AuthselectProfile._get_name = get_name

        self.assertEqual(profile.name, "SSSD profile-ü")
        get_name.assert_called_once_with(profile)

    def test_name_fails_when_getter_returns_null(self):
        profile = self.make_profile()
        AuthselectProfile._get_name = Mock(return_value=None)

        with self.assertRaisesRegex(
            RuntimeError,
            r"authselect_profile_name\(\) returned NULL",
        ):
            discard = profile.name

    def test_path_decodes_utf8_string(self):
        profile = self.make_profile()
        get_path = Mock(return_value="/usr/share/authselect/default/sssd".encode("utf-8"))
        AuthselectProfile._get_path = get_path

        self.assertEqual(
            profile.path,
            "/usr/share/authselect/default/sssd",
        )
        get_path.assert_called_once_with(profile)

    def test_path_fails_when_getter_returns_null(self):
        profile = self.make_profile()
        AuthselectProfile._get_path = Mock(return_value=None)

        with self.assertRaisesRegex(
            RuntimeError,
            r"authselect_profile_path\(\) returned NULL",
        ):
            discard = profile.path

    def test_description_decodes_utf8_string(self):
        profile = self.make_profile()
        get_description = Mock(return_value="Profile description-ü".encode("utf-8"))
        AuthselectProfile._get_description = get_description

        self.assertEqual(
            profile.description,
            "Profile description-ü",
        )
        get_description.assert_called_once_with(profile)

    def test_description_returns_none_when_getter_returns_null(self):
        profile = self.make_profile()
        AuthselectProfile._get_description = Mock(return_value=None)

        self.assertIsNone(profile.description)

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

        with self.assertRaisesRegex(
            RuntimeError,
            r"authselect_profile_features\(\) returned NULL",
        ):
            discard = profile.features

    def test_nsswitch_maps_passes_requested_features_and_closes_returned_array(self):
        profile = self.make_profile()
        values = FakeStringArray(["passwd", "group"])
        get_nsswitch_maps = Mock(return_value=values)
        AuthselectProfile._get_nsswitch_maps = get_nsswitch_maps
        c_features = object()

        with patch.object(
            authselect_profile.CStringArray,
            "from_strings",
            return_value=c_features,
        ) as from_strings:
            result = profile.nsswitch_maps(
                [
                    "with-faillock",
                    "with-mkhomedir",
                ]
            )

        from_strings.assert_called_once_with(
            [
                "with-faillock",
                "with-mkhomedir",
            ]
        )
        get_nsswitch_maps.assert_called_once_with(profile, c_features)
        self.assertEqual(result, ["passwd", "group"])
        self.assertTrue(values.entered)
        self.assertTrue(values.exited)

    def test_nsswitch_maps_uses_empty_feature_list_when_features_omitted(self):
        profile = self.make_profile()
        values = FakeStringArray(["passwd"])
        AuthselectProfile._get_nsswitch_maps = Mock(return_value=values)
        c_features = object()

        with patch.object(
            authselect_profile.CStringArray,
            "from_strings",
            return_value=c_features,
        ) as from_strings:
            result = profile.nsswitch_maps()

        from_strings.assert_called_once_with([])
        self.assertEqual(result, ["passwd"])

    def test_nsswitch_maps_fails_when_getter_returns_null(self):
        profile = self.make_profile()
        AuthselectProfile._get_nsswitch_maps = Mock(return_value=None)

        with self.assertRaisesRegex(
            RuntimeError,
            r"authselect_profile_nsswitch_maps\(\) returned NULL",
        ):
            profile.nsswitch_maps(["with-faillock"])

    def test_requirements_passes_requested_features_and_closes_returned_string(self):
        profile = self.make_profile()
        value = FakeAllocatedString(b"Requirement text")
        get_requirements = Mock(return_value=value)
        AuthselectProfile._get_requirements = get_requirements
        c_features = object()

        with patch.object(
            authselect_profile.CStringArray,
            "from_strings",
            return_value=c_features,
        ) as from_strings:
            result = profile.requirements(["with-faillock"])

        from_strings.assert_called_once_with(["with-faillock"])
        get_requirements.assert_called_once_with(profile, c_features)
        self.assertEqual(result, "Requirement text")
        self.assertTrue(value.entered)
        self.assertTrue(value.exited)

    def test_requirements_uses_empty_feature_list_when_features_omitted(self):
        profile = self.make_profile()
        value = FakeAllocatedString(b"Requirement text")
        AuthselectProfile._get_requirements = Mock(return_value=value)
        c_features = object()

        with patch.object(
            authselect_profile.CStringArray,
            "from_strings",
            return_value=c_features,
        ) as from_strings:
            result = profile.requirements()

        from_strings.assert_called_once_with([])
        self.assertEqual(result, "Requirement text")

    def test_requirements_fails_when_getter_returns_null(self):
        profile = self.make_profile()
        AuthselectProfile._get_requirements = Mock(return_value=None)

        with self.assertRaisesRegex(
            RuntimeError,
            r"authselect_profile_requirements\(\) returned NULL",
        ):
            profile.requirements(["with-faillock"])

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

    def test_null_pointer_cannot_access_properties(self):
        profile = AuthselectProfile()

        with self.assertRaisesRegex(
            RuntimeError,
            "Authselect profile pointer is NULL",
        ):
            discard = profile.id

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

    def test_closed_profile_cannot_access_properties(self):
        profile = self.make_profile()
        free_function = Mock()
        AuthselectProfile._free = free_function
        AuthselectProfile._get_id = Mock(return_value=b"sssd")
        profile.close()

        with self.assertRaisesRegex(
            RuntimeError,
            "Authselect profile has already been freed",
        ):
            discard = profile.id

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
