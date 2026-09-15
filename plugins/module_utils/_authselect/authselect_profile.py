# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import ctypes
from typing import Callable

from .c_array import NullTerminatedStringArray


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
    _get_features: Callable[[AuthselectProfile], NullTerminatedStringArray | None] | None = None

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
