# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json

import pytest
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import set_module_args

from ansible_collections.community.general.plugins.module_utils._module_helper import ModuleHelperException
from ansible_collections.community.general.plugins.modules import authselect

VALID = (authselect.AuthselectValidationStatus.VALIDATION_COMPLETE, True)
INVALID = (authselect.AuthselectValidationStatus.VALIDATION_COMPLETE, False)
NOT_MANAGED = (authselect.AuthselectValidationStatus.NOT_MANAGED, False)
NO_CONFIGURATION = (authselect.AuthselectValidationStatus.NO_CONFIGURATION, False)


@pytest.fixture
def backend(mocker):
    backend = mocker.MagicMock(spec=authselect.Authselect)
    backend.get_current_profile_id.return_value = "sssd"
    backend.get_current_features.return_value = ["with-sudo", "with-faillock"]
    backend.validate_configuration.return_value = VALID
    profiles = {}
    for name, features in {
        "sssd": {"with-faillock", "with-mkhomedir", "with-sudo"},
        "minimal": {"with-faillock", "with-mkhomedir"},
    }.items():
        profile = mocker.MagicMock()
        profile.__enter__.return_value.features = features
        profiles[name] = profile
    backend.get_profiles_list.return_value = list(profiles)
    backend.get_profile.side_effect = profiles.__getitem__
    mocker.patch.object(authselect, "Authselect", return_value=backend)
    return backend


@pytest.fixture
def run_module(capsys):
    def run(failed=False, **params):
        with set_module_args(params):
            with pytest.raises(SystemExit):
                authselect.main()
        result = json.loads(capsys.readouterr().out)
        assert result.get("failed", False) is failed
        return result

    return run


def configuration_calls(backend):
    return [
        call
        for call in backend.method_calls
        if call[0]
        in {
            "activate_profile",
            "validate_configuration",
            "create_profile_backup",
            "restore_profile_backup",
            "remove_profile_backup",
        }
    ]


@pytest.mark.parametrize("check_mode", [False, True], ids=["apply", "check"])
@pytest.mark.parametrize("profile", [None, "sssd"], ids=["current", "named"])
@pytest.mark.parametrize(
    "state, requested, expected",
    [
        ("present", ["with-mkhomedir", "with-mkhomedir"], ["with-faillock", "with-mkhomedir", "with-sudo"]),
        ("absent", ["with-faillock", "not-a-feature", "with-faillock"], ["with-sudo"]),
    ],
)
def test_feature_changes_preserve_unrequested_features(
    backend, run_module, mocker, state, requested, expected, profile, check_mode
):
    result = run_module(
        state=state,
        profile=profile,
        features=requested,
        force=True,
        _ansible_check_mode=check_mode,
        rollback_on_failure=check_mode,
    )

    assert result["changed"] is True
    assert (result["profile"], result["features"]) == ("sssd", expected)
    assert configuration_calls(backend) == (
        []
        if check_mode
        else [
            mocker.call.activate_profile(profile_id="sssd", features=expected, force_overwrite=True),
        ]
    )


@pytest.mark.parametrize("check_mode", [False, True], ids=["apply", "check"])
@pytest.mark.parametrize("features", [None, ["with-mkhomedir"]], ids=["no-features", "explicit-features"])
def test_switching_profiles_replaces_features(backend, run_module, mocker, features, check_mode):
    result = run_module(profile="minimal", features=features, _ansible_check_mode=check_mode)

    assert result["changed"] is True
    assert (result["profile"], result["features"]) == ("minimal", features or [])
    assert configuration_calls(backend) == (
        []
        if check_mode
        else [
            mocker.call.activate_profile(profile_id="minimal", features=features or [], force_overwrite=False),
        ]
    )


@pytest.mark.parametrize("validate", [False, True])
@pytest.mark.parametrize(
    "params",
    [
        pytest.param({"profile": "sssd"}, id="same-profile"),
        pytest.param({"features": ["with-faillock"]}, id="enabled-feature"),
        pytest.param({"features": []}, id="empty-present"),
        pytest.param({"state": "absent", "features": []}, id="empty-absent"),
        pytest.param({"state": "absent", "features": ["with-mkhomedir", "unknown"]}, id="missing-features"),
        pytest.param({"state": "absent", "profile": "minimal", "features": ["with-sudo"]}, id="inactive-profile"),
        pytest.param({"features": ["with-faillock"], "_ansible_check_mode": True}, id="check-no-change"),
    ],
)
def test_no_change_leaves_configuration_and_backups_alone(backend, run_module, mocker, params, validate):
    result = run_module(**params, validate=validate, rollback_on_failure=True)

    assert result["changed"] is False
    assert (result["profile"], result["features"]) == ("sssd", ["with-faillock", "with-sudo"])
    assert configuration_calls(backend) == ([mocker.call.validate_configuration()] if validate else [])


