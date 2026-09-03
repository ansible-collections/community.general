# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import errno
from enum import IntEnum


class AuthselectValidationStatus(IntEnum):
    VALIDATION_COMPLETE = 0
    NO_CONFIGURATION = errno.ENOENT
    NOT_MANAGED = errno.EEXIST
