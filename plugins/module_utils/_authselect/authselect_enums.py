# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import errno
from enum import IntEnum, IntFlag
from typing import cast


class AuthselectValidationStatus(IntEnum):
    VALIDATION_COMPLETE = 0
    NO_CONFIGURATION = errno.ENOENT
    NOT_MANAGED = errno.EEXIST


class AuthselectProfileType(IntEnum):
    DEFAULT = 0
    VENDOR = 1
    CUSTOM = 2
    ANY = 3

    def __str__(self) -> str:
        return self.name.lower()

    @classmethod
    def from_string(cls, value: str) -> AuthselectProfileType:
        try:
            return cls[value.upper()]
        except KeyError:
            raise ValueError(f"Invalid authselect profile type: {value}") from None


class AuthselectSymlinkFlag(IntFlag):
    NONE = 0x0000
    META = 0x0001
    NSSWITCH = 0x0002
    PAM = 0x0004
    DCONF = 0x0008

    def __str__(self) -> str:
        return "|".join(self.to_strings()) or "none"

    def to_strings(self) -> list[str]:
        return [
            cast(str, flag.name).lower()
            for flag in AuthselectSymlinkFlag
            if (flag is not AuthselectSymlinkFlag.NONE and flag in self)
        ]

    @classmethod
    def from_string(cls, value: str) -> AuthselectSymlinkFlag:
        try:
            return cls[value.upper()]
        except KeyError:
            raise ValueError(f"Invalid authselect symlink flag: {value}") from None

    @classmethod
    def from_strings(cls, values: list[str]) -> AuthselectSymlinkFlag:
        flags = cls.NONE

        for value in values:
            flags |= cls.from_string(value)

        return flags
