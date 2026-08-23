# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import ctypes
from typing import Callable

from .c_array import CStringArray, NullTerminatedStringArray
from .c_string import AllocatedCString


class _AuthselectProfileStruct(ctypes.Structure):
    """
    struct authselect_profile;
    This is just placeholder meant to represent a struct that exists.
    """

    pass


class AuthselectProfile(ctypes.POINTER(_AuthselectProfileStruct)):  # type: ignore[misc]
    _type_ = _AuthselectProfileStruct

    #
    # Populated by authselect_lib.py.
    #
    _free: Callable[[AuthselectProfile], None] | None = None
    _get_id: Callable[[AuthselectProfile], bytes | None] | None = None
    _get_name: Callable[[AuthselectProfile], bytes | None] | None = None
    _get_path: Callable[[AuthselectProfile], bytes | None] | None = None
    _get_description: Callable[[AuthselectProfile], bytes | None] | None = None
    _get_features: Callable[[AuthselectProfile], NullTerminatedStringArray | None] | None = None
    _get_nsswitch_maps: Callable[[AuthselectProfile, CStringArray], NullTerminatedStringArray | None] | None = None
    _get_requirements: Callable[[AuthselectProfile, CStringArray], AllocatedCString | None] | None = None

    def __enter__(self):
        self._assert_valid()
        return self

    def __exit__(self, *args) -> None:
        self.close()

    def _assert_valid(self) -> None:
        if not self:
            raise RuntimeError("Authselect profile pointer is NULL")

        if getattr(self, "_closed", False):
            raise RuntimeError("Authselect profile has already been freed")

    def close(self) -> None:
        if not self:
            return

        if getattr(self, "_closed", False):
            return

        free = type(self)._free

        if free is None:
            raise RuntimeError("AuthselectProfile free function has not been configured")

        free(self)
        self._closed = True

    @property
    def id(self) -> str:
        self._assert_valid()

        get_id = type(self)._get_id

        if get_id is None:
            raise RuntimeError("AuthselectProfile id function has not been configured")

        value = get_id(self)

        if value is None:
            raise RuntimeError("authselect_profile_id() returned NULL")

        return value.decode("utf-8")

    @property
    def name(self) -> str:
        self._assert_valid()

        name = type(self)._get_name

        if name is None:
            raise RuntimeError("AuthselectProfile name function has not been configured")

        value = name(self)

        if value is None:
            raise RuntimeError("authselect_profile_name() returned NULL")

        return value.decode("utf-8")

    @property
    def path(self) -> str:
        self._assert_valid()

        path = type(self)._get_path

        if path is None:
            raise RuntimeError("AuthselectProfile path function has not been configured")

        value = path(self)

        if value is None:
            raise RuntimeError("authselect_profile_path() returned NULL")

        return value.decode("utf-8")

    @property
    def description(self) -> str | None:
        self._assert_valid()

        description = type(self)._get_description

        if description is None:
            raise RuntimeError("AuthselectProfile description function has not been configured")

        value = description(self)

        return None if value is None else value.decode("utf-8")

    @property
    def features(self) -> list[str]:
        self._assert_valid()

        features = type(self)._get_features

        if features is None:
            raise RuntimeError("AuthselectProfile features function has not been configured")

        values = features(self)

        if not values:
            raise RuntimeError("authselect_profile_features() returned NULL")

        with values:
            return list(values)

    def nsswitch_maps(self, features: list[str] | None = None) -> list[str]:
        self._assert_valid()
        c_features = CStringArray.from_strings(features or [])
        nsswitch_maps = type(self)._get_nsswitch_maps

        if nsswitch_maps is None:
            raise RuntimeError("AuthselectProfile nsswitch_maps function has not been configured")

        values = nsswitch_maps(self, c_features)

        if not values:
            raise RuntimeError("authselect_profile_nsswitch_maps() returned NULL")

        with values:
            return list(values)

    def requirements(self, features: list[str] | None = None) -> str:
        self._assert_valid()

        c_features = CStringArray.from_strings(features or [])
        get_requirements = type(self)._get_requirements

        if get_requirements is None:
            raise RuntimeError("AuthselectProfile requirements function has not been configured")

        value = get_requirements(self, c_features)

        if not value:
            raise RuntimeError("authselect_profile_requirements() returned NULL")

        with value:
            return value.decode("utf-8")
