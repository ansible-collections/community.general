# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import ctypes
import errno
import os
from typing import Optional

from .authselect_enums import AuthselectProfileType, AuthselectSymlinkFlag, AuthselectValidationStatus
from .authselect_files import AuthselectFiles
from .authselect_lib import get_authselect_lib
from .authselect_profile import AuthselectProfile
from .c_array import CStringArray, NullTerminatedStringArray
from .c_string import AllocatedCString


class Authselect:
    def __init__(self):
        self._lib = get_authselect_lib()

    def get_nsswitch_path(self) -> str:
        return self._lib.authselect_path_nsswitch().decode("utf-8")

    def get_systemauth_path(self) -> str:
        return self._lib.authselect_path_systemauth().decode("utf-8")

    def get_passwordauth_path(self) -> str:
        return self._lib.authselect_path_passwordauth().decode("utf-8")

    def get_smartcardauth_path(self) -> str:
        return self._lib.authselect_path_smartcardauth().decode("utf-8")

    def get_fingerprintauth_path(self) -> str:
        return self._lib.authselect_path_fingerprintauth().decode("utf-8")

    def get_switchableauth_path(self) -> str:
        if not hasattr(self._lib, "authselect_path_switchableauth"):
            raise RuntimeError("The installed libauthselect does not support switchable-auth")

        return self._lib.authselect_path_switchableauth().decode("utf-8")

    def get_postlogin_path(self) -> str:
        return self._lib.authselect_path_postlogin().decode("utf-8")

    def get_dconf_db_path(self) -> str:
        return self._lib.authselect_path_dconf_db().decode("utf-8")

    def get_dconf_lock_path(self) -> str:
        return self._lib.authselect_path_dconf_lock().decode("utf-8")

    def get_profiles_list(self) -> list[str]:
        with self._lib.authselect_list() as profiles:
            return list(profiles)

    def get_backups_list(self) -> list[str]:
        with self._lib.authselect_backup_list() as backup_list:
            return list(backup_list)

    def get_profile(self, profile_id: str) -> AuthselectProfile:
        profile = AuthselectProfile()

        result = self._lib.authselect_profile(
            profile_id.encode("utf-8"),
            ctypes.byref(profile),
        )

        if result != 0:
            raise RuntimeError(f"authselect_profile() failed: [{result}] {os.strerror(result)}")

        if not profile:
            raise RuntimeError("authselect_profile() returned a NULL profile")

        return profile

    def get_files(self, profile_id: str, features: list[str] | None = None) -> AuthselectFiles:
        files = AuthselectFiles()
        c_features = CStringArray.from_strings(features or [])
        result = self._lib.authselect_files(profile_id.encode("utf-8"), c_features, ctypes.byref(files))

        if result == errno.ENOENT:
            raise RuntimeError(f"Authselect profile '{profile_id}' does not exist")

        if result != 0:
            raise RuntimeError(f"authselect_files() failed: [{result}] {os.strerror(result)}")

        if not files:
            raise RuntimeError("authselect_files() succeeded but returned a NULL AuthselectFiles pointer")

        return files

    def get_current_profile_id(self) -> Optional[str]:
        profile_id = AllocatedCString()

        result = self._lib.authselect_current_configuration(ctypes.byref(profile_id), None)

        if result == errno.ENOENT:
            return None

        if result != 0:
            raise RuntimeError(f"authselect_current_configuration() failed: [{result}] {os.strerror(result)}")

        if not profile_id:
            raise RuntimeError("authselect_current_configuration() returned a NULL profile ID")

        with profile_id:
            return profile_id.decode()

    def activate_profile(
        self, profile_id: str, features: list[str] | None = None, force_overwrite: bool = False
    ) -> None:

        c_features = CStringArray.from_strings(features or [])

        result = self._lib.authselect_activate(profile_id.encode("utf-8"), c_features, force_overwrite)

        if result == 0:
            return

        if result == errno.ENOENT:
            raise RuntimeError(f"Authselect profile '{profile_id}' does not exist")

        if result == errno.EINVAL:
            raise RuntimeError(f"One or more features are not supported by profile '{profile_id}'")

        if result == errno.EEXIST:
            raise RuntimeError(
                "Existing system authentication configuration prevents authselect from activating the profile"
            )

        if result == errno.EACCES:
            raise PermissionError(f"Permission denied while activating authselect profile '{profile_id}'")

        raise RuntimeError(f"authselect_activate() failed: [{result}] {os.strerror(result)}")

    def get_current_features(self) -> Optional[list[str]]:
        features = NullTerminatedStringArray()
        profile_id = AllocatedCString()

        result = self._lib.authselect_current_configuration(ctypes.byref(profile_id), ctypes.byref(features))

        if result == errno.ENOENT:
            return None

        if result != 0:
            raise RuntimeError(f"authselect_current_configuration() failed: [{result}] {os.strerror(result)}")
        try:
            if not features:
                raise RuntimeError("authselect_current_configuration() succeeded but returned NULL features")

            with features:
                return list(features)
        finally:
            if profile_id:
                profile_id.close()

    def validate_configuration(self) -> tuple[AuthselectValidationStatus, bool]:
        is_valid = ctypes.c_bool()
        result = self._lib.authselect_validate_configuration(ctypes.byref(is_valid))
        try:
            status = AuthselectValidationStatus(result)
        except ValueError:
            raise RuntimeError(
                f"authselect_validate_configuration() failed: [{result}] {os.strerror(result)}"
            ) from None

        return status, is_valid.value

    def is_feature_enabled(self, feature: str) -> bool:
        if not hasattr(self._lib, "authselect_feature_enabled"):
            raise RuntimeError("The installed libauthselect does not support authselect_feature_enabled()")
        result = self._lib.authselect_feature_enabled(feature.encode("utf-8"))

        if result == 0:
            return True

        if result == errno.ENOENT:
            return False

        raise RuntimeError(f"authselect_feature_enabled() failed: [{result}] {os.strerror(result)}")

    def enable_feature(self, feature: str) -> None:
        result = self._lib.authselect_feature_enable(feature.encode("utf-8"))

        if result == 0:
            return

        if result == errno.ENOENT:
            raise RuntimeError("Cannot enable feature because there is no existing authselect configuration")

        raise RuntimeError(f"authselect_apply_changes() failed: [{result}] {os.strerror(result)}")

    def disable_feature(self, feature: str) -> None:
        result = self._lib.authselect_feature_disable(feature.encode("utf-8"))

        if result == 0:
            return

        if result == errno.ENOENT:
            raise RuntimeError("Cannot disable feature because there is no existing authselect configuration")

        raise RuntimeError(f"authselect_apply_changes() failed: [{result}] {os.strerror(result)}")

    def apply_changes(self, upgrade: bool = False) -> bool:
        result = self._lib.authselect_apply_changes(upgrade)

        if result == 0:
            return True

        if result == errno.EAGAIN:
            return False

        if result == errno.ENOENT:
            raise RuntimeError("No existing authselect configuration")

        if result == errno.EEXIST:
            raise RuntimeError("Existing configuration is not managed by authselect")

        raise RuntimeError(f"authselect_apply_changes() failed: [{result}] {os.strerror(result)}")

    def create_profile_backup(self, name: str | None = None) -> str:
        path = AllocatedCString()
        c_name = None if name is None else name.encode("utf-8")
        result = self._lib.authselect_backup(c_name, ctypes.byref(path))

        if result != 0:
            raise RuntimeError(f"authselect_backup() failed: [{result}] {os.strerror(result)}")

        if not path:
            raise RuntimeError("authselect_backup() succeeded but returned a NULL path")

        with path:
            return path.decode()

    def remove_profile_backup(self, name: str) -> None:
        result = self._lib.authselect_backup_remove(name.encode("utf-8"))

        if result != 0:
            raise RuntimeError(f"authselect_backup_remove() failed: [{result}] {os.strerror(result)}")

    def restore_profile_backup(self, name: str) -> None:
        result = self._lib.authselect_backup_restore(name.encode("utf-8"))

        if result != 0:
            raise RuntimeError(f"authselect_backup_restore() failed: [{result}] {os.strerror(result)}")

    def create_profile(
        self,
        name: str,
        profile_type: AuthselectProfileType,
        base_id: str | None = None,
        base_type: AuthselectProfileType = AuthselectProfileType.ANY,
        symlink_flags: AuthselectSymlinkFlag = AuthselectSymlinkFlag.NONE,
        symlinks: list[str] | None = None,
    ) -> str:

        path = AllocatedCString()
        c_symlinks = CStringArray.from_strings(symlinks or [])

        result = self._lib.authselect_profile_create(
            name.encode("utf-8"),
            int(profile_type),
            (None if base_id is None else base_id.encode("utf-8")),
            int(base_type),
            int(symlink_flags),
            c_symlinks,
            ctypes.byref(path),
        )

        if result == errno.EEXIST:
            raise RuntimeError(f"Authselect profile '{name}' already exists")

        if result == errno.ENOENT:
            raise RuntimeError(f"Base authselect profile '{base_id}' does not exist")

        if result == errno.EINVAL:
            raise RuntimeError("Invalid arguments supplied to authselect_profile_create()")

        if result != 0:
            raise RuntimeError(f"authselect_profile_create() failed: [{result}] {os.strerror(result)}")

        if not path:
            raise RuntimeError("authselect_profile_create() succeeded but returned a NULL path")

        with path:
            return path.decode()

    def uninstall(self) -> None:
        result = self._lib.authselect_uninstall()

        if result != 0:
            raise RuntimeError(f"authselect_backup_restore() failed: [{result}] {os.strerror(result)}")
