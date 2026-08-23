# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from unittest.mock import patch

from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    ModuleTestCase,
    set_module_args,
)

from ansible_collections.community.general.plugins.modules import authselect

PROFILE_FEATURES = {
    "sssd": {
        "with-faillock",
        "with-mkhomedir",
        "with-sudo",
    },
    "minimal": {
        "with-faillock",
        "with-mkhomedir",
    },
}


class FakeProfile:
    def __init__(self, features):
        self.features = set(features)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False


class FakeAuthselect:
    """
    Stateful fake for the public Authselect wrapper used by the module.

    It intentionally models only the operations the authselect module calls.
    Tests can inject failures or validation results at specific stages.
    """

    def __init__(
        self,
        current_profile="sssd",
        current_features=None,
        profile_features=None,
        validation_results=None,
        activate_exception=None,
        create_backup_exception=None,
        restore_backup_exception=None,
        remove_backup_exception=None,
        apply_activation=True,
    ):
        self.current_profile = current_profile

        if current_profile is None:
            self.current_features = None
        elif current_features is None:
            self.current_features = set()
        else:
            self.current_features = set(current_features)

        self.profile_features = {
            profile: set(features) for profile, features in (profile_features or PROFILE_FEATURES).items()
        }

        self.validation_results = list(validation_results or [(None, True)])
        self._last_validation_result = self.validation_results[-1]

        self.activate_exception = activate_exception
        self.create_backup_exception = create_backup_exception
        self.restore_backup_exception = restore_backup_exception
        self.remove_backup_exception = remove_backup_exception
        self.apply_activation = apply_activation

        self.events = []
        self.activate_calls = []
        self.validate_calls = 0
        self.create_backup_calls = []
        self.restore_backup_calls = []
        self.remove_backup_calls = []
        self.backups = {}

    def get_current_profile_id(self):
        return self.current_profile

    def get_current_features(self):
        if self.current_features is None:
            return None
        return list(self.current_features)

    def get_profiles_list(self):
        return list(self.profile_features)

    def get_profile(self, profile_id):
        return FakeProfile(self.profile_features[profile_id])

    def activate_profile(self, profile_id, features, force_overwrite=False):
        features = set(features)

        self.events.append("activate")
        self.activate_calls.append(
            {
                "profile_id": profile_id,
                "features": features,
                "force_overwrite": force_overwrite,
            }
        )

        if self.activate_exception is not None:
            raise self.activate_exception

        if self.apply_activation:
            self.current_profile = profile_id
            self.current_features = features

    def validate_configuration(self):
        self.events.append("validate")
        self.validate_calls += 1

        if self.validation_results:
            self._last_validation_result = self.validation_results.pop(0)

        return self._last_validation_result

    def create_profile_backup(self, backup_name):
        self.events.append("create_backup")
        self.create_backup_calls.append(backup_name)

        if self.create_backup_exception is not None:
            raise self.create_backup_exception

        features = None if self.current_features is None else set(self.current_features)
        self.backups[backup_name] = (self.current_profile, features)

    def restore_profile_backup(self, backup_name):
        self.events.append("restore_backup")
        self.restore_backup_calls.append(backup_name)

        if self.restore_backup_exception is not None:
            raise self.restore_backup_exception

        profile, features = self.backups[backup_name]
        self.current_profile = profile
        self.current_features = None if features is None else set(features)

    def remove_profile_backup(self, backup_name):
        self.events.append("remove_backup")
        self.remove_backup_calls.append(backup_name)

        if self.remove_backup_exception is not None:
            raise self.remove_backup_exception

        del self.backups[backup_name]


class FakeAuthselectWrongProfile(FakeAuthselect):
    def activate_profile(
        self,
        profile_id,
        features,
        force_overwrite=False,
    ):
        super().activate_profile(
            profile_id=profile_id,
            features=features,
            force_overwrite=force_overwrite,
        )

        self.current_profile = "wrong-profile"


