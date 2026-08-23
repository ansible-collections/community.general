from __future__ import annotations

import ctypes


class _AuthselectFilesStruct(ctypes.Structure):
    """
    struct authselect_files;
    This is just placeholder meant to represent a struct that exists.
    """

    pass


class AuthselectFiles(ctypes.POINTER(_AuthselectFilesStruct)):
    _type_ = _AuthselectFilesStruct

    #
    # Populated by authselect_lib.py
    #
    _free = None
    _get_nsswitch = None
    _get_systemauth = None
    _get_passwordauth = None
    _get_smartcardauth = None
    _get_fingerprintauth = None
    _get_switchableauth = None
    _get_postlogin = None
    _get_dconf_db = None
    _get_dconf_lock = None

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

        if type(self)._free is None:
            raise RuntimeError("AuthselectFiles free function has not been configured")

        type(self)._free(self)
        self._closed = True

    @property
    def nsswitch(self) -> str | None:
        self._assert_valid()
        value = type(self)._get_nsswitch(self)
        return None if value is None else value.decode("utf-8")

    @property
    def systemauth(self) -> str | None:
        self._assert_valid()
        value = type(self)._get_systemauth(self)
        return None if value is None else value.decode("utf-8")

    @property
    def passwordauth(self) -> str | None:
        self._assert_valid()
        value = type(self)._get_passwordauth(self)
        return None if value is None else value.decode("utf-8")

    @property
    def smartcardauth(self) -> str | None:
        self._assert_valid()
        value = type(self)._get_smartcardauth(self)
        return None if value is None else value.decode("utf-8")

    @property
    def fingerprintauth(self) -> str | None:
        self._assert_valid()
        value = type(self)._get_fingerprintauth(self)
        return None if value is None else value.decode("utf-8")

    @property
    def switchableauth(self) -> str | None:
        self._assert_valid()

        if type(self)._get_switchableauth is None:
            raise RuntimeError(
                "The installed libauthselect does not support switchable-auth"
            )

        value = type(self)._get_switchableauth(self)
        return None if value is None else value.decode("utf-8")

    @property
    def postlogin(self) -> str | None:
        self._assert_valid()
        value = type(self)._get_postlogin(self)
        return None if value is None else value.decode("utf-8")

    @property
    def dconf_db(self) -> str:
        self._assert_valid()
        value = type(self)._get_dconf_db(self)

        if value is None:
            raise RuntimeError("authselect_files_dconf_db() returned NULL")

        return value.decode("utf-8")

    @property
    def dconf_lock(self) -> str:
        self._assert_valid()
        value = type(self)._get_dconf_lock(self)

        if value is None:
            raise RuntimeError("authselect_files_dconf_lock() returned NULL")

        return value.decode("utf-8")
