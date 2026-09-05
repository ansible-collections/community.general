#!/usr/bin/python

# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: authselect
short_description: Manage authselect profiles and profile features
version_added: 13.4.0
description:
  - Manage the active authselect profile and its enabled optional features.
  - The module uses the libauthselect shared library directly.
  - Feature management is additive or subtractive when the requested
    profile is already active.
  - When changing to another profile, the features specified by
    O(features) become the enabled optional features for the newly
    selected profile.
author:
  - Nicholas Brodersen (@NicholasBrodersen)
requirements:
  - libauthselect
extends_documentation_fragment:
  - community.general._attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  profile:
    description:
      - Name of the authselect profile to manage.
      - When O(state=present), the specified profile is made active
        if it is not already active.
      - When O(state=absent), the profile itself is not removed or
        deactivated.
      - With O(state=absent), features are only removed when this
        profile is currently active.
      - At least one of O(profile) or O(features) must be specified.
    type: str

  features:
    description:
      - Optional authselect profile features to manage.
      - When O(state=present), all listed features are enabled.
      - Features that are already enabled are left unchanged.
      - Other enabled features are preserved when the active profile
        is not changed.
      - When O(state=absent), all listed features are disabled.
      - Features not listed are left unchanged.
      - If O(profile) is omitted, features are managed on the
        currently active profile.
      - When changing to another profile, the listed features become
        the optional features enabled for that profile.
      - At least one of O(profile) or O(features) must be specified.
    type: list
    elements: str

  state:
    description:
      - Desired state of the specified profile features.
      - When V(present), O(profile), if supplied, is made active and
        the listed features are enabled.
      - When V(absent), the listed features are disabled.
      - V(absent) does not remove profiles, uninstall authselect, or
        switch profiles.
    type: str
    choices:
      - present
      - absent
    default: present

  validate:
    description:
      - Validate the authselect configuration.
      - Validation occurs even when no configuration change is required.
      - Normally validation occurs after requested changes are applied.
      - When O(rollback_on_failure=true), an existing authselect-managed
        configuration is validated before changes are attempted and the
        resulting configuration is validated after changes are applied.
    type: bool
    default: false

  rollback_on_failure:
    description:
      - Restore the authentication configuration to its pre-change
        state if applying the requested change or post-change validation
        fails.
      - A temporary authselect backup is created before required changes.
      - The temporary backup is removed after successful completion.
      - If a change fails, the backup is restored and removed after a
        successful rollback.
      - The task still fails after a successful rollback.
      - Has no effect when no configuration change is required.
    type: bool
    default: false

  force:
    description:
      - Allow authselect to overwrite an authentication configuration
        that is not currently managed by authselect.
      - Applies only when activating or changing the selected profile.
      - When V(false), the module fails rather than overwrite an
        unmanaged authentication configuration.
    type: bool
    default: false
"""

EXAMPLES = r"""
- name: Ensure SSSD is the active authselect profile
  community.general.authselect:
    profile: sssd

- name: Ensure features are enabled on the current profile
  community.general.authselect:
    features:
      - with-faillock
      - with-mkhomedir

- name: Ensure SSSD is active with required features
  community.general.authselect:
    profile: sssd
    features:
      - with-faillock
      - with-mkhomedir

- name: Disable features on the current profile
  community.general.authselect:
    features:
      - with-faillock
      - with-mkhomedir
    state: absent

- name: Configure and validate with automatic rollback
  community.general.authselect:
    profile: sssd
    features:
      - with-faillock
      - with-mkhomedir
    validate: true
    rollback_on_failure: true

- name: Take over an unmanaged configuration
  community.general.authselect:
    profile: sssd
    features:
      - with-faillock
      - with-mkhomedir
    force: true
"""

RETURN = r"""
profile:
  description:
    - Active authselect profile after module execution.
    - In check mode, when a change would be required, this is the
      profile that would be active after applying the requested changes.
  returned: success
  type: str
  sample: sssd

