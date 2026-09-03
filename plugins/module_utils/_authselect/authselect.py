# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import ctypes
import errno
import os
from typing import Optional

from .authselect_enums import AuthselectValidationStatus
from .authselect_lib import get_authselect_lib
from .authselect_profile import AuthselectProfile
from .c_array import CStringArray, NullTerminatedStringArray
from .c_string import AllocatedCString


class Authselect:
    def __init__(self):
        self._lib = get_authselect_lib()

    def get_profiles_list(self) -> list[str]:
        with self._lib.authselect_list() as profiles:
            return list(profiles)

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
