# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import ctypes
from typing import Callable


class _AuthselectFilesStruct(ctypes.Structure):
    """
    struct authselect_files;
    This is just placeholder meant to represent a struct that exists.
    """

    pass


class AuthselectFiles(ctypes.POINTER(_AuthselectFilesStruct)):  # type: ignore[misc]
    _type_ = _AuthselectFilesStruct

    #
    # Populated by authselect_lib.py
    #
    _free: Callable[[AuthselectFiles], None] | None = None
    _get_nsswitch: Callable[[AuthselectFiles], bytes | None] | None = None
    _get_systemauth: Callable[[AuthselectFiles], bytes | None] | None = None
    _get_passwordauth: Callable[[AuthselectFiles], bytes | None] | None = None
    _get_smartcardauth: Callable[[AuthselectFiles], bytes | None] | None = None
    _get_fingerprintauth: Callable[[AuthselectFiles], bytes | None] | None = None
    _get_switchableauth: Callable[[AuthselectFiles], bytes | None] | None = None
    _get_postlogin: Callable[[AuthselectFiles], bytes | None] | None = None
    _get_dconf_db: Callable[[AuthselectFiles], bytes | None] | None = None
    _get_dconf_lock: Callable[[AuthselectFiles], bytes | None] | None = None

    def __enter__(self):
        self._assert_valid()
        return self

    def __exit__(self, *args) -> None:
        self.close()

    def _assert_valid(self) -> None:
        if not self:
            raise RuntimeError("AuthselectFiles pointer is NULL")

        if getattr(self, "_closed", False):
            raise RuntimeError("AuthselectFiles has already been freed")

    def close(self) -> None:
        if not self:
            return

        if getattr(self, "_closed", False):
            return

        free = type(self)._free

        if free is None:
            raise RuntimeError("AuthselectFiles free function has not been configured")

        free(self)
        self._closed = True

    @property
    def nsswitch(self) -> str | None:
        self._assert_valid()

        nsswitch = type(self)._get_nsswitch

        if nsswitch is None:
            raise RuntimeError("AuthselectFiles nsswitch function has not been configured")

        value = nsswitch(self)
        return None if value is None else value.decode("utf-8")

    @property
    def systemauth(self) -> str | None:
        self._assert_valid()

        systemauth = type(self)._get_systemauth

        if systemauth is None:
            raise RuntimeError("The installed libauthselect does not support system-auth")

        value = systemauth(self)

        return None if value is None else value.decode("utf-8")

    @property
    def passwordauth(self) -> str | None:
        self._assert_valid()

        passwordauth = type(self)._get_passwordauth

        if passwordauth is None:
            raise RuntimeError("The installed libauthselect does not support password-auth")

        value = passwordauth(self)

        return None if value is None else value.decode("utf-8")

    @property
    def smartcardauth(self) -> str | None:
        self._assert_valid()

        smartcardauth = type(self)._get_smartcardauth

        if smartcardauth is None:
            raise RuntimeError("The installed libauthselect does not support smartcard-auth")

        value = smartcardauth(self)

        return None if value is None else value.decode("utf-8")

    @property
    def fingerprintauth(self) -> str | None:
        self._assert_valid()

        fingerprintauth = type(self)._get_fingerprintauth

        if fingerprintauth is None:
            raise RuntimeError("The installed libauthselect does not support fingerprint-auth")

        value = fingerprintauth(self)

        return None if value is None else value.decode("utf-8")

    @property
    def switchableauth(self) -> str | None:
        self._assert_valid()

        switchableauth = type(self)._get_switchableauth

        if switchableauth is None:
            raise RuntimeError("The installed libauthselect does not support switchable-auth")

        value = switchableauth(self)
        return None if value is None else value.decode("utf-8")

    @property
    def postlogin(self) -> str | None:
        self._assert_valid()

        postlogin = type(self)._get_postlogin

        if postlogin is None:
            raise RuntimeError("AuthselectFiles postlogin function has not been configured")

        value = postlogin(self)

        return None if value is None else value.decode("utf-8")

    @property
    def dconf_db(self) -> str:
        self._assert_valid()

        dconf_db = type(self)._get_dconf_db

        if dconf_db is None:
            raise RuntimeError("AuthselectFiles dconf_db function has not been configured")

        value = dconf_db(self)

        if value is None:
            raise RuntimeError("authselect_files_dconf_db() returned NULL")

        return value.decode("utf-8")

    @property
    def dconf_lock(self) -> str:
        self._assert_valid()

        dconf_lock = type(self)._get_dconf_lock

        if dconf_lock is None:
            raise RuntimeError("AuthselectFiles dconf_lock function has not been configured")

        value = dconf_lock(self)

        if value is None:
            raise RuntimeError("authselect_files_dconf_lock() returned NULL")

        return value.decode("utf-8")