features:
  description:
    - Enabled optional features on the active authselect profile after
      module execution.
    - In check mode, when a change would be required, these are the
      features that would be enabled after applying the requested changes.
  returned: success
  type: list
  elements: str
  sample:
    - with-faillock
    - with-mkhomedir
"""

import time
from enum import Enum, auto
from typing import Callable, List, NoReturn, cast

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.general.plugins.module_utils._authselect.authselect import (
    Authselect,
    AuthselectValidationStatus,
)


class AuthselectProfileState(Enum):
    PRESENT = "present"
    ABSENT = "absent"


class IncorrectAuthselectStateError(Exception):
    pass


class AuthselectProfileNotValidError(Exception):
    pass


class AuthselectFeatureNotValid(Exception):
    pass


class AuthselectConfigurationNotValidError(Exception):
    pass


class AuthselectError(Exception):
    pass


# Attached to Enum states
class AuthselectState(Enum):
    ValidateProfile = auto()
    ValidateFeatures = auto()

    DetermineFinalProfile = auto()
    DetermineFinalFeatures = auto()

    DetermineIfChangesAreNeeded = auto()

    MakeChanges = auto()
    ValidateChanges = auto()

    SuccessExit = auto()
    FailExit = auto()

    ValidateConfig = auto()

    CreateBackup = auto()
    RevertFromBackup = auto()
    RemoveBackup = auto()


class AuthselectModule:
    TEMP_BACKUP_NAME: str = "ansible-tmp-backup-{0}"

    def __init__(self, module: AnsibleModule):
        self.ansible_module: AnsibleModule = module
        self.authselect: Authselect = Authselect()

        self.failure: Exception | None = None

        self.changes_needed = False
        self.changes_made = False

        self.requested_profile: str = self._get_requested_authselect_profile()
        self.current_profile: str = self._get_current_authselect_profile()

        self.requested_features: set[str] = self._get_requested_authselect_features()
        self.current_features: set[str] = self._get_current_authselect_features()

        self.requested_state: AuthselectProfileState = self._get_authselect_state_requested()

        self.validate: bool = self._is_authselect_validate_requested()

        self.force: bool = self._is_authselect_force_requested()

        self.backup: bool = self._is_authselect_backup_requested()
        self.backup_name: str = self._get_authselect_backup_name()
        self.backup_created: bool = False
        self.rollback_required: bool = False

        self.final_profile: str = ""
        self.final_features: set[str] = set()

    def __iter__(self):
        # This acts as the modules state machine

        # First the profile needs to validated.
        # Then the final requested profile needs to be determined because validating the state depends on it.
        yield AuthselectState.ValidateProfile

        if self.requested_state is AuthselectProfileState.ABSENT:
            if self.is_authselect_profile_requested() and self.is_current_authselect_profile_set():
                if self.requested_profile != self.current_profile:
                    # Return here, no changes need to be made.
                    # Module behavior is defined that when state is absent, the only thing that can be changed
                    # are the features.
                    # if the requested name if different from the current, then no change occurs.
                    if self.validate:
                        yield AuthselectState.ValidateConfig
                    yield AuthselectState.SuccessExit
                    return

        yield AuthselectState.DetermineFinalProfile

        yield AuthselectState.ValidateFeatures

        yield AuthselectState.DetermineFinalFeatures

        yield AuthselectState.DetermineIfChangesAreNeeded

        if not self.changes_needed:
            if self.validate:
                yield AuthselectState.ValidateConfig
            yield AuthselectState.SuccessExit
            return

        if self.ansible_module.check_mode:
            if self.validate:
                yield AuthselectState.ValidateConfig
            yield AuthselectState.SuccessExit
            return

        if self.backup:
            if self.validate:
                yield AuthselectState.ValidateConfig
            yield AuthselectState.CreateBackup

        yield AuthselectState.MakeChanges

        yield AuthselectState.ValidateChanges

        if self.validate:
            yield AuthselectState.ValidateConfig

        if self.backup and self.backup_created:
            yield AuthselectState.RemoveBackup

        yield AuthselectState.SuccessExit

        return

    def __call__(self) -> None:
        state_to_function: dict[AuthselectState, Callable] = self._get_state_to_function_mapping()

        for state in self:
            # SuccessExit is the normal end of module execution.
            # Keep it outside the failure handler so a successful exit is not treated like an error.
            if state is AuthselectState.SuccessExit:
                state_to_function[state]()
                return

            try:
                state_to_function[state]()
            except Exception as exception:
                self._handle_module_failure(exception=exception, state_to_function=state_to_function)
        return

    def _handle_module_failure(self, exception: Exception, state_to_function: dict[AuthselectState, Callable]):
        self.failure = exception
        if self.rollback_required and self.backup_created:
            try:
                state_to_function[AuthselectState.RevertFromBackup]()
            except Exception as rollback_exception:
                self.failure = AuthselectError(
                    f"{self.failure}. "
                    f"Rollback also failed: {rollback_exception}. "
                    f"Backup '{self.backup_name}' was preserved."
                )
                state_to_function[AuthselectState.FailExit]()
                return

            try:
                if self.validate:
                    state_to_function[AuthselectState.ValidateConfig]()
            except Exception as validate_exception:
                self.failure = AuthselectError(
                    f"{self.failure}. "
                    f"Validation after backup also failed: {validate_exception}. "
                    f"Backup '{self.backup_name}' was preserved."
                )
                state_to_function[AuthselectState.FailExit]()
                return

            try:
                state_to_function[AuthselectState.RemoveBackup]()
            except Exception as delete_backup_exception:
                self.failure = AuthselectError(
                    f"{self.failure}. "
                    f"Unable to delete backup: {delete_backup_exception}. "
                    f"Backup '{self.backup_name}' was preserved."
                )
                state_to_function[AuthselectState.FailExit]()
                return

        state_to_function[AuthselectState.FailExit]()

    def _get_state_to_function_mapping(self) -> dict[AuthselectState, Callable]:
        return {
            AuthselectState.ValidateProfile: self.validate_requested_authselect_profile,
            AuthselectState.ValidateFeatures: self.validate_requested_authselect_features,
            AuthselectState.DetermineFinalProfile: self.determine_final_authselect_profile,
            AuthselectState.DetermineFinalFeatures: self.determine_final_authselect_features,
            AuthselectState.DetermineIfChangesAreNeeded: self.determine_if_changes_are_needed,
            AuthselectState.MakeChanges: self.make_changes,
            AuthselectState.ValidateChanges: self.validate_changes,
            AuthselectState.SuccessExit: self.success_exit,
            AuthselectState.FailExit: self.fail_exit,
            AuthselectState.ValidateConfig: self.validate_config,
            AuthselectState.CreateBackup: self.create_backup,
            AuthselectState.RevertFromBackup: self.revert_from_backup,
            AuthselectState.RemoveBackup: self.remove_backup,
        }

    def is_authselect_profile_requested(self) -> bool:
        return bool(self.ansible_module.params.get("profile", False))

    def _get_requested_authselect_profile(self) -> str:
        if self.is_authselect_profile_requested():
            return self.ansible_module.params["profile"]
        else:
            return ""

    def is_current_authselect_profile_set(self) -> bool:
        return self.authselect.get_current_profile_id() is not None

    def _get_current_authselect_profile(self):
        if self.is_current_authselect_profile_set():
            return self.authselect.get_current_profile_id()
        else:
            return ""

    def is_authselect_features_requested(self) -> bool:
        return bool(self.ansible_module.params.get("features", False))

    def _get_requested_authselect_features(self) -> set[str]:
        if self.is_authselect_features_requested():
            return set(self.ansible_module.params["features"])
        else:
            return set()

    def is_current_authselect_features_set(self) -> bool:
        return self.authselect.get_current_features() is not None

    def _get_current_authselect_features(self) -> set[str]:
        if self.is_current_authselect_features_set():
            return set(cast(List[str], self.authselect.get_current_features()))
        else:
            return set()

    def _get_authselect_state_requested(self) -> AuthselectProfileState:
        try:
            return AuthselectProfileState(self.ansible_module.params["state"])
        except ValueError:
            raise IncorrectAuthselectStateError('State must be "present" or "absent".') from None

    def _is_authselect_validate_requested(self) -> bool:
        return self.ansible_module.params["validate"]

    def _is_authselect_force_requested(self) -> bool:
        return self.ansible_module.params["force"]

    def _is_authselect_backup_requested(self) -> bool:
        return self.ansible_module.params["rollback_on_failure"]

    def _get_authselect_backup_name(self) -> str:
        if self._is_authselect_backup_requested():
            return self.TEMP_BACKUP_NAME.format(time.time_ns())
        else:
            return ""

    #################
    # State methods #
    #################
    def validate_requested_authselect_profile(self) -> None:
        # Ensure requested profile is valid if set
        all_authselect_profiles = self.authselect.get_profiles_list()
        if self.is_authselect_profile_requested():
            if self.requested_profile not in all_authselect_profiles:
                raise AuthselectProfileNotValidError(
                    f"the requested authselect profile {self.requested_profile} is not a valid authselect profile. "
                    f"Valid authselect profiles: {', '.join(all_authselect_profiles)}"
                )
        return

    def determine_final_authselect_profile(self) -> None:
        profile_requested: bool = self.is_authselect_profile_requested()
        current_profile_set: bool = self.is_current_authselect_profile_set()
        module_state: AuthselectProfileState = self.requested_state

        if not current_profile_set and not profile_requested:
            raise AuthselectProfileNotValidError(
                "There are no currently configured authselect profiles. Please specify one."
            )

        if module_state is AuthselectProfileState.ABSENT and profile_requested and not current_profile_set:
            raise AuthselectProfileNotValidError(
                "There are no currently configured authselect profiles. Activate a profile first to use `absent`."
            )

        if module_state is AuthselectProfileState.ABSENT:
            if profile_requested and current_profile_set:
                if self.requested_profile == self.current_profile:
                    self.final_profile = self.current_profile

            elif not profile_requested and current_profile_set:
                self.final_profile = self.current_profile

        elif module_state is AuthselectProfileState.PRESENT:
            if profile_requested and current_profile_set:
                self.final_profile = self.requested_profile

            elif profile_requested and not current_profile_set:
                self.final_profile = self.requested_profile

            elif not profile_requested and current_profile_set:
                self.final_profile = self.current_profile
        return

    def validate_requested_authselect_features(self) -> None:
        with self.authselect.get_profile(self.final_profile) as profile:
            all_features = profile.features

        all_invalid_requested_features = {feature for feature in self.requested_features if feature not in all_features}

        # Invalid feature names are intentionally ignored for state=absent.
        # This allows users to ensure features are absent regardless of whether
        # they are supported by the currently active profile.
        if self.requested_state is AuthselectProfileState.PRESENT and all_invalid_requested_features:
            raise AuthselectFeatureNotValid(
                f"The requested features {', '.join(all_invalid_requested_features)} "
                f"are not valid for the profile {self.final_profile}. "
                f"All valid features for the {self.final_profile} profile are: "
                f"{', '.join(all_features)}"
            )

    def determine_final_authselect_features(self) -> None:
        if self.requested_state is AuthselectProfileState.ABSENT:
            self.final_features = self.current_features - self.requested_features
        elif self.requested_state is AuthselectProfileState.PRESENT:
            if self.final_profile != self.current_profile:
                self.final_features = self.requested_features
            else:
                self.final_features = self.current_features | self.requested_features
        return

    def determine_if_changes_are_needed(self) -> None:
        self.changes_needed = self.final_profile != self.current_profile or self.final_features != self.current_features
        return

    def make_changes(self) -> None:
        self.authselect.activate_profile(
            profile_id=self.final_profile,
            features=sorted(self.final_features),
            force_overwrite=self.force,
        )
        self.changes_made = True
        return

    def validate_changes(self) -> None:
        new_profile: str = self.authselect.get_current_profile_id() or ""
        new_features: set[str] = set(self.authselect.get_current_features() or set())

        profiles_match: bool = new_profile == self.final_profile
        features_match: bool = new_features == self.final_features

        if not profiles_match or not features_match:
            raise AuthselectError(
                "Authselect configuration does not match what was declared! "
                f'Profile requested: "{self.final_profile}". '
                f'Profile currently set: "{new_profile}". '
                f"Features requested: {', '.join(sorted(self.final_features))}. "
                f"Features currently configured: {', '.join(sorted(new_features))}."
            )

    def success_exit(self) -> NoReturn:
        if self.ansible_module.check_mode and self.changes_needed and not self.changes_made:
            profile = self.final_profile
            features = self.final_features
            changed = True
        else:
            profile = self.authselect.get_current_profile_id() or ""
            features = set(self.authselect.get_current_features() or set())
            changed = self.changes_made

        self.ansible_module.exit_json(
            changed=changed,
            profile=profile,
            features=sorted(features),
        )

    def fail_exit(self) -> NoReturn:
        if self.failure is None:
            raise RuntimeError("FailExit was reached without a recorded failure.")

        self.ansible_module.fail_json(
            changed=self.changes_made,
            msg=str(self.failure),
        )

    def validate_config(self) -> None:
        validation_status, is_valid = self.authselect.validate_configuration()
        if validation_status is AuthselectValidationStatus.NOT_MANAGED:
            if self.requested_state is AuthselectProfileState.ABSENT or not self.force or self.changes_made:
                # `force` can be used to take over an unmanaged configuration
                # We want to error for this AFTER a configuration change has happened.
                # If state is absent then you also have a problem because you cannot remove things from
                # a profile that does not exist
                raise AuthselectConfigurationNotValidError(
                    "Authselect does not currently manage the system authentication configuration."
                )
            return

        elif validation_status is AuthselectValidationStatus.NO_CONFIGURATION:
            if self.requested_state is AuthselectProfileState.ABSENT or self.changes_made:
                raise AuthselectConfigurationNotValidError("There currently is no Authselect configuration.")
            return

        if not is_valid:
            current_profile = self.authselect.get_current_profile_id() or ""
            current_features = set(self.authselect.get_current_features() or set())

            raise AuthselectConfigurationNotValidError(
                "The current configuration is not valid. "
                f"Profile: {current_profile}. "
                f"Features: {', '.join(sorted(current_features))}."
            )
        return

    def create_backup(self) -> None:
        self.authselect.create_profile_backup(self.backup_name)
        self.backup_created = True
        self.rollback_required = True
        return

    def revert_from_backup(self) -> None:
        self.authselect.restore_profile_backup(self.backup_name)
        self.changes_made = False
        return

    def remove_backup(self) -> None:
        self.rollback_required = False
        self.authselect.remove_profile_backup(self.backup_name)
        self.backup_created = False
        return


def main():
    module = AnsibleModule(
        argument_spec={
            "profile": {
                "type": "str",
            },
            "features": {
                "type": "list",
                "elements": "str",
            },
            "state": {
                "type": "str",
                "choices": ["present", "absent"],
                "default": "present",
            },
            "validate": {
                "type": "bool",
                "default": False,
            },
            "rollback_on_failure": {
                "type": "bool",
                "default": False,
            },
            "force": {
                "type": "bool",
                "default": False,
            },
        },
        required_one_of=[
            ["profile", "features"],
        ],
        required_if=[
            ["state", "absent", ["features"]],
        ],
        supports_check_mode=True,
    )

    # __call__ is the entry point into the module running
    AuthselectModule(module)()


if __name__ == "__main__":
    main()
