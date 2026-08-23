from __future__ import annotations

import ctypes

from .c_array import CStringArray


class _AuthselectProfileStruct(ctypes.Structure):
    """
    struct authselect_profile;
    This is just placeholder meant to represent a struct that exists.
    """

    pass


class AuthselectProfile(ctypes.POINTER(_AuthselectProfileStruct)):
    _type_ = _AuthselectProfileStruct

    #
    # Populated by authselect_lib.py.
    #
    _free = None
    _get_id = None
    _get_name = None
    _get_path = None
    _get_description = None
    _get_features = None
    _get_nsswitch_maps = None
    _get_requirements = None

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

        if type(self)._free is None:
            raise RuntimeError("AuthselectProfile free function has not been configured")

        type(self)._free(self)
        self._closed = True

    @property
    def id(self) -> str:
        self._assert_valid()

        value = type(self)._get_id(self)

        if value is None:
            raise RuntimeError("authselect_profile_id() returned NULL")

        return value.decode("utf-8")

    @property
    def name(self) -> str:
        self._assert_valid()

        value = type(self)._get_name(self)

        if value is None:
            raise RuntimeError("authselect_profile_name() returned NULL")

        return value.decode("utf-8")

    @property
    def path(self) -> str:
        self._assert_valid()

        value = type(self)._get_path(self)

        if value is None:
            raise RuntimeError("authselect_profile_path() returned NULL")

        return value.decode("utf-8")

    @property
    def description(self) -> str | None:
        self._assert_valid()

        value = type(self)._get_description(self)

        return None if value is None else value.decode("utf-8")

    @property
    def features(self) -> list[str]:
        self._assert_valid()

        values = type(self)._get_features(self)

        if not values:
            raise RuntimeError("authselect_profile_features() returned NULL")

        with values:
            return list(values)

    def nsswitch_maps(self, features: list[str] | None = None) -> list[str]:
        self._assert_valid()
        c_features = CStringArray.from_strings(features or [])
        values = type(self)._get_nsswitch_maps(self, c_features)

        if not values:
            raise RuntimeError("authselect_profile_nsswitch_maps() returned NULL")

        with values:
            return list(values)

    def requirements(self, features: list[str] | None = None) -> str:
        self._assert_valid()

        c_features = CStringArray.from_strings(features or [])

        value = type(self)._get_requirements(self, c_features)

        if not value:
            raise RuntimeError("authselect_profile_requirements() returned NULL")

        with value:
            return value.decode("utf-8")