@pytest.mark.parametrize(
    "params, invalid_value",
    [
        ({"profile": "missing"}, "missing"),
        ({"state": "absent", "profile": "missing", "features": []}, "missing"),
        ({"features": ["unknown"]}, "unknown"),
        ({"profile": "minimal", "features": ["with-sudo"]}, "with-sudo"),
    ],
)
def test_invalid_requests_fail_before_writing(backend, run_module, params, invalid_value):
    result = run_module(failed=True, **params)

    assert invalid_value in result["msg"]
    assert configuration_calls(backend) == []


@pytest.mark.parametrize("params", [{}, {"state": "absent"}, {"state": "absent", "profile": "sssd"}])
def test_features_require_an_active_profile(backend, run_module, params):
    backend.get_current_profile_id.return_value = None
    backend.get_current_features.return_value = None

    run_module(failed=True, features=["with-mkhomedir"], **params)

    backend.get_profile.assert_not_called()
    assert configuration_calls(backend) == []


@pytest.mark.parametrize(
    "params",
    [
        pytest.param({"features": ["with-faillock"]}, id="unchanged-present"),
        pytest.param({"state": "absent", "features": ["with-mkhomedir"]}, id="unchanged-absent"),
        pytest.param({"state": "absent", "profile": "minimal", "features": ["with-sudo"]}, id="inactive-profile"),
        pytest.param({"features": ["with-mkhomedir"], "_ansible_check_mode": True}, id="check-present"),
        pytest.param({"state": "absent", "features": ["with-sudo"], "_ansible_check_mode": True}, id="check-absent"),
        pytest.param({"features": ["with-mkhomedir"], "rollback_on_failure": True}, id="before-backup"),
    ],
)
def test_invalid_existing_configuration_stops_before_writing(backend, run_module, mocker, params):
    backend.validate_configuration.return_value = INVALID

    run_module(failed=True, validate=True, **params)

    assert configuration_calls(backend) == [mocker.call.validate_configuration()]


@pytest.mark.parametrize("state", ["present", "absent"])
def test_check_mode_validates_without_creating_backups(backend, run_module, mocker, state):
    result = run_module(
        state=state,
        features=["with-faillock", "with-mkhomedir"],
        validate=True,
        rollback_on_failure=True,
        _ansible_check_mode=True,
    )

    assert result["changed"] is True
    assert configuration_calls(backend) == [mocker.call.validate_configuration()]


@pytest.mark.parametrize(
    "status, state, force",
    [(NOT_MANAGED, "present", False), (NOT_MANAGED, "absent", True), (NO_CONFIGURATION, "absent", False)],
)
def test_unmanaged_or_missing_configuration_is_not_safe_to_modify(backend, run_module, mocker, status, state, force):
    backend.validate_configuration.return_value = status

    run_module(
        failed=True,
        state=state,
        features=["with-faillock", "with-mkhomedir"],
        validate=True,
        rollback_on_failure=True,
        force=force,
    )

    assert configuration_calls(backend) == [mocker.call.validate_configuration()]


@pytest.mark.parametrize("status, force", [(NO_CONFIGURATION, False), (NOT_MANAGED, True)])
def test_initial_configuration_and_forced_takeover_are_allowed(backend, run_module, status, force):
    backend.get_current_profile_id.return_value = None
    backend.get_current_features.return_value = None
    backend.validate_configuration.side_effect = [status, VALID]

    result = run_module(profile="sssd", validate=True, rollback_on_failure=True, force=force)

    assert result["changed"] is True
    assert (result["profile"], result["features"]) == ("sssd", [])
    backend.activate_profile.assert_called_once_with(profile_id="sssd", features=[], force_overwrite=force)


@pytest.mark.parametrize("status", [INVALID, NOT_MANAGED, NO_CONFIGURATION], ids=["invalid", "unmanaged", "missing"])
@pytest.mark.parametrize("state", ["present", "absent"])
def test_post_change_validation_cannot_be_bypassed_by_force(backend, run_module, mocker, state, status):
    backend.validate_configuration.return_value = status
    features = ["with-faillock", "with-mkhomedir"]
    expected = ["with-faillock", "with-mkhomedir", "with-sudo"] if state == "present" else ["with-sudo"]

    run_module(failed=True, state=state, features=features, validate=True, force=True)

    assert configuration_calls(backend) == [
        mocker.call.activate_profile(profile_id="sssd", features=expected, force_overwrite=True),
        mocker.call.validate_configuration(),
    ]


@pytest.mark.parametrize("validate", [False, True])
def test_successful_change_discards_temporary_backup(backend, run_module, mocker, validate):
    result = run_module(features=["with-mkhomedir"], rollback_on_failure=True, validate=validate)
    backup = backend.create_profile_backup.call_args[0][0]
    validation = [mocker.call.validate_configuration()] if validate else []

    assert result["changed"] is True
    assert configuration_calls(backend) == validation + [
        mocker.call.create_profile_backup(backup),
        mocker.call.activate_profile(
            profile_id="sssd", features=["with-faillock", "with-mkhomedir", "with-sudo"], force_overwrite=False
        ),
    ] + validation + [mocker.call.remove_profile_backup(backup)]


