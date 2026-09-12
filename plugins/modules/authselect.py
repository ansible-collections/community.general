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
    type: str

  features:
    description:
      - Optional authselect profile features to manage.
      - When O(state=present), all listed features are enabled.
      - When O(state=absent), all listed features are disabled.
      - Features not listed are left unchanged unless
        O(profile) is changed.
      - If O(profile) is omitted, features are managed on the
        currently active profile.
      - When O(state=present) changes the active profile, exactly the
        features listed in O(features) are enabled on the new profile.
        If O(features) is omitted, no optional features are enabled.
      - When O(state=absent) and the profile specified is not
        the currently active profile, no feature changes are made.
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
      - In check mode, the existing configuration is validated because
        predicted changes are not applied.
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
      - Used when applying profile or feature changes.
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
from typing import Optional

from ansible_collections.community.general.plugins.module_utils._authselect.authselect import (
    Authselect,
    AuthselectValidationStatus,
)
from ansible_collections.community.general.plugins.module_utils._module_helper import (
    StateModuleHelper,
)


class AuthselectModule(StateModuleHelper):
    TEMP_BACKUP_NAME: str = "ansible-tmp-backup-{0}"

    module = dict(
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

    def __init_module__(self):
        self.authselect = Authselect()
        self.current_profile = self.authselect.get_current_profile_id()
        self.current_features = self.authselect.get_current_features()
        self.requested_features = self.vars.features or []
        self.requested_profile = self.vars.profile

    def validate_configuration(self):
        validation_status, is_valid = self.authselect.validate_configuration()

        if validation_status is AuthselectValidationStatus.NOT_MANAGED:
            if self.vars.state == "absent" or not self.vars.force or self.changed:
                # `force` in authselect can be used to take over an unmanaged configuration
                # We want to error for this AFTER a configuration change has happened.
                # If `state` is absent then you also have a problem because you cannot remove things from
                # a profile that does not exist.
                self.do_raise("authselect does not currently manage the systems authentication configuration")

        elif validation_status is AuthselectValidationStatus.NO_CONFIGURATION:
            if self.vars.state == "absent" or self.changed:
                self.do_raise("there currently is no authselect configuration.")

        else:
            if not is_valid:
                self.do_raise("the current authselect configuration is not valid")

        return

    def create_backup(self) -> str:
        backup_name = self.TEMP_BACKUP_NAME.format(time.time_ns())
        self.authselect.create_profile_backup(backup_name)
        return backup_name

    def is_current_authselect_profile_set(self) -> bool:
        return self.current_profile is not None

    def is_profile_requested(self) -> bool:
        return bool(self.requested_profile)

    def absent_validate_requested_authselect_profile(self) -> None:
        if self.is_profile_requested() and not self.is_current_authselect_profile_set():
            self.do_raise("there are no currently configured authselect profiles")
        return

    def validate_requested_authselect_profile(self) -> None:
        # Ensure requested profile is valid if set
        all_authselect_profiles = self.authselect.get_profiles_list()

        if self.requested_profile and (self.requested_profile not in all_authselect_profiles):
            self.do_raise(f"not a valid authselect profile: {self.requested_profile}")

        if not self.is_current_authselect_profile_set() and not self.is_profile_requested():
            self.do_raise("there are no currently configured authselect profiles")

        return

    def present_validate_requested_authselect_features(self, final_profile: str) -> None:
        with self.authselect.get_profile(final_profile) as profile:
            all_features = profile.features

        all_invalid_requested_features = {feature for feature in self.requested_features if feature not in all_features}

        if all_invalid_requested_features:
            self.do_raise(f"not valid profile features: {', '.join(sorted(all_invalid_requested_features))}")
        return

    def present_get_final_profile(self) -> str:
        return self.requested_profile or self.current_profile

    def present_get_final_features(self, final_profile: str) -> set[str]:
        # When changing profiles, only use the provided, if any, features.
        # When profile is the same, just add on any new features
        # This is how authselect actually functions.
        if final_profile != self.current_profile:
            final_features = set(self.requested_features)
        else:
            final_features = set(self.current_features) | set(self.requested_features)
        return final_features

    def changes_needed(self, final_profile: str, final_features: set[str]) -> bool:
        return (self.current_profile != final_profile) or (set(self.current_features) != final_features)

    @staticmethod
    def _get_error_message(exception: Exception) -> str:
        if message := getattr(exception, "msg", None):
            return message
        else:
            return str(exception)

    def _handle_config_rollback_error(self, rollback_error: Exception, operation_error_message) -> None:
        # The configuration might still reflect the attempted change.
        rollback_error_message = self._get_error_message(rollback_error)
        self.changed = True
        self.do_raise(
            f"unable to apply authselect changes: {operation_error_message}. "
            f"rollback also failed: {rollback_error_message}"
        )

    def _handle_activate_profile_error(self, operation_error: Exception, backup_name: Optional[str]) -> None:
        operation_error_message = self._get_error_message(operation_error)
        if backup_name is None:
            self.do_raise(f"unable to apply authselect changes: {operation_error_message}")

        try:
            self.authselect.restore_profile_backup(backup_name)
            self.changed = False

            if self.vars.validate:
                self.validate_configuration()

        except Exception as rollback_error:
            self._handle_config_rollback_error(rollback_error, operation_error_message)

        try:
            self.authselect.remove_profile_backup(backup_name)
        except Exception as cleanup_error:
            # Rollback succeeded, so the effective configuration is unchanged.
            cleanup_error_message = self._get_error_message(cleanup_error)
            self.do_raise(
                f"unable to apply authselect changes: {operation_error_message}. "
                f"the original configuration was restored, but temporary "
                f"backup {backup_name} could not be removed: {cleanup_error_message}"
            )

        self.do_raise(
            f"unable to apply authselect changes: {operation_error_message}. the original configuration was restored"
        )

    def make_changes(self, final_profile: str, final_features: set[str]) -> None:
        backup_name = None
        if self.vars.rollback_on_failure:
            if self.vars.validate:
                self.validate_configuration()
            backup_name = self.create_backup()

        try:
            self.authselect.activate_profile(
                profile_id=final_profile,
                features=sorted(final_features),
                force_overwrite=self.vars.force,
            )

            self.changed = True

            # This must be inside the try so failure triggers rollback
            if self.vars.validate:
                self.validate_configuration()
        except Exception as operation_error:
            self._handle_activate_profile_error(operation_error, backup_name)

        if backup_name is not None:
            try:
                self.authselect.remove_profile_backup(backup_name)
            except Exception as exception:
                self.do_raise(
                    f"authselect changes were applied, but unable to remove "
                    f"temporary backup {backup_name}: "
                    f"{self._get_error_message(exception)}"
                )
        return

    def state_absent(self):
        self.absent_validate_requested_authselect_profile()
        self.validate_requested_authselect_profile()

        if self.requested_profile and self.requested_profile != self.current_profile:
            # Return here, no changes need to be made.
            # Module behavior is defined that when state is absent, the only thing that can be changed
            # are the features.
            # if the requested profile is different from the current profile, then no change occurs.

            self.update_output(
                profile=self.current_profile,
                features=sorted(self.current_features or []),
            )

            if self.vars.validate:
                self.validate_configuration()

            return

        final_profile = self.current_profile

        # No validation is done on features because invalid feature names are intentionally ignored for `state: absent`.
        # This allows users to ensure features are absent regardless of whether
        # they are supported by the currently active profile.
        final_features = set(self.current_features) - set(self.requested_features)

        self.update_output(
            profile=final_profile,
            features=sorted(final_features),
        )

        if not self.changes_needed(final_profile, final_features):
            if self.vars.validate:
                self.validate_configuration()
            return

        if self.check_mode:
            if self.vars.validate:
                self.validate_configuration()

            self.changed = True
            return

        self.make_changes(final_profile, final_features)

        return

    def state_present(self):
        self.validate_requested_authselect_profile()
        final_profile = self.present_get_final_profile()
        self.present_validate_requested_authselect_features(final_profile)
        final_features = self.present_get_final_features(final_profile)

        self.update_output(
            profile=final_profile,
            features=sorted(final_features),
        )

        if not self.changes_needed(final_profile, final_features):
            if self.vars.validate:
                self.validate_configuration()
            return

        if self.check_mode:
            if self.vars.validate:
                self.validate_configuration()

            self.changed = True
            return

        self.make_changes(final_profile, final_features)

        return


def main():
    AuthselectModule().run()


if __name__ == "__main__":
    main()