class TestAuthselect(ModuleTestCase):
    def run_success(self, module_args, fake_authselect):
        with set_module_args(module_args):
            with patch.object(authselect, "Authselect", return_value=fake_authselect):
                with self.assertRaises(AnsibleExitJson) as result:
                    authselect.main()

        return result.exception.args[0]

    def run_failure(self, module_args, fake_authselect=None):
        fake_authselect = fake_authselect or FakeAuthselect()

        with set_module_args(module_args):
            with patch.object(authselect, "Authselect", return_value=fake_authselect):
                with self.assertRaises(AnsibleFailJson) as result:
                    authselect.main()

        return result.exception.args[0]

    # ------------------------------------------------------------------
    # Argument validation
    # ------------------------------------------------------------------

    def test_profile_or_features_is_required(self):
        result = self.run_failure({})

        self.assertIn("one of the following is required", result["msg"])

    def test_absent_requires_features(self):
        result = self.run_failure(
            {
                "profile": "sssd",
                "state": "absent",
            }
        )

        self.assertIn("features", result["msg"])

    def test_invalid_state_is_rejected(self):
        result = self.run_failure(
            {
                "profile": "sssd",
                "state": "invalid",
            }
        )

        self.assertIn("state", result["msg"])

    # ------------------------------------------------------------------
    # Profile validation
    # ------------------------------------------------------------------

    def test_invalid_profile_fails(self):
        fake = FakeAuthselect()

        result = self.run_failure(
            {
                "profile": "does-not-exist",
            },
            fake,
        )

        self.assertFalse(result["changed"])
        self.assertIn("not a valid authselect profile", result["msg"])
        self.assertEqual(fake.activate_calls, [])

    def test_present_features_without_current_profile_fails(self):
        fake = FakeAuthselect(
            current_profile=None,
            current_features=None,
        )

        result = self.run_failure(
            {
                "features": ["with-mkhomedir"],
            },
            fake,
        )

        self.assertFalse(result["changed"])
        self.assertEqual(fake.activate_calls, [])

    def test_present_profile_activates_when_no_profile_is_current(self):
        fake = FakeAuthselect(
            current_profile=None,
            current_features=None,
        )

        result = self.run_success(
            {
                "profile": "sssd",
            },
            fake,
        )

        self.assertTrue(result["changed"])
        self.assertEqual(result["profile"], "sssd")
        self.assertEqual(result["features"], [])
        self.assertEqual(
            fake.activate_calls,
            [
                {
                    "profile_id": "sssd",
                    "features": set(),
                    "force_overwrite": False,
                }
            ],
        )

    def test_present_profile_only_same_profile_is_idempotent(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock"},
        )

        result = self.run_success(
            {
                "profile": "sssd",
            },
            fake,
        )

        self.assertFalse(result["changed"])
        self.assertEqual(result["profile"], "sssd")
        self.assertEqual(result["features"], ["with-faillock"])
        self.assertEqual(fake.activate_calls, [])

    def test_present_profile_only_switches_profile_with_no_optional_features(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock", "with-sudo"},
        )

        result = self.run_success(
            {
                "profile": "minimal",
            },
            fake,
        )

        self.assertTrue(result["changed"])
        self.assertEqual(result["profile"], "minimal")
        self.assertEqual(result["features"], [])
        self.assertEqual(
            fake.activate_calls,
            [
                {
                    "profile_id": "minimal",
                    "features": set(),
                    "force_overwrite": False,
                }
            ],
        )

    # ------------------------------------------------------------------
    # state=present feature behavior
    # ------------------------------------------------------------------

    def test_present_adds_feature_to_current_profile(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock"},
        )

        result = self.run_success(
            {
                "features": ["with-mkhomedir"],
            },
            fake,
        )

        self.assertTrue(result["changed"])
        self.assertEqual(result["profile"], "sssd")
        self.assertEqual(
            result["features"],
            ["with-faillock", "with-mkhomedir"],
        )
        self.assertEqual(
            fake.activate_calls[0]["features"],
            {"with-faillock", "with-mkhomedir"},
        )

    def test_present_preserves_unspecified_features_on_current_profile(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock", "with-sudo"},
        )

        result = self.run_success(
            {
                "features": ["with-mkhomedir"],
            },
            fake,
        )

        self.assertTrue(result["changed"])
        self.assertEqual(
            set(result["features"]),
            {"with-faillock", "with-mkhomedir", "with-sudo"},
        )

    def test_present_existing_feature_is_idempotent(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock", "with-mkhomedir"},
        )

        result = self.run_success(
            {
                "features": ["with-mkhomedir"],
            },
            fake,
        )

        self.assertFalse(result["changed"])
        self.assertEqual(fake.activate_calls, [])

    def test_present_switch_profile_uses_requested_features_as_complete_set(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock", "with-sudo"},
        )

        result = self.run_success(
            {
                "profile": "minimal",
                "features": ["with-mkhomedir"],
            },
            fake,
        )

        self.assertTrue(result["changed"])
        self.assertEqual(result["profile"], "minimal")
        self.assertEqual(result["features"], ["with-mkhomedir"])
        self.assertEqual(
            fake.activate_calls[0]["features"],
            {"with-mkhomedir"},
        )

    def test_present_invalid_feature_fails(self):
        fake = FakeAuthselect()

        result = self.run_failure(
            {
                "features": ["not-a-feature"],
            },
            fake,
        )

        self.assertFalse(result["changed"])
        self.assertIn("not valid for the profile sssd", result["msg"])
        self.assertEqual(fake.activate_calls, [])

    # ------------------------------------------------------------------
    # state=absent feature behavior
    # ------------------------------------------------------------------

    def test_absent_removes_requested_feature(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock", "with-mkhomedir"},
        )

        result = self.run_success(
            {
                "features": ["with-mkhomedir"],
                "state": "absent",
            },
            fake,
        )

        self.assertTrue(result["changed"])
        self.assertEqual(result["profile"], "sssd")
        self.assertEqual(result["features"], ["with-faillock"])

    def test_absent_missing_feature_is_idempotent(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock"},
        )

        result = self.run_success(
            {
                "features": ["with-mkhomedir"],
                "state": "absent",
            },
            fake,
        )

        self.assertFalse(result["changed"])
        self.assertEqual(fake.activate_calls, [])

    def test_absent_invalid_feature_is_ignored(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock"},
        )

        result = self.run_success(
            {
                "features": ["not-a-feature"],
                "state": "absent",
            },
            fake,
        )

        self.assertFalse(result["changed"])
        self.assertEqual(result["features"], ["with-faillock"])
        self.assertEqual(fake.activate_calls, [])

    def test_absent_named_current_profile_removes_feature(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock", "with-mkhomedir"},
        )

        result = self.run_success(
            {
                "profile": "sssd",
                "features": ["with-mkhomedir"],
                "state": "absent",
            },
            fake,
        )

        self.assertTrue(result["changed"])
        self.assertEqual(result["profile"], "sssd")
        self.assertEqual(result["features"], ["with-faillock"])

    def test_absent_named_different_profile_is_noop(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock", "with-mkhomedir"},
        )

        result = self.run_success(
            {
                "profile": "minimal",
                "features": ["with-mkhomedir"],
                "state": "absent",
            },
            fake,
        )

        self.assertFalse(result["changed"])
        self.assertEqual(result["profile"], "sssd")
        self.assertEqual(
            result["features"],
            ["with-faillock", "with-mkhomedir"],
        )
        self.assertEqual(fake.activate_calls, [])

    def test_absent_without_current_profile_fails(self):
        fake = FakeAuthselect(
            current_profile=None,
            current_features=None,
        )

        result = self.run_failure(
            {
                "features": ["with-mkhomedir"],
                "state": "absent",
            },
            fake,
        )

        self.assertFalse(result["changed"])
        self.assertIn("no currently configured authselect profiles", result["msg"].lower())

    def test_absent_named_profile_without_current_profile_fails(self):
        fake = FakeAuthselect(
            current_profile=None,
            current_features=None,
        )

        result = self.run_failure(
            {
                "profile": "sssd",
                "features": ["with-mkhomedir"],
                "state": "absent",
            },
            fake,
        )

        self.assertFalse(result["changed"])
        self.assertIn("Activate a profile first", result["msg"])
        self.assertEqual(fake.activate_calls, [])

    # ------------------------------------------------------------------
    # Check mode
    # ------------------------------------------------------------------

    def test_check_mode_present_reports_change_without_activation(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock"},
        )

        result = self.run_success(
            {
                "features": ["with-mkhomedir"],
                "_ansible_check_mode": True,
            },
            fake,
        )

        self.assertTrue(result["changed"])
        self.assertEqual(
            result["features"],
            ["with-faillock", "with-mkhomedir"],
        )
        self.assertEqual(fake.activate_calls, [])
        self.assertEqual(fake.current_features, {"with-faillock"})

    def test_check_mode_profile_switch_reports_predicted_profile(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock"},
        )

        result = self.run_success(
            {
                "profile": "minimal",
                "features": ["with-mkhomedir"],
                "_ansible_check_mode": True,
            },
            fake,
        )

        self.assertTrue(result["changed"])
        self.assertEqual(result["profile"], "minimal")
        self.assertEqual(result["features"], ["with-mkhomedir"])
        self.assertEqual(fake.current_profile, "sssd")
        self.assertEqual(fake.activate_calls, [])

    def test_check_mode_absent_reports_predicted_feature_removal(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock", "with-mkhomedir"},
        )

        result = self.run_success(
            {
                "features": ["with-mkhomedir"],
                "state": "absent",
                "_ansible_check_mode": True,
            },
            fake,
        )

        self.assertTrue(result["changed"])
        self.assertEqual(result["features"], ["with-faillock"])
        self.assertEqual(
            fake.current_features,
            {"with-faillock", "with-mkhomedir"},
        )
        self.assertEqual(fake.activate_calls, [])

    def test_check_mode_idempotent_state_reports_no_change(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock"},
        )

        result = self.run_success(
            {
                "features": ["with-faillock"],
                "_ansible_check_mode": True,
            },
            fake,
        )

        self.assertFalse(result["changed"])
        self.assertEqual(fake.activate_calls, [])

    def test_check_mode_with_validate_validates_without_mutation(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock"},
            validation_results=[(None, True)],
        )

        result = self.run_success(
            {
                "features": ["with-mkhomedir"],
                "validate": True,
                "_ansible_check_mode": True,
            },
            fake,
        )

        self.assertTrue(result["changed"])
        self.assertEqual(fake.validate_calls, 1)
        self.assertEqual(fake.activate_calls, [])

    def test_check_mode_invalid_configuration_fails_without_mutation(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock"},
            validation_results=[
                (None, False),
            ],
        )

        result = self.run_failure(
            {
                "features": ["with-mkhomedir"],
                "validate": True,
                "_ansible_check_mode": True,
            },
            fake,
        )

        self.assertFalse(result["changed"])
        self.assertEqual(fake.activate_calls, [])
        self.assertEqual(fake.current_features, {"with-faillock"})
        self.assertEqual(fake.validate_calls, 1)

    def test_check_mode_with_rollback_does_not_create_backup(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock"},
        )

        result = self.run_success(
            {
                "features": ["with-mkhomedir"],
                "rollback_on_failure": True,
                "_ansible_check_mode": True,
            },
            fake,
        )

        self.assertTrue(result["changed"])
        self.assertEqual(fake.activate_calls, [])
        self.assertEqual(fake.create_backup_calls, [])
        self.assertEqual(fake.restore_backup_calls, [])
        self.assertEqual(fake.remove_backup_calls, [])

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def test_validate_noop_validates_current_configuration(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock"},
            validation_results=[(None, True)],
        )

        result = self.run_success(
            {
                "features": ["with-faillock"],
                "validate": True,
            },
            fake,
        )

        self.assertFalse(result["changed"])
        self.assertEqual(fake.validate_calls, 1)

    def test_validate_noop_invalid_configuration_fails(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock"},
            validation_results=[(None, False)],
        )

        result = self.run_failure(
            {
                "features": ["with-faillock"],
                "validate": True,
            },
            fake,
        )

        self.assertFalse(result["changed"])
        self.assertIn("current configuration is not valid", result["msg"].lower())

    def test_absent_named_different_profile_still_validates(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock"},
            validation_results=[(None, False)],
        )

        result = self.run_failure(
            {
                "profile": "minimal",
                "features": ["with-mkhomedir"],
                "state": "absent",
                "validate": True,
            },
            fake,
        )

        self.assertFalse(result["changed"])
        self.assertEqual(fake.validate_calls, 1)
        self.assertEqual(fake.activate_calls, [])

    def test_post_change_validate_invalid_fails_with_changed_true_without_rollback(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock"},
            validation_results=[(None, False)],
        )

        result = self.run_failure(
            {
                "features": ["with-mkhomedir"],
                "validate": True,
            },
            fake,
        )

        self.assertTrue(result["changed"])
        self.assertEqual(fake.current_features, {"with-faillock", "with-mkhomedir"})

    def test_invalid_configuration_with_rollback_fails_before_change(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock"},
            validation_results=[
                (None, False),
            ],
        )

        result = self.run_failure(
            {
                "features": ["with-mkhomedir"],
                "validate": True,
                "rollback_on_failure": True,
            },
            fake,
        )

        self.assertFalse(result["changed"])
        self.assertEqual(fake.activate_calls, [])
        self.assertEqual(fake.create_backup_calls, [])
        self.assertEqual(fake.restore_backup_calls, [])

    def test_validate_changes_fails_when_profile_does_not_match(self):
        fake = FakeAuthselectWrongProfile(
            current_profile="sssd",
            current_features={"with-faillock"},
        )

        result = self.run_failure(
            {
                "features": ["with-mkhomedir"],
            },
            fake,
        )

        self.assertTrue(result["changed"])
        self.assertIn(
            "does not match what was declared",
            result["msg"],
        )

    # ------------------------------------------------------------------
    # force and validation status
    # ------------------------------------------------------------------

    def test_force_is_passed_to_activate(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock"},
        )

        result = self.run_success(
            {
                "features": ["with-mkhomedir"],
                "force": True,
            },
            fake,
        )

        self.assertTrue(result["changed"])
        self.assertTrue(fake.activate_calls[0]["force_overwrite"])

    def test_not_managed_without_force_fails_before_backup(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock"},
            validation_results=[
                (authselect.AuthselectValidationStatus.NOT_MANAGED, False),
            ],
        )

        result = self.run_failure(
            {
                "features": ["with-mkhomedir"],
                "validate": True,
                "rollback_on_failure": True,
            },
            fake,
        )

        self.assertFalse(result["changed"])
        self.assertEqual(fake.create_backup_calls, [])
        self.assertEqual(fake.activate_calls, [])

    def test_force_allows_not_managed_prechange_then_requires_valid_postchange(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock"},
            validation_results=[
                (authselect.AuthselectValidationStatus.NOT_MANAGED, False),
                (None, True),
            ],
        )

        result = self.run_success(
            {
                "features": ["with-mkhomedir"],
                "validate": True,
                "rollback_on_failure": True,
                "force": True,
            },
            fake,
        )

        self.assertTrue(result["changed"])
        self.assertEqual(fake.validate_calls, 2)
        self.assertEqual(fake.events, ["validate", "create_backup", "activate", "validate", "remove_backup"])

    def test_force_not_managed_after_change_fails_and_rolls_back(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock"},
            validation_results=[
                (authselect.AuthselectValidationStatus.NOT_MANAGED, False),
                (authselect.AuthselectValidationStatus.NOT_MANAGED, False),
                (authselect.AuthselectValidationStatus.NOT_MANAGED, False),
            ],
        )

        result = self.run_failure(
            {
                "features": ["with-mkhomedir"],
                "validate": True,
                "rollback_on_failure": True,
                "force": True,
            },
            fake,
        )

        self.assertFalse(result["changed"])
        self.assertEqual(fake.current_features, {"with-faillock"})
        self.assertEqual(fake.validate_calls, 3)
        self.assertEqual(len(fake.restore_backup_calls), 1)
        self.assertEqual(len(fake.remove_backup_calls), 1)

    def test_absent_not_managed_configuration_fails_after_change(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock", "with-mkhomedir"},
            validation_results=[
                (authselect.AuthselectValidationStatus.NOT_MANAGED, False),
            ],
        )

        result = self.run_failure(
            {
                "features": ["with-mkhomedir"],
                "state": "absent",
                "validate": True,
            },
            fake,
        )

        self.assertTrue(result["changed"])
        self.assertIn(
            "does not currently manage",
            result["msg"],
        )
        self.assertEqual(
            fake.current_features,
            {"with-faillock"},
        )

    def test_no_configuration_present_is_allowed_before_first_configuration(self):
        fake = FakeAuthselect(
            current_profile=None,
            current_features=None,
            validation_results=[
                (authselect.AuthselectValidationStatus.NO_CONFIGURATION, False),
                (None, True),
            ],
        )

        result = self.run_success(
            {
                "profile": "sssd",
                "features": ["with-mkhomedir"],
                "validate": True,
                "rollback_on_failure": True,
            },
            fake,
        )

        self.assertTrue(result["changed"])
        self.assertEqual(result["profile"], "sssd")
        self.assertEqual(result["features"], ["with-mkhomedir"])
        self.assertEqual(fake.validate_calls, 2)

    def test_no_configuration_after_change_fails(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock"},
            validation_results=[
                (authselect.AuthselectValidationStatus.NO_CONFIGURATION, False),
            ],
        )

        result = self.run_failure(
            {
                "features": ["with-mkhomedir"],
                "validate": True,
            },
            fake,
        )

        self.assertTrue(result["changed"])
        self.assertEqual(
            fake.current_features,
            {"with-faillock", "with-mkhomedir"},
        )

    # ------------------------------------------------------------------
    # Backup and rollback
    # ------------------------------------------------------------------

    def test_rollback_on_failure_does_not_create_backup_when_no_change_needed(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock"},
        )

        result = self.run_success(
            {
                "features": ["with-faillock"],
                "rollback_on_failure": True,
            },
            fake,
        )

        self.assertFalse(result["changed"])
        self.assertEqual(fake.create_backup_calls, [])
        self.assertEqual(fake.restore_backup_calls, [])
        self.assertEqual(fake.remove_backup_calls, [])
        self.assertEqual(fake.activate_calls, [])

    def test_rollback_enabled_successful_change_creates_and_removes_backup(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock"},
        )

        result = self.run_success(
            {
                "features": ["with-mkhomedir"],
                "rollback_on_failure": True,
            },
            fake,
        )

        self.assertTrue(result["changed"])
        self.assertEqual(len(fake.create_backup_calls), 1)
        self.assertEqual(fake.restore_backup_calls, [])
        self.assertEqual(fake.remove_backup_calls, fake.create_backup_calls)
        self.assertEqual(fake.backups, {})
        self.assertEqual(fake.events, ["create_backup", "activate", "remove_backup"])

    def test_create_backup_failure_prevents_activation(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock"},
            create_backup_exception=RuntimeError("backup creation failed"),
        )

        result = self.run_failure(
            {
                "features": ["with-mkhomedir"],
                "rollback_on_failure": True,
            },
            fake,
        )

        self.assertFalse(result["changed"])
        self.assertIn("backup creation failed", result["msg"])
        self.assertEqual(fake.activate_calls, [])
        self.assertEqual(fake.restore_backup_calls, [])

    def test_activation_failure_rolls_back_and_removes_backup(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock"},
            activate_exception=RuntimeError("activation failed"),
        )

        result = self.run_failure(
            {
                "features": ["with-mkhomedir"],
                "rollback_on_failure": True,
            },
            fake,
        )

        self.assertFalse(result["changed"])
        self.assertIn("activation failed", result["msg"])
        self.assertEqual(fake.current_profile, "sssd")
        self.assertEqual(fake.current_features, {"with-faillock"})
        self.assertEqual(len(fake.restore_backup_calls), 1)
        self.assertEqual(len(fake.remove_backup_calls), 1)
        self.assertEqual(fake.backups, {})
        self.assertEqual(
            fake.events,
            ["create_backup", "activate", "restore_backup", "remove_backup"],
        )

    def test_validate_changes_failure_rolls_back_even_when_validate_false(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock"},
            apply_activation=False,
        )

        result = self.run_failure(
            {
                "features": ["with-mkhomedir"],
                "rollback_on_failure": True,
            },
            fake,
        )

        self.assertFalse(result["changed"])
        self.assertIn("does not match what was declared", result["msg"])
        self.assertEqual(fake.current_features, {"with-faillock"})
        self.assertEqual(len(fake.restore_backup_calls), 1)

    def test_post_change_validation_failure_rolls_back(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock"},
            validation_results=[
                (None, True),
                (None, False),
                (None, True),
            ],
        )

        result = self.run_failure(
            {
                "features": ["with-mkhomedir"],
                "validate": True,
                "rollback_on_failure": True,
            },
            fake,
        )

        self.assertFalse(result["changed"])
        self.assertEqual(fake.current_features, {"with-faillock"})
        self.assertEqual(fake.validate_calls, 3)
        self.assertEqual(
            fake.events,
            [
                "validate",
                "create_backup",
                "activate",
                "validate",
                "restore_backup",
                "validate",
                "remove_backup",
            ],
        )

    def test_rollback_failure_preserves_backup_and_reports_both_failures(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock"},
            activate_exception=RuntimeError("activation failed"),
            restore_backup_exception=RuntimeError("restore failed"),
        )

        result = self.run_failure(
            {
                "features": ["with-mkhomedir"],
                "rollback_on_failure": True,
            },
            fake,
        )

        self.assertFalse(result["changed"])
        self.assertIn("activation failed", result["msg"])
        self.assertIn("restore failed", result["msg"])
        self.assertIn("was preserved", result["msg"])
        self.assertEqual(len(fake.backups), 1)
        self.assertEqual(fake.remove_backup_calls, [])

    def test_validation_after_rollback_failure_preserves_backup(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock"},
            validation_results=[
                (None, True),
                (None, False),
                (None, False),
            ],
        )

        result = self.run_failure(
            {
                "features": ["with-mkhomedir"],
                "validate": True,
                "rollback_on_failure": True,
            },
            fake,
        )

        self.assertFalse(result["changed"])
        self.assertIn("Validation after backup also failed", result["msg"])
        self.assertIn("was preserved", result["msg"])
        self.assertEqual(len(fake.backups), 1)
        self.assertEqual(fake.remove_backup_calls, [])

    def test_backup_delete_failure_after_rollback_reports_failure_and_preserves_backup(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock"},
            activate_exception=RuntimeError("activation failed"),
            remove_backup_exception=RuntimeError("delete failed"),
        )

        result = self.run_failure(
            {
                "features": ["with-mkhomedir"],
                "rollback_on_failure": True,
            },
            fake,
        )

        self.assertFalse(result["changed"])
        self.assertIn("activation failed", result["msg"])
        self.assertIn("delete failed", result["msg"])
        self.assertIn("was preserved", result["msg"])
        self.assertEqual(len(fake.backups), 1)

    def test_backup_delete_failure_after_success_does_not_rollback_valid_change(self):
        fake = FakeAuthselect(
            current_profile="sssd",
            current_features={"with-faillock"},
            remove_backup_exception=RuntimeError("delete failed"),
        )

        result = self.run_failure(
            {
                "features": ["with-mkhomedir"],
                "rollback_on_failure": True,
            },
            fake,
        )

        self.assertTrue(result["changed"])
        self.assertIn("delete failed", result["msg"])
        self.assertEqual(
            fake.current_features,
            {"with-faillock", "with-mkhomedir"},
        )
        self.assertEqual(fake.restore_backup_calls, [])
        self.assertEqual(len(fake.backups), 1)