def test_backup_failure_prevents_activation(backend, run_module):
    backend.create_profile_backup.side_effect = RuntimeError("backup unavailable")

    run_module(failed=True, features=["with-mkhomedir"], rollback_on_failure=True)

    backend.activate_profile.assert_not_called()
    backend.restore_profile_backup.assert_not_called()
    backend.remove_profile_backup.assert_not_called()


@pytest.mark.parametrize("error_type", [RuntimeError, ModuleHelperException])
@pytest.mark.parametrize("rollback", [False, True])
def test_activation_failure_preserves_cause_and_rolls_back_only_when_requested(
    backend, run_module, mocker, error_type, rollback
):
    cause = "injected activation failure"
    backend.activate_profile.side_effect = error_type(cause)

    result = run_module(failed=True, features=["with-mkhomedir"], rollback_on_failure=rollback)

    assert cause in result["msg"]
    expected = [
        mocker.call.activate_profile(
            profile_id="sssd",
            features=["with-faillock", "with-mkhomedir", "with-sudo"],
            force_overwrite=False,
        )
    ]
    if rollback:
        backup = backend.create_profile_backup.call_args[0][0]
        expected = (
            [mocker.call.create_profile_backup(backup)]
            + expected
            + [
                mocker.call.restore_profile_backup(backup),
                mocker.call.remove_profile_backup(backup),
            ]
        )
    assert configuration_calls(backend) == expected


@pytest.mark.parametrize("initial_status, force", [(VALID, False), (NOT_MANAGED, True)], ids=["managed", "unmanaged"])
@pytest.mark.parametrize("rollback_valid", [True, False], ids=["restored", "restored-but-invalid"])
def test_failed_validation_restores_and_revalidates_before_cleanup(
    backend, run_module, mocker, initial_status, force, rollback_valid
):
    backend.validate_configuration.side_effect = [
        initial_status,
        INVALID,
        initial_status if rollback_valid else INVALID,
    ]

    run_module(failed=True, features=["with-mkhomedir"], validate=True, rollback_on_failure=True, force=force)
    backup = backend.create_profile_backup.call_args[0][0]

    expected = [
        mocker.call.validate_configuration(),
        mocker.call.create_profile_backup(backup),
        mocker.call.activate_profile(
            profile_id="sssd", features=["with-faillock", "with-mkhomedir", "with-sudo"], force_overwrite=force
        ),
        mocker.call.validate_configuration(),
        mocker.call.restore_profile_backup(backup),
        mocker.call.validate_configuration(),
    ]
    if rollback_valid:
        expected.append(mocker.call.remove_profile_backup(backup))
    assert configuration_calls(backend) == expected


def test_failed_restore_preserves_backup_and_both_causes(backend, run_module):
    operation_cause, restore_cause = "injected activation failure", "injected restore failure"
    backend.activate_profile.side_effect = RuntimeError(operation_cause)
    backend.restore_profile_backup.side_effect = RuntimeError(restore_cause)

    result = run_module(failed=True, features=["with-mkhomedir"], rollback_on_failure=True)

    assert operation_cause in result["msg"]
    assert restore_cause in result["msg"]
    backend.restore_profile_backup.assert_called_once_with(backend.create_profile_backup.call_args[0][0])
    backend.remove_profile_backup.assert_not_called()


@pytest.mark.parametrize("error_type", [RuntimeError, ModuleHelperException])
def test_cleanup_failure_after_rollback_preserves_both_causes(backend, run_module, error_type):
    operation_cause, cleanup_cause = "injected activation failure", "injected cleanup failure"
    backend.activate_profile.side_effect = error_type(operation_cause)
    backend.remove_profile_backup.side_effect = RuntimeError(cleanup_cause)

    result = run_module(failed=True, features=["with-mkhomedir"], rollback_on_failure=True)
    backup = backend.create_profile_backup.call_args[0][0]

    assert operation_cause in result["msg"]
    assert cleanup_cause in result["msg"]
    assert backup in result["msg"]
    backend.restore_profile_backup.assert_called_once_with(backup)
    backend.remove_profile_backup.assert_called_once_with(backup)


def test_cleanup_failure_does_not_rollback_a_successful_change(backend, run_module):
    cause = "injected cleanup failure"
    backend.remove_profile_backup.side_effect = RuntimeError(cause)

    result = run_module(failed=True, features=["with-mkhomedir"], rollback_on_failure=True)
    backup = backend.create_profile_backup.call_args[0][0]

    assert cause in result["msg"]
    assert backup in result["msg"]
    backend.activate_profile.assert_called_once_with(
        profile_id="sssd",
        features=["with-faillock", "with-mkhomedir", "with-sudo"],
        force_overwrite=False,
    )
    backend.restore_profile_backup.assert_not_called()
    backend.remove_profile_backup.assert_called_once_with(backup)
